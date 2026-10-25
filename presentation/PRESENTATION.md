# Project Status & Next Steps
### Hybrid NLP Pipeline for Explicit Action-Item Triplet Extraction from Multi-Turn Meeting Conversations

> **How to use this file:** every `## Slide N` below is one slide. Each slide has a **Key message**
> (put it on the slide as the takeaway line), short **bullet** text (paste as-is), a suggested
> **Visual**, and optional **Say** notes for yourself. Slides marked `CUT IF SHORT ON TIME` are the
> first to drop.

---

## Slide 1 — Title

**Hybrid NLP Pipeline for Explicit Action-Item Triplet Extraction from Multi-Turn Meeting Conversations**

- Extract `(Person, Action, Deadline)` from multi-party meeting transcripts (ICSI corpus)
- Rules + classical ML + transformer, evaluated against a hand-made answer key
- Status: full pipeline running end-to-end · 4 detectors compared · evaluation completed against the plan
- Course project status review

*Visual:* project name + team name + date. Optionally the one-line formula:
`ICSI Transcript + Speaker Info → Your Annotation → NLP Pipeline → (Person, Action, Deadline)`

---

## Slide 2 — Motivation

**Key message:** decisions are spoken, but tasks must be *structured* to be usable.

- Meetings bury tasks inside informal multi-turn conversation
- Example (from the project plan):

  > **Alice:** We need to update the documentation.
  > **Bob:** I'll take care of it.
  > **Alice:** Okay, have it done by Friday.

  → a human instantly reads **(Bob, update the documentation, Friday)**

- Machines must recover three things that are *scattered across turns*: who, what, when
- Downstream value: meeting assistants, task trackers, automatic meeting summaries

*Visual:* the 3-line dialogue arrow → `(Bob, update documentation, Friday)` box.
*Say:* emphasise that person/action/deadline usually live in **different turns** — that is what makes this an NLP problem, not a regex problem.

---

## Slide 3 — Why it is hard

**Key message:** three sub-problems, each of which can fail independently.

1. **Is there an action item at all?** (detection) — speech is full of *"should"*, *"have to"* that are NOT tasks
2. **Who is responsible?** — the commitment ("I'll do it") and the task ("send the report") are often in different turns
3. **Is that date a deadline?** — *"our next meeting is on Friday"* contains a date but no task deadline

- Explicitly **out of scope**: long-range reasoning, unresolved references, full meeting understanding
- Local context only: windows of **±2 turns (5 turns total)**

*Visual:* three icons/boxes: Detect · Link Person · Link Deadline, with the two counter-examples.

---

## Slide 4 — Data

**Key message:** ICSI gives the conversation; we built the missing annotation layer ourselves.

- **ICSI Meeting Corpus**: 76 `.mrt` multi-party transcripts (audio-aligned, speaker IDs)
- Only 3 ICSI layers are used: transcript text · speaker info · our own annotation
  (dialogue-act layer = optional, not used)
- Each unit = one **context**: 5 consecutive turns, at most one triplet per context
- Label schema: `is_action`, `person`, `action`, `deadline` (`NULL` when unknown)
- Candidate generation: windows centered on cue words + 30 % random cue-free windows as negatives

| | contexts | action items |
|---|---|---|
| Labeled (6 meetings) | 261 | 46 |
| Generated, awaiting labeling (8 new meetings) | 330 | — |
| **Total available** | **591** | — |

*Visual:* bar showing 261 labeled + 330 pending = 591, with a band marking the plan's 500–1,000 target.

---

## Slide 5 — Annotation protocol

**Key message:** the answer key is human-made and kept strictly separate from the model.

- Interactive terminal tool, saves after every answer, resumable, editable (`y / n / s / b / q`)
- Guidelines: concrete commitments/assignments = positive; status reports, opinions, questions = negative
- **Leak prevention by design**
  - `input.jsonl` (no labels) → only ever seen by the model
  - `gold.jsonl` (answer key) → only ever read by the scorer
- Multi-annotator support ready: Cohen's κ (`kappa.py`), majority-vote merge + Fleiss' κ + conflicts file (`merge_annotations.py`)

*Visual:* two-column diagram "Student (input) vs Teacher (gold)".
*Say:* current gold is a **single-annotator demo** — this is limitation #1 and the reason the next step is labeling.

---

## Slide 6 — System architecture

**Key message:** a 7-stage pipeline where each stage can be evaluated on its own.

1. Preprocess / normalize (noise tags, disfluencies, `O_K`→`OK`, merge speaker fragments)
2. Turn structure (speaker + order preserved)
3. **Action-item detection** ← the only stage where the 4 detectors differ
4. Entity + time extraction (action phrase, temporal expressions) — with **spaCy dependency trimming**
5. **Responsibility linking** (commitment speaker, or next speaker for requests)
6. **Deadline linking** (a time expression must be *justified*: cue word or commitment)
7. Output `(Person, Action, Deadline)` / JSONL

*Visual:* horizontal 7-box flow; box 3 highlighted with 4 detector names underneath; boxes 5–6 highlighted as "cross-turn linking".

---

## Slide 7 — The four detectors

**Key message:** same extraction/linking code, four different yes/no decisions — an honest comparison.

| detector | what it is | training |
|---|---|---|
| `rule` | commitment/directive regex with anti-patterns (`I can imagine`, questions) | none |
| `tfidf` | TF-IDF 1-2 grams + Logistic Regression | 131 train contexts |
| `hybrid` | tfidf **+ rule flags as extra features** | 131 train contexts |
| `bert` | RoBERTa fine-tuned for detection | 131 contexts, 15 epochs, CPU |

- All four share stages 4–7 (extraction, linking) → differences isolate the *detector*
- Detector interface is uniform (`turns → bool`), which is why BERT plugs into the existing pipeline with no changes downstream

*Visual:* table or 4 logos (regex / sklearn / sklearn+rules / RoBERTa).

---

## Slide 8 — Evaluation protocol (integrity slide)

**Key message:** no leakage — split by meeting, tune on validation, never touch the test gold.

- **Split by meeting**, never by utterance: same-meeting windows share topics and speakers
- 131 train / **35 validation** / 95 test contexts (20 / 11 / 15 action items)
- Validation is used **only** for model selection: TF-IDF threshold + C, best BERT epoch, BERT threshold
- Test gold is read by the scorer alone — never by any detector

*Visual:* three boxes (train → val → test) with an arrow "model selection" between train and val, and a crossed-out arrow "tuning ← test".

---

## Slide 9 — Metrics reported

**Key message:** detection, each field, and the full triplet — at component granularity the plan asked for.

1. **Detection**: accuracy, P/R/F1, plus the *"always say no"* baseline (data is imbalanced: 84 % negatives)
2. **Field accuracy** (conditional on detected items, and strict where misses count as wrong)
3. **Component P/R/F1** for person, action, deadline — each as its own task
4. **Extraction vs linking**: accuracy bucketed by *where the answer came from*
   (same turn = extraction, different turn = linking)
5. **End-to-end triplet**: exact match and relaxed match (person =, action word-overlap ≥ 0.5, deadline =)
6. Per-example errors with the **failed stage** labelled: `detect` / `responsibility_link` / `action_extract` / `deadline_link`

*Visual:* a stack of 6 labelled layers = "the scorecard".

---

## Slide 10 — Results: detection

**Key message:** rule and BERT tie on recall; hybrid wins on precision; nobody wins outright.

| detector | precision | recall | F1 |
|---|---|---|---|
| **rule** | 0.30 | 0.67 | **0.42** |
| tfidf | 0.24 | 0.60 | 0.35 |
| **hybrid** | **0.50** | 0.33 | 0.40 |
| bert | 0.22 | **0.73** | 0.34 |

- Test = 95 contexts, **15** gold action items → one example ≈ 6.7 F1 points
- Baseline "always predict no action item" = 0.84 accuracy, 0 F1

*Visual:* grouped bar chart, P/R/F1 per detector.
*Say:* at this scale, precision/recall trade off between detectors — no single winner, which is itself the finding.

---

## Slide 11 — Results: component-level P/R/F1

**Key message:** action phrasing is the weakest field; deadlines look best only because most are `NULL`.

| detector | person P/R/F1 | action P/R/F1 | deadline P/R/F1 |
|---|---|---|---|
| rule | 0.30 / 0.67 / **0.42** | 0.18 / 0.40 / **0.25** | 0.30 / 0.67 / 0.42 |
| tfidf | 0.16 / 0.40 / 0.23 | 0.14 / 0.33 / 0.19 | 0.24 / 0.60 / 0.35 |
| hybrid | **0.50** / 0.33 / 0.40 | **0.40** / 0.27 / 0.32 | **0.50** / 0.33 / 0.40 |
| bert | 0.18 / 0.60 / 0.28 | 0.12 / 0.40 / 0.19 | 0.22 / 0.73 / 0.34 |

- Action phrase F1 is the lowest row for **every** detector → phrasing, not detection, is the bottleneck
- Deadline "success" is mostly *predicting NULL correctly* (only 2 of 46 positives have a real deadline)

*Visual:* heat-map of the 4×3 table, or grouped bars with "action" highlighted.

---

## Slide 12 — Results: end-to-end triplet

**Key message:** relaxed triplet is the meaningful end-to-end number; exact match is a wording test.

| detector | exact F1 | relaxed P / R / F1 |
|---|---|---|
| rule | **0.04** | 0.18 / 0.40 / **0.25** |
| tfidf | **0.04** | 0.14 / 0.33 / 0.19 |
| hybrid | 0.00 | **0.40** / 0.27 / 0.32 |
| bert | 0.03 | 0.12 / 0.40 / 0.19 |

- Exact match went **0.00 → 0.04** this pass: filler cleanup made `Bmr007_t845` match literally
  (`send me thoughts for an agenda`, previously `send me , you know , thoughts for an agenda , yeah …`)
- Exact stays ≈ 0 because gold phrases tasks differently than people speak — a property of the key, not of the model

*Visual:* two mini-panels: "exact match: gold vs prediction, one token off" vs "relaxed: word-overlap ≥ 0.5 ✓".

---

## Slide 13 — Where do the errors come from? (key analysis slide)

**Key message:** cross-turn *action* linking is the real failure mode — detection is not.

Accuracy of each field, pooled over all 4 detectors, split by where the answer was taken from:

| component | same turn (extraction) | different turn (linking) |
|---|---|---|
| Responsibility (person) | 0.87 (20/23) | 0.73 (8/11) |
| **Action phrase** | **0.74 (17/23)** | **0.27 (3/11)** |
| Deadline | 1.00 (4/4) | 1.00 (30/30) |

- Action accuracy collapses from **0.74 → 0.27** when the task must be borrowed from another turn
  (anaphora: *"I'll do that"* → what is "that"?)
- Person survives the cross-turn case reasonably (speaker IDs + request→next-speaker rule)
- Deadline is "perfect" only because ~94 % of deadlines are `NULL`

*Visual:* two-bar comparison for the Action row (0.74 vs 0.27) — this is the slide that shows you understood *why* the system fails.

---

## Slide 14 — Error analysis (concrete examples)

**Key message:** every error is attributed to a stage, so we know what to fix next.

| id | failure | stage |
|---|---|---|
| `Bmr007_t12` | predicted "do so" (from *"please do so"*), gold *"sign the consent form"* — task is in an earlier turn | `action_extract` |
| `Bmr007_t471` | *"I'll do that"* → no action; "that" = *"seat number … next set of forms"* (coreference beyond window) | `action_extract` |
| `Bmr007_t101` | long rambling sentence classified as a task | `detect` |
| `Bmr007_t845` | **fixed**: filler removal → exact match | — |
| `Bro018_t151` | gold *"study the France Telecom proposal"* never appears in that form in the window | gold phrasing |

- Error files: `outputs/*_errors.csv`, one row per mistake with `failed_stage`

*Visual:* screenshot/quote of one window (turns) with the gold vs predicted triplet underneath.

---

## Slide 15 — Closing the gaps from the plan

**Key message:** every plan requirement that code could satisfy is now implemented.

| plan requirement | status |
|---|---|
| Rule + ML + **transformer compared** | ✅ 4 detectors, BERT scored in the same report |
| Component P/R/F1 for person / action / deadline | ✅ score report §4 |
| Responsibility & deadline **linking measured separately** | ✅ §5, provenance-based buckets |
| **train / validation / test** split | ✅ meeting-level, val-only tuning |
| spaCy POS/dependency action extraction + NER | ✅ dependency trimming + PERSON names |
| Which stage fails | ✅ `failed_stage` column (beyond the plan) |
| 500–1,000 annotated contexts | ⏳ 591 generated, 261 labeled — **human work remaining** |
| Dialogue-act features (optional layer) | ❌ not used — `.da` files not in repo |

*Visual:* two columns ✅ done / ⏳ next, exactly as above.
*(Full mapping: `PLAN_TRACEABILITY.md`.)*

---

## Slide 16 — Engineering delivered this pass

**Key message:** reproducible, tested, documented repo — not a notebook.

- `.venv` + `requirements.txt`: scikit-learn, spaCy (+ model), PyTorch CPU, transformers
- **Validation split** with threshold/C selection (`--val-meetings`)
- **BERT integrated**: `train_bert.py` → `outputs/bert_model` → `predict.py --detector bert`
- **Scoring upgraded**: component P/R/F1, extraction-vs-linking, stage-attributed errors
- **spaCy trimming** + PERSON NER, with `--no-spacy` fallback (fully optional)
- Bug fix: sliding-window dedup no longer drops a deadline spoken one turn later
- 14 source files, 1,713 lines, all Black-formatted, all compile
- Git initialised: 2 commits, 119 files, clean working tree, reproducible output

*Visual:* repo tree or a "commits + files" badge row.

---

## Slide 17 — BERT experiment: what went wrong and what fixed it

**Key message:** we diagnosed a failed run instead of hiding it.

- **Attempt 1** (defaults: 4 epochs, threshold 0.5): model learned nothing —
  probabilities clustered at ≈ 0.20 for *both* classes → validation F1 = **0.00**
- Diagnosis: 15 % positive class + only 36 optimizer steps → the model just predicts the class prior
- **Fixes**: repeat positives ×4 (balanced batches), 15 epochs @ 5e-5, checkpoint by validation loss,
  and pick the **decision threshold on validation** (0.30) instead of assuming 0.5
- **Result of round 1**: validation F1 **0.00 → 0.667** (P 0.70 / R 0.64)
- **Round 2 — the truncation fix:** 53% of the training windows were cut off at 128 tokens
  (mean window length 179) → retrain with `max_length=256` + per-epoch validation-F1 selection
  (3 seeds compared) → validation F1 **0.833**, test **F1 0.32 → 0.34, recall 0.67 → 0.73 —
  the best recall of all four detectors**
- Caveat honestly: test precision 0.22 is still the worst → 131 contexts is very little data for RoBERTa

*Visual:* the validation-F1 ladder "0.00 → 0.667 → 0.833", with each fix as a bullet.

---

## Slide 18 — Two ablations we ran

**Key message:** the improvements are measurable, not asserted.

**1. Validation-tuned threshold (same training data, only the cut changes)**

| detector | default th = 0.50 | val-tuned threshold |
|---|---|---|
| tfidf | test F1 **0.12** | test F1 **0.35** (th 0.40) |
| hybrid | test F1 **0.33** | test F1 **0.42** (th 0.45) |

**2. spaCy dependency trimming (rule detector)**

- exact triplet F1: **0.00 → 0.04**; relaxed triplet unchanged → trimming changes *wording*, not detection
- `--no-spacy` reproduces 0.00, so the effect is attributable

*Visual:* two before/after arrows.

---

## Slide 19 — Limitations (say these before the prof does)

**Key message:** we know exactly how much to trust these numbers.

1. **Single-annotator gold** (261 contexts) — not yet double-annotated, no κ reported
2. Only **6 of 76 meetings** labeled; metrics describe this sample, not all of ICSI
3. Cue-centered sampling → action items *without* a cue phrase are invisible
4. **±2-turn window** → commitments further away cannot be linked (by design)
5. Almost no real deadlines in ICSI (2 of 46) → deadline accuracy ≈ "predict NULL"
6. Test has only **15 positives** → one example moves a metric ~6.7 points
7. Exact-triplet F1 is bounded by gold wording consistency

*Visual:* numbered list with a small "trust level" tag per item (high / medium / low).

---

## Slide 20 — What's next (roadmap)

**Key message:** the remaining work is data, not code.

**Next 2 weeks — data quality**
1. Label the 330 generated windows (`annotate.py`, resumable) → 591 contexts, inside the plan's 500–1,000 target
2. Second annotator on the same file → Cohen's κ + Fleiss' κ + `conflicts.csv` reconciliation
3. Re-run the full experiment and report **before/after** metrics and κ

**Then — model improvements (targeting the measured weakness)**
4. Lightweight **classifier for responsibility linking** (plan asks for "rules + a lightweight classifier"; features: speaker, pronouns, distance, commitment type)
5. Wider window (±2 → ±4) + anaphora handling for *"I'll do that"* — directly targets the 0.74 → 0.27 cross-turn drop
6. Optional: pretrained date NER · ICSI dialogue-act features · larger transformer on a GPU

**Deliverable:** final report with double-annotated gold, κ, per-stage metrics, ablations.

*Visual:* timeline with 3 milestones (label → re-measure → improve).

---

## Slide 21 — What we need

**Key message:** two asks.

- **A second annotator** (or your confirmation that single-annotator + demo labels is acceptable for this submission)
- **Time / GPU access** if we want to fine-tune a larger transformer (current BERT run: 24 min on CPU, 131 contexts)
- Optional: ICSI dialogue-act files (`.da`) if you want the plan's optional feature layer evaluated

*Visual:* three checkboxes.

---

## Slide 22 — Reproducibility

**Key message:** one command reproduces every number in this deck.

```bash
.venv/bin/python run_all.py --val-meetings Bmr029 --with-bert
```

- Reports → `outputs/<detector>_report.md` · mistakes → `outputs/<detector>_errors.csv`
- Docs → `README.md` (usage), `HOW_IT_WORKS.md` (concepts), `REPO_SUMMARY.md` (technical),
  `PLAN_TRACEABILITY.md` (plan § → code)
- Data → `data/` (261 labeled + 330 pending) · code → 14 Python files, 1,713 lines
- Verified: Black-clean, all files compile, `--skip-split` reproduces the tables byte-for-byte,
  both examples from the plan reproduce verbatim

*Visual:* the 4-detector results table one last time + the single command.

---

## Backup slides (only if asked)

**B1 — Pipeline on real text**
```
me026: I have it for Macrophone already, and I think by tomorrow I'll have it
→ (me026, have the information for the rest, tomorrow)
```
Rule: `COMMIT` matched ("I'll"), `TIME_RE` found "tomorrow", cue "by" justifies it as a deadline.

**B2 — Why split by meeting?**
Same-meeting windows share topic and speakers; a random utterance split would leak them and inflate every score.

**B3 — Detector internals**
- `rule`: first-person commitments (`I'll`, `I will`, `let me`) minus hedges (`I can imagine`), or directives (`please`, `can you`, `someone should`); questions skipped
- `tfidf`: 1–2 gram TF-IDF, class-balanced Logistic Regression
- `hybrid`: tfidf text + `RULECOMMIT` / `RULEDIRECTIVE` / `RULERULEDET` flag tokens
- `bert`: `bert_text(turns)` = `"spk: text </s> spk: text …"`, max length 128

**B4 — Provenance keys**
Predictions carry `commit_turn / person_turn / action_turn / deadline_turn`; the scorer uses them to
separate *extraction* (answer in the task turn) from *linking* (answer pulled from another turn).

---

### Numbers used in this deck (all verified against the repo)
- Split: 131 train / 35 val / 95 test · positives 20 / 11 / 15
- Detection P/R/F1: rule .30/.67/.42 · tfidf .24/.60/.35 · hybrid .50/.33/.40 · bert .22/.73/.34
- Exact F1: rule .04 · tfidf .04 · hybrid .00 · bert .03
- Relaxed P/R/F1: rule .18/.40/.25 · tfidf .14/.33/.19 · hybrid .40/.27/.32 · bert .12/.40/.19
- Pooled extraction vs linking: action 0.74 (17/23) vs 0.27 (3/11) · person 0.87 (20/23) vs 0.73 (8/11)
- Ablations: tfidf 0.12 → 0.35, hybrid 0.33 → 0.42 (threshold) · rule exact 0.00 → 0.04 (spaCy)
- BERT: val F1 0.00 → 0.667 (balanced batches + val-tuned threshold) → 0.833 after fixing
  53% window truncation (max_length 256); test F1 0.32 → 0.34
- Data: 76 transcripts · 261 labeled (46 positives, 6 meetings) · 330 pending (8 meetings) · 591 total
- Code: 14 files, 1,713 lines · 2 git commits, 119 files
