"""Inter-annotator agreement on SHARED contexts.  python kappa.py --a annotator1.jsonl --b annotator2.jsonl"""

import json, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True)
ap.add_argument("--b", required=True)
x = ap.parse_args()
L = lambda p: {
    r["id"]: r
    for r in map(json.loads, open(p, encoding="utf-8"))
    if r["is_action"] is not None
}
A, B = L(x.a), L(x.b)
ids = sorted(set(A) & set(B))
n = len(ids)
assert n, "no shared ids"
po = sum(A[i]["is_action"] == B[i]["is_action"] for i in ids) / n
pa, pb = (
    sum(A[i]["is_action"] for i in ids) / n,
    sum(B[i]["is_action"] for i in ids) / n,
)
pe = pa * pb + (1 - pa) * (1 - pb)
kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
both = [i for i in ids if A[i]["is_action"] and B[i]["is_action"]]
f = lambda k: (
    sum((A[i][k] or "").lower() == (B[i][k] or "").lower() for i in both) / len(both)
    if both
    else float("nan")
)
print(
    f"shared contexts: {n} | observed agreement {po:.3f} | Cohen's kappa (is_action) {kappa:.3f}"
)
print(
    f"where both say action item (n={len(both)}): same person {f('person'):.2f} | same deadline {f('deadline'):.2f}"
)
