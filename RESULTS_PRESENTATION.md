# Results — for presentation (test split: 95 contexts, 15 gold action items)

## Detection (is this context an action item?)

| detector | precision | recall | F1 | accuracy |
|---|---|---|---|---|
| rule | 0.303 | 0.667 | **0.417** | 0.705 |
| tfidf | 0.243 | 0.600 | 0.346 | 0.642 |
| hybrid | **0.500** | 0.333 | 0.400 | **0.842** |
| bert | 0.224 | **0.733** | 0.344 | 0.558 |

Best: precision = hybrid (0.500), recall = bert (0.733), F1 = rule (0.417), accuracy = hybrid (0.842).

## End-to-end triplet (relaxed: person = , action overlap ≥ 0.5, deadline =)

| detector | precision | recall | F1 |
|---|---|---|---|
| rule | 0.182 | 0.400 | 0.250 |
| tfidf | 0.135 | 0.333 | 0.192 |
| hybrid | 0.400 | 0.267 | 0.320 |
| bert | 0.122 | 0.400 | 0.188 |

Exact triplet match is ~0 for all detectors.

## Component-level F1

| detector | person | action | deadline |
|---|---|---|---|
| rule | 0.417 | 0.250 | 0.417 |
| tfidf | 0.231 | 0.192 | 0.346 |
| hybrid | 0.400 | 0.320 | 0.400 |
| bert | 0.281 | 0.188 | 0.344 |

## Confusion (TP / FP / FN)

| detector | TP | FP | FN |
|---|---|---|---|
| rule | 10 | 23 | 5 |
| tfidf | 9 | 28 | 6 |
| hybrid | 5 | 5 | 10 |
| bert | 11 | 38 | 4 |

## Key takeaways

- **Rule** is the best overall F1 (0.417) and needs no training.
- **Hybrid** has the best precision (0.500) and accuracy (0.842).
- **BERT** has the best recall (0.733) but worst precision (0.224).
- Majority-vote ensemble (rule + tfidf + hybrid) reaches relaxed F1 **0.35**.
- Test set has only 15 positives: one example ≈ 6.7 F1 points, so treat small differences as noise.
- All results use the original 261 labeled contexts; the 330 expansion windows are pre-annotated (AI) but not yet in any metric.

Source: `outputs/*_report.md`. Full detail: `RESULTS.md`.
