"""Merge 2-3+ annotators' files into ONE gold-ready file + agreement report.
  python merge_annotations.py --files data/ann_A.jsonl data/ann_B.jsonl data/ann_C.jsonl --out data/annotated.jsonl
Rules: is_action = majority vote. For action items: person/deadline = majority among annotators who said yes;
action text = the annotator's phrase most similar to the others. Contexts with no majority or with different
person/deadline are written to data/conflicts.csv -> discuss together, fix, rerun.
Prints pairwise Cohen's kappa and Fleiss' kappa (is_action)."""

import json, argparse, csv, itertools
from collections import Counter
from pipeline import tok_f1

ap = argparse.ArgumentParser()
ap.add_argument("--files", nargs="+", required=True)
ap.add_argument("--out", default="data/annotated.jsonl")
ap.add_argument("--conflicts", default="data/conflicts.csv")
a = ap.parse_args()
L = lambda p: {
    r["id"]: r
    for r in map(json.loads, open(p, encoding="utf-8"))
    if r["is_action"] is not None
}
ann = [L(f) for f in a.files]
k = len(ann)
ids = sorted(set.intersection(*[set(x) for x in ann]))
print(
    f"{k} annotators, {len(ids)} contexts labeled by all (union: {len(set.union(*[set(x) for x in ann]))})"
)


def cohen(x, y):
    n = len(ids)
    po = sum(x[i]["is_action"] == y[i]["is_action"] for i in ids) / n
    pa, pb = (
        sum(x[i]["is_action"] for i in ids) / n,
        sum(y[i]["is_action"] for i in ids) / n,
    )
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, ((po - pe) / (1 - pe) if pe < 1 else 1.0)


for (i, x), (j, y) in itertools.combinations(enumerate(ann), 2):
    po, kp = cohen(x, y)
    print(f"  {a.files[i]} vs {a.files[j]}: agreement {po:.3f}, kappa {kp:.3f}")
yes = [sum(x[i]["is_action"] for x in ann) for i in ids]  # Fleiss kappa, 2 categories
P = [(y * (y - 1) + (k - y) * (k - y - 1)) / (k * (k - 1)) for y in yes]
pj = sum(yes) / (len(ids) * k)
Pe = pj**2 + (1 - pj) ** 2
Pbar = sum(P) / len(ids)
print(f"  Fleiss kappa (all {k}): {(Pbar - Pe) / (1 - Pe) if Pe < 1 else 1.0:.3f}")

base = {r["id"]: r for r in map(json.loads, open(a.files[0], encoding="utf-8"))}
conf, out = [], []
for i in ids:
    votes = [x[i] for x in ann]
    ny = sum(v["is_action"] for v in votes)
    r = dict(base[i])
    if ny * 2 == k:
        conf.append((i, "tie on is_action", votes))
        r["is_action"] = None
        out.append(r)
        continue
    r["is_action"] = ny * 2 > k
    if r["is_action"]:
        pos = [v for v in votes if v["is_action"]]
        pc, dc = (
            Counter(v["person"] for v in pos).most_common(),
            Counter(v["deadline"] for v in pos).most_common(),
        )
        r["person"], r["deadline"] = pc[0][0], dc[0][0]
        r["action"] = max(
            (v["action"] for v in pos),
            key=lambda s: sum(tok_f1(s, v["action"]) for v in pos),
        )
        if len(pc) > 1 or len(dc) > 1:
            conf.append((i, "person/deadline differ", votes))
        if ny < k:
            conf.append((i, "not unanimous on is_action", votes))
    else:
        r["person"] = r["action"] = r["deadline"] = None
        if ny > 0:
            conf.append((i, "not unanimous on is_action", votes))
    out.append(r)
with open(a.out, "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(a.conflicts, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "issue"] + [f"annotator{j+1}" for j in range(k)])
    for i, why, votes in conf:
        w.writerow(
            [i, why]
            + [
                (
                    "NO"
                    if not v["is_action"]
                    else f'{v["person"]} | {v["action"]} | {v["deadline"]}'
                )
                for v in votes
            ]
        )
print(
    f"wrote {len(out)} merged contexts -> {a.out}  (is_action=null on ties: unlabeled until you resolve)"
)
print(f"{len(conf)} contexts to discuss -> {a.conflicts}")
