"""ICSI .mrt parsing + candidate-context generation (library; CLI is icsi_candidates.py)."""

import re, glob, os
from pipeline import norm

CUE = re.compile(
    r"\b(gonna|going to|wanna|let's|i need to|we need to|i'?ll|i will|i can|let me|should|"
    r"needs? to|have to|has to|must|can you|could you|will you|please|action item|remind)\b",
    re.I,
)


def parse_mrt(path):
    raw = open(path, encoding="iso-8859-1").read()  # ICSI files are iso-8859-1
    segs = re.findall(r"<Segment([^>]*)>(.*?)</Segment>", raw, flags=re.S)
    items = []
    for attrs, body in segs:
        spk = re.search(r'Participant="([^"]+)"', attrs)
        st = re.search(r'StartTime="([\d.]+)"', attrs)
        if not spk:
            continue
        body = re.sub(
            r"<(?:VocalSound|NonVocalSound|Comment|Pause)\b[^>]*/>", " ", body
        )
        text = norm(re.sub(r"<[^>]+>", " ", body))
        if re.search(r"[A-Za-z]", text):
            items.append((float(st.group(1)) if st else 0.0, spk.group(1), text))
    items.sort(key=lambda x: x[0])
    turns = []
    for _, s, t in items:  # merge consecutive fragments of one speaker
        if turns and turns[-1]["speaker"] == s and len(turns[-1]["text"].split()) < 60:
            turns[-1]["text"] += " " + t
        else:
            turns.append({"speaker": s, "text": t})
    return turns


def meeting_files(d):
    return sorted(
        f
        for f in glob.glob(os.path.join(d, "**", "*.mrt"), recursive=True)
        if not os.path.basename(f).startswith("preamble")
    )


STRONG = re.compile(
    r"\b(i'?ll|i will|i can(?!'?t)|let me|i'?m going to|i'?m gonna|i need to|i should|we need to|we should|"
    r"you should|you need to|someone should|someone needs to|can you|could you|will you|please|"
    r"action item|remind me|i'?ll try|have to|has to|needs to)\b",
    re.I,
)


def make_contexts(turns, meeting, cue=STRONG, win=2, min_gap=4):
    """Non-overlapping windows (+-win turns) centred on cue turns."""
    out, last = [], -(10**9)
    for i, t in enumerate(turns):
        if (
            len(t["text"].split()) >= 4
            and cue.search(t["text"])
            and i - last >= min_gap
        ):
            lo, hi = max(0, i - win), min(len(turns), i + win + 1)
            out.append(
                {
                    "id": f"{meeting}_t{i}",
                    "meeting": meeting,
                    "center": i - lo,
                    "turns": turns[lo:hi],
                }
            )
            last = i
    return out
