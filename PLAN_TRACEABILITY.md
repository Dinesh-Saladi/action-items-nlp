# Plan → implementation traceability

Maps every requirement of the original plan (`Nlp project.md`) to the code in this repository.
Status: **✅ implemented** · **⚠️ partial** · **❌ not implemented** (gap).

## 1–3. Title, motivation, problem statement (§1–§3)

| Plan requirement | Status | Where |
|---|---|---|
| Hybrid pipeline (rules + ML + transformer) | ✅ | `pipeline.py` (`rule_detect`, `MLDetector`, `BERTDetector` in `predict.py`); the "hybrid" detector literally concatenates rule flags with TF-IDF features |
| Identify explicit action-item contexts in multi-party transcripts | ✅ | `rule_detect` / `MLDetector` / `BERTDetector` over 5-turn windows |
| Extract `(Person, Action, Deadline)` triplets | ✅ | `pipeline.extract()` / `extract_detail()`, written by `predict.py` |
| Limited local context window for linking (3–5 turns) | ✅ | `icsi.make_contexts(win=2)` → 5-turn windows |
| Ambiguous / long-range reasoning out of scope | ✅ | documented in `README.md` §9 and `HOW_IT_WORKS.md` |

## 4. Dataset and annotation (§4)

| Plan requirement | Status | Where / note |
|---|---|---|
| ICSI corpus as primary dataset | ✅ | `transcripts/*.mrt` (76 files), parser `icsi.parse_mrt` |
| Task-specific annotation layer | ✅ | `annotate.py` (interactive, resumable), `merge_annotations.py`, `kappa.py`; format `{id, is_action, person, action, deadline}` |
| 500–1,000 annotated contexts | ❌ | **261 contexts / 46 positives** are checked in (demo gold by one annotator, `claude_labels.py`). Tooling exists: generate more with `icsi_candidates.py`, label with `annotate.py` |
| Double annotation / agreement | ⚠️ | `kappa.py` + `merge_annotations.py` ready, but only one annotator's file exists |
| Split **by meeting** | ✅ | `make_dataset.py` |
| train / **validation** / test split | ✅ | `make_dataset.py --val-meetings`; val is carved out of train and used **only** for threshold/C and best-epoch selection (`predict.py`, `train_bert.py`) |

## 5. Methodology (§5)

| Plan requirement | Status | Where / note |
|---|---|---|
| Preprocessing, keep speaker + boundaries | ✅ | `pipeline.norm`, `icsi.parse_mrt` (noise tags, fillers, `O_K`→`OK`, fragment merge) |
| Utterance segmentation from ICSI turns | ✅ | `pipeline.make_turns`, merged segments stay ordered |
| Detection: TF-IDF + Logistic Regression / SVM | ✅ | `MLDetector` (LR; `C` selectable). SVM itself not added — the plan allows either |
| Detection: **BERT/RoBERTa compared** | ✅ | `train_bert.py` (shared split, best epoch chosen on val) + `predict.py --detector bert` + `run_all.py --with-bert`; scores appear in the same table and the same `score.py` report as the others |
| Rule-based linguistic techniques | ✅ | `COMMIT` / `DIRECTIVE` / `NOT_COMMIT` / `OBLIG` / `NEGDL` regexes |
| Person from ICSI speaker info | ✅ | `link_person` (commitment speaker, else next speaker for requests) |
| spaCy NER for person names in the dialogue | ✅ (supplementary) | `pipeline.mentioned_people` → optional `mentioned_people` key on prediction rows. Not scored: gold `person` is a speaker id, so names are reported, not judged |
| Action via POS tags / dependency relations | ✅ | `pipeline.trim_action`: dependency parse trims the captured phrase to its minimal verb phrase (keeps shared-subject coordination, drops clauses with their own subject/modal); falls back to the regex phrase without spaCy |
| Temporal extraction with patterns | ✅ | `TIME_RE` (`Friday`, `tomorrow`, `next week`, `in two weeks`, dates…) |
| Temporal extraction with pretrained NER | ❌ | rule patterns only (plan allows "NER **and** rule-based patterns"); adding a date model would need another download and would not change scores, since deadline *use* is decided by `link_deadline` |
| Responsibility linking over local context | ✅ | `link_person` + `link_action` (anaphora borrow from nearest turn) over the 5-turn window |
| Responsibility linking with rules **and** a lightweight classifier | ⚠️ | rules only; the learned component exists for *detection*, not for the link itself |
| Deadline linking (DATE ≠ deadline) | ✅ | `deadline_in_turn` + `NEGDL`: "our next meeting is on Friday" → `NULL`; never invents a deadline |
| Structured output with `NULL` defaults | ✅ | `extract()` → `(person, action, deadline)` |

## 5. Evaluation (§5 "Evaluation")

| Plan requirement | Status | Where |
|---|---|---|
| P/R/F1 for **action-item detection** | ✅ | `score.py` §1 (+ always-no baseline) |
| P/R/F1 for **person extraction** | ✅ | `score.py` §4 (row "Person (responsibility)") |
| P/R/F1 for **action extraction** | ✅ | `score.py` §4 (row "Action phrase") |
| P/R/F1 for **deadline extraction** | ✅ | `score.py` §4 (row "Deadline") |
| **Responsibility linking** measured separately | ✅ | `score.py` §5, bucket `cross-turn link` vs `same turn as action` (needs the provenance keys `predict.py` writes) |
| **Deadline linking** measured separately | ✅ | `score.py` §5, bucket `cross-turn link` vs `same turn as action` |
| **Exact triplet P/R/F1** | ✅ | `score.py` §3 (plus a relaxed variant) |
| Locate *which stage* fails | ✅ (beyond plan) | `*_errors.csv` column `failed_stage`: `detect` / `responsibility_link` / `action_extract` / `deadline_link` |

## 6. Final diagram and ICSI layers (§"Entire project is basically this")

| Plan requirement | Status | Where |
|---|---|---|
| select meetings → annotate → model → predict → compare | ✅ | `run_all.py` = split → predict (4 detectors) → score → comparison table |
| Layer 1: transcript text | ✅ | `transcripts/*.mrt` → `turns` |
| Layer 2: speaker information | ✅ | `Participant` attribute → `turns[i].speaker` |
| Layer 3: dialogue-act annotations as optional features | ❌ | they are separate `.da` files, not in `transcripts/`; plan marks this optional |
| Layer 4: own `(Action-item, Person, Action, Deadline)` layer | ✅ | `data/annotated.jsonl` |

## Closed in this pass

1. **BERT is now a real fourth detector** — trained on the *same* meeting split, selected on the
   validation split, loaded by `predict.py --detector bert`, scored by `score.py`, shown in the
   `run_all.py` table (`--with-bert`). Its first training run collapsed to the class prior
   (all probabilities ≈ 0.20, val F1 = 0.00); fixed with positive oversampling (`--pos-mult`),
   15 epochs and a **validation-selected threshold** → val F1 0.667; a later `bert_tune.py` pass
   found 53% of windows truncated at 128 tokens and retrained with `max_length=256` +
   per-epoch val-F1 selection (3 seeds) → val F1 0.833, test detection P 0.22 / R 0.73 / F1 0.34.
2. **Component-level evaluation** — `score.py` §4 gives P/R/F1 for person/action/deadline;
   §5 separates plain extraction from cross-turn linking; errors name the failed stage.
3. **Validation split** — `make_dataset.py --val-meetings`, used for threshold/C selection.
4. **spaCy dependency trimming + PERSON NER** — `trim_action`, `mentioned_people`
   (`--no-spacy` / `--no-ner` to switch off).
5. **Dedup bug** — `run_on_transcript` no longer drops a deadline that appears one turn later.
6. **Environment** — `.venv` with scikit-learn 1.9.1, spaCy 3.8.16 + `en_core_web_sm`,
   torch 2.14.1+cpu, transformers 5.19.0 (Python 3.14), `.gitignore`.

## Still open (highest value first)

1. **Annotation size** (plan: 500–1,000 contexts; evaluated: 261, single annotator) — the
   candidate windows are **generated and pre-annotated**: `data/candidates_expansion.jsonl` adds
   330 windows from 8 new meetings (`data/annotated_expansion.jsonl`, 54 positives, AI bootstrap)
   → **591 contexts total**, inside the plan's range. What remains is the human part: the three
   sheets (`data/ann_A|B|C.jsonl`) contain identical copies of the AI labels, so restore the blank
   templates and label them independently with `annotate.py`, then reconcile with
   `merge_annotations.py` / `kappa.py` (see README "Expanding the annotation set" and
   `data/ANNOTATION_PROVENANCE.md`). Re-run the experiment on the merged 591 contexts. This is the
   only open item that limits *every* metric.
2. **Exact-triplet F1 is gold-phrasing-bound** — e.g. gold `go through that list` cannot be
   produced from a window whose text only says `I'll go through that`. Double annotation +
   a wording convention in the guidelines (or relying on the relaxed metric) is the fix.
3. **Lightweight *classifier* for responsibility linking** — currently rule-only; a small
   scorer over (speaker, pronoun, distance, commitment-type) features would satisfy the plan
   literally.
4. **Pretrained date NER** for temporal candidates (plan wording); low expected impact.
5. **Dialogue-act features** (optional layer 3) — needs the ICSI `.da` files, which are not
   in this repo.
