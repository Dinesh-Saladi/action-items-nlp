# Score report: rule
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_rule.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.705 |
| Precision | 0.303 |
| Recall | 0.667 |
| F1 | 0.417 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=10 FP=23 FN=5 TN=57

## 2. Field accuracy (only on gold action items the pipeline also detected, n=10)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 1.000 |
| Action (word-overlap F1 >= 0.5) | 0.600 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.667 | action 0.400 | deadline 0.667

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.030 | 0.067 | 0.042 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.182 | 0.400 | 0.250 |

Error counts by type: {'wrong_action': 4, 'false_positive': 23, 'missed_action_item': 5}
Failed stage counts: {'action_extract': 4, 'detect': 28}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (33);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.303 | 0.667 | 0.417 |
| Action phrase | 0.182 | 0.400 | 0.250 |
| Deadline | 0.303 | 0.667 | 0.417 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | cross-turn link | linking | 3 | 1.000 |
| Responsibility linking | same turn as action | extraction | 7 | 1.000 |
| Action extraction | linked from other turn | linking | 3 | 0.333 |
| Action extraction | anchor turn (detected turn) | extraction | 7 | 0.714 |
| Deadline linking | cross-turn link | linking | 9 | 1.000 |
| Deadline linking | same turn as action | extraction | 1 | 1.000 |
