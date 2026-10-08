# Score report: tfidf
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_tfidf.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.642 |
| Precision | 0.243 |
| Recall | 0.600 |
| F1 | 0.346 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=9 FP=28 FN=6 TN=52

## 2. Field accuracy (only on gold action items the pipeline also detected, n=9)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 0.667 |
| Action (word-overlap F1 >= 0.5) | 0.556 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.400 | action 0.333 | deadline 0.600

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.027 | 0.067 | 0.038 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.135 | 0.333 | 0.192 |

Error counts by type: {'missed_action_item': 6, 'false_positive': 28, 'wrong_action': 1, 'wrong_person+action': 3}
Failed stage counts: {'detect': 34, 'action_extract': 1, 'responsibility_link+action_extract': 3}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (37);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.162 | 0.400 | 0.231 |
| Action phrase | 0.135 | 0.333 | 0.192 |
| Deadline | 0.243 | 0.600 | 0.346 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | same turn as action | extraction | 5 | 0.800 |
| Responsibility linking | cross-turn link | linking | 4 | 0.500 |
| Action extraction | anchor turn (detected turn) | extraction | 5 | 0.800 |
| Action extraction | linked from other turn | linking | 4 | 0.250 |
| Deadline linking | cross-turn link | linking | 8 | 1.000 |
| Deadline linking | same turn as action | extraction | 1 | 1.000 |
