"""Fine-tune BERT/RoBERTa for action-item DETECTION (the plan's transformer arm, plan stage 3).

Unlike the old version this uses the SAME meeting-level split as make_dataset.py (no private
70/30 split), so the resulting predictions are scored by score.py against the same gold as the
rule / tfidf / hybrid detectors:

  python train_bert.py --train-input data/train/input.jsonl --train-gold data/train/gold.jsonl \
      --val-input data/val/input.jsonl --val-gold data/val/gold.jsonl \
      --out outputs/bert_model --model roberta-base --epochs 4

- input text = bert_text() from pipeline.py (identical encoding is used at prediction time)
- detection only: person/action/deadline extraction + linking stay the shared rule code, so
  `predict.py --detector bert` swaps ONLY the is_action decision
- with a validation split, the checkpoint with the lowest validation loss is kept and the
  decision threshold is selected on that split (saved as `<out>/threshold.json`); positives are
  repeated `--pos-mult` times so batches are not dominated by the 15% positive class
"""

import json, argparse, shutil, os

from pipeline import bert_text

ap = argparse.ArgumentParser()
ap.add_argument("--train-input", default="data/train/input.jsonl")
ap.add_argument("--train-gold", default="data/train/gold.jsonl")
ap.add_argument("--val-input")
ap.add_argument("--val-gold")
ap.add_argument("--out", default="outputs/bert_model")
ap.add_argument("--model", default="roberta-base")
ap.add_argument("--epochs", type=int, default=15)
ap.add_argument(
    "--pos-mult",
    type=int,
    default=4,
    help="repeat positives this many times (balanced batches)",
)
ap.add_argument("--max-length", type=int, default=128)
ap.add_argument("--batch", type=int, default=16)
ap.add_argument("--lr", type=float, default=5e-5)
a = ap.parse_args()

from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from sklearn.metrics import f1_score, precision_recall_fscore_support


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def rows(inp, goldp):
    g = {x["id"]: x for x in load(goldp)}
    return [
        dict(c, is_action=g[c["id"]]["is_action"]) for c in load(inp) if c["id"] in g
    ]


train = rows(a.train_input, a.train_gold)
val = rows(a.val_input, a.val_gold) if a.val_input and a.val_gold else []
print(
    f"train: {len(train)} contexts ({sum(r['is_action'] for r in train)} action items)"
    + (
        f" | val: {len(val)} contexts ({sum(r['is_action'] for r in val)} action items)"
        if val
        else " | no val split"
    )
)

# positives are rare (~15%); without balancing the model just learns the class prior and
# outputs ~0.2 for everything. Repeat the positive windows so a batch is roughly balanced.
pos = [r for r in train if r["is_action"]]
train_bal = train + pos * (a.pos_mult - 1)
print(
    f"balanced train: {len(train_bal)} rows ({sum(r['is_action'] for r in train_bal)} positives, "
    f"pos_mult={a.pos_mult})"
)

tok = AutoTokenizer.from_pretrained(a.model)


def enc(rs):
    d = Dataset.from_dict(
        {
            "text": [bert_text(r["turns"]) for r in rs],
            "label": [int(r["is_action"]) for r in rs],
        }
    )
    return d.map(
        lambda b: tok(
            b["text"], truncation=True, max_length=a.max_length, padding="max_length"
        ),
        batched=True,
    )


model = AutoModelForSequenceClassification.from_pretrained(a.model, num_labels=2)


def metrics(p):
    pr, rc, f, _ = precision_recall_fscore_support(
        p.label_ids, p.predictions.argmax(-1), average="binary", zero_division=0
    )
    return {"precision": pr, "recall": rc, "f1": f}


ckpt = a.out + "_ckpt"
shutil.rmtree(ckpt, ignore_errors=True)
trainer = Trainer(
    model=model,
    args=TrainingArguments(
        ckpt,
        num_train_epochs=a.epochs,
        per_device_train_batch_size=a.batch,
        learning_rate=a.lr,
        warmup_steps=10,
        eval_strategy="epoch" if val else "no",
        save_strategy="epoch" if val else "no",
        load_best_model_at_end=bool(val),
        metric_for_best_model=(
            "loss" if val else None
        ),  # F1 at the default 0.5 cut can be 0 for
        greater_is_better=False if val else None,  # every epoch; loss always moves
        seed=0,
        report_to=[],
        logging_steps=20,
    ),
    train_dataset=enc(train_bal),
    eval_dataset=enc(val) if val else None,
    compute_metrics=metrics,
)
trainer.train()
shutil.rmtree(ckpt, ignore_errors=True)

# ---- pick the decision threshold on the VALIDATION split (never the test split) and store it
#      next to the model, so predict.py applies exactly the same cut.
threshold = 0.5
if val:
    import torch
    from pipeline import bert_text as _bt, prf

    model.eval()
    ps = []
    for r in val:
        e = tok(
            _bt(r["turns"]),
            return_tensors="pt",
            truncation=True,
            max_length=a.max_length,
        )
        with torch.no_grad():
            ps.append(float(torch.softmax(model(**e).logits, -1)[0][1]))
    ys = [int(r["is_action"]) for r in val]
    best = (-1.0, 0.5, 0.0, 0.0)
    for th in [i / 100 for i in range(5, 96, 5)]:
        tp = sum(1 for p, y in zip(ps, ys) if y and p >= th)
        fp = sum(1 for p, y in zip(ps, ys) if not y and p >= th)
        fn = sum(1 for p, y in zip(ps, ys) if y and p < th)
        P, R, F = prf(tp, fp, fn)
        if F > best[0]:
            best = (F, th, P, R)
    f1, threshold, P, R = best
    json.dump(
        {"threshold": threshold}, open(os.path.join(a.out, "threshold.json"), "w")
    )
    print(
        f"val threshold search: F1={f1:.3f} (P={P:.3f} R={R:.3f}) -> threshold={threshold}"
    )

model.save_pretrained(a.out)
tok.save_pretrained(a.out)
print(f"saved detector -> {a.out}  (threshold {threshold})")
print(
    "next: python predict.py --input data/test/input.jsonl --out outputs/pred_bert.jsonl "
    "--detector bert --bert-dir " + a.out
)
