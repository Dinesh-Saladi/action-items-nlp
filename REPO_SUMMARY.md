# Repository Summary

## Purpose

This repository extracts meeting action items as `(Person, Action, Deadline)`
triples from ICSI meeting transcripts. It also evaluates the extractor against
manually prepared labels.

The normal end-to-end run is:

```text
ICSI .mrt transcripts
  -> candidate conversation windows
  -> human/demo annotations
  -> meeting-level train/test split
  -> action-item prediction
  -> scoring and error reports
```

The checked-in run uses 261 candidate contexts, of which 46 are labeled as
action items. The generated split contains 131 training contexts (20 action
items), 35 validation contexts (11 action items) and 95 test contexts (15
action items). There are 76 `.mrt` transcript files in `transcripts/`.

## Important conclusion about the model

`run_all.py` runs four detectors:

1. `rule`: regular-expression detection.
2. `tfidf`: TF-IDF word and bigram features plus Logistic Regression.
3. `hybrid`: TF-IDF plus rule-derived features.
4. `bert`: RoBERTa fine-tuned by `train_bert.py` (included when the model
   exists or `--with-bert` is passed; needs `torch` + `transformers`).

All four share the same extraction/linking code; they differ only in the
yes/no decision. Model selection (TF-IDF threshold/C, best BERT epoch) uses
the validation split only - never the test gold.

## End-to-end stages

### 1. Parse and normalize transcripts

`icsi.py` reads ICSI XML-like `.mrt` files using ISO-8859-1 encoding. It
removes transcript noise tags, normalizes text through `pipeline.norm`, sorts
segments by timestamp, and merges consecutive fragments from the same speaker.

### 2. Generate candidate contexts

`icsi_candidates.py` uses `icsi.make_contexts` to create five-turn windows
(two turns before and after a cue turn). Cue windows are separated by at least
four turns. It also samples cue-free negative windows according to
`--neg_ratio`. The output is unlabeled `data/candidates.jsonl`.

### 3. Create labels

`annotate.py` is the interactive labeling tool. It reads candidate JSONL rows,
asks the annotator whether each context is an action item, and, for positive
items, asks for person, action, and deadline. It saves after each answer and
can resume or edit previous answers.

`claude_labels.py` contains the included demo label dictionary. `apply_labels.py`
applies those labels to the candidate file and writes
`data/annotated.jsonl`. The included labels are a demo gold set and should be
reviewed before treating them as authoritative.

`merge_annotations.py` supports two or more annotator files, including three
annotators. It intersects their context IDs, majority-votes `is_action`,
selects majority person/deadline values among positive votes, chooses the most
similar action phrase, reports pairwise Cohen kappa and Fleiss kappa, and
writes disagreements to a conflicts CSV.

`kappa.py` is the simpler two-file agreement utility. It calculates Cohen
kappa for `is_action`, plus person and deadline agreement where both annotators
marked an action.

### 4. Split without meeting leakage

`make_dataset.py` separates labeled rows by meeting. Test meetings are
explicitly supplied; with `--val-meetings` the validation meetings are carved
out too and removed from training, so every other meeting becomes training
data. Each split gets:

- `input.jsonl`: context and turns only.
- `gold.jsonl`: `is_action`, person, action, and deadline labels.

The test gold file is reserved for scoring and is never passed to a detector.
The validation gold is used only to choose the TF-IDF decision threshold and
C (and, in `train_bert.py`, the best epoch).

### 5. Detect and extract predictions

`pipeline.py` contains the main seven-stage library:

1. Text normalization.
2. Turn structure preservation.
3. Action-item detection.
4. Action and time-expression extraction.
5. Responsibility/person linking.
6. Deadline linking.
7. Output triplets.

The rule detector looks for first-person commitments and direct requests or
assignments, while filtering several non-task phrases. The machine-learning
detector uses TF-IDF with Logistic Regression. The hybrid detector adds
commitment/directive rule flags to the TF-IDF text. The `bert` detector is a
RoBERTa sequence classifier loaded from `outputs/bert_model`.

The extraction logic uses regular expressions for action phrases, passive
voice, anaphoric phrases such as “do that,” and temporal expressions such as
“tomorrow” or “by Friday.” It links a commitment to its speaker and a request
to the next speaker when appropriate. When `spacy` with `en_core_web_sm` is
installed, the captured action phrase is additionally trimmed to its minimal
verb phrase with the dependency parse, and PERSON names spoken in the window
are collected into an optional `mentioned_people` field.

`predict.py` applies one selected detector to an input file and writes
prediction JSONL rows. For `tfidf` and `hybrid`, it trains only on the
training input and training gold files and, when `--val-*` files are given,
picks the threshold/C on them. Every prediction row also carries provenance
keys (`commit_turn`, `person_turn`, `action_turn`, `deadline_turn`) that
record which turn each field was taken from.

### 6. Score results

`score.py` compares predictions with gold labels and writes a Markdown report
with five sections:

1. Detection accuracy, precision, recall, F1, and the always-no baseline.
2. Field accuracy, conditional (on detected gold actions) and strict.
3. Exact and relaxed end-to-end triplet precision/recall/F1.
4. Component-level precision/recall/F1 for person, action, and deadline.
5. Accuracy bucketed by provenance: extraction (answer in the task turn) vs
   cross-turn linking (responsibility/deadline linking on their own).

It also writes a CSV error list whose rows name the failed stage (`detect`,
`responsibility_link`, `action_extract`, `deadline_link`).

`run_all.py` orchestrates splitting, runs every available detector, scores
each result, and prints a comparison table.

### 7. Optional user interface and transformer experiment

`app.py` provides a small Streamlit interface for pasting plain-text
`Speaker: text` transcripts and displaying extracted triplets.

`train_bert.py` fine-tunes a Hugging Face RoBERTa-style sequence classifier
for action-item detection. It requires `transformers`, `datasets`, `torch`,
and `accelerate`, plus model access. It trains on the same meeting-level
split as `make_dataset.py` (picking the best epoch on the validation split),
saves the model to `outputs/bert_model`, and only replaces detection: the
extraction/linking logic in `predict.py` stays shared with the other
detectors.

## File-by-file reference

### Documentation

- `README.md`: quick start, file layout, formats, commands, scoring
  definitions, detector descriptions, results, and caveats.
- `HOW_IT_WORKS.md`: conceptual explanation of the seven pipeline stages and
  annotation guidelines.
- `REPO_SUMMARY.md`: this repository-wide technical summary.
- `Nlp project.md`: the original project plan this repository implements.
- `PLAN_TRACEABILITY.md`: plan section -> implementation map and remaining gaps.

### Python source

- `icsi.py`: transcript parser, speaker-fragment merger, meeting discovery,
  and candidate-window creation.
- `icsi_candidates.py`: command-line candidate generation from `.mrt` files.
- `pipeline.py`: normalization, detectors, extraction, linking, optional spaCy
  refinement (action trimming, PERSON NER), provenance records, metrics
  helpers, and transcript demo behavior.
- `annotate.py`: interactive, resumable manual annotation.
- `claude_labels.py`: included demo labels keyed by context ID.
- `apply_labels.py`: applies demo labels to candidates.
- `merge_annotations.py`: multi-annotator majority merge and agreement report.
- `kappa.py`: two-annotator Cohen kappa report.
- `make_dataset.py`: meeting-based train/validation/test dataset creation.
- `predict.py`: prediction CLI for rule, TF-IDF, hybrid, and BERT detectors,
  with validation-based threshold/C selection and provenance output.
- `score.py`: prediction evaluation - five report sections (including
  component P/R/F1 and extraction vs linking) plus stage-attributed errors.
- `run_all.py`: complete experiment orchestration, incl. `--val-meetings` and
  `--with-bert`.
- `train_bert.py`: RoBERTa/BERT detection training on the shared split,
  exporting `outputs/bert_model`.
- `app.py`: optional Streamlit demonstration UI.

### Documentation

- `README.md`: quick start, file layout, formats, commands, scoring
  definitions, detector descriptions, results, and caveats.
- `HOW_IT_WORKS.md`: conceptual explanation of the seven pipeline stages and
  annotation guidelines.
- `REPO_SUMMARY.md`: this repository-wide technical summary.

### Input and generated data

- `transcripts/`: raw ICSI `.mrt` files and a transcript readme. These are
  source material, not generated by the pipeline.
- `data/candidates.jsonl`: unlabeled candidate contexts.
- `data/annotated.jsonl`: candidate contexts plus the included labels.
- `data/train/input.jsonl`: training contexts without labels.
- `data/train/gold.jsonl`: training labels used by TF-IDF and hybrid training.
- `data/val/input.jsonl`, `data/val/gold.jsonl`: validation split (model
  selection only: threshold/C, best BERT epoch).
- `data/test/input.jsonl`: test contexts without labels.
- `data/test/gold.jsonl`: test answer key used only by scoring.

### Output files

- `outputs/pred_rule.jsonl`: rule-detector predictions.
- `outputs/pred_tfidf.jsonl`: TF-IDF-detector predictions.
- `outputs/pred_hybrid.jsonl`: hybrid-detector predictions.
- `outputs/pred_bert.jsonl`: BERT-detector predictions.
- `outputs/bert_model/`: fine-tuned RoBERTa detector saved by `train_bert.py`.
- `outputs/*_report.md`: metrics reports for each detector.
- `outputs/*_errors.csv`: per-context prediction errors for each detector.

## How to run

Install the dependencies (a virtual environment is required on PEP 668
systems; only `scikit-learn` is mandatory):

```bash
python -m venv .venv
.venv/bin/pip install scikit-learn
.venv/bin/pip install spacy && .venv/bin/python -m spacy download en_core_web_sm
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install transformers datasets accelerate
```

Run the existing data end to end:

```bash
.venv/bin/python run_all.py --val-meetings Bmr029
.venv/bin/python run_all.py --val-meetings Bmr029 --with-bert   # include RoBERTa
```

Regenerate candidates from selected transcript meetings:

```bash
python icsi_candidates.py \
  --dir transcripts \
  --meetings Bed010 Bed017 Bmr029 Bro018 Bmr007 Bns002 \
  --out data/candidates.jsonl
```

Create manual labels:

```bash
python annotate.py \
  --inp data/candidates.jsonl \
  --out data/annotated.jsonl
```

Merge three annotators before splitting and scoring:

```bash
python merge_annotations.py \
  --files data/ann_A.jsonl data/ann_B.jsonl data/ann_C.jsonl \
  --out data/annotated.jsonl
python run_all.py
```

## Validation performed

All 14 Python source files were formatted with Black and pass Black's check
mode and `py_compile`. Verified in the `.venv` on Python 3.14.7:

- `run_all.py --val-meetings Bmr029 --with-bert` completed end to end and
  produced reports for all four detectors (rule / tfidf / hybrid / bert).
- `run_all.py --skip-split` reproduces the README §8 table bit-for-bit for
  all four detectors (and `--val-meetings Bmr029 --with-bert` regenerates the
  same split, since the split is deterministic).
- `predict.py --detector rule --no-spacy --no-ner` runs without spaCy
  (regex-only fallback), confirming the optional dependency is truly optional.
- `pipeline.py demo --file <transcript>` reproduces both examples from
  `Nlp project.md` verbatim: `(Sarah, update the documentation, Friday)` and
  `(Bob, update the documentation, Friday)`.
- The `.mrt` path (`icsi.py`, `icsi_candidates.py`) and the annotation tools
  (`annotate.py`, `apply_labels.py`, `kappa.py`, `merge_annotations.py`)
  are unchanged by this pass.

## Known limitations

- The included demo labels were produced by one annotator and are not a
  three-annotator consensus; 261 annotated contexts are also below the
  500-1,000 target in the plan.
- `merge_annotations.py` compares only context IDs present in every annotator
  file, so shared IDs are required for a complete agreement calculation.
- Candidate generation focuses on cue-centered windows and sampled negatives;
  action items without cue phrases may be missed.
- Rule-based action and deadline extraction can miss long-distance references,
  indirect commitments, and actions expressed far from the cue turn; spaCy
  trimming reduces over-long phrases but cannot resolve coreference.
- Exact triplet match stays near zero because the demo gold phrases actions
  differently than the transcripts do; the relaxed metric is the meaningful one.
- ICSI dialogue-act annotations (optional layer 3 in the plan) are not used -
  they are distributed as separate `.da` files that are not in `transcripts/`.
- The BERT detector is CPU-trained on 131 contexts, so its scores have high
  variance (15 test positives).
