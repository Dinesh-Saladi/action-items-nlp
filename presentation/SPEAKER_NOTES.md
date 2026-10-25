# Speaker Notes — 30-second script per slide

Companion to `PRESENTATION.md`. Each note is ~30–40 seconds spoken (~80–110 words).
**Bold** = the one sentence you must not skip.

**Timing:** 22 slides × ~35 s ≈ **13 minutes**, + ~7 min for questions = 20 min slot.
If you have 10 minutes: slides 1, 2, 6, 8, 10, **13**, 15, 19, 20, 22 (bold path below ✓).

---

**Slide 1 — Title** ✓
Good morning. This project turns meeting conversation into structured tasks: given a transcript, we extract
*(person, action, deadline)*. The pipeline combines rules, classical ML and a transformer, and it's evaluated
against an answer key we annotated ourselves. **Everything you'll see today is reproducible with a single
command from the repository.**

**Slide 2 — Motivation** ✓
Take this exchange: Alice says we need to update the docs, Bob says "I'll take care of it", Alice adds
"have it done by Friday". A person instantly reads *Bob, update the documentation, Friday*. **The hard part is
that those three pieces live in three different turns** — and that's what makes this a linking problem rather
than a search problem. Structured output like this is what task trackers and meeting assistants need.

**Slide 3 — Why it is hard**
Three independent failure points: is there a task at all — meetings are full of "should" and "have to" that are
not tasks; who is responsible — often decided in another turn; and is a date a deadline — "our next meeting is
Friday" has a date but no task. **We deliberately limit ourselves to a ±2-turn window**, so long-range
reasoning is out of scope by design, not by accident.

**Slide 4 — Data** ✓
We use the ICSI corpus: 76 multiparty transcripts with speaker IDs. ICSI doesn't provide action-item labels,
so we built the annotation layer ourselves — that's the main contribution of the data side. Each unit is a
5-turn context. **Right now 261 contexts are labeled from 6 meetings, and 330 more from 8 new meetings are
generated and waiting — 591 total, which lands inside the plan's 500-to-1,000 target.**

**Slide 5 — Annotation protocol**
Labeling runs through a terminal tool that saves after every answer and can be resumed or edited. The important
design choice is separation: the model only ever sees `input.jsonl` with no labels, and the answer key
`gold.jsonl` is read only by the scorer. **We also built the multi-annotator tooling — Cohen's kappa, majority
vote, Fleiss' kappa and a conflicts file — so a second annotator plugs in without any code change.**

**Slide 6 — Architecture** ✓
Seven stages: normalize, preserve turn structure, detect, extract entities and times, link responsibility,
link deadline, output. **Stage three — detection — is the only place where our four detectors differ; stages
four to seven are shared code.** That matters, because it means any difference in the results is attributable
to the detector and nothing else.

**Slide 7 — The four detectors**
A regex detector built on commitment and directive patterns with anti-patterns; TF-IDF with logistic
regression; a hybrid that adds the rule flags as features; and a fine-tuned RoBERTa. **They implement one
common interface — turns in, yes/no out — which is why the transformer slots into the existing pipeline
without touching extraction or linking.**

**Slide 8 — Evaluation protocol** ✓
This is the integrity slide. We split by meeting, never by utterance, because same-meeting windows share
speakers and topics and a random split would leak them. 131 train, 35 validation, 95 test. **The validation
split is used only for model selection — threshold, C, best epoch — and the test gold is read by the scorer
alone.** No tuning has ever touched the test set.

**Slide 9 — Metrics**
Six layers of scoring: detection with an always-say-no baseline, conditional and strict field accuracy,
component-level precision/recall/F1 for each of the three fields, an extraction-versus-linking split,
exact and relaxed triplet scores, and a per-example error file that names the stage that failed. **That last
one is beyond the plan — we don't just know we're wrong, we know where.**

**Slide 10 — Detection results** ✓
Detection: rule gets 0.42 F1, hybrid the best precision at 0.50, BERT the best recall at 0.73 after our tuning pass.
**Nobody wins outright — precision and recall trade off between detectors.** And keep in mind the test set has
only 15 positives, so one example moves a metric by about 6.7 points. The trivial always-say-no baseline
scores 0.84 accuracy and zero F1, which is exactly why we report F1 and not accuracy.

**Slide 11 — Component results**
Each field scored as its own task. **The action phrase is the lowest row for every single detector** — between
0.16 and 0.40 F1 — so phrasing, not detection, is the bottleneck. Deadlines look best, but that's mostly
predicting NULL correctly: only two of 46 positives in the whole dataset have a real deadline.

**Slide 12 — Triplet results**
End-to-end. Relaxed triplet, where action matches on word overlap, peaks at 0.40 precision and 0.25 F1 for the
rule detector. Exact match is near zero — **and this pass it stopped being zero: filler cleanup made one case
match literally**, `send me thoughts for an agenda`, which previously came out with "you know" and "yeah" in
the middle. Exact stays low because the gold phrases tasks differently than people speak.

**Slide 13 — Where the errors come from** ✓ — *this is your centrepiece*
Here's the analysis I'd most like to highlight. Pooling all four detectors and splitting each answer by where
it was taken from: person linking holds up across turns, 0.87 same-turn versus 0.73 cross-turn. Deadlines are
near perfect — but only because they're almost all NULL. **Action phrasing collapses from 0.74 when the task
is in the same turn down to 0.27 when it has to be borrowed from another turn.** So the system's real weakness
is anaphora — "I'll do that" — not detection. That tells us exactly what to build next.

**Slide 14 — Error examples**
Four concrete cases. "Please do so" gives us the action "do so" while the real task, "sign the consent form",
is one turn earlier. "I'll do that" resolves to nothing because "that" refers outside the window. One false
positive is a rambling sentence the classifier accepted. **And one case was fixed this pass and now matches
exactly.** Each error row in the CSV names the stage: detect, responsibility link, action extract, deadline link.

**Slide 15 — Plan gaps** ✓
Against the original plan: four detectors compared, component P/R/F1, linking measured separately, the
train/validation/test split, spaCy dependency extraction and NER — all implemented. **Two remain: the
annotation count, which is human work in progress, and the optional dialogue-act features, whose files aren't
in this repository.** Full mapping is in `PLAN_TRACEABILITY.md`.

**Slide 16 — Engineering**
On the engineering side: a pinned environment, the validation split, BERT integrated end to end, the scoring
upgrade, spaCy trimming with a working fallback, and a real bug fix — the sliding-window deduplication used to
drop a deadline spoken one turn later. **Fourteen files, 1,713 lines, Black-formatted, all compiling, two git
commits, clean tree, and re-running the pipeline reproduces the tables byte for byte.**

**Slide 17 — BERT story**
I want to be transparent about a failure. The first BERT run learned nothing — every probability clustered at
0.20 for both classes, validation F1 of zero. Cause: a 15% positive class and only 36 optimizer steps, so it
just predicted the class prior. **We fixed it with balanced batches, more epochs, and picking the decision
threshold on validation instead of assuming 0.5 — validation F1 went from 0.00 to 0.667.** A second round
found that 53% of windows were truncated at 128 tokens; retraining at 256 pushed validation F1 to 0.833 and
test recall to 0.73, the best of all four detectors — at the cost of precision, because 131 contexts is very
little data for a transformer.

**Slide 18 — Ablations**
Two controlled checks. Same training data, only the decision threshold changes: TF-IDF goes from 0.12 to 0.35
F1, hybrid from 0.33 to 0.42. And switching spaCy trimming off reproduces an exact-triplet F1 of exactly
zero. **So both improvements are attributable to the change, not to luck.**

**Slide 19 — Limitations** ✓
Seven limitations, and I'd rather state them myself. Single-annotator gold, no kappa yet. Six of 76 meetings
labeled. Cue-centred sampling means tasks without a cue phrase were never sampled. The ±2-turn window by
design. Almost no real deadlines in ICSI. A test set of only 15 positives. And exact match being bounded by
gold wording. **The most important one is the first — it's exactly what the next two weeks are for.**

**Slide 20 — Next steps** ✓
The remaining work is data, not code. Label the 330 generated windows, get a second annotator for kappa, and
re-run to report before-and-after numbers. **Then we attack the measured weakness: a small learned classifier
for responsibility linking — which the plan asked for anyway — plus a wider window and anaphora handling to
recover that 0.74-to-0.27 drop.**

**Slide 21 — What we need**
Two asks: a second annotator, or your confirmation that single-annotator gold is acceptable for this
submission; and, if we should push the transformer further, GPU access — the current run takes 24 minutes on
CPU and only uses 131 contexts.

**Slide 22 — Reproducibility** ✓
Everything comes down to one command: `run_all.py --val-meetings Bmr029 --with-bert`, which splits, predicts
with all four detectors, scores and prints the comparison table. Reports and per-example errors land in
`outputs/`. **Docs, data, code and this deck are all in the repository.** Happy to walk through any window or
any error file you'd like.

---

## Backup slides — only if asked

**B1** — Real example: `me026: …by tomorrow I'll have it` → commitment matched, "tomorrow" found, the word "by"
justifies it as a deadline, speaker becomes the person. Three regexes, one turn.
**B2** — Split by meeting because same-meeting windows share topic and speakers; a random split inflates scores.
**B3** — Detector internals if someone asks what the rules actually are (commitments minus hedges, directives,
questions skipped; hybrid adds flag tokens).
**B4** — Provenance keys are how we separate extraction from linking without new annotations.

---

## Likely questions and short answers

**Q: Why is exact triplet F1 almost zero?**
Because the key words tasks differently than speech. Gold says *"go through that list"*; the window only says
*"I'll go through that"*. Relaxed match — word overlap ≥ 0.5 — is the honest end-to-end metric. And it *can*
reach exact: `Bmr007_t845` does, after we removed filler.

**Q: Isn't 95 test contexts too small?**
Yes — that's limitation six. 15 positives means ±1 example ≈ 6.7 recall points. It's why we report components,
error files and ablations rather than a single headline number, and why the annotation expansion is the top
priority.

**Q: Doesn't the model see the answer key?**
No. `input.jsonl` has no labels and goes to the model; `gold.jsonl` goes only to the scorer. Train and test
share no meeting, and thresholds are picked on a separate validation split.

**Q: Why not just use an LLM?**
The plan specifies rules + classical ML + transformer. We also wanted every stage inspectable — that's what
lets us say *which* stage failed, which is the analysis in slide 13.

**Q: What would you do with more time?**
Label more meetings (directly raises every metric), add the learned responsibility-linker, widen the window
and handle anaphora — all targeted at the measured cross-turn action drop.

**Q: Is the BERT result a success?**
It's an honest comparison: best recall of the four, worst precision, on very little training data. Its value
right now is proving the detector interface generalizes and that validation-based threshold selection works.

**Q: Where does the gold come from?**
Written by one annotator reading each window, following the written guidelines in `HOW_IT_WORKS.md`. It's a
stand-in — that's why double annotation with kappa is the first next step.

**Q: Can I reproduce this?**
Yes: `run_all.py --val-meetings Bmr029 --with-bert`. It regenerates the split, all four prediction files and
all four reports; `--skip-split` reproduces the deck's tables byte for byte.
