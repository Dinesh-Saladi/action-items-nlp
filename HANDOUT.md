# One-Page Handout — Action-Item Triplet Extraction

**Hybrid NLP Pipeline for Explicit Action-Item Triplet Extraction from Multi-Turn Meeting Conversations**

### Problem
Meetings hide tasks in informal multi-turn speech. Given a 5-turn window of a multi-party transcript, output a
structured triplet **(Person, Action, Deadline)**. The three pieces usually sit in *different turns*
(`Alice: update the docs` → `Bob: I'll do it` → `Alice: by Friday`), so this is a **linking** problem, not a
search problem. Long-range reasoning is out of scope: context is ±2 turns.

### Approach — one pipeline, four detectors
7 stages: normalize → turn structure → **detect** → extract entity/time → **link responsibility** →
**link deadline** → output. Stages 4–7 are shared code; only stage 3 differs:

| detector | idea |
|---|---|
| `rule` | commitment/directive regex + anti-patterns (`I can imagine`, questions skipped) |
| `tfidf` | TF-IDF 1–2 grams + class-balanced Logistic Regression |
| `hybrid` | tfidf + rule flags as extra features |
| `bert` | RoBERTa fine-tuned for detection (threshold chosen on validation) |

Action phrases are trimmed to a minimal verb phrase with a **spaCy dependency parse**; PERSON names are
collected with NER (informational — gold uses speaker IDs).

### Data & protocol
- ICSI corpus, 76 `.mrt` transcripts; we use transcript + speaker + our own annotation layer
- **261 contexts labeled (46 action items, 6 meetings)** · **330 generated from 8 new meetings, awaiting labels** · **591 total** (plan target 500–1,000)
- Split **by meeting**: 131 train / **35 validation** / 95 test (20 / 11 / 15 action items)
- Validation only for model selection (threshold, C, epoch). **Test gold is read by the scorer alone.**

### Results (test: 95 contexts, 15 gold action items)

| detector | det P / R / F1 | exact F1 | relaxed P / R / F1 |
|---|---|---|---|
| rule | 0.30 / **0.67** / **0.42** | **0.04** | 0.18 / 0.40 / **0.25** |
| tfidf | 0.24 / 0.60 / 0.35 | **0.04** | 0.14 / 0.33 / 0.19 |
| hybrid | **0.50** / 0.33 / 0.40 | 0.00 | **0.40** / 0.27 / 0.32 |
| bert | 0.21 / **0.67** / 0.32 | 0.03 | 0.11 / 0.33 / 0.16 |

Component P/R/F1 (report §4): action phrase is the weakest field for **every** detector (0.16–0.40 F1);
deadline scores high only because 44 of 46 positives have `NULL`.

### Key finding
Splitting every answer by *where it came from* (report §5):

| field | same turn (extraction) | different turn (linking) |
|---|---|---|
| person | 0.87 (20/23) | 0.73 (8/11) |
| **action** | **0.74 (17/23)** | **0.27 (3/11)** |
| deadline | 1.00 (4/4) | 1.00 (30/30) |

**Action phrasing collapses 0.74 → 0.27 when the task must be borrowed from another turn** (anaphora:
*"I'll do that"*). The bottleneck is cross-turn action linking — not detection.

### Ablations
- Validation-tuned threshold (same training data): tfidf F1 **0.12 → 0.35**, hybrid **0.33 → 0.42**
- spaCy trimming off: exact triplet F1 **0.04 → 0.00** (relaxed unchanged) → attributable, not luck
- BERT first run collapsed to the class prior (val F1 0.00) → balanced batches + 15 epochs + validation-chosen threshold 0.30 → **val F1 0.667**, best test recall (0.67)

### Plan status
✅ 4 detectors compared (incl. transformer) · ✅ component P/R/F1 · ✅ linking measured separately ·
✅ train/validation/test split · ✅ spaCy POS/dep + NER · ✅ failed-stage attribution
⏳ 591 contexts generated, **261 labeled** (human work) · ❌ optional dialogue-act layer (files not in repo)

### Limitations
Single-annotator gold (no κ yet) · 6 of 76 meetings labeled · cue-centred sampling · ±2-turn window ·
almost no real deadlines (2 of 46) · test has only 15 positives (1 example ≈ 6.7 pts) · exact match bounded by gold wording

### Next steps
1. Label the 330 generated windows → 591 contexts in the plan's range
2. Second annotator → Cohen's/Fleiss' κ + conflict reconciliation → re-run, report before/after
3. Attack the measured weakness: **learned responsibility-linker classifier**, wider window (±2 → ±4), anaphora handling
4. Optional: pretrained date NER, ICSI dialogue-act features, larger transformer on GPU

### Reproduce
```bash
.venv/bin/python run_all.py --val-meetings Bmr029 --with-bert
```
Reports + per-example errors → `outputs/` · Docs: `README`, `HOW_IT_WORKS`, `REPO_SUMMARY`, `PLAN_TRACEABILITY`,
`PRESENTATION` (22 slides), `SPEAKER_NOTES` · 14 files / 1,713 lines / Black-clean / 3 git commits
