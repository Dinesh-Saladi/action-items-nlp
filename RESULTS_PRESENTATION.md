# Results — for presentation (test split: 95 contexts, 15 gold action items)

## Detection (is this context an action item?)

| detector | precision | recall | F1 | accuracy |
|---|---|---|---|---|
| rule | 0.303 | 0.667 | 0.417 | 0.705 |
| tfidf | 0.288 | **1.000** | 0.448 | 0.611 |
| hybrid | **0.500** | 0.600 | **0.545** | **0.842** |
| bert | 0.224 | 0.733 | 0.344 | 0.558 |

Best: precision = hybrid (0.500), recall = tfidf (1.000), F1 = hybrid (0.545), accuracy = hybrid (0.842).

## End-to-end triplet (relaxed: person = , action overlap ≥ 0.5, deadline =)

| detector | precision | recall | F1 |
|---|---|---|---|
| rule | 0.182 | 0.400 | 0.250 |
| tfidf | 0.115 | 0.400 | 0.179 |
| hybrid | 0.333 | 0.400 | 0.364 |
| bert | 0.122 | 0.400 | 0.188 |

Exact triplet match is ~0 for all detectors.

## Component-level F1

| detector | person | action | deadline |
|---|---|---|---|
| rule | 0.417 | 0.250 | 0.417 |
| tfidf | 0.299 | 0.179 | 0.448 |
| hybrid | 0.545 | 0.364 | 0.545 |
| bert | 0.281 | 0.188 | 0.344 |

## Confusion (TP / FP / FN)

| detector | TP | FP | FN |
|---|---|---|---|
| rule | 10 | 23 | 5 |
| tfidf | 15 | 37 | 0 |
| hybrid | 9 | 9 | 6 |
| bert | 11 | 38 | 4 |

## Key takeaways

- **Hybrid** now has the best F1 (0.545), precision (0.500), and accuracy (0.842) after training on 2,781 contexts.
- **TF-IDF** has perfect recall (1.000) — catches all 15 test action items.
- **Rule** needs no training and still competitive (F1 0.417).
- **BERT** has the best recall (0.733) but worst precision (0.224); unchanged by more data.
- Majority-vote ensemble (rule + tfidf + hybrid) reaches relaxed F1 **0.35**.
- Test set has only 15 positives: one example ≈ 6.7 F1 points, so treat small differences as noise.
- All results use the original 261 labeled contexts; the 2,650 expansion windows are pre-annotated (AI) but not yet in any metric.

Source: `outputs/*_report.md`. Full detail: `RESULTS.md`.
