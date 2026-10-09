# PROGRESS PPT — slide content (6 slides)

Paste-ready content, ordered exactly as requested:
input processing → pipeline (2 slides) → results → next steps.
Each block: **Title** = slide heading · bullets/tables = slide body · **Worth mentioning** = say it aloud or keep for Q&A · **🎤 note** = prep material.

---

## SLIDE 1 — Title

**Progress Review: Action-Item Extraction from Meeting Conversations**
*Structured (Person, Action, Deadline) extraction — hybrid NLP pipeline*

- Course project progress update
- [Team name] · [Course] · [Date]
- Covered today: data processing → pipeline → results → what's next

---

## SLIDE 2 — How we process the input

**From raw transcripts to a labeled dataset**

- **Input:** ICSI meeting transcripts (`.mrt`) + speaker IDs → sliding **5-turn context windows** (±2 turns around a task cue), max one triplet per window
- **`annotate.py` — the labeling tool:**
  - interactive terminal: `y / n` for action item, then person / action / deadline (`NULL` allowed)
  - **saves after every answer → resumable & editable** (go back with `b`, quit with `q`)
  - writes `data/annotated.jsonl` — currently **261 contexts (46 action items, 6 meetings)**
- **`kappa.py` — agreement:** Cohen's κ between two annotators' files
- **`merge_annotations.py` — reconciliation:** majority-vote merge → Fleiss' κ (3+ annotators) + `conflicts.csv` for manual review
- **Leak prevention by design:**
  - `input.jsonl` (no labels) → only ever seen by the model
  - `gold.jsonl` (answer key) → only ever read by the scorer
- **Ready and waiting:** 330 more candidate windows generated from 8 new meetings → **591 total** (plan target 500–1,000)

*Worth mentioning:* κ code is written and tested but **not yet exercised** — current gold is single-annotator, so running a second annotator through `kappa.py` is the top next step.

🎤 *Note:* "Every context is one 5-turn window with at most one triplet. The labeler never loses work — it flushes to disk after each answer. The agreement machinery (Cohen's κ, Fleiss' κ, conflict file) is already built; it just needs a second human."

---

## SLIDE 3 — The pipeline (overall)

**7-stage pipeline: transcript in, structured triplet out**

```
1 normalize → 2 turn structure → 3 DETECT → 4 extract entity/time → 5 link person → 6 link deadline → 7 output
```

- **1 Normalize:** strip noise tags, repair disfluencies, `O_K`→`OK`, merge speaker fragments
- **2 Turn structure:** speaker + order preserved (speaker IDs drive responsibility)
- **3 Detect:** *is this window an action item?* ← the only stage where detectors differ (next slide)
- **4 Extract:** action phrase + time expression via regex + **spaCy dependency trimming**
  (`"I think I'll go through that whole list, I guess"` → `"go through that whole list"`)
- **5 Link person:** speaker of a commitment (`I'll…`) takes the task; for requests (`can you…`) → next speaker
- **6 Link deadline:** fires **only if justified** (cue: *by / before / due*, or inside a commitment turn) → otherwise `NULL` — the system never invents dates
- **7 Output:** `(Person, Action, Deadline)` + JSONL

*Worth mentioning (pick 2–3):*
- **Provenance keys** recorded per prediction (`commit_turn`, `person_turn`, `action_turn`, `deadline_turn`) → lets us score *extraction vs cross-turn linking* separately, and attribute **every error to a stage** (`failed_stage` in `*_errors.csv`)
- **Stages 4–7 are shared** by all detectors → any score difference is caused by the detector alone
- **spaCy is optional** — `--no-spacy` falls back to regex trimming (fully reproducible either way)
- Sliding-window **dedup** so a commitment and its deadline in adjacent windows don't double-count

🎤 *Note:* "It's deliberately modular: detection is a plug-in question — yes/no — and everything downstream (who, what, when) is common code. That's what makes the four-way comparison fair and the error analysis possible."

---

## SLIDE 4 — Detection: four alternatives

**Same interface (`turns → bool`), four ways to answer**

| detector | how it decides | training | tuning |
|---|---|---|---|
| **rule** | regex: commitments (`I'll, let me`) minus hedges (`I can imagine`) + directives (`please, can you`); questions skipped | none | hand-written patterns |
| **tfidf** | TF-IDF 1–2 grams + class-balanced Logistic Regression | 131 contexts | grid on **val**: C × threshold (20 combos) |
| **hybrid** | tfidf **+ rule flags as extra tokens** (`RULECOMMIT`, `RULEDIRECTIVE`, `RULERULEDET`) | 131 contexts | grid on **val** |
| **bert** | RoBERTa fine-tuned for the yes/no decision | 131 contexts + pretrained LM | 15 epochs, positives ×4 oversample, checkpoint by val loss, threshold **0.30** chosen on val |

- **Leak-free protocol:** split **by meeting** → 131 train / **35 validation** / 95 test
  (validation picks thresholds & C — **test gold is never touched**)
- Rule detector = **cold-start fallback** (needs zero data); hybrid tests *"rules + ML > either alone"*

*Worth mentioning:* first BERT run **collapsed to the class prior** (all probabilities ≈0.20, val F1 0.00) because 15% positives + only 36 optimizer steps — fixed by balanced batches + validation-chosen threshold (val F1 → 0.667). Good example of *why the validation split exists*.

🎤 *Note:* "Three lightweight arms and one transformer, all answering the identical question with the same downstream code. The threshold isn't assumed to be 0.5 — it's selected on validation, which turned out to matter a lot."

---

## SLIDE 5 — Results so far

**Test set: 95 contexts, 15 gold action items** (1 example ≈ 6.7 points)

| detector | detection P / R / F1 | relaxed triplet F1 | exact F1 |
|---|---|---|---|
| rule | 0.30 / **0.67** / **0.42** | **0.25** | **0.04** |
| tfidf | 0.24 / 0.60 / 0.35 | 0.19 | **0.04** |
| hybrid | **0.50** / 0.33 / 0.40 | **0.32** | 0.00 |
| bert | 0.21 / **0.67** / 0.32 | 0.16 | 0.03 |

- **No winner:** rule = best F1, hybrid = best precision, tied best recall — precision/recall trade off
- **Key finding — cross-turn linking is the bottleneck:** action-phrase accuracy **0.74 same-turn → 0.27 cross-turn** (`"I'll do that"` → what is "that"?) — detection is *not* the ceiling (oracle: 14/15 detectable)
- Component scores: action phrase is the weakest field for **every** detector (F1 0.16–0.32)
- **BERT: not functioning well yet** — ties for best recall but lowest precision (0.21) and lowest relaxed F1 (0.16); diagnosis done, performance pending
  - **TODO:** more training data (only 131 contexts) · hyperparameter/epoch tuning · larger backbone or GPU · calibrate threshold on a bigger validation set

*Worth mentioning:* baseline "always say no" = 0.84 accuracy / 0 F1 → that's why we report F1, not accuracy. Exact ≈ 0 is gold-wording-bound, not a crash (one case matches exactly after filler cleanup).

🎤 *Note:* "Honest headline: the simple rule detector still holds the best F1, and BERT is the weakest overall — we'll say that plainly. The interesting result isn't the leaderboard, it's *where* errors happen: borrowing an action from another turn."

---

## SLIDE 6 — What's next

**Three tracks: data · BERT · pipeline refinements**

**1. Multi-annotated dataset (highest priority)**
- Label the **330 generated windows** → 591 contexts, inside the plan's 500–1,000 target
- **Second annotator** on the same file → `kappa.py` (Cohen's κ) → `merge_annotations.py` (majority vote + Fleiss' κ + conflicts) → report agreement as a metric
- Add more meetings to val/test (15 positives → 6.7 pts per example; too noisy to measure gains)
- Re-run everything → **before/after table**

**2. BERT proper functionality**
- Root-cause precision collapse: 131 contexts is far too little data for RoBERTa
- Bigger training set (track 1) + epoch/LR sweep on validation + calibrated threshold
- Consider stronger backbone, class weights, or **ensemble with rules** (quick win measured: majority-vote of detectors lifts relaxed F1 0.32 → 0.34 with zero new data)
- **TODO (tracked):** `predict.py --detector bert` metrics currently below rule/hybrid — target: beat rule's 0.42 F1

**3. Pipeline refinements**
- **Wider window ±2 → ±4 + anaphora resolution** — directly targets the 0.74 → 0.27 cross-turn drop
- **Learned responsibility/action linker** (the plan asks for "rules + a lightweight classifier")
- Action normalization at scoring (lemma, passive, fillers) → lift exact/relaxed match
- Optional: ICSI dialogue-act features (`.da`), pretrained date NER for deadlines

🎤 *Note:* "The roadmap is data-first: labeling improves every detector at once, and it's what makes BERT trainable. Then we attack the measured bottleneck — cross-turn linking — not the leaderboard."

---

### Numbers used (all verified against `outputs/*_report.md`)
- Annotation: 261 labeled / 46 positives / 6 meetings · 330 pending / 8 meetings · 591 total
- Split: 131 / 35 / 95 contexts (20 / 11 / 15 positives)
- Detection P/R/F1: rule .30/.67/.42 · tfidf .24/.60/.35 · hybrid .50/.33/.40 · bert .21/.67/.32
- Relaxed F1: .25 / .19 / .32 / .16 · Exact F1: .04 / .04 / .00 / .03
- Cross-turn action: 0.74 (17/23) same-turn vs 0.27 (3/11) cross-turn · oracle detection 14/15
- BERT: first run val F1 0.00 (probs ≈0.20) → fixed (×4 oversample, 15 epochs, threshold 0.30) → val F1 0.667, test P .21 / R .67
- Ensemble measured on existing predictions: majority≥3 → relaxed F1 .34 (best single .32), rule∧hybrid → detection P .56
