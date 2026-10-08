"""Step 3: split a labeled file into INPUT files (what the pipeline sees) and GOLD files (the answer key),
by meeting (so no meeting appears in both train and test).

  python make_dataset.py --annotated data/annotated.jsonl --test-meetings Bro018 Bmr007

Creates:  data/train/input.jsonl  data/train/gold.jsonl   (used only to train the TF-IDF detector)
          data/test/input.jsonl   data/test/gold.jsonl    (the exam: input goes to predict.py, gold only to score.py)
  with --val-meetings: also data/val/{input,gold}.jsonl   (model selection only: threshold/C, epochs;
  those meetings are then REMOVED from the train split so nothing is trained on its own validation set)
input.jsonl rows: {id, meeting, center, turns}                       <- NO labels
gold.jsonl  rows: {id, is_action, person, action, deadline}          <- the key"""

import json, argparse, os

ap = argparse.ArgumentParser()
ap.add_argument("--annotated", default="data/annotated.jsonl")
ap.add_argument("--test-meetings", nargs="+", required=True)
ap.add_argument(
    "--val-meetings", nargs="+", default=[], help="optional validation meetings"
)
ap.add_argument("--out", default="data")
a = ap.parse_args()
rows = [json.loads(l) for l in open(a.annotated, encoding="utf-8") if l.strip()]
rows = [r for r in rows if r["is_action"] is not None]  # skip unlabeled
for split in ("train", "val", "test"):
    if split == "val" and not a.val_meetings:
        continue
    os.makedirs(f"{a.out}/{split}", exist_ok=True)
    sel = [
        r
        for r in rows
        if (
            (r["meeting"] in a.test_meetings) == (split == "test")
            and (split != "val" or r["meeting"] in a.val_meetings)
            and (split != "train" or r["meeting"] not in a.val_meetings)
        )
    ]
    with open(f"{a.out}/{split}/input.jsonl", "w", encoding="utf-8") as fi, open(
        f"{a.out}/{split}/gold.jsonl", "w", encoding="utf-8"
    ) as fg:
        for r in sel:
            fi.write(
                json.dumps(
                    {k: r[k] for k in ("id", "meeting", "center", "turns")},
                    ensure_ascii=False,
                )
                + "\n"
            )
            fg.write(
                json.dumps(
                    {
                        k: r[k]
                        for k in ("id", "is_action", "person", "action", "deadline")
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(
        f"{split}: {len(sel)} contexts, {sum(r['is_action'] for r in sel)} action items, "
        f"meetings={sorted({r['meeting'] for r in sel})}"
    )
