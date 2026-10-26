"""Bootstrap the 330-window expansion batch from claude_labels_expansion.py.

This writes the SAME single-annotator AI labels into all three annotation sheets
(data/ann_A.jsonl, ann_B.jsonl, ann_C.jsonl) and produces data/annotated_expansion.jsonl.
The three sheets are therefore NOT independent annotations - see
data/ANNOTATION_PROVENANCE.md before computing/reporting kappa.

Refuses to overwrite a sheet that already has human labels unless --force is given.
"""

import argparse
import json
import sys

from claude_labels_expansion import LABELS

CANDIDATES = "data/candidates_expansion.jsonl"
SHEETS = ["data/ann_A.jsonl", "data/ann_B.jsonl", "data/ann_C.jsonl"]
OUT = "data/annotated_expansion.jsonl"


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def label_row(row):
    lab = LABELS.get(row["id"])
    if lab is None:
        row["is_action"], row["person"], row["action"], row["deadline"] = (
            False,
            None,
            None,
            None,
        )
    else:
        row["is_action"] = True
        row["person"], row["action"], row["deadline"] = lab


def dump(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite existing labels")
    args = ap.parse_args()

    cands = load(CANDIDATES)
    ids = [r["id"] for r in cands]
    assert len(ids) == len(set(ids)), f"duplicate candidate ids: {len(ids) - len(set(ids))}"
    missing = sorted(set(LABELS) - set(ids))
    assert not missing, f"label ids not in candidates: {missing}"

    for path in SHEETS:
        rows = load(path)
        if [r["id"] for r in rows] != ids:
            sys.exit(f"{path}: rows/ids do not match {CANDIDATES}")
        if any(r.get("is_action") is not None for r in rows) and not args.force:
            sys.exit(f"{path}: already contains labels (use --force to overwrite)")

    for row in cands:
        label_row(row)
    for path in SHEETS:
        dump(path, [dict(row) for row in cands])
    dump(OUT, cands)

    positives = sum(r["is_action"] for r in cands)
    print(f"{len(cands)} contexts, {positives} action items")
    print("wrote:", ", ".join(SHEETS), "and", OUT)


if __name__ == "__main__":
    main()
