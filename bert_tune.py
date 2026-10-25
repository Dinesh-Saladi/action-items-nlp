"""Validation-only hyperparameter sweep for the BERT detector (companion to train_bert.py).

  .venv/bin/python bert_tune.py --run "p0;max_length=128,epochs=15,lr=5e-5,pos_mult=4,seed=0"
  .venv/bin/python bert_tune.py --run "p1;max_length=256,epochs=15,lr=5e-5,pos_mult=4,seed=0"

- selection = best VALIDATION detection F1 with a fine threshold grid (0.01); the test split is
  NEVER touched here (evaluate the winner afterwards with predict.py + score.py).
- hand-rolled training loop (no Trainer) so every epoch's validation probabilities are available
- options: max_length, epochs, lr, batch, pos_mult, seed, warmup, avg_k (average the k epoch
  checkpoints with the highest validation F1), class_weight (CE class weighting, 0 = off)
- writes outputs/bert_tune/<name>/{model,tokenizer,threshold.json,run.json}
"""

import argparse, json, os, time, random
import torch
from torch.utils.data import DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from pipeline import bert_text, prf

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True, help='"name;key=val,key=val"')
ap.add_argument("--train-input", default="data/train/input.jsonl")
ap.add_argument("--train-gold", default="data/train/gold.jsonl")
ap.add_argument("--val-input", default="data/val/input.jsonl")
ap.add_argument("--val-gold", default="data/val/gold.jsonl")
ap.add_argument("--out-root", default="outputs/bert_tune")
ap.add_argument("--threads", type=int, default=6)
a = ap.parse_args()

name, _, spec = a.run.partition(";")
cfg = dict(
    model="roberta-base", epochs=15, lr=5e-5, batch=16, max_length=128,
    pos_mult=4, seed=0, warmup=10, avg_k=0, class_weight=0.0,
)
for kv in filter(None, spec.split(",")):
    k, _, v = kv.partition("=")
    assert k in cfg, f"unknown key {k}"
    cfg[k] = type(cfg[k])(v)
cfg["lr"] = float(cfg["lr"])

torch.set_num_threads(a.threads)
torch.manual_seed(cfg["seed"])
random.seed(cfg["seed"])

L = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def rows(inp, goldp):
    g = {x["id"]: x for x in L(goldp)}
    return [dict(c, is_action=g[c["id"]]["is_action"]) for c in L(inp) if c["id"] in g]


train, val = rows(a.train_input, a.train_gold), rows(a.val_input, a.val_gold)
pos = [r for r in train if r["is_action"]]
train = train + pos * (cfg["pos_mult"] - 1)
random.shuffle(train)
print(f"[{name}] train={len(train)} ({sum(r['is_action'] for r in train)} pos) "
      f"val={len(val)} ({sum(r['is_action'] for r in val)} pos) cfg={cfg}", flush=True)

tok = AutoTokenizer.from_pretrained(cfg["model"])
model = AutoModelForSequenceClassification.from_pretrained(cfg["model"], num_labels=2)


def collate(batch):
    ex = [
        {"input_ids": r["input_ids"], "attention_mask": r["attention_mask"],
         "labels": torch.tensor(int(r["is_action"]))}
        for r in batch
    ]
    ex = tok.pad(ex, return_tensors="pt")
    return ex


def enc_rows(rs):
    return [
        dict(tok(bert_text(r["turns"]), truncation=True, max_length=cfg["max_length"]),
             is_action=int(r["is_action"]))
        for r in rs
    ]


train_ds, val_ds = enc_rows(train), enc_rows(val)
val_texts = [bert_text(r["turns"]) for r in val]
ys = [int(r["is_action"]) for r in val]


def val_probs(m):
    m.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(val_ds), 32):
            b = collate(val_ds[i : i + 32])
            b.pop("labels")
            out += torch.softmax(m(**b).logits, -1)[:, 1].tolist()
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


opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=0.01)
total = len(train_ds) * cfg["epochs"]
sched = get_linear_schedule_with_warmup(
    opt, num_warmup_steps=cfg["warmup"], num_training_steps=total)
loss_f = torch.nn.CrossEntropyLoss()
if cfg["class_weight"] > 0:
    n_neg = len(train) - sum(r["is_action"] for r in train)
    w = torch.tensor([1.0, cfg["class_weight"] * n_neg / max(1, len(pos))])
    loss_f = torch.nn.CrossEntropyLoss(weight=w)
    print(f"[{name}] class weights {w.tolist()}", flush=True)

t0 = time.time(); best = (-1.0, 0, 0.5, 0.0, 0.0); last_states = []
for ep in range(1, cfg["epochs"] + 1):
    model.train()
    for b in DataLoader(train_ds, batch_size=cfg["batch"], shuffle=True, collate_fn=collate):
        opt.zero_grad(); out = model(**b)
        loss = loss_f(out.logits, b["labels"]); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step()
    f1, th, P, R = best_f1(val_probs(model))
    print(f"[{name}] epoch {ep:2}: val F1={f1:.3f} (P={P:.3f} R={R:.3f}) th={th:.2f} "
          f"{time.time()-t0:.0f}s", flush=True)
    state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    last_states.append((ep, f1, state))
    last_states = last_states[-max(2, cfg["avg_k"]):]  # keep only what averaging may need
    if f1 > best[0]:
        best = (f1, ep, th, P, R); best_state = state

f1, ep, th, P, R = best
final_state = best_state
if cfg["avg_k"] > 1 and len(last_states) >= 2:
    top = sorted(last_states, key=lambda x: -x[1])[: cfg["avg_k"]]
    if len(top) > 1:
        avg = {k: sum(s[k].float() for _, _, s in top) / len(top) for k in top[0][2]}
        final_state = {k: v.to(best_state[list(best_state)[0]].dtype) for k, v in avg.items()}
        model.load_state_dict(final_state)
        f1, th, P, R = best_f1(val_probs(model))
        print(f"[{name}] averaged {len(top)} ckpts -> val F1={f1:.3f} th={th:.2f}", flush=True)

outdir = os.path.join(a.out_root, name)
os.makedirs(outdir, exist_ok=True)
model.load_state_dict(final_state)
model.save_pretrained(outdir); tok.save_pretrained(outdir)
json.dump({"threshold": th}, open(os.path.join(outdir, "threshold.json"), "w"))
json.dump({"name": name, "cfg": cfg, "best_epoch": ep, "val_f1": f1, "val_P": P,
           "val_R": R, "threshold": th, "minutes": round((time.time() - t0) / 60, 1)},
          open(os.path.join(outdir, "run.json"), "w"), indent=1)
print(f"[{name}] DONE val F1={f1:.3f} @epoch {ep} th={th:.2f} -> {outdir}", flush=True)
