# Score report: hybrid
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_hybrid.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.842 |
| Precision | 0.500 |
| Recall | 0.333 |
| F1 | 0.400 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=5 FP=5 FN=10 TN=75

## 2. Field accuracy (only on gold action items the pipeline also detected, n=5)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 1.000 |
| Action (word-overlap F1 >= 0.5) | 0.800 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.333 | action 0.267 | deadline 0.333

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.000 | 0.000 | 0.000 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.400 | 0.267 | 0.320 |

Error counts by type: {'missed_action_item': 10, 'wrong_action': 1, 'false_positive': 5}
Failed stage counts: {'detect': 15, 'action_extract': 1}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (10);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.500 | 0.333 | 0.400 |
| Action phrase | 0.400 | 0.267 | 0.320 |
| Deadline | 0.500 | 0.333 | 0.400 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | same turn as action | extraction | 4 | 1.000 |
| Responsibility linking | cross-turn link | linking | 1 | 1.000 |
| Action extraction | anchor turn (detected turn) | extraction | 4 | 1.000 |
| Action extraction | linked from other turn | linking | 1 | 0.000 |
| Deadline linking | cross-turn link | linking | 4 | 1.000 |
| Deadline linking | same turn as action | extraction | 1 | 1.000 |
