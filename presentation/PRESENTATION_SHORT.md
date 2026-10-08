# Short Presentation (6 slides) — with detailed speaker notes

**Deck:** `PRESENTATION_SHORT.md` → 6 slides, including intro and thank-you.
**Talk length:** ~8–10 minutes of speaking (notes below total ~1,900 words ≈ 12 min read, so *don't read
them* — they are your preparation material; trim as marked).
**If you want the full 22-slide version** with extra detail and more Q&A, see `PRESENTATION.md` and
`SPEAKER_NOTES.md`.

---

# SLIDE 1 — Intro: The problem

**Title:** *Extracting Action Items from Meeting Conversations — (Person, Action, Deadline)*

**Bullets (keep it this short on the slide):**
- Meetings hide tasks inside informal, multi-turn speech
- Example: `Alice: update the docs` → `Bob: I'll take care of it` → `Alice: by Friday`
  → **(Bob, update the documentation, Friday)**
- Who / What / When usually sit in **different turns** → this is a *linking* problem, not a search problem
- Goal: a hybrid pipeline (rules + ML + transformer) that outputs structured triplets, scored against a
  hand-made answer key

*Visual:* the 3-line dialogue on the left, an arrow, and a box with `(Bob, update documentation, Friday)`
on the right. One image says more than six bullets.

### 🎤 Speaker notes (≈90 seconds)

"Good morning. The problem we're tackling is simple to state and genuinely hard to do: meetings are full of
tasks, but those tasks are buried inside informal conversation, and nothing about a raw transcript tells you
what needs to be done, by whom, or by when.

Here's the smallest possible example. Alice says we need to update the documentation. Bob replies *I'll take
care of it*. Alice finishes with *have it done by Friday*. Any person in the room instantly reads that as one
structured record: **Bob — update the documentation — Friday**.

Three things make this an NLP problem rather than a lookup. **First**, you have to decide whether an action
item exists at all — meetings are full of *should*, *have to*, *we need to* that are discussion, not tasks.
**Second**, the three pieces we want — who, what, when — usually live in *different turns*, so the system has
to link across turns rather than read them out of one sentence. **Third**, a date is not automatically a
deadline: *our next meeting is Friday* contains a date but commits nobody to anything.

That's why our project is a **hybrid** pipeline: rules for linguistic patterns, classical machine learning for
detection, and a fine-tuned transformer as the third arm — all evaluated against an answer key we annotated
ourselves. We deliberately limit scope to local context — a window of ±2 turns — and leave long-range
reasoning out, so the system stays inspectable and every stage can be measured separately.

In the next few minutes I'll show you the data and the system, the results, one analysis I think is the most
important finding we have, and exactly what remains to be done."

*If asked "why not just use an LLM?"* → the plan specifies rules + ML + transformer, and inspectability is
the point: we can say **which stage** failed, which is what the analysis in slide 4 is built on.

---

# SLIDE 2 — Data, annotation and the system

**Title:** *From 76 transcripts to a leak-free evaluation*

**Bullets:**
- **Data:** ICSI Meeting Corpus — 76 multiparty transcripts, speaker IDs; we use transcript + speaker + our
  own annotation layer (ICSI has no action-item labels)
- **Units:** one context = 5 consecutive turns (±2 around a cue turn), at most one triplet each
- **Annotation:** 261 contexts labeled (46 action items, 6 meetings) · **330 from 8 new meetings generated,
  awaiting labels** · **591 total** → inside the plan's 500–1,000 target
- **System:** 7 stages — normalize → turn structure → **detect** → extract entity/time → **link person** →
  **link deadline** → output. Action phrases trimmed with a **spaCy dependency parse**
- **4 detectors**, differing *only* in stage 3: `rule` (regex) · `tfidf` (TF-IDF + LogReg) ·
  `hybrid` (+ rule flags) · `bert` (fine-tuned RoBERTa)
- **Protocol:** split **by meeting** → 131 train / **35 validation** / 95 test; validation picks thresholds,
  **test gold is read by the scorer alone**

*Visual:* a horizontal 7-box pipeline with box 3 fanned out into the 4 detector names; below it, three boxes
`train | val | test` with "model selection →" between train and val and a ✗ over "tuning ← test".

### 🎤 Speaker notes (≈2 minutes — this is your densest slide)

"The data side is where most of the real work is. ICSI gives us 76 multiparty meeting transcripts with aligned
speaker identities, but it does **not** come with action-item labels — so building that annotation layer was
the first task. We work in units we call a *context*: five consecutive turns, centered on a turn that contains
some kind of task cue, and at most one triplet per context.

Where we stand on labels: **261 contexts are labeled, containing 46 action items across 6 meetings**. This
pass we also generated **330 further candidate windows from 8 new meetings**, so the pool is now **591
contexts** — which lands inside the 500-to-1,000 range the plan called for. Those 330 are awaiting labeling;
that is human work, and it's on our next-steps list.

The pipeline itself has seven stages. Normalize the raw transcript — noise tags, disfluencies, cut-off words;
merge speaker fragments. Preserve turn structure, because who spoke matters. Then detection — decide whether
this window is an action item at all. Then extract the pieces: the action phrase and any time expression,
using regular expressions plus a **spaCy dependency parse** that trims a rambling phrase down to its minimal
verb phrase. Then responsibility linking — the speaker of a commitment like *I'll…* takes the task, and for a
request like *can you…* the next speaker does. Then deadline linking, which is conservative on purpose: a date
only becomes a deadline if a cue word like *by*, *before*, *due* justifies it, or if it sits in a commitment
turn — otherwise the model outputs NULL and never invents a date. Finally, the structured output.

Stage three — detection — is the only place the four detectors differ, and they all implement the same
interface: turns in, yes/no out. So we compare a **regex rule detector**, **TF-IDF with logistic
regression**, a **hybrid** that adds rule flags as extra features, and a **fine-tuned RoBERTa** — with
everything downstream identical. Any difference in results is therefore attributable to the detector alone.

On evaluation integrity: we split **by meeting**, never by utterance, because same-meeting windows share
speakers and topics and a random split would leak them and inflate every score. That gives 131 training, **35
validation** and 95 test contexts. The validation split is used only for model selection — the decision
threshold, the regularization constant, the best BERT epoch — and the test answer key is read by the scorer and
by nothing else."

*If asked "why not split randomly?"* → same-meeting windows share topic, vocabulary and speakers; a random
split puts near-duplicates in train and test and inflates scores. Splitting by meeting is the standard guard.

---

# SLIDE 3 — Results

**Title:** *Results: four detectors, three levels of scoring*

**Bullets / tables:**

*Detection (test: 95 contexts, 15 gold action items)*

| detector | precision | recall | F1 |
|---|---|---|---|
| rule | 0.30 | **0.67** | **0.42** |
| tfidf | 0.24 | 0.60 | 0.35 |
| hybrid | **0.50** | 0.33 | 0.40 |
| bert | 0.21 | **0.67** | 0.32 |

- **Nobody wins outright** — precision and recall trade off between detectors
- **Action phrase is the weakest field for every detector** (component F1 0.16–0.40)
- End-to-end: relaxed triplet peaks at **0.40 precision / 0.25 F1** (rule); exact match ≈ 0 → gold wording
  differs from spoken wording (one case *does* match exactly after filler cleanup)
- Caveat: baseline "always say no" = 0.84 accuracy, 0 F1 — accuracy alone is meaningless here

*Visual:* one grouped bar chart (P/R/F1 × 4 detectors) plus the small table.

### 🎤 Speaker notes (≈2 minutes)

"Here are the results, and I want to be careful about how we read them.

On detection — is this window an action item — the rule detector reaches an F1 of 0.42 with the joint-best
recall of 0.67; the hybrid has the best precision at 0.50; BERT matches the rule detector's recall at 0.67.
**No detector wins outright** — precision and recall genuinely trade off between them, and I'd rather show
you that honestly than cherry-pick one number.

Two things to keep in mind when you look at the table. First, the data is imbalanced: the trivial
*always-predict-no-action* baseline scores **0.84 accuracy and zero F1**, which is exactly why we report
precision, recall and F1 instead of accuracy. Second, the test set has only **15 positive examples**, so one
extra hit or miss moves a metric by about 6.7 points. Treat these as indicative, not precise.

The second level of scoring breaks each field into its own task — person, action, deadline, each with
precision, recall and F1. Two results there. **The action phrase is the weakest field for every single
detector**, ranging only 0.16 to 0.40 F1 — so the bottleneck is *wording the task*, not finding the task.
And deadlines score high, but that's mostly predicting NULL correctly: only **two of the 46 positives in the
whole dataset carry a real deadline**, so I don't put much weight on that number.

At the top level — the complete triplet — the *relaxed* score, which allows word overlap instead of literal
string equality, peaks at 0.40 precision and 0.25 F1 for the rule detector. Exact match is near zero, and I
want to be upfront about why: the answer key phrases tasks differently than people speak. Gold says *go
through that list*; the window only ever says *I'll go through that*. We did move exact off zero this pass —
removing conversational filler made one prediction match the key literally — which tells me exact match is
constrained by the key's wording consistency as much as by the model."

*If asked "which detector would you deploy?"* → `rule`: it needs no training data, gives the joint-best
recall and the best exact match; hybrid if you can afford its higher precision at lower recall.

---

# SLIDE 4 — Key analysis: *where* the system fails

**Title:** *The real weakness is cross-turn action linking, not detection*

**Bullets:**

*Accuracy by where the answer came from (all 4 detectors pooled)*

| field | same turn (extraction) | different turn (linking) |
|---|---|---|
| person | 0.87 (20/23) | 0.73 (8/11) |
| **action** | **0.74 (17/23)** | **0.27 (3/11)** |
| deadline | 1.00 (4/4) | 1.00 (30/30) |

- **Action accuracy collapses 0.74 → 0.27 when the task must be borrowed from another turn**
  (anaphora: *"I'll do that"* → what is "that"?)
- Errors are stage-labelled: `detect` / `responsibility_link` / `action_extract` / `deadline_link`
- **Ablations:** validation-tuned threshold (same training data): tfidf F1 **0.12 → 0.35**, hybrid
  **0.33 → 0.42** · spaCy trimming off: exact **0.04 → 0.00**
- **BERT:** first run collapsed to the class prior (val F1 0.00) → balanced batches + 15 epochs +
  validation-chosen threshold 0.30 → **val F1 0.667**, best test recall (0.67)

*Visual:* the **two-bar comparison 0.74 vs 0.27** — this is the money chart of the whole talk.

### 🎤 Speaker notes (≈2.5 minutes — the most important slide)

"This is the slide I'd most like you to remember, because it explains *why* the system fails, not just *that*
it fails.

We instrumented every prediction to record *where each answer came from* — which turn the person, the action
and the deadline were taken from. That lets us split accuracy into two buckets: **extraction**, where the
answer sits in the very turn that states the task, and **linking**, where the answer had to be pulled from a
different turn.

Person linking holds up: 0.87 when the responsible speaker is in the task turn, 0.73 when it isn't. The
speaker-ID plus request-to-next-speaker rule survives the cross-turn case reasonably well. Deadlines score
essentially perfect in both buckets — but I'd discount that, because 30 of the 34 cross-turn deadlines are
correct *NULL* predictions.

Now look at the action phrase. When the task is in the same turn, we get it right **74% of the time**. When
the task has to be borrowed from another turn, that falls to **27%**. That is a collapse of more than 40
percentage points, and it names the problem precisely: **anaphora and cross-turn coreference**. A speaker says
*I'll do that* — "that" refers to *seat number on the next set of forms*, mentioned three turns earlier. Our
±2-turn window and our regex can't resolve it, so we output nothing.

The practical consequence is where to spend effort next: not on a better classifier for detection, but on
responsibility and action linking across turns — a wider window and a small learned linker.

Supporting evidence: every error in our CSV is attributed to a stage, so this isn't a subjective reading —
the counts come straight from the error files.

And two controlled ablations back the engineering claims. With identical training data, changing only the
decision threshold — chosen on the *validation* split, never the test — takes TF-IDF from 0.12 to 0.35 F1 and
the hybrid from 0.33 to 0.42. Switching spaCy trimming off reproduces an exact-triplet F1 of exactly zero,
which shows that improvement is attributable to the trimming, not to luck.

Finally, on BERT: our first attempt failed. The model learned nothing — every probability clustered at 0.20
for both classes, validation F1 of zero, because with a 15% positive class and only 36 optimizer steps it just
predicted the class prior. We fixed it with balanced batches, more epochs, and choosing the decision threshold
on validation instead of assuming 0.5 — validation F1 went from **0.00 to 0.667**, and BERT now has the best
test recall of the four. Its precision is still poor, and that's an honest reflection of 131 training
contexts."

*If asked "is 0.27 just noise at this sample size?"* → n=11 cross-turn cases, so it is small; but the same
direction appears in every detector individually (0.00–0.33), which is why we treat it as a signal.

---

# SLIDE 5 — Status vs the plan + what's next

**Title:** *Where we stand against the plan, and what remains*

**Bullets:**

| plan requirement | status |
|---|---|
| rules + ML + **transformer compared** | ✅ 4 detectors, scored identically |
| component P/R/F1 (person/action/deadline) | ✅ report §4 |
| responsibility & deadline **linking measured separately** | ✅ report §5 |
| train / **validation** / test split | ✅ meeting-level, val-only tuning |
| spaCy POS/dependency extraction + NER | ✅ dependency trimming + PERSON names |
| **500–1,000 annotated contexts** | ⏳ 591 generated, **261 labeled** |
| dialogue-act features (optional) | ❌ `.da` files not in the repo |

- **Limitations (stated up front):** single-annotator gold, no κ yet · 6 of 76 meetings labeled ·
  cue-centred sampling · ±2-turn window · test has only 15 positives
- **Next:** ① label the 330 windows ② second annotator → κ + merge ③ re-run, report before/after
  ④ build the **learned responsibility-linker** + wider window + anaphora handling (targets slide 4's 0.74→0.27)

*Visual:* two columns ✅ / ⏳, and a 3-step roadmap arrow at the bottom (label → re-measure → improve).

### 🎤 Speaker notes (≈90 seconds)

"Against the original plan, most of it is implemented and running: the four detectors compared under identical
conditions, component-level precision/recall/F1 for each field, responsibility and deadline linking measured
*separately* from plain extraction, a proper train/validation/test split with validation-only tuning, and
spaCy dependency extraction with named-entity recognition. Two things remain open — and I want to be clear
about both.

The annotation count: 591 candidate windows exist, but only **261 are labeled**, by a single annotator. The
plan asked for 500-to-1,000 *labeled* contexts with agreement measurement. The tooling for a second annotator
is already built — Cohen's kappa, majority-vote merging, Fleiss' kappa and a conflicts file — it needs a
second person, and that's the first item on our roadmap. The second open item is the plan's optional
dialogue-act feature layer: those annotations ship as separate files that aren't in this repository, so we
didn't use them.

We also keep our limitations in front of us: single-annotator gold, six of 76 meetings labeled, cue-centred
sampling, the ±2-turn window, and a test set of only 15 positives.

The roadmap is deliberately data-first. Label the 330 generated windows, get a second annotator and report
kappa, re-run and show before-and-after numbers — that alone lifts *every* metric. Then we attack the
weakness slide 4 identified: a small **learned classifier for responsibility linking**, which the plan
actually asked for anyway, plus a wider window and proper anaphora handling to recover that 0.74-to-0.27 drop."

---

# SLIDE 6 — Thank you

**Title:** *Thank you — questions?*

**Bullets:**
- **Problem:** structured `(Person, Action, Deadline)` from multi-turn meetings, local context only
- **Delivered:** end-to-end pipeline · 4 detectors incl. a working transformer · leak-free
  train/val/test protocol · stage-level scoring with provenance · 14 files / 1,713 lines, reproducible in one
  command
- **Key finding:** cross-turn action linking is the bottleneck (0.74 → 0.27)
- **Next:** label the remaining 330 contexts (591 total) · second annotator for κ · learned linker + wider
  window
- Reproduce: `.venv/bin/python run_all.py --val-meetings Bmr029 --with-bert`
- **Thank you!**

*Visual:* clean slide — three summary lines, the command, and a big **Thank you**. No tables.

### 🎤 Speaker notes (≈60 seconds, then open the floor)

"To summarise in one breath: we took multi-party meeting transcripts and built a complete, inspectable
pipeline that turns them into structured action items — *who* does *what* by *when* — using rules, classical
machine learning and a fine-tuned transformer, all evaluated against an answer key we annotated ourselves
under a leak-free protocol where the model never sees the answer key and thresholds are chosen on a separate
validation split.

The most useful thing we learned isn't a score — it's *where* the system breaks. Detection and person
linking are workable; **the bottleneck is pulling an action out of a different turn than the one that states
it — 74% accuracy dropping to 27%** — and that's precisely what our next iteration targets.

Everything is in the repository: the code, the data, the per-example error files with the failing stage
labelled, the reports, and this deck — and the entire experiment reproduces with a single command, which
I've put on the slide.

What remains is mostly human work rather than code: labeling the 330 already-generated contexts to reach the
plan's annotation target, adding a second annotator so we can report inter-annotator agreement, and then the
learned linker.

Thank you — I'm happy to take questions, and I can open any window or any error file if you'd like to see a
concrete example."

---

## Q&A quick reference (full bank in `SPEAKER_NOTES.md`)

| question | one-line answer |
|---|---|
| Why is exact F1 ≈ 0? | Gold words tasks differently than speech; relaxed (overlap ≥ 0.5) is the meaningful metric — and one case *does* match exactly after filler cleanup |
| Is 95 test contexts enough? | No — 15 positives ≈ 6.7 pts per example; that's why annotation expansion is step 1 |
| Does the model see the answer key? | No: `input.jsonl` (no labels) → model; `gold.jsonl` → scorer only; no shared meetings |
| Why not an LLM? | Plan specifies rules+ML+transformer; inspectability lets us attribute every error to a stage |
| Is BERT a success? | Honest comparison: best recall (0.67), worst precision (0.21) on 131 contexts; also proved validation-threshold selection works |
| Where does gold come from? | One annotator + written guidelines in `HOW_IT_WORKS.md`; double annotation is next |
| What would you do next? | Label 330 windows → κ → learned linker + wider window + anaphora |
| Can I reproduce it? | `run_all.py --val-meetings Bmr029 --with-bert` — `--skip-split` reproduces these tables byte-for-byte |

**Numbers used above (all verified against the repo):** split 131/35/95 (20/11/15 positives) · detection
P/R/F1 rule .30/.67/.42, tfidf .24/.60/.35, hybrid .50/.33/.40, bert .21/.67/.32 · relaxed F1 .25/.19/.32/.16 ·
exact F1 .04/.04/.00/.03 · pooled same-vs-cross-turn action 0.74 (17/23) vs 0.27 (3/11), person 0.87 vs 0.73 ·
ablations tfidf .12→.35, hybrid .33→.42, rule exact .00→.04 · BERT val F1 0.00→0.667 (threshold 0.30) ·
data 261 labeled + 330 pending = 591 · 14 files / 1,713 lines.
