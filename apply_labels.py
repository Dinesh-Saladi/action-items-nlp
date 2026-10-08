"""Turn candidates.jsonl + claude_labels.py into a fully labeled data/annotated.jsonl
(the same format annotate.py produces for YOUR manual labels)."""

import json
from claude_labels import LABELS

rows = [json.loads(l) for l in open("data/candidates.jsonl", encoding="utf-8")]
ids = {r["id"] for r in rows}
missing = [k for k in LABELS if k not in ids]
assert not missing, f"label ids not in candidates: {missing}"
with open("data/annotated.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        if r["id"] in LABELS:
            r["is_action"], (r["person"], r["action"], r["deadline"]) = (
                True,
                LABELS[r["id"]],
            )
        else:
            r["is_action"] = False
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(
    len(rows),
    "contexts,",
    sum(r["is_action"] for r in rows),
    "action items ->",
    "data/annotated.jsonl",
)
