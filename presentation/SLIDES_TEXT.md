# SLIDES — paste-ready text for PowerPoint / Google Slides

6 slides, title + bullets only (no notes — rehearse from `PRESENTATION_SHORT.md`).
Each `## SLIDE N` block = one slide. Copy everything under the heading onto that slide.
Tables are marked `[TABLE]` — recreate them with Insert → Table (values shown exactly).

---

## SLIDE 1 — Title / Intro

**Extracting Action Items from Meeting Conversations**
*Hybrid NLP pipeline for structured (Person, Action, Deadline) extraction*

- Meetings hide tasks inside informal, multi-turn speech
- `Alice: update the docs` → `Bob: I'll take care of it` → `Alice: by Friday`
  ⇒ **(Bob, update the documentation, Friday)**
- Who / What / When sit in **different turns** → linking problem, not a search problem
- Goal: rules + ML + transformer, scored against a hand-made answer key
- [Team name] · [Course / date]

---

## SLIDE 2 — Data, Annotation & System

**From 76 transcripts to a leak-free evaluation**

- **Data:** ICSI Meeting Corpus — 76 multiparty transcripts, speaker IDs
  (ICSI has **no** action-item labels → we built the annotation layer)
- **Unit:** one context = 5 consecutive turns, at most one triplet each
- **Annotation:** 261 contexts labeled (46 action items, 6 meetings)
  **+ 330 generated from 8 new meetings, awaiting labels = 591 total**
- **Pipeline (7 stages):** normalize → turn structure → **detect** →
  extract entity/time → **link person** → **link deadline** → output
  (action phrases trimmed with a **spaCy dependency parse**)
- **4 detectors** — they differ only in the detect stage:
  `rule` (regex) · `tfidf` (TF-IDF + LogReg) · `hybrid` (+ rule flags) · `bert` (RoBERTa)
- **Protocol:** split **by meeting** → 131 train / **35 validation** / 95 test
  thresholds chosen on validation · **test gold read by scorer only**

---

## SLIDE 3 — Results

**Four detectors, three levels of scoring**

*[TABLE — detection, test set = 95 contexts / 15 gold action items]*

| detector | precision | recall | F1 |
|---|---|---|---|
| rule | 0.30 | **0.67** | **0.42** |
| tfidf | 0.24 | 0.60 | 0.35 |
| hybrid | **0.50** | 0.33 | 0.40 |
| bert | 0.21 | **0.67** | 0.32 |

- **Nobody wins outright** — precision/recall trade off between detectors
- Baseline "always say no" = 0.84 accuracy, 0 F1 → why we score P/R/F1, not accuracy
- Component scores: **action phrase is the weakest field for every detector** (F1 0.16–0.40)
- End-to-end triplet: relaxed match peaks at **0.40 P / 0.25 F1** (rule)
- Exact match ≈ 0 → gold words tasks differently than speech (one case matches exactly after filler cleanup)
- ⚠ test has only 15 positives → 1 example ≈ 6.7 points

---

## SLIDE 4 — Key analysis

**The real weakness: cross-turn action linking, not detection**

*[TABLE — accuracy by where the answer came from, all 4 detectors pooled]*

| field | same turn (extraction) | different turn (linking) |
|---|---|---|
| person | 0.87 (20/23) | 0.73 (8/11) |
| **action** | **0.74 (17/23)** | **0.27 (3/11)** |
| deadline | 1.00 (4/4) | 1.00 (30/30) |

- **Action accuracy collapses 0.74 → 0.27** when the task must come from another turn
  (`"I'll do that"` → what is "that"? anaphora beyond the window)
- Every error is labelled with its failed stage: detect / responsibility link / action extract / deadline link
- **Ablation — validation-tuned threshold** (same training data): tfidf F1 **0.12 → 0.35**, hybrid **0.33 → 0.42**
- **Ablation — spaCy trimming off:** exact triplet **0.04 → 0.00** → improvements are attributable
- **BERT:** first run collapsed to class prior (val F1 0.00) → balanced batches + 15 epochs +
  validation-chosen threshold 0.30 → **val F1 0.667**, best test recall (0.67)

---

## SLIDE 5 — Status vs plan + What's next

**Where we stand, and what remains**

*[TABLE — plan requirements]*

| plan requirement | status |
|---|---|
| rules + ML + **transformer compared** | ✅ 4 detectors, scored identically |
| component P/R/F1 (person/action/deadline) | ✅ report §4 |
| responsibility & deadline **linking measured separately** | ✅ report §5 |
| train / **validation** / test split | ✅ meeting-level, val-only tuning |
| spaCy POS/dependency extraction + NER | ✅ dependency trimming + PERSON NER |
| **500–1,000 annotated contexts** | ⏳ 591 generated, **261 labeled** |
| dialogue-act features (optional) | ❌ `.da` files not in repo |

- **Limitations:** single-annotator gold (no κ yet) · 6 of 76 meetings · cue-centred sampling · ±2-turn window · small test set
- **Next:** ① label the 330 windows ② 2nd annotator → κ + merge ③ re-run, before/after numbers
  ④ **learned responsibility-linker + wider window + anaphora handling** (targets slide 4's 0.74 → 0.27)

---

## SLIDE 6 — Thank you

**Thank you — questions?**

- **Problem:** structured (Person, Action, Deadline) from multi-turn meetings, local context only
- **Delivered:** end-to-end pipeline · 4 detectors incl. working transformer · leak-free train/val/test · stage-level scoring · 14 files / 1,713 lines
- **Key finding:** cross-turn action linking is the bottleneck (**0.74 → 0.27**)
- **Next:** label remaining 330 contexts (591 total) · second annotator for κ · learned linker + wider window
- **Reproduce:** `.venv/bin/python run_all.py --val-meetings Bmr029 --with-bert`
- **Thank you!**
