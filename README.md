# Meeting Action-Item Extraction: (Person, Action, Deadline)

Extract `(Person, Action, Deadline)` triplets from multi-party ICSI meeting transcripts, and **score** the system
against a hand-made answer key. See `HOW_IT_WORKS.md` for the concepts and every pipeline stage in detail.

## 1. The big idea: student, exam, answer key

```
 transcripts/*.mrt                    <- raw ICSI meetings
        |  icsi_candidates.py         (cut into small conversation windows, "contexts")
        v
 data/candidates.jsonl                <- unlabeled contexts
        |  annotate.py   (YOU label)  or  apply_labels.py (Claude's labels, included for demo)
        v
 data/annotated.jsonl                 <- contexts + labels
        |  make_dataset.py            (split BY MEETING)
        v
 data/train/{input,gold}.jsonl        data/test/{input,gold}.jsonl
        |                                   |             \
        |  (only to train tfidf/hybrid)     |input         |gold   <- the answer key
        v                                   v              |
     predict.py  ---------------------> outputs/pred_*.jsonl |
        (the "student": sees INPUT only)        |            |
                                                v            v
                                              score.py  (the "teacher": compares prediction vs gold)
                                                |
                                                v
                                   outputs/*_report.md  +  outputs/*_errors.csv
```

| Role | File | Contains | Who reads it |
|---|---|---|---|
| **Input** (the exam questions) | `data/test/input.jsonl` | conversation windows, **no labels** | `predict.py` |
| **Gold** (the answer key) | `data/test/gold.jsonl` | the correct `is_action / person / action / deadline` per window | `score.py` only |
| **Prediction** (the student's answers) | `outputs/pred_*.jsonl` | what the pipeline answered | `score.py` |
| Train input/gold | `data/train/*` | other meetings, used only to teach the TF-IDF/hybrid detector | `predict.py` (tfidf/hybrid) |

Input and gold are linked by `id`. Train and test never share a meeting.

## 2. Quick start (everything is already set up in this folder)

```bash
python -m venv .venv                       # PEP 668 systems need a venv
.venv/bin/pip install scikit-learn         # minimum to run rule/tfidf/hybrid
.venv/bin/pip install spacy && .venv/bin/python -m spacy download en_core_web_sm   # optional: action trimming + name NER
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install transformers datasets accelerate                             # optional: the BERT detector
.venv/bin/python run_all.py                # split -> predict (rule / tfidf / hybrid / bert) -> score -> table
```
Open `outputs/hybrid_report.md` for full metrics and `outputs/hybrid_errors.csv` for every mistake.

Useful variants:
```bash
.venv/bin/python run_all.py --val-meetings Bmr029   # carve a VALIDATION split; threshold/C chosen on it
.venv/bin/python run_all.py --with-bert             # fine-tune RoBERTa first, then score it too
.venv/bin/python run_all.py --skip-split            # reuse the existing data/train + data/val + data/test
```
`scikit-learn` is the only hard requirement. `spacy` (action trimming + PERSON NER) and
`torch`/`transformers` (the `bert` detector) are optional: without them everything still runs,
the rule-based trimming stays in effect and the `bert` detector is skipped.
`outputs/bert_model/` (498 MB) is gitignored - recreate it any time with
`train_bert.py` (~24 min on CPU), or rebuild the shipped **tuned** model with
`bert_tune.py --run "p1;max_length=256,epochs=15,lr=5e-5,pos_mult=4,seed=0" --threads 6`
(~110 min; hyperparameters and results in the "How bert was improved" note in the results section).

This folder ships the 76 ICSI `.mrt` files in `transcripts/`. To regenerate candidates from other
meetings, put your ICSI `.mrt` files in `transcripts/` (`transcripts/Bdb001.mrt`, ...). Running
`run_all.py` does NOT need them, because the needed text is already inside `data/`.

## 3. Folder layout

| Path | What it is |
|---|---|
| `transcripts/` | ICSI `.mrt` files (you can delete the ones you don't use) |
| `icsi.py` | library: `.mrt` parser (cleans noise tags, `O_K`->`OK`, merges speaker fragments) + window maker |
| `icsi_candidates.py` | **step 1** CLI: transcripts -> `data/candidates.jsonl` |
| `annotate.py` | **step 2** CLI: terminal tool for YOUR manual labels (back/edit, optional `--suggest`) -> `data/annotated.jsonl` |
| `claude_labels.py`, `apply_labels.py` | the demo gold I (Claude) wrote for 6 meetings; **review/replace with yours** |
| `make_dataset.py` | **step 3** CLI: `annotated.jsonl` -> train/val/test `input.jsonl` + `gold.jsonl` (split by meeting) |
| `pipeline.py` | the NLP system (stages 1-7) as a library, incl. optional spaCy refinement + provenance |
| `predict.py` | **step 4** CLI: input file -> predictions file (rule / tfidf / hybrid / bert detector) |
| `score.py` | **step 5** CLI: predictions + gold -> 5-section metrics report + error list |
| `run_all.py` | steps 3-5 in one command + comparison table (`--val-meetings`, `--with-bert`) |
| `kappa.py` | Cohen's kappa between two annotators on shared contexts |
| `merge_annotations.py` | merge 2-3 annotators: majority-vote gold, pairwise + Fleiss kappa, `data/conflicts.csv` to discuss |
| `train_bert.py` | RoBERTa/BERT detector training on the SAME meeting split; saves `outputs/bert_model` |
| `app.py` | optional Streamlit demo (`pip install streamlit pandas`) |
| `PLAN_TRACEABILITY.md` | plan (`Nlp project.md`) section -> implementation, incl. remaining gaps |
| `data/`, `outputs/` | generated data and results |

## 4. File formats

**Context (one JSON per line)** in `input.jsonl`:
```json
{"id": "Bmr029_t391", "meeting": "Bmr029", "center": 2,
 "turns": [{"speaker": "me018", "text": "Right. But I'm just wondering how long it will take..."},
           {"speaker": "mn017", "text": "He already has the information. Right?"},
           {"speaker": "me026", "text": "I have it for Macrophone already, and I think by tomorrow I'll have it"},
           {"speaker": "mn017", "text": "OK."},
           {"speaker": "me026", "text": "for for the rest."}]}
```
`center` = index of the turn that triggered the window (informational). `id` = `<meeting>_t<turn index>` (cue window)
or `<meeting>_n<turn index>` (random cue-free negative window).

**Gold row** in `gold.jsonl`:
```json
{"id": "Bmr029_t391", "is_action": true, "person": "me026", "action": "have the information for the rest", "deadline": "tomorrow"}
{"id": "Bmr029_t23",  "is_action": false, "person": null, "action": null, "deadline": null}
```
**Prediction row** in `pred_*.jsonl`: same five keys. For non-actions the three fields are `null`; for actions, an unknown
field is the string `"NULL"`. Action rows also carry **provenance** keys (`commit_turn`, `person_turn`, `action_turn`,
`deadline_turn` = index of the turn each value was taken from) used by `score.py` section 5, and optionally
`mentioned_people` (PERSON names spaCy heard in the window - informational, gold uses speaker ids).

### Using YOUR OWN input and gold (the important part)
You can swap in anything as long as the formats match:
1. **Different transcripts:** put `.mrt` files in `transcripts/`, then
   `python icsi_candidates.py --dir transcripts --meetings MeetingA MeetingB ... --out data/candidates.jsonl`
   (omit `--meetings` for all).
2. **Your labels:** `python annotate.py --inp data/candidates.jsonl --out data/annotated.jsonl`
   (`y`/`n`/Enter=skip; resumable). Several people: give each a different slice of `candidates.jsonl`, annotate to
   separate files, then `cat` them together.
3. **Split:** `python make_dataset.py --annotated data/annotated.jsonl --test-meetings <meetings kept for the exam>
   [--val-meetings <meetings held out for tuning> - recommended: threshold/epoch selection happens there]
4. **Run + score:** `python run_all.py --skip-split` or the individual commands below.
5. **Hand-made files:** you can also write `data/test/input.jsonl` and `data/test/gold.jsonl` yourself (formats above), then
   `python predict.py --input data/test/input.jsonl --out outputs/pred_rule.jsonl --detector rule` and
   `python score.py --pred outputs/pred_rule.jsonl --gold data/test/gold.jsonl --name rule`.
   Any plain-text transcript works too: `python pipeline.py demo --file my.txt` with lines `Speaker: text`.

## 4b. Editing while annotating (`annotate.py`)
* `y` = action item, `n` = not, `s` = skip, `b` = go back, `q` = quit. Everything is saved after each answer; rerun to resume.
* After `y`, each field shows a `[default]`: **Enter** keeps it, **typing** replaces it, **`-`** sets NULL.
* To fix an earlier answer: press `b` until you reach it, press `y` again, and retype only the wrong fields.
* `--suggest` pre-fills the fields from the rule pipeline so you only correct them. Use it only to save time on YOUR OWN
  labeling; do NOT use it when measuring agreement (kappa) or building the final gold, because it anchors annotators to the
  pipeline and inflates the pipeline's score.
* You can also edit the `.jsonl` in any text editor: one JSON object per line; change `person`/`action`/`deadline`.

### Expanding the annotation set (the biggest open gap)
`data/candidates_expansion.jsonl` holds **330 unlabeled windows from 8 new meetings**
(Bdb001, Bed003, Bed016, Bmr010, Bmr026, Bns003, Bro010, Bro024 - no ID collides with the existing
set). Together with the 261 already labeled contexts that is **591 contexts**, inside the plan's
500-1,000 target.

**Three annotation sheets are pre-created: `data/ann_A.jsonl`, `data/ann_B.jsonl`,
`data/ann_C.jsonl`** - the same 330 windows with empty labels, one per annotator. Give one
file to each person, label independently (no comparing answers, and no `--suggest` - it anchors
you to the pipeline), and leave the existing `data/annotated.jsonl` untouched:

```bash
# annotator A labels their own sheet; rerun the same command to resume.
# every row is preserved, so the file is always a complete sheet
.venv/bin/python annotate.py --inp data/ann_A.jsonl --out data/ann_A.jsonl
# annotator B: --inp/--out data/ann_B.jsonl      annotator C: data/ann_C.jsonl
# (or edit the .jsonl by hand: set is_action true/false, then person / action / deadline)
```

```bash
# 1. agreement: pairwise Cohen's kappa (+ person/deadline agreement where both say yes)
.venv/bin/python kappa.py --a data/ann_A.jsonl --b data/ann_B.jsonl
# 2. merge: majority-vote gold + pairwise + Fleiss kappa + data/conflicts.csv to discuss
.venv/bin/python merge_annotations.py \
    --files data/ann_A.jsonl data/ann_B.jsonl data/ann_C.jsonl \
    --out data/annotated_expansion.jsonl
# 3. resolve data/conflicts.csv (ties stay is_action=null), re-run merge, then combine
#    with the 261 existing labels (safe: ids never overlap) and re-run the experiment
cat data/annotated.jsonl data/annotated_expansion.jsonl > data/annotated_all.jsonl
.venv/bin/python run_all.py --annotated data/annotated_all.jsonl \
    --test-meetings Bro018 Bmr007 --val-meetings Bmr029
```
All 8 new meetings are train/val material - the held-out test meetings (Bmr007, Bro018) do not
change, so before/after numbers stay comparable. Downstream tools skip `"is_action": null` rows,
so partially labeled sheets are safe to use.

## 5. Commands in detail

```bash
# 1 candidates (unlabeled windows)
python icsi_candidates.py --dir transcripts --meetings Bed010 Bed017 Bmr029 Bro018 Bmr007 Bns002 --out data/candidates.jsonl --neg_ratio 0.3
# 2 label (yours)                       or: python apply_labels.py   (Claude's demo labels)
python annotate.py --inp data/candidates.jsonl --out data/annotated.jsonl
# for the 330-window multi-annotator batch use data/ann_A|B|C.jsonl - see "Expanding the annotation set"
# 3 split by meeting (+ optional validation meetings, for model selection only)
python make_dataset.py --annotated data/annotated.jsonl --test-meetings Bro018 Bmr007 --val-meetings Bmr029
# 4 predict (rule needs no training; tfidf/hybrid learn from the train split and, if given,
#            pick their threshold/C on the VALIDATION split; bert loads the model train_bert.py saved)
python predict.py --input data/test/input.jsonl --out outputs/pred_rule.jsonl   --detector rule
python predict.py --input data/test/input.jsonl --out outputs/pred_hybrid.jsonl --detector hybrid \
                  --train-input data/train/input.jsonl --train-gold data/train/gold.jsonl \
                  --val-input   data/val/input.jsonl   --val-gold   data/val/gold.jsonl
python train_bert.py --val-input data/val/input.jsonl --val-gold data/val/gold.jsonl
python predict.py --input data/test/input.jsonl --out outputs/pred_bert.jsonl   --detector bert
# 5 score
python score.py --pred outputs/pred_hybrid.jsonl --gold data/test/gold.jsonl --name hybrid
# agreement between two annotators
python kappa.py --a person1.jsonl --b person2.jsonl
```

## 6. How scores are computed (`score.py`)

For each gold context, the matching prediction is looked up by `id` (no prediction = "no action item").

* **Detection** (is it an action item?): accuracy, precision, recall, F1 for the positive class, TP/FP/FN/TN, plus the
  accuracy of the trivial "always say no" baseline (important: data is imbalanced, so accuracy alone is misleading).
* **Person**: predicted speaker id equals gold (case-insensitive).
* **Action**: word-overlap F1 between predicted and gold phrase >= 0.5 (lenient on wording).
* **Deadline**: lowercased, leading "by/before/until" removed, `NULL` must match `NULL`.
* Field accuracies are shown **conditional** (only gold actions the pipeline also detected) and **strict** (missed ones count wrong).
* **Triplet exact**: person equal AND action string identical AND deadline equal. **Triplet relaxed**: person equal AND action
  overlap >= 0.5 AND deadline equal. Precision = correct / predicted action items; recall = correct / gold action items.
* `*_errors.csv` lists every mistake with type: `false_positive`, `missed_action_item`, `wrong_person`, `wrong_action`,
  `wrong_deadline` (combinations joined by `+`) **and a `failed_stage` column** (`detect`,
  `responsibility_link`, `action_extract`, `deadline_link`) that says which pipeline stage broke.
* **Section 4 - component-level P/R/F1**: person, action and deadline each scored as their own task
  (precision = correct / predicted action items, recall = correct / gold action items).
* **Section 5 - extraction vs linking**: every field's accuracy bucketed by *where the answer was taken
  from* - the very turn that states the task (`extraction`) vs a different turn (`linking`). This is the
  plan's "responsibility linking / deadline linking" measured separately from plain extraction; it needs
  the provenance keys `predict.py` writes (`person_turn`, `action_turn`, `deadline_turn`, `commit_turn`).

## 7. The three detectors compared
| detector | what it is |
|---|---|
| `rule` | regex: first-person commitments ("I'll", "I will", "let me", "I can"...) or directives ("can you", "please", "someone should") |
| `tfidf` | TF-IDF (1-2 grams) + Logistic Regression trained on the train split; threshold/C picked on the **val** split when `--val-*` is given |
| `hybrid` | same, plus the rule signals as extra features |
| `bert` | RoBERTa fine-tuned on the same split (plan's transformer arm), `max_length=256` so windows are not truncated; trained by `train_bert.py`, tuned & selected on val by `bert_tune.py` / `bert_ensemble.py`; needs `torch` + `transformers` |
(Extraction/linking of person, action, deadline is the same rule-based code for all four detectors -
only the yes/no decision changes. spaCy dependency trimming of the action phrase is used by all of
them when `spacy` + `en_core_web_sm` are installed; `--no-spacy` turns it off.)

## 8. Results on the included data (examples of what you will see)
Split **by meeting**: train = Bed010, Bed017, Bns002 (131 contexts, 20 action items) ·
val = Bmr029 (35 contexts, 11 action items, used **only** to pick the TF-IDF threshold/C) ·
test = Bmr007 + Bro018 (95 contexts, 15 gold action items).

| detector | det. P | det. R | det. F1 | person / action / deadline (conditional) | triplet exact F1 | triplet relaxed P / R / F1 |
|---|---|---|---|---|---|---|
| rule | 0.30 | 0.67 | 0.42 | 1.00 / 0.60 / 1.00 | 0.04 | 0.18 / 0.40 / 0.25 |
| tfidf | 0.24 | 0.60 | 0.35 | 0.67 / 0.56 / 1.00 | 0.04 | 0.14 / 0.33 / 0.19 |
| hybrid | 0.50 | 0.33 | 0.40 | 1.00 / 0.80 / 1.00 | 0.00 | 0.40 / 0.27 / 0.32 |
| bert | 0.22 | 0.73 | 0.34 | 0.82 / 0.55 / 1.00 | 0.03 | 0.12 / 0.40 / 0.19 |

Component-level P/R/F1 (report section 4 - each field scored as its own task, precision = correct /
predicted action items, recall = correct / gold action items):

| detector | person P / R / F1 | action P / R / F1 | deadline P / R / F1 |
|---|---|---|---|
| rule | 0.30 / 0.67 / 0.42 | 0.18 / 0.40 / 0.25 | 0.30 / 0.67 / 0.42 |
| tfidf | 0.16 / 0.40 / 0.23 | 0.14 / 0.33 / 0.19 | 0.24 / 0.60 / 0.35 |
| hybrid | 0.50 / 0.33 / 0.40 | 0.40 / 0.27 / 0.32 | 0.50 / 0.33 / 0.40 |
| bert | 0.18 / 0.60 / 0.28 | 0.12 / 0.40 / 0.19 | 0.22 / 0.73 / 0.34 |

Read these as a *working demo*, not final results: the test set has only 15 positives, so one example moves a metric by ~7 points.
Notes on what the numbers mean:
* **Exact triplet match is no longer always 0**: `Bmr007_t845` now matches literally
  (`send me thoughts for an agenda` - the filler cleanup in `_clean_action` removed
  `", you know ,"` and `", yeah that that would be"`). It stays *near* 0 because gold phrases tasks
  differently than people speak ("look to try if I move this parameter..." vs gold "try moving this parameter...").
* **bert has the best recall (0.73) and the worst precision (0.22)**: 131 training contexts is very
  little for RoBERTa, and its threshold 0.03 was selected on only 35 validation contexts. Treat it as
  a working transformer baseline, not a win - that honest comparison is what the plan asked for.
* **How bert was improved (Oct tuning pass, validation-only selection):** the original run
  truncated **53% of windows at 128 tokens** (mean length 179) and picked its checkpoint by val
  loss; `bert_tune.py` retrains with `max_length=256`, a fine 0.01 threshold grid and per-epoch
  val-F1 selection. Three seeds were compared (val F1 0.833 / 0.696 / 0.667 - large seed variance;
  `bert_ensemble.py` checked averaging, which did not beat the best single). The val-selected winner
  (seed 0, epoch 3) moved test detection **F1 0.32 -> 0.34, recall 0.67 -> 0.73, relaxed triplet
  0.16 -> 0.19**. On 15 test positives that is ~1 context per metric: directionally good, still noisy.
* **hybrid has the best precision (0.50) and the best conditional action accuracy (0.80)**; **rule
  balances both** and is the only detector that needs no training at all.
Typical errors (see `outputs/*_errors.csv`, column `failed_stage`):
* `Bmr007_t12` pred action "do so" (from "please do so") vs gold "sign the consent form" -> `action_extract`, the action is in an earlier turn.
* `Bmr007_t471` action missing: "I'll do that" refers back to "seat number... next set of forms" -> coreference beyond the window.
* `Bmr007_t101` long rambling false positive -> `detect`.
* `Bro018_t151` gold "study the France Telecom proposal"; the window never says it in that form -> gold-phrasing gap.

## 9. IMPORTANT caveats (put these in your report)
1. **The gold here was written by Claude (one annotator)** after reading each window, as a stand-in until you label your own.
   Review `claude_labels.py`; change labels you disagree with and rerun `python apply_labels.py && python run_all.py`.
   A final report should use labels you made, ideally double-annotated (`kappa.py`).
   330 further windows from 8 new meetings are already generated; three blank annotation sheets
   (`data/ann_A|B|C.jsonl`) are ready for the multi-annotator pass - see "Expanding the annotation set" above.
2. Only 6 of 76 meetings are *labeled*, and only windows around cue words (+30% random cue-free windows, auto-labeled "not action").
   Metrics describe *this sample*, not all of ICSI. Actions without any cue phrase were not sampled.
3. Real ICSI has few action items and almost no explicit deadlines (2 of 46 positives have one), so deadline accuracy is
   mostly "predict NULL correctly".
4. Labeling rules used: see `HOW_IT_WORKS.md` section "Annotation guidelines".
5. Windows are +-2 turns, so a commitment far from its task (>2 turns) can't be linked.
6. The validation split (`Bmr029`) is removed from training, so TF-IDF/hybrid now train on 131
   contexts instead of 166 - model selection costs training data at this scale. That is the
   price of not tuning on the test set; the alternative (tuning on test) would inflate every number.
7. Exact triplet match stays near 0 because gold phrases tasks differently than people speak
   ("go through that list" cannot be produced from a window that only says "I'll go through that").
   Read the *relaxed* triplet score as the real end-to-end number; exact is a wording-consistency test.
8. The BERT detector trains on CPU on 131 contexts with only 15 test positives, so its scores are
   high-variance - one example moves a metric ~7 points. Treat it as a working comparison, not a conclusion.

## 10. Troubleshooting
* `ModuleNotFoundError: sklearn` -> `pip install scikit-learn`.
* A `.mrt` yields 0 contexts -> open it; the parser expects `<Segment ... Participant="..."> text </Segment>`.
* `python` not found on Windows -> use `py`.
* Garbled characters in terminal -> files are iso-8859-1; the parser handles it, your terminal may not.
