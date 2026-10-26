"""Terminal annotation tool. Resumable, with BACK/EDIT and optional pipeline suggestions.

  python annotate.py --inp data/candidates.jsonl --out data/ann_A.jsonl
  python annotate.py --inp data/candidates.jsonl --out data/ann_A.jsonl --suggest   (pre-fills from the rule pipeline)

Commands at the prompt:   y = action item   n = not an action item   s = skip   b = go back one   q = quit
After 'y' you get three prompts. Each shows a [default]:
    Enter = keep the default      type text = replace it      '-' = set NULL
Going back (b) re-opens a context with YOUR previous answers as defaults, so editing = b, then Enter on what is fine and
type over what is wrong. Everything is saved after every answer."""

import json, argparse, os
from pipeline import rule_detect, extract

ap = argparse.ArgumentParser()
ap.add_argument("--inp", required=True)
ap.add_argument("--out", required=True)
ap.add_argument(
    "--suggest",
    action="store_true",
    help="pre-fill person/action/deadline from the rule pipeline",
)
a = ap.parse_args()

rows = [json.loads(l) for l in open(a.inp, encoding="utf-8") if l.strip()]
labels = {}
if os.path.exists(a.out):
    labels = {
        r["id"]: r
        for r in map(json.loads, open(a.out, encoding="utf-8"))
        if r["is_action"] is not None
    }


def save():
    # Write EVERY row: answered rows carry their labels, unanswered rows keep their
    # original (null) labels. This keeps --inp/--out usable as one resumable file
    # (e.g. three annotators each working on data/ann_A.jsonl, ann_B, ann_C).
    with open(a.out + ".tmp", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(labels.get(r["id"], r), ensure_ascii=False) + "\n")
    os.replace(a.out + ".tmp", a.out)


def ask(name, default):
    shown = f" [{default}]" if default not in (None, "", "NULL") else ""
    s = input(f"  {name}{shown}: ").strip()
    if s == "-":
        return "NULL"
    return s if s else (default if default not in (None, "") else "NULL")


i = next((k for k, r in enumerate(rows) if r["id"] not in labels), 0)
print(
    f"{len(labels)}/{len(rows)} already labeled. Commands: y / n / s=skip / b=back / q=quit"
)
while i < len(rows):
    r = rows[i]
    old = labels.get(r["id"])
    print("\n" + "-" * 70, f"[{i + 1}/{len(rows)}]", r["id"])
    for k, t in enumerate(r["turns"]):
        print(("> " if k == r.get("center") else "  ") + f'{t["speaker"]}: {t["text"]}')
    if old:
        print(
            "  (your saved answer:",
            (
                "NO"
                if not old["is_action"]
                else f'{old["person"]} | {old["action"]} | {old["deadline"]}'
            ),
            ")",
        )
    sug = extract(r["turns"], rule_detect) if a.suggest else None
    if sug and not old:
        print(f"  (suggestion: {sug[0]} | {sug[1]} | {sug[2]})")
    c = input("[y/n/s/b/q] > ").strip().lower()
    if c == "q":
        break
    if c == "b":
        i = max(0, i - 1)
        continue
    if c in ("s", ""):
        i += 1
        continue
    if c == "n":
        labels[r["id"]] = dict(
            r, is_action=False, person=None, action=None, deadline=None
        )
    elif c == "y":
        d = (
            (old["person"], old["action"], old["deadline"])
            if old and old["is_action"]
            else (sug or (None, None, None))
        )
        p = ask("person (speaker id; '-' = NULL)", d[0])
        ac = ask("action", d[1])
        dl = ask("deadline ('-' = NULL)", d[2])
        labels[r["id"]] = dict(r, is_action=True, person=p, action=ac, deadline=dl)
    else:
        print("  ? use y / n / s / b / q")
        continue
    save()
    i += 1
save()
print(f"saved {len(labels)} labeled contexts -> {a.out}")
