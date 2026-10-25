"""Ensemble evaluator for BERT detectors: average probabilities across models, tune the
decision threshold on VALIDATION only, report every subset, then write predictions once.

  # see what is best on validation (singles, pairs, full ensemble):
  .venv/bin/python bert_ensemble.py --dirs outputs/bert_tune/p1 outputs/bert_tune/s1 outputs/bert_tune/s2 \
      --val-input data/val/input.jsonl --val-gold data/val/gold.jsonl --input data/test/input.jsonl \
      --out /dev/null

Selection rule: best VAL F1 among subsets (never test). The chosen subset is printed with
[SELECTED]; re-run with the same --dirs to write real predictions for predict/score.
"""

import argparse, json, itertools, os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pipeline import bert_text, extract_detail, prf

ap = argparse.ArgumentParser()
ap.add_argument("--dirs", nargs="+", required=True)
ap.add_argument("--val-input", default="data/val/input.jsonl")
ap.add_argument("--val-gold", default="data/val/gold.jsonl")
ap.add_argument("--input", default="data/test/input.jsonl")
ap.add_argument("--out", default="outputs/pred_bert.jsonl")
ap.add_argument("--threads", type=int, default=6)
a = ap.parse_args()
torch.set_num_threads(a.threads)

L = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
val = L(a.val_input)
vg = {x["id"]: x for x in L(a.val_gold)}
val = [r for r in val if r["id"] in vg]
ys = [int(vg[r["id"]]["is_action"]) for r in val]

models = []
for d in a.dirs:
    m = AutoModelForSequenceClassification.from_pretrained(d)
    m.eval()
    models.append((m, AutoTokenizer.from_pretrained(d)))
    th = json.load(open(os.path.join(d, "threshold.json")))["threshold"] if os.path.exists(
        os.path.join(d, "threshold.json")) else None
    print(f"loaded {d}" + (f" (its own val threshold {th})" if th else ""))


def probs(subset, rows):
    out = []
    for i in range(0, len(rows), 16):
        chunk = rows[i : i + 16]
        acc = None
        for mi in subset:
            m, tok = models[mi]
            enc = tok([bert_text(r["turns"]) for r in chunk], return_tensors="pt",
                      truncation=True, max_length=256, padding=True)
            with torch.no_grad():
                p = torch.softmax(m(**enc).logits, -1)[:, 1]
            acc = p if acc is None else acc + p
        out += (acc / len(subset)).tolist()
    return out


def best_f1(ps, step=0.01):
    best = (-1.0, 0.5, 0.0, 0.0)
    th = step
    while th < 1.0:
        tp = sum(1 for p, y in zip(ps, ys) if y and p >= th)
        fp = sum(1 for p, y in zip(ps, ys) if not y and p >= th)
        fn = sum(1 for p, y in zip(ps, ys) if y and p < th)
        P, R, F = prf(tp, fp, fn)
        if F > best[0]:
            best = (F, th, P, R)
        th = round(th + step, 2)
    return best


names = [os.path.basename(d.rstrip("/")) for d in a.dirs]
print(f"\nvalidation selection ({len(val)} contexts, {sum(ys)} positives):")
best = None
for k in range(1, len(a.dirs) + 1):
    for sub in itertools.combinations(range(len(a.dirs)), k):
        f1, th, P, R = best_f1(probs(sub, val))
        label = "+".join(names[i] for i in sub)
        print(f"  {label:24} val F1={f1:.3f} (P={P:.3f} R={R:.3f}) th={th:.2f}")
        if best is None or f1 > best[0]:
            best = (f1, th, sub)
print(f"\n[SELECTED by val] {'+'.join(names[i] for i in best[2])}  val F1={best[0]:.3f} th={best[1]:.2f}")

# one test pass with the val-selected subset
test = L(a.input)
ps = probs(best[2], test)
det = lambda turns: probs(best[2], [ {"turns": turns} ])[0] >= best[1]
n = 0
with open(a.out, "w", encoding="utf-8") as f:
    for c in test:
        d = extract_detail(c["turns"], det)
        row = {"id": c["id"], "is_action": d is not None,
               "person": d["person"] if d else None,
               "action": d["action"] if d else None,
               "deadline": d["deadline"] if d else None}
        if d:
            row.update(commit_turn=d["commit_turn"], person_turn=d["person_turn"],
                       action_turn=d["action_turn"], deadline_turn=d["deadline_turn"])
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        n += 1
print(f"wrote {n} predictions -> {a.out}  (ensemble: {'+'.join(names[i] for i in best[2])}, th={best[1]:.2f})")
