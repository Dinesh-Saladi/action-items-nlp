# Score report: bert
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_bert.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.558 |
| Precision | 0.224 |
| Recall | 0.733 |
| F1 | 0.344 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=11 FP=38 FN=4 TN=42

## 2. Field accuracy (only on gold action items the pipeline also detected, n=11)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 0.818 |
| Action (word-overlap F1 >= 0.5) | 0.545 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.600 | action 0.400 | deadline 0.733

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.020 | 0.067 | 0.031 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.122 | 0.400 | 0.188 |

Error counts by type: {'wrong_action': 3, 'false_positive': 38, 'missed_action_item': 4, 'wrong_person+action': 2}
Failed stage counts: {'action_extract': 3, 'detect': 42, 'responsibility_link+action_extract': 2}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (49);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.184 | 0.600 | 0.281 |
| Action phrase | 0.122 | 0.400 | 0.188 |
| Deadline | 0.224 | 0.733 | 0.344 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | cross-turn link | linking | 3 | 1.000 |
| Responsibility linking | same turn as action | extraction | 8 | 0.750 |
| Action extraction | linked from other turn | linking | 3 | 0.333 |
| Action extraction | anchor turn (detected turn) | extraction | 8 | 0.625 |
| Deadline linking | cross-turn link | linking | 9 | 1.000 |
| Deadline linking | same turn as action | extraction | 2 | 1.000 |
