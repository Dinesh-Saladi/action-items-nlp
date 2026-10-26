# How the project works

## The problem
Meetings hide tasks in conversation. Example (real ICSI, meeting Bmr029, speaker ids are ICSI codes):
```
me018: ... how long will it take to get that information?
me026: I have it for Macrophone already, and I think by tomorrow I'll have it
me026: for for the rest.
=> (me026, have the information for the rest, tomorrow)
```
Three hard things: (1) is there an action item at all, (2) who/what/when are often in different turns,
(3) a time expression is not always a deadline ("our next meeting is on Friday").

## Data units
* **Turn** = one speaker's contiguous speech (ICSI segments from the same speaker are merged).
* **Context (window)** = 5 consecutive turns (+-2 around a cue turn). One context -> at most one triplet.
* **Gold label** per context: `is_action` (bool) and, if true, `person`, `action`, `deadline`.

## Pipeline stages (`pipeline.py`) and what happens on real text
1. **Preprocess** (`norm`, `icsi.parse_mrt`): drop `<VocalSound>`/`<NonVocalSound>`/`<Pause>`/`<Comment>` tags, `@@`, cut-off words
   (`w-`), dangling dashes, fillers (`uh`, `um`), `O_K`->`OK`; keep speaker ids; merge same-speaker fragments.
2. **Turn structure**: a context is a list of `{speaker, text}`; order is preserved because who spoke matters.
3. **Detection**: decides `is_action` for the whole window.
   * `rule`: commitment regex (`I'll`, `I will`, `I can`, `let me`, `I'm going to`) not followed by non-task verbs (`I can imagine`),
     or directive (`can you`, `please`, `someone should`); questions skipped.
   * `tfidf`: TF-IDF 1-2 grams + logistic regression (class-balanced), trained on train split (speaker names removed from text).
   * `hybrid`: tfidf + the rule flags as features.
   * `bert`: RoBERTa fine-tuned by `train_bert.py` on the same split; it replaces only this yes/no
     decision (`predict.py --detector bert`), everything below is shared code.
4. **Entity/time extraction**: temporal regex (`Friday`, `tomorrow`, `next week`, `in two weeks`, `end of the week`, dates);
   action phrase via patterns ("needs to X", "I'll X", "can you X", passive "the report needs to be sent" -> "send the report"),
   then - when `spacy` is installed - trimmed to its minimal verb phrase with the dependency parse:
   a second clause is only dropped if it brings its own subject/modal ("send the file and I will review it"
   -> "send the file"), while shared-subject coordination stays ("go back and look at the ones on the list").
   PERSON names spoken in the window are also collected (spaCy NER) into the optional
   `mentioned_people` key - supplementary only, because gold `person` is a speaker id.
5. **Responsibility linking** (`link_person`): the speaker of the commitment turn (`I'll...`) is the person. For requests
   ("can you...?") the *next* speaker is the person. If neither -> `NULL`. Anaphoric commitments ("I'll do it", "I'll handle that")
   borrow the action from the nearest other turn (`link_action`).
6. **Deadline linking** (`link_deadline`): a time expression counts only if (a) a cue precedes it (`by`, `before`, `until`, `due`,
   `ready`), or (b) it is in a commitment/obligation turn that is not about a meeting/discussion/lunch/agenda. Otherwise -> `NULL`.
   The model never invents a deadline.
7. **Output**: `(person, action, deadline)` per window; `predict.py` writes it as JSON lines.

## Why train/test are split by meeting
Same-meeting windows share topics and speakers; random splitting would leak them and inflate scores.

## Annotation guidelines (used for the included gold)
* `is_action = true` when a speaker commits to, offers to do, or is asked/assigned a concrete task
  ("I'll send you the link", "can you talk to him?", "please sign the form", "I'm gonna put labels on the chairs").
* `false` for: status reports, explanations, opinions, discussion suggestions ("we should look at the details"), generic "you have to"
  statements, questions, past actions, "let me explain...".
* `person` = ICSI speaker id of who takes the task (the requested speaker if they accepted); `NULL` if addressed to everybody or nobody.
* `action` = short verb phrase, from the text, pronouns resolved when the task is named nearby ("do that" -> "put the seat number...").
* `deadline` = the time expression for when the task is to be done/happen ("tomorrow", "in two weeks"); `NULL` otherwise
  (meeting times and past times are not deadlines).
* Several tasks in one window: label the one for the most central turn; windows are spaced >= 4 turns apart to limit this.
* Random cue-free windows are auto-labeled `false` (spot-check them if you can).
* The 662-window expansion batch is pre-annotated with one AI annotator's provisional labels
  (`data/annotated_expansion.jsonl`; review `claude_labels_expansion.py`). The same labels are copied
  into `data/ann_A.jsonl`, `ann_B.jsonl` and `ann_C.jsonl`, so those sheets are not independent
  annotations and kappa across them is 1.000 by construction - see README "Expanding the annotation
  set" and `data/ANNOTATION_PROVENANCE.md` for how to restore blank sheets and label for real agreement.

## Evaluation beyond the headline numbers
Each prediction row also records **where every field came from** (`commit_turn`, `person_turn`,
`action_turn`, `deadline_turn`). `score.py` uses it to report two extra things per detector:
* section 4: person / action / deadline as separate precision-recall tasks (the plan's
  component-level evaluation), and
* section 5: accuracy split into *extraction* (answer sits in the turn that states the task) vs
  *linking* (answer had to be pulled from another turn) - i.e. responsibility/deadline linking
  measured on their own.

`--val-meetings` (in `make_dataset.py` / `run_all.py`) holds meetings out for **model selection only**
(TF-IDF threshold, C, best BERT epoch); the test gold is never used for tuning.

## Extending
* Detector: `train_bert.py` + `predict.py --detector bert` already swap the yes/no decision; try other
  checkpoints (`--model`) or a larger context.
* More data: label more meetings; ICSI has 75 - this is the highest-value remaining gap
  (see `PLAN_TRACEABILITY.md`).
