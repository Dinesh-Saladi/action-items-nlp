# Explaining the LAST 3 SLIDES of `Progress_Review_Action_Items_Edited.pptx`

Deck: 8 slides · your part for the last 3 ≈ **2 min + 90 s + 30 s ≈ 3½ min**, then Q&A.

## ✅ PPT check (verified against the repo)

| check | verdict |
|---|---|
| Slide 6 table numbers (.30/.67/.42 · .24/.60/.35 · .50/.33/.40 · .21/.67/.32) | ✅ match `outputs/*_report.md` exactly |
| "rule best F1 0.42" / "hybrid best precision 0.50" / "recall tie 0.67" | ✅ correct |
| "0.74 → 0.27 cross-turn" · "95 contexts / 15 positives / 6.7 points" · "BERT 131 contexts" | ✅ correct |
| Slide 7 three tracks vs roadmap | ✅ consistent |
| Speaker notes already present for all 8 slides | ✅ |
| **⚠️ Slide 6 text says "Best value in each metric is bold" — but only `0.42` is bold** | ❌ also bold **0.50** (hybrid precision) and **both 0.67** (rule + bert recall) |
| **⚠️ Slide 7 "Calibrate the threshold"** reads as if it's never been calibrated | ⚠️ it already is (0.30, chosen on validation) — see Q3 below before you say "we will calibrate" |

---

## SLIDE 6 — Results So Far  `[~2 min]`

**Your goal:** show the leaderboard, then pivot to the finding that matters, then own the BERT weakness.

**1. Set up (10 s):** "All four detectors were scored under identical conditions on the held-out test set — 95 windows, 15 real action items."

**2. Read the table — don't read 12 numbers. Three takeaways (30 s):**
- *"Rule has the best overall F1, 0.42."*
- *"Hybrid trades recall for precision — 0.50 precision, best in the table."*
- *"Rule and BERT tie for best recall, 0.67."*
- Punchline: *"So there is no single winner — precision and recall trade off. That's expected with so little data."*

**3. Key finding — the real message (45 s):**
*"But the more important result isn't in the table. Every prediction records **where** the answer came from. Action accuracy is **0.74** when the task is in the same turn as the commitment, and **0.27** when it has to be borrowed from another turn — think 'I'll do that', where 'that' was said three turns earlier. So detection is not the bottleneck; **cross-turn linking is**. That's what slide 7 targets first."*

**4. BERT bullet — honest, with the fix story (30 s):**
*"BERT is the weakest overall right now: it ties for best recall but has the lowest precision, 0.21. The cause is known — 131 training contexts is tiny for a transformer. We also hit and fixed a real failure: the first run learned nothing, every probability sat at 0.20 and validation F1 was zero. Balanced batches plus a threshold chosen on validation brought validation F1 to 0.667. The remaining gap is data — track 2."*

**5. If time is short, cut:** the accuracy-baseline and exact-vs-relaxed lines (keep for Q&A — Q1/Q2 below).

**Transition:** *"So the numbers tell us two things: more data, and fix cross-turn linking. That's the roadmap."*

---

## SLIDE 7 — What's Next: Three Tracks  `[~90 s]`

**Frame first (5 s):** *"The roadmap is data-first — labeling improves every detector at once, and it's what makes BERT trainable."*

**Track 1 · Data — highest priority (35 s), with the "because" of each bullet:**
- **Label the 330 windows** → train grows **131 → ~461**, total **591**, inside the plan's 500–1,000 target. This is the single biggest lever for tfidf, hybrid *and* BERT.
- **"All three annotators + Cohen's and Fleiss' kappa"** → *all three of us label the **same** windows; one command does everything:* `merge_annotations.py --files A B C` *prints pairwise Cohen's κ and Fleiss' κ, majority-votes the labels, and writes disputed contexts to `conflicts.csv` so we discuss them.* Right now the gold is single-annotator — this makes it defensible.
- **More meetings in validation and test** → today's test has only 15 positives: **one example moves a metric 6.7 points**, so we can't reliably measure small gains.
- **Re-run → before/after table** → same protocol, so numbers are directly comparable.

**Track 2 · BERT (25 s):**
- **Bigger training set** = the root cause (131 is far too little for RoBERTa).
- **Epoch & LR sweep on validation** → we currently train one configuration (15 epochs, 5e-5); a small grid on validation, the same way tfidf picks its C and threshold.
- **"Calibrate the threshold"** → ⚠️ say it precisely: *"the threshold is already selected on validation — 0.30 — which is exactly how we fixed the collapse; with a bigger validation set that selection becomes reliable instead of noisy."*
- **Target: beat rule's 0.42 F1** — a concrete, checkable goal.

**Track 3 · Pipeline (25 s) — decode the plain-English bullets:**
- *"more surrounding turns … 'it' or 'that'"* = **widen the window ±2 → ±4 + anaphora handling** — directly attacks the 0.74 → 0.27 drop.
- *"identifies who is responsible"* = **a learned responsibility-linker** — the plan itself asks for "rules + a lightweight classifier"; features: turn distance, speaker, pronouns, commitment type.
- *"differently worded versions … evaluation"* = **normalize action phrases when scoring** (lemmas, strip fillers), applied to **both** gold and prediction — today exact match is bounded by wording: gold says *"go through that list"*, the window says *"I'll go through that"*.

**Transition:** *"All three tracks reuse the existing evaluation, so every gain will be visible in the same before/after table."*

---

## SLIDE 8 — Thank You / Questions  `[~30 s + Q&A]`

**Closing script (say it, then stop talking):**
*"To summarise: we built the input processing and labeling tools, a working seven-stage pipeline, four detectors compared under identical conditions, and a leak-free scoring setup. The main finding is that cross-turn action linking — not detection — is the bottleneck. Next: more labeled data, BERT trained properly, and pipeline refinements. Thank you — happy to take questions."*

Then introduce Q&A by inviting the specific thing you want them to ask: *"I can open any error file or walk through a specific window if you'd like."*

---

## 🔥 Likely questions on these 3 slides

**Q1. "Why keep BERT if the rule detector wins?"**
*"The goal was a comparison, not a trophy. BERT ties for best recall with zero hand-written patterns, and its weakness has a known cause — 131 contexts. Rule stays the reference because it needs no training data at all."*

**Q2. "Isn't exact match ~0 a failure?"**
*"It's mostly a property of the answer key: gold words tasks differently than people speak — gold 'go through that list' vs window 'I'll go through that'. That's why we report relaxed match (word overlap ≥ 0.5) as the main end-to-end metric — and we can hit exact when wording aligns: one case matches literally after filler cleanup."*

**Q3. "Is the BERT threshold calibrated or not?" (slide 7 trap)**
*"It is — 0.30 was chosen by a grid search on validation, and that's precisely what rescued the first run from validation F1 0.00. What's weak is the 35-context validation set it was chosen on, so recalibration happens once we add validation meetings."*

**Q4. "How do you know cross-turn is the bottleneck and not a guess?"**
*"Every prediction carries provenance keys recording which turn each answer came from, and every error row names its failed stage. Pooling all four detectors: 17 of 23 correct when the answer is in the same turn, 3 of 11 when it must come from another turn."*

**Q5. "Three annotators — how exactly do you combine them?"**
*"One command: majority vote per context, pairwise Cohen's κ plus Fleiss' κ over all three, and disputed contexts go to a conflicts file we resolve by discussion."*

**Q6. "How will you show improvement is real?"**
*"Same held-out test, before/after table, plus a bigger test set — because with 15 positives we can't distinguish a real gain from one lucky example. Label quality gets its own number: κ."*

---

### Speaking reminders
- **Slide 6:** never read the table cell-by-cell — say the three takeaways only.
- **Slide 7:** every bullet gets its *because*; track order = priority order.
- **Slide 8:** stop at "Thank you" — silence invites the questions.
