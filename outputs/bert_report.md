# Score report: bert
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_bert.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.853 |
| Precision | 0.526 |
| Recall | 0.667 |
| F1 | 0.588 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=10 FP=9 FN=5 TN=71

## 2. Field accuracy (only on gold action items the pipeline also detected, n=10)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 0.900 |
| Action (word-overlap F1 >= 0.5) | 0.600 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.600 | action 0.400 | deadline 0.667

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.053 | 0.067 | 0.059 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.316 | 0.400 | 0.353 |

Error counts by type: {'missed_action_item': 5, 'false_positive': 9, 'wrong_action': 3, 'wrong_person+action': 1}
Failed stage counts: {'detect': 14, 'action_extract': 3, 'responsibility_link+action_extract': 1}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (19);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.474 | 0.600 | 0.529 |
| Action phrase | 0.316 | 0.400 | 0.353 |
| Deadline | 0.526 | 0.667 | 0.588 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | same turn as action | extraction | 8 | 0.875 |
| Responsibility linking | cross-turn link | linking | 2 | 1.000 |
| Action extraction | anchor turn (detected turn) | extraction | 8 | 0.625 |
| Action extraction | linked from other turn | linking | 2 | 0.500 |
| Deadline linking | cross-turn link | linking | 8 | 1.000 |
| Deadline linking | same turn as action | extraction | 2 | 1.000 |
