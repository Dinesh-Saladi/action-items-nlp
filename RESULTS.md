# Results — Action-Item Extraction on the ICSI Meeting Corpus

All numbers below are on the **official test split**: 95 contexts from two held-out
meetings (`Bro018`, `Bmr007`), 15 of which are gold action items. Model selection
(threshold / C / BERT epoch) was done on the validation meeting `Bmr029` only;
the test gold was never used for tuning. Source: `outputs/*_report.md`.

## Headline: action-item detection (is this context an action item?)

| detector | accuracy | precision | recall | F1 | TP | FP | FN | predicted action items |
|---|---|---|---|---|---|---|---|---|
| rule | 0.705 | 0.303 | **0.667** | **0.417** | 10 | 23 | 5 | 33 |
| tfidf | 0.642 | 0.243 | 0.600 | 0.346 | 9 | 28 | 6 | 37 |
| hybrid | **0.842** | **0.500** | 0.333 | 0.400 | 5 | 5 | 10 | 10 |
| bert (RoBERTa) | 0.558 | 0.224 | 0.733 | 0.344 | 11 | 38 | 4 | 49 |

Baseline accuracy ("always say no action item") = 0.842 on this split.

Best per metric: precision **hybrid (0.500)**, recall **bert (0.733)**, F1 **rule (0.417)**,
accuracy **hybrid (0.842)**.

## End-to-end triplet (Person, Action, Deadline)

| detector | exact P/R/F1 | relaxed P/R/F1 |
|---|---|---|
| rule | 0.030 / 0.067 / 0.042 | 0.182 / 0.400 / 0.250 |
| tfidf | 0.027 / 0.067 / 0.038 | 0.135 / 0.333 / 0.192 |
| hybrid | 0.000 / 0.000 / 0.000 | 0.400 / 0.267 / 0.320 |
| bert | 0.020 / 0.067 / 0.031 | 0.122 / 0.400 / 0.188 |

Exact triplet match stays near zero because gold phrases tasks differently than people speak.
The relaxed score (person =, action word-overlap >= 0.5, deadline =) is the realistic
end-to-end number.

## Component-level P/R/F1 (each field evaluated as its own task)

| detector | person P/R/F1 | action P/R/F1 | deadline P/R/F1 |
|---|---|---|---|
| rule | 0.303 / 0.667 / 0.417 | 0.182 / 0.400 / 0.250 | 0.303 / 0.667 / 0.417 |
| tfidf | 0.162 / 0.400 / 0.231 | 0.135 / 0.333 / 0.192 | 0.243 / 0.600 / 0.346 |
| hybrid | 0.500 / 0.333 / 0.400 | 0.400 / 0.267 / 0.320 | 0.500 / 0.333 / 0.400 |
| bert | 0.184 / 0.600 / 0.281 | 0.122 / 0.400 / 0.188 | 0.224 / 0.733 / 0.344 |

Hybrid has the best conditional field accuracy on the items it does detect (person 1.000,
action 0.800, deadline 1.000 on 5 items).

## Field accuracy on detected items (conditional on detection)

| detector | n detected | person | action (overlap >= 0.5) | deadline |
|---|---|---|---|---|
| rule | 10 | 1.000 | 0.600 | 1.000 |
| tfidf | 9 | 0.667 | 0.556 | 1.000 |
| hybrid | 5 | 1.000 | 0.800 | 1.000 |
| bert | 11 | 0.818 | 0.545 | 1.000 |

## Ensemble check

A val-only ensemble tool (`bert_ensemble.py`) compared `p1 + s1 + s2` and every pair on
validation F1. The best single model (`p1`) won on val, so no ensemble was adopted.

## BERT validation ladder (val F1, 35 contexts / 11 positives)

| config | val F1 |
|---|---|
| original (max_length 128) | 0.667 |
| p0 (max_length 256) | 0.706 |
| p1 (max_length 256, seed 0, epoch 3, threshold 0.03) | **0.833** |
| s1 (seed 1) | 0.696 |
| s2 (seed 2) | 0.667 |

Shipped BERT = `p1` config; `predict.py` reads `max_length` from `tune_run.json`
(128 fallback for legacy models). Root cause of the gain: `max_length=128` was truncating
53% of train / 40% of val+test windows (mean 179 tokens).

## Majority-vote figure

Combining the rule, TF-IDF and hybrid detectors by majority vote reaches relaxed
F1 **0.35** (up from 0.32 with the older BERT predictions).

## Caveats

1. **Single annotator.** The gold was written by one annotator (Claude) after reading each
   window, as a stand-in. Review `claude_labels.py`; a final report should use labels you
   made, ideally double-annotated (`kappa.py`). The 662-window expansion batch is
   pre-annotated by the same AI annotator and is **not** part of any reported metric yet.
2. **Only 6 of 76 meetings are labeled** in the evaluated dataset; 16 more (662 windows) have
   provisional AI pre-annotations. Only cue-centered windows (+30% random cue-free windows,
   auto-labeled "not action") were sampled. Actions without any cue phrase were not sampled.
3. **Real ICSI has few action items and almost no explicit deadlines** (2 of 46 positives have
   one), so deadline accuracy is mostly "predict NULL correctly".
4. **15 test positives** means one example moves a metric ~6.7 points; treat small differences
   as noise. BERT in particular has high variance (3-seed spread 0.833 / 0.696 / 0.667 on val).
5. **Exact triplet match stays near zero** because gold phrases tasks differently than people
   speak; read the relaxed triplet as the real end-to-end number.
6. **Windows are ±2 turns**, so a commitment far from its task (>2 turns) cannot be linked.
7. **The validation split (`Bmr029`) is removed from training**, so TF-IDF/hybrid train on
   131 contexts instead of 166 - model selection costs training data at this scale. This is
   the price of not tuning on the test set.

## Per-detector detail

Full per-context breakdowns, confusion matrices, and stage-attributed errors are in
`outputs/*_report.md` and `outputs/*_errors.csv` (columns `failed_stage`, `error_type`).
The score definitions and extraction-vs-linking split are in `HOW_IT_WORKS.md`.
