# Score report: tfidf
gold file: `data/test/gold.jsonl`  |  predictions: `outputs/pred_tfidf.jsonl`  |  contexts: 95  (gold action items: 15, non-action: 80)

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | 0.695 |
| Precision | 0.333 |
| Recall | 0.933 |
| F1 | 0.491 |
| Baseline accuracy ("always say no action item") | 0.842 |

Confusion: TP=14 FP=28 FN=1 TN=52

## 2. Field accuracy (only on gold action items the pipeline also detected, n=14)
| field | accuracy |
|---|---|
| Person (exact speaker id match) | 0.643 |
| Action (word-overlap F1 >= 0.5) | 0.429 |
| Deadline (normalized match, NULL=NULL) | 1.000 |

Same fields, strict version (missed action items count as wrong, n=15): person 0.600 | action 0.400 | deadline 0.933

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | 0.024 | 0.067 | 0.035 |
| Relaxed (person=, action overlap>=0.5, deadline =) | 0.143 | 0.400 | 0.211 |

Error counts by type: {'wrong_action': 3, 'false_positive': 28, 'wrong_person+action': 5, 'missed_action_item': 1}
Failed stage counts: {'action_extract': 3, 'detect': 29, 'responsibility_link+action_extract': 5}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items (42);  recall = correct / gold action items (15)

| component | precision | recall | F1 |
|---|---|---|---|
| Person (responsibility) | 0.214 | 0.600 | 0.316 |
| Action phrase | 0.143 | 0.400 | 0.211 |
| Deadline | 0.333 | 0.933 | 0.491 |

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
| Responsibility linking | cross-turn link | linking | 6 | 0.500 |
| Responsibility linking | same turn as action | extraction | 8 | 0.750 |
| Action extraction | linked from other turn | linking | 6 | 0.167 |
| Action extraction | anchor turn (detected turn) | extraction | 8 | 0.625 |
| Deadline linking | cross-turn link | linking | 12 | 1.000 |
| Deadline linking | same turn as action | extraction | 2 | 1.000 |
