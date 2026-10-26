# Score report: tfidf
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_tfidf.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.611 |
| Precision | 0.288 |
| Recall | 1.000 |
| F1 | 0.448 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=15 FP=37 FN=0 TN=43

## 2. Field accuracy (only on gold action items the pipeline also detected, n=15)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 0.667 |
| Action (word-overlap F1 >= 0.5) | 0.400 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.667 | action 0.400 | deadline 1.000

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.019 | 0.067 | 0.030 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.115 | 0.400 | 0.179 |

Error counts by type: {'wrong_action': 4, 'false_positive': 37, 'wrong_person+action': 5}
Failed stage counts: {'action_extract': 4, 'detect': 37, 'responsibility_link+action_extract': 5}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (52);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.192 | 0.667 | 0.299 |
| Action phrase | 0.115 | 0.400 | 0.179 |
| Deadline | 0.288 | 1.000 | 0.448 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | cross-turn link | linking | 6 | 0.500 |
| Responsibility linking | same turn as action | extraction | 9 | 0.778 |
| Action extraction | linked from other turn | linking | 6 | 0.167 |
| Action extraction | anchor turn (detected turn) | extraction | 9 | 0.556 |
| Deadline linking | cross-turn link | linking | 13 | 1.000 |
| Deadline linking | same turn as action | extraction | 2 | 1.000 |
