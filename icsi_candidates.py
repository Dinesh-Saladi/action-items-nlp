"""Step 1: cut ICSI .mrt transcripts into small conversation windows ("contexts").

  python icsi_candidates.py --dir transcripts --meetings Bed010 Bed017 Bmr029 Bro018 Bmr007 Bns002 \
         --out data/candidates.jsonl --neg_ratio 0.3

* positives-ish: windows (+-2 turns) around turns with a commitment/obligation cue (STRONG regex)
* negatives:     random windows around turns with no cue at all (so detection isn't only 'hard' cases)
Omit --meetings to use every .mrt file in --dir. Output has NO labels (is_action etc. = null)."""

import json, random, argparse, os
from icsi import parse_mrt, meeting_files, make_contexts, CUE

ap = argparse.ArgumentParser()
ap.add_argument("--dir", default="transcripts")
ap.add_argument(
    "--meetings", nargs="*", help="meeting ids, e.g. Bed010 Bmr007 (default: all)"
)
ap.add_argument("--out", default="data/candidates.jsonl")
ap.add_argument(
    "--neg_ratio",
    type=float,
    default=0.3,
    help="random cue-free windows per cue window",
)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
random.seed(a.seed)

rows = []
for f in meeting_files(a.dir):
    m = os.path.splitext(os.path.basename(f))[0]
    if a.meetings and m not in a.meetings:
        continue
    turns = parse_mrt(f)
    pos = make_contexts(turns, m)
    used = {c["id"] for c in pos}
    near = set()
    for c in pos:
        i = int(c["id"].split("_t")[1])
        near.update(range(i - 4, i + 5))
    free = [
        i
        for i, t in enumerate(turns)
        if i not in near
        and 2 <= i < len(turns) - 2
        and len(t["text"].split()) >= 4
        and not CUE.search(t["text"])
    ]
    random.shuffle(free)
    negs = []
    for i in free:
        if len(negs) >= int(len(pos) * a.neg_ratio):
            break
        if (
            all(abs(i - j) > 4 for j in near_neg)
            if (near_neg := [int(n["id"].split("_n")[1]) for n in negs])
            else True
        ):
            negs.append(
                {
                    "id": f"{m}_n{i}",
                    "meeting": m,
                    "center": 2,
                    "turns": turns[i - 2 : i + 3],
                }
            )
    rows += pos + negs
    print(f"{m}: {len(pos)} cue windows + {len(negs)} random negative windows")

with open(a.out, "w", encoding="utf-8") as fo:
    for r in rows:
        r.update({"is_action": None, "person": None, "action": None, "deadline": None})
        fo.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"wrote {len(rows)} unlabeled contexts -> {a.out}")
