# Annotation provenance: the 330-window expansion batch

## What was labeled

`data/candidates_expansion.jsonl` contains 330 cue-centered windows from 8 meetings that are
**not** used in the original 261-context set: Bdb001, Bed003, Bed016, Bmr010, Bmr026, Bns003,
Bro010, Bro024. No context ID overlaps with `data/candidates.jsonl`.

The labels were written by the AI assistant (Claude) after reading each window, using the same
guidelines as `claude_labels.py` (see `HOW_IT_WORKS.md`, "Annotation guidelines"). Reviewable
table: `claude_labels_expansion.py`.

* 330 contexts
* **54 action items** (~16%, comparable to 46/261 in the original set)
* 5 deadlines (`in about an hour`, `Friday afternoon`, `the Friday after next`, `the next day`,
  `in about one hour`)

Generated files:

* `data/annotated_expansion.jsonl` - all 330 rows with labels
* `data/ann_A.jsonl`, `data/ann_B.jsonl`, `data/ann_C.jsonl` - the same 330 rows

## The three sheets are copies, not independent annotations

All three annotation sheets contain **the same labels**. `kappa.py` and `merge_annotations.py`
therefore report **kappa = 1.000** for every pair and for Fleiss' kappa. That number is an artefact
of construction and must **not** be reported as inter-annotator agreement.

The blank 330-row templates are preserved in commit `e436bac`; restore one with:

```bash
git show e436bac:data/ann_A.jsonl > data/ann_A.jsonl   # repeat for ann_B / ann_C
```

Then have three people label them independently (no comparing answers, no `--suggest`) and run
`kappa.py` / `merge_annotations.py` as described in the README. Only those results measure
agreement.

## Effect on the reported results

None yet. The 8 new meetings are training data under the current split; the held-out test meetings
(Bmr007, Bro018) and the validation meeting (Bmr029) are unchanged. The metrics in the README and
presentation still use the original 261 contexts. Re-run with
`--annotated data/annotated_all.jsonl` to include the expansion.

## Changing the labels

Edit `claude_labels_expansion.py` and re-run:

```bash
.venv/bin/python apply_expansion_labels.py --force
```

or edit the JSONL sheets directly. If you replace the sheets with real human annotations, do not
run `apply_expansion_labels.py` again.
