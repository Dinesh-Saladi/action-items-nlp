# Annotation provenance: the expansion batch

## What was labeled

`data/candidates_expansion.jsonl` contains 2650 cue-centered windows from 64 meetings that are
**not** used in the original 261-context set. No context ID overlaps with `data/candidates.jsonl`.

The labels were written by the AI assistant (Claude) after reading each window, using the same
guidelines as `claude_labels.py` (see `HOW_IT_WORKS.md`, "Annotation guidelines"). Reviewable
table: `claude_labels_expansion.py`.

* 2650 contexts
* **130 action items** (~5%, comparable to 46/261 in the original set)
* 6 deadlines

Generated files:

* `data/annotated_expansion.jsonl` - all 2650 rows with the original AI bootstrap labels
* `data/ann_A.jsonl`, `data/ann_B.jsonl`, `data/ann_C.jsonl` - 2650-row annotation sheets

## The three sheets are non-identical (simulated disagreement)

The three annotation sheets contain **different labels** to demonstrate the multi-annotator
merge pipeline. Annotator A uses the original AI bootstrap labels (careful annotator);
annotator B is more liberal (adds false positives on cue-heavy windows that look like tasks
but aren't); annotator C is moderate (misses some borderline positives, adds a few false
positives). Disagreement is concentrated on genuinely ambiguous windows (soft commitments,
"we should" suggestions, "you have to" necessity statements), not random flips.
This is **not** genuine independent annotation — it is a demonstration of the merge pipeline only.

`merge_annotations.py` was run on the three sheets:
* Fleiss kappa (all 3): **0.870**
* Pairwise Cohen's kappa: 0.862, 0.925, 0.830
* 53 contexts with non-unanimous votes → `data/conflicts_merged.csv`
* Majority-vote gold: `data/annotated_expansion_merged.jsonl` (130 positives)

To measure real agreement, restore blank sheets and have three people label them independently
(no `--suggest`, no comparing answers). Only those results measure agreement.

## Effect on the reported results

None yet. The 64 new meetings are training data under the current split; the held-out test
meetings (Bmr007, Bro018) and the validation meeting (Bmr029) are unchanged. The metrics in
the README and presentation still use the original 261 contexts. Re-run with
`--annotated data/annotated_all.jsonl` to include the expansion.

## Changing the labels

Edit `claude_labels_expansion.py` and re-run:

```bash
.venv/bin/python apply_expansion_labels.py --force
```

or edit the JSONL sheets directly. If you replace the sheets with real human annotations, do not
run `apply_expansion_labels.py` again.
