"""Step 4: run the pipeline (the 'student'). It only ever reads INPUT files. It never opens a gold
file unless you choose --detector tfidf/hybrid (train gold) or pass --val-* (validation gold, used
ONLY to pick the decision threshold / C, never test gold).

  python predict.py --input data/test/input.jsonl --out outputs/pred_rule.jsonl   --detector rule
  python predict.py --input data/test/input.jsonl --out outputs/pred_tfidf.jsonl  --detector tfidf \\
                    --train-input data/train/input.jsonl --train-gold data/train/gold.jsonl \\
                    --val-input data/val/input.jsonl --val-gold data/val/gold.jsonl
  python predict.py --input data/test/input.jsonl --out outputs/pred_bert.jsonl   --detector bert \\
                    --bert-dir outputs/bert_model

Output rows: {id, is_action, person, action, deadline} + provenance keys
(person_turn / action_turn / deadline_turn / commit_turn) that score.py uses to separate
extraction from cross-turn linking, + 'mentioned_people' (spaCy NER, supplementary, not scored).
"""

import json, argparse
from pipeline import (
    rule_detect,
    MLDetector,
    extract_detail,
    mentioned_people,
    set_spacy,
    bert_text,
)
from pipeline import prf


class BERTDetector:
    """RoBERTa/BERT sequence classifier saved by train_bert.py. Same interface as rule_detect:
    turns -> bool. Encoding MUST match train_bert.py (bert_text). The decision threshold is the one
    train_bert.py selected on the validation split (threshold.json), not a hard-coded 0.5.
    """

    def __init__(self, model_dir):
        import os
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.threshold = 0.5
        path = os.path.join(model_dir, "threshold.json")
        if os.path.exists(path):
            self.threshold = json.load(open(path)).get("threshold", 0.5)
        self.tok = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.eval()

    def __call__(self, turns):
        enc = self.tok(
            bert_text(turns), return_tensors="pt", truncation=True, max_length=128
        )
        with self.torch.no_grad():
            p = float(self.torch.softmax(self.model(**enc).logits, -1)[0][1])
        return p >= self.threshold


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True)
ap.add_argument("--out", required=True)
ap.add_argument(
    "--detector", choices=["rule", "tfidf", "hybrid", "bert"], default="rule"
)
ap.add_argument("--train-input")
ap.add_argument("--train-gold")
ap.add_argument("--val-input", help="validation contexts (threshold/C selection only)")
ap.add_argument("--val-gold", help="validation labels (threshold/C selection only)")
ap.add_argument("--bert-dir", default="outputs/bert_model")
ap.add_argument(
    "--no-spacy", action="store_true", help="disable spaCy action trimming + NER"
)
ap.add_argument(
    "--no-ner", action="store_true", help="keep provenance but skip PERSON-name NER"
)
a = ap.parse_args()
if a.no_spacy:
    set_spacy(False)


def train_rows(inp, goldp):
    g = {x["id"]: x for x in load(goldp)}
    return [
        dict(c, is_action=g[c["id"]]["is_action"]) for c in load(inp) if c["id"] in g
    ]


def det_f1(detector, rows):
    tp = fp = fn = 0
    for r in rows:
        p = bool(detector(r["turns"]))
        tp += p and r["is_action"]
        fp += p and not r["is_action"]
        fn += (not p) and r["is_action"]
    return prf(tp, fp, fn)[2]


detector = rule_detect
if a.detector in ("tfidf", "hybrid"):
    assert (
        a.train_input and a.train_gold
    ), "tfidf/hybrid need --train-input and --train-gold"
    train = train_rows(a.train_input, a.train_gold)
    hybrid = a.detector == "hybrid"
    if a.val_input and a.val_gold:
        # select threshold + C on the VALIDATION split only (test gold is never consulted)
        val = train_rows(a.val_input, a.val_gold)
        best = None
        for C in (0.25, 0.5, 1.0, 2.0):
            for th in (0.3, 0.4, 0.5, 0.6, 0.7):
                d = MLDetector(hybrid=hybrid, threshold=th, C=C).fit(train)
                s = det_f1(d, val)
                if best is None or s > best[0]:
                    best = (s, th, C)
        score, th, C = best
        print(f"val selection: detection F1={score:.3f} -> threshold={th}, C={C}")
        detector = MLDetector(hybrid=hybrid, threshold=th, C=C).fit(train)
    else:
        detector = MLDetector(hybrid=hybrid).fit(train)
    print(f"trained TF-IDF+LR on {len(train)} contexts")
elif a.detector == "bert":
    detector = BERTDetector(a.bert_dir)
    print(f"loaded {a.bert_dir} (threshold {detector.threshold})")

n = 0
with open(a.out, "w", encoding="utf-8") as f:
    for c in load(a.input):
        d = extract_detail(c["turns"], detector)
        row = {
            "id": c["id"],
            "is_action": d is not None,
            "person": d["person"] if d else None,
            "action": d["action"] if d else None,
            "deadline": d["deadline"] if d else None,
        }
        if d:
            row.update(
                commit_turn=d["commit_turn"],
                person_turn=d["person_turn"],
                action_turn=d["action_turn"],
                deadline_turn=d["deadline_turn"],
            )
            if not a.no_ner:
                ppl = mentioned_people(c["turns"])
                if ppl:
                    row["mentioned_people"] = ppl
        n += row["is_action"]
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"predicted {n} action items -> {a.out}")
