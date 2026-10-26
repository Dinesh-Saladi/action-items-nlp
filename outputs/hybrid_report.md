# Score report: hybrid
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_hybrid.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.863 |
| Precision | 0.600 |
| Recall | 0.400 |
| F1 | 0.480 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=6 FP=4 FN=9 TN=76

## 2. Field accuracy (only on gold action items the pipeline also detected, n=6)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 1.000 |
| Action (word-overlap F1 >= 0.5) | 0.833 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.400 | action 0.333 | deadline 0.400

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.100 | 0.067 | 0.080 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.500 | 0.333 | 0.400 |

Error counts by type: {'missed_action_item': 9, 'false_positive': 4, 'wrong_action': 1}
Failed stage counts: {'detect': 13, 'action_extract': 1}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (10);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.600 | 0.400 | 0.480 |
| Action phrase | 0.500 | 0.333 | 0.400 |
| Deadline | 0.600 | 0.400 | 0.480 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | same turn as action | extraction | 4 | 1.000 |
| Responsibility linking | cross-turn link | linking | 2 | 1.000 |
| Action extraction | anchor turn (detected turn) | extraction | 4 | 1.000 |
| Action extraction | linked from other turn | linking | 2 | 0.500 |
| Deadline linking | cross-turn link | linking | 5 | 1.000 |
| Deadline linking | same turn as action | extraction | 1 | 1.000 |
