# Score report: bert
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_bert.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.874 |
| Precision | 1.000 |
| Recall | 0.200 |
| F1 | 0.333 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=3 FP=0 FN=12 TN=80

## 2. Field accuracy (only on gold action items the pipeline also detected, n=3)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 0.667 |
| Action (word-overlap F1 >= 0.5) | 0.333 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.133 | action 0.067 | deadline 0.200

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.000 | 0.000 | 0.000 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.333 | 0.067 | 0.111 |

Error counts by type: {'missed_action_item': 12, 'wrong_action': 1, 'wrong_person+action': 1}
Failed stage counts: {'detect': 12, 'action_extract': 1, 'responsibility_link+action_extract': 1}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (3);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.667 | 0.133 | 0.222 |
| Action phrase | 0.333 | 0.067 | 0.111 |
| Deadline | 1.000 | 0.200 | 0.333 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | same turn as action | extraction | 2 | 0.500 |
| Responsibility linking | cross-turn link | linking | 1 | 1.000 |
| Action extraction | anchor turn (detected turn) | extraction | 2 | 0.500 |
| Action extraction | linked from other turn | linking | 1 | 0.000 |
| Deadline linking | cross-turn link | linking | 1 | 1.000 |
| Deadline linking | same turn as action | extraction | 2 | 1.000 |
