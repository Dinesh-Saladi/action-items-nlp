"""Step 5: the 'teacher'. Compares predictions with the gold key and prints/saves scores.

  python score.py --pred outputs/pred_rule.jsonl --gold data/test/gold.jsonl --name rule
Writes outputs/<name>_report.md and outputs/<name>_errors.csv
A gold context with no prediction row counts as 'predicted: no action item'.

Report sections
  1. action-item detection (accuracy, P/R/F1, always-no baseline)
  2. field accuracy, conditional (on detected gold actions) and strict (misses count wrong)
  3. end-to-end triplet, exact and relaxed
  4. component-level precision/recall/F1 for person, action, deadline   (plan: "Evaluation")
  5. extraction vs linking: accuracy of every field bucketed by WHERE the answer was taken from
     (needs the provenance keys predict.py writes: person_turn/action_turn/deadline_turn/commit_turn)
"""

import json, argparse, csv, re, os
from collections import Counter
from pipeline import tok_f1, nd, prf


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


ap = argparse.ArgumentParser()
ap.add_argument("--pred", required=True)
ap.add_argument("--gold", required=True)
ap.add_argument("--name", default="run")
ap.add_argument("--outdir", default="outputs")
a = ap.parse_args()

gold = {g["id"]: g for g in load(a.gold)}
pred = {p["id"]: p for p in load(a.pred)}
tp = fp = fn = tn = 0
cnt = dict(person=0, action=0, deadline=0, exact=0, relaxed=0)
ok = {}  # id -> (person_ok, action_ok, deadline_ok) on jointly detected actions
errors = []
for i, g in gold.items():
    p = pred.get(i, {"is_action": False})
    if p["is_action"] and g["is_action"]:
        tp += 1
        p_ok = (p["person"] or "").lower() == (g["person"] or "").lower()
        f1 = tok_f1(g["action"], p["action"] or "")
        a_ok = f1 >= 0.5
        d_ok = nd(p["deadline"] or "NULL") == nd(g["deadline"] or "NULL")
        a_exact = (p["action"] or "").lower().strip() == g["action"].lower().strip()
        cnt["person"] += p_ok
        cnt["action"] += a_ok
        cnt["deadline"] += d_ok
        cnt["exact"] += p_ok and a_exact and d_ok
        cnt["relaxed"] += p_ok and a_ok and d_ok
        ok[i] = (p_ok, a_ok, d_ok)
        if not (p_ok and a_ok and d_ok):
            why = [
                n
                for n, o in (("person", p_ok), ("action", a_ok), ("deadline", d_ok))
                if not o
            ]
            stage = {
                "person": "responsibility_link",
                "action": "action_extract",
                "deadline": "deadline_link",
            }
            errors.append(
                (i, "wrong_" + "+".join(why), "+".join(stage[n] for n in why), g, p)
            )
    elif p["is_action"]:
        fp += 1
        ok[i] = None
        errors.append((i, "false_positive", "detect", g, p))
    elif g["is_action"]:
        fn += 1
        ok[i] = None
        errors.append((i, "missed_action_item", "detect", g, p))
    else:
        tn += 1
N, G = len(gold), tp + fn
P, R, F = prf(tp, fp, fn)
acc = (tp + tn) / N
ex_p, ex_r = cnt["exact"] / (tp + fp) if tp + fp else 0, cnt["exact"] / G if G else 0
rl_p, rl_r = cnt["relaxed"] / (tp + fp) if tp + fp else 0, (
    cnt["relaxed"] / G if G else 0
)
f = lambda p, r: 2 * p * r / (p + r) if p + r else 0
cond = lambda k: cnt[k] / tp if tp else 0
strict = lambda k: cnt[k] / G if G else 0
n_pred = tp + fp

# ---- section 4: component-level precision / recall / F1 (each field as its own task)
comp_rows = "\n".join(
    f"| {name} | {cnt[k] / n_pred if n_pred else 0:.3f} | {cnt[k] / G if G else 0:.3f} | "
    f"{f(cnt[k] / n_pred if n_pred else 0, cnt[k] / G if G else 0):.3f} |"
    for k, name in (
        ("person", "Person (responsibility)"),
        ("action", "Action phrase"),
        ("deadline", "Deadline"),
    )
)

# ---- section 5: extraction vs linking (bucketed by the provenance predict.py records)
BUCKETS = {
    "person": (
        "Responsibility linking",
        lambda p: (
            "same turn as action"
            if p.get("person_turn") == p.get("action_turn")
            else "cross-turn link"
        ),
        lambda i, p: ok[i][0],
    ),
    "action": (
        "Action extraction",
        lambda p: (
            "anchor turn (detected turn)"
            if p.get("action_turn") == p.get("commit_turn")
            else "linked from other turn"
        ),
        lambda i, p: ok[i][1],
    ),
    "deadline": (
        "Deadline linking",
        lambda p: (
            "same turn as action"
            if p.get("deadline_turn") == p.get("action_turn")
            else "cross-turn link"
        ),
        lambda i, p: ok[i][2],
    ),
}
have_prov = any(p.get("is_action") and "action_turn" in p for p in pred.values())
if have_prov:
    stats = {k: Counter() for k in BUCKETS}  # bucket -> [n, correct]
    for i, g in gold.items():
        if not g["is_action"] or ok.get(i) is None:
            continue
        p = pred[i]
        for k, (_, bucket, good) in BUCKETS.items():
            b = bucket(p)
            stats[k][b] += 1
            stats[k][b + "\x00"] += bool(good(i, p))
    link_rows = []
    for k, (label, _, _) in BUCKETS.items():
        for b in [x for x in stats[k] if not x.endswith("\x00")]:
            n = stats[k][b]
            c = stats[k][b + "\x00"]
            kind = (
                "extraction"
                if b
                in (
                    "same turn as action",
                    "anchor turn (detected turn)",
                )
                else "linking"
            )
            link_rows.append(f"| {label} | {b} | {kind} | {n} | {c / n:.3f} |")
    link_tbl = "\n".join(link_rows)
else:
    link_tbl = (
        "_not available: these predictions were written without provenance keys "
        "(regenerate them with `python predict.py`)_"
    )

rep = f"""# Score report: {a.name}
gold file: `{a.gold}`  |  predictions: `{a.pred}`  |  contexts: {N}  (gold action items: {G}, non-action: {N-G})

## 1. Action-item detection (is this context an action item?)
| metric | value |
|---|---|
| Accuracy | {acc:.3f} |
| Precision | {P:.3f} |
| Recall | {R:.3f} |
| F1 | {F:.3f} |
| Baseline accuracy ("always say no action item") | {(N-G)/N:.3f} |

Confusion: TP={tp} FP={fp} FN={fn} TN={tn}

## 2. Field accuracy (only on gold action items the pipeline also detected, n={tp})
| field | accuracy |
|---|---|
| Person (exact speaker id match) | {cond('person'):.3f} |
| Action (word-overlap F1 >= 0.5) | {cond('action'):.3f} |
| Deadline (normalized match, NULL=NULL) | {cond('deadline'):.3f} |

Same fields, strict version (missed action items count as wrong, n={G}): person {strict('person'):.3f} | action {strict('action'):.3f} | deadline {strict('deadline'):.3f}

## 3. End-to-end triplet (Person, Action, Deadline)
| match type | precision | recall | F1 |
|---|---|---|---|
| Exact (person=, action string =, deadline =) | {ex_p:.3f} | {ex_r:.3f} | {f(ex_p, ex_r):.3f} |
| Relaxed (person=, action overlap>=0.5, deadline =) | {rl_p:.3f} | {rl_r:.3f} | {f(rl_p, rl_r):.3f} |

Error counts by type: {dict(Counter(e[1] for e in errors))}
Failed stage counts: {dict(Counter(e[2] for e in errors))}

## 4. Component-level P/R/F1 (each field evaluated as its own task)
precision = correct / predicted action items ({n_pred});  recall = correct / gold action items ({G})

| component | precision | recall | F1 |
|---|---|---|---|
{comp_rows}

## 5. Extraction vs linking (accuracy by WHERE the answer was taken from)
`extraction` = answer sits in the very turn that states the task; `linking` = answer had to be
pulled from a different turn (the cross-turn cases the plan calls responsibility/deadline linking).
Reported on predicted action items only; a missed action item cannot have provenance.

| component | source of the answer | kind | n | accuracy |
|---|---|---|---|---|
{link_tbl}
"""

os.makedirs(a.outdir, exist_ok=True)
open(f"{a.outdir}/{a.name}_report.md", "w").write(rep)
with open(f"{a.outdir}/{a.name}_errors.csv", "w", newline="", encoding="utf-8") as fo:
    w = csv.writer(fo)
    w.writerow(
        [
            "id",
            "error_type",
            "failed_stage",
            "gold_person",
            "gold_action",
            "gold_deadline",
            "pred_person",
            "pred_action",
            "pred_deadline",
        ]
    )
    for i, t, stage, g, p in errors:
        w.writerow(
            [
                i,
                t,
                stage,
                g["person"],
                g["action"],
                g["deadline"],
                p.get("person"),
                p.get("action"),
                p.get("deadline"),
            ]
        )
print(rep)
print(f"saved {a.outdir}/{a.name}_report.md and {a.outdir}/{a.name}_errors.csv")
