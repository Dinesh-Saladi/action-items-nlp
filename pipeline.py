"""Meeting action-item extraction: conversation -> (Person, Action, Deadline).

Stages (matches the deck):
 1 preprocess  2 turn structure  3 detection (rules / TF-IDF+LR / BERT)
 4 entity+time extraction  5 responsibility linking  6 deadline linking  7 output
Library used by predict.py. Quick demo: python pipeline.py demo --file my_transcript.txt  (lines 'Bob: text')
"""

import re, json, argparse
from collections import Counter


# ---------------------------------------------------------------- Stage 1/2
def norm(t):
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = re.sub(r"@@+", " ", t)  # ICSI uncertain/unintelligible
    t = re.sub(r"(?<=[A-Z])_(?=[A-Z])", "", t)  # O_K -> OK, X_M_L -> XML
    t = re.sub(r"\b\w+-(?=\s)", " ", t)  # cut-off words: "w- how"
    t = re.sub(r"(?<=\s)-+(?=\s|$)|^-+\s", " ", t)  # dangling dashes
    t = re.sub(r"\b(uh+|um+|mm+|hmm+|mm-hmm)\b[,.]?", "", t, flags=re.I)  # disfluencies
    t = re.sub(r"\{[^}]*\}|\[[^\]]*\]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def make_turns(pairs):
    return [{"speaker": s, "text": norm(t)} for s, t in pairs]


# ---------------------------------------------------------------- patterns
DAY = r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
MON = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
TIME_RE = re.compile(
    rf"\b((?:(?:next|this|coming)\s+)?{DAY}|tomorrow|tonight|today|"
    rf"(?:the\s+)?end\s+of\s+(?:the\s+)?(?:day|week|month)|eod|eow|"
    rf"next\s+(?:week|month)|(?:in|within)\s+(?:\d+|a|an|two|three|four|five|few)\s+(?:days?|weeks?|hours?)|"
    rf"{MON}\s+\d{{1,2}}(?:st|nd|rd|th)?|\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?{MON})\b",
    re.I,
)
COMMIT = re.compile(
    r"\b(i'?ll|i\s+will|i\s+can(?!'?t|not)|i'?m\s+going\s+to|let\s+me|i\s+could|i\s+got\s+it)\b",
    re.I,
)
REQUEST = re.compile(r"\b(can|could|will)\s+you\b", re.I)
OBLIG = re.compile(
    r"\b(?:needs?\s+to|should|have\s+to|has\s+to|must|can\s+you|could\s+you|will\s+you|please)\b"
    r"(?!\s*(?:probably\s+)?(?:discuss|talk|think|consider|look\s+at|chat))",
    re.I,
)
NEGDL = re.compile(
    r"\b(meeting|agenda|lunch|talk about|discuss|holiday|vacation|away|out of office)\b",
    re.I,
)
PASSIVE = re.compile(
    r"^\W*(.+?)\s+(?:still\s+|really\s+)?(?:needs?|has|have)\s+to\s+be\s+(\w+)", re.I
)
VERB_AFTER = re.compile(
    r"\b(?:needs?\s+to|should|have\s+to|has\s+to|must|going\s+to|can\s+you|could\s+you|will\s+you|"
    r"i'?ll|i\s+will|i\s+can|i\s+could|let\s+me|please)\b\s*(?:probably\s+)?(.+)",
    re.I,
)
ANAPH = re.compile(
    r"^(?:(?:take\s+care\s+of|handle|do|deal\s+with|own|get|take)\s+(?:it|that|this|them)\b|(?:it|that|this)$)",
    re.I,
)
IRREG = {
    "updated": "update",
    "prepared": "prepare",
    "scheduled": "schedule",
    "created": "create",
    "sent": "send",
    "written": "write",
    "done": "do",
    "made": "make",
    "merged": "merge",
    "organized": "organize",
    "shared": "share",
    "revised": "revise",
    "released": "release",
}

# ---------------------------------------------------------------- Stage 3: detection
# Real meeting speech is full of "should"/"have to" in ordinary discussion, so the detector only fires on
# (a) first-person commitments/offers, or (b) direct requests / assignments.
NOT_COMMIT = re.compile(
    r"\bi\s+can\s+(?:imagine|see|say|tell|understand|hear|think|believe|assume|guess|just|also say)\b|"
    r"\bi'?ll\s+(?:be|say|tell you what|admit|bet)\b|\bi\s+will\s+(?:be|say)\b|"
    r"\blet\s+me\s+(?:explain|say|ask|see|just|rephrase|restate|back|know)\b|\bso\s+that\s+i\s+can\b",
    re.I,
)
DIRECTIVE = re.compile(
    r"\b(?:please|can\s+you|could\s+you|will\s+you|someone\s+(?:should|needs\s+to|has\s+to)|"
    r"somebody\s+(?:should|needs\s+to)|everybody\s+(?:should|needs\s+to))\b",
    re.I,
)


def rule_detect(turns):
    for t in turns:
        x = t["text"]
        if x.rstrip().endswith("?") and not COMMIT.search(
            x
        ):  # questions are rarely commitments
            continue
        if (COMMIT.search(x) and not NOT_COMMIT.search(x)) or DIRECTIVE.search(x):
            return True
    return False


def ctx_text(
    turns,
):  # speaker names removed on purpose (avoid leaking names into the classifier)
    return " ".join(t["text"].lower() for t in turns)


def bert_text(turns):
    """Turn encoding used by BOTH train_bert.py and predict.py --detector bert (must match)."""
    return " </s> ".join(f'{t["speaker"]}: {t["text"]}' for t in turns)


class MLDetector:
    """TF-IDF + Logistic Regression. hybrid=True also feeds the rule signals (commitment / directive found,
    center-turn commitment) as extra features -> the 'hybrid' detector."""

    def __init__(self, hybrid=False, threshold=0.5, C=1.0):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression

        self.hybrid, self.threshold = hybrid, threshold
        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2)
        self.clf = LogisticRegression(class_weight="balanced", max_iter=2000, C=C)

    def _txt(self, turns):
        s = ctx_text(turns)
        if self.hybrid:
            s += " " + " ".join(f"RULE{k}" for k, v in self._flags(turns).items() if v)
        return s

    @staticmethod
    def _flags(turns):
        has = lambda rx: any(
            rx.search(t["text"]) and not t["text"].rstrip().endswith("?") for t in turns
        )
        return {
            "COMMIT": any(
                COMMIT.search(t["text"]) and not NOT_COMMIT.search(t["text"])
                for t in turns
            ),
            "DIRECTIVE": has(DIRECTIVE),
            "RULEDET": rule_detect(turns),
        }

    def fit(self, ctxs):
        self.clf.fit(
            self.vec.fit_transform([self._txt(c["turns"]) for c in ctxs]),
            [int(c["is_action"]) for c in ctxs],
        )
        return self

    def __call__(self, turns):
        return (
            self.clf.predict_proba(self.vec.transform([self._txt(turns)]))[0][1]
            >= self.threshold
        )


# ---------------------------------------------------------------- Stage 4: extraction
def _clean_action(s):
    s = re.split(r"\s+(?:by|before|until|so that|and then)\b|[.?!;]", s)[0]
    s = TIME_RE.sub("", s).strip(" ,")
    s = re.sub(r"^(?:to|go ahead and)\s+", "", s, flags=re.I).strip()
    s = re.sub(r",\s*(?:you know|I mean|I guess)\b,?", " ", s, flags=re.I)
    s = re.split(r",\s*(?:yeah|yes|okay|ok|well|sure)\b", s, flags=re.I)[0]
    s = re.sub(r"\s+([,.])", r"\1", s)
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ,")
    if (
        not s
        or ANAPH.match(s)
        or re.fullmatch(r"(?:it|that|this|them|so|sure|yes|yeah|okay)", s, re.I)
    ):
        return None
    return s[0].lower() + s[1:]


def extract_action(text):
    raw = None
    m = PASSIVE.match(text)
    if m:
        np_, pp = m.group(1).strip(), m.group(2).lower()
        base = IRREG.get(pp) or (pp[:-2] if pp.endswith("ed") else pp)
        np_ = np_[0].lower() + np_[1:]
        raw = f"{base} {np_}"
    else:
        m = VERB_AFTER.search(text)
        raw = _clean_action(m.group(1)) if m else None
    if raw is None:
        return None
    return trim_action(raw) or raw  # dependency-based trimming if spaCy is installed


# ------------------------------------------------- optional spaCy refinement (plan: POS/dep + NER)
_SPACY = {"on": True, "nlp": None, "tried": False}


def set_spacy(on):
    """Enable/disable the optional spaCy refinement (action trimming + person-name NER)."""
    _SPACY["on"] = bool(on)


def _get_nlp():
    if not _SPACY["tried"]:
        _SPACY["tried"] = True
        try:
            import spacy

            _SPACY["nlp"] = spacy.load("en_core_web_sm")
        except Exception:
            _SPACY["nlp"] = None
    return _SPACY["nlp"] if _SPACY["on"] else None


def spacy_ready():
    return _get_nlp() is not None


def trim_action(phrase):
    """Cut a captured action phrase down to its minimal verb phrase with the dependency parse.

    Keeps the head verb + its objects; drops a second clause that brings its OWN subject or modal
    ('send the file and I will review it' -> 'send the file') while keeping shared-subject
    coordination ('go back and look at the ones on the list' stays intact).
    Returns None when spaCy is unavailable / no verb is found -> caller keeps the regex phrase.
    """
    nlp = _get_nlp()
    if nlp is None:
        return None
    doc = nlp(phrase)
    vi = next(
        (
            i
            for i, t in enumerate(doc)
            if t.pos_ in ("VERB", "AUX") and t.dep_ not in ("aux", "auxpass")
        ),
        None,
    )
    if vi is None:
        return None
    sub = [t for t in doc[vi].subtree if t.i >= vi]
    cut = len(sub)
    for j, t in enumerate(sub):
        # drop a COORDINATED or ADJUNCT clause only if it brings its own subject/modal
        if j and t.pos_ in ("VERB", "AUX") and t.dep_ in ("conj", "advcl"):
            kids = {c.dep_ for c in t.children}
            if kids & {"nsubj", "nsubjpass", "aux", "auxpass"}:
                first = min(x.i for x in t.subtree)
                cut = min(
                    cut, next((k for k, x in enumerate(sub) if x.i >= first), cut)
                )
                break
    if cut == 0:
        return None
    # slice the ORIGINAL text so hyphens/quotes survive (joining spaCy tokens would give "off - line")
    out = doc[sub[0].i : sub[cut - 1].i + 1].text.strip(" ,.;:")
    out = re.sub(r"^(?:to|and|then|so|well|okay|ok|yeah|right)\s+", "", out, flags=re.I)
    out = out.strip()
    if not out or not any(t.pos_ in ("VERB", "AUX") for t in nlp(out)):
        return None
    return out[0].lower() + out[1:]


def mentioned_people(turns):
    """PERSON names spoken inside the window (spaCy NER). Supplementary information only:
    gold 'person' is an ICSI speaker id, so these are reported, not scored."""
    nlp = _get_nlp()
    if nlp is None:
        return []
    doc = nlp(" ".join(t["text"] for t in turns))
    return sorted(
        {e.text.strip() for e in doc.ents if e.label_ == "PERSON" and e.text.strip()}
    )


# ---------------------------------------------------------------- Stage 5: responsibility
def link_person(turns):
    ci = None
    for i, t in enumerate(turns):
        if COMMIT.search(t["text"]):
            ci = i
    if ci is not None:
        return turns[ci]["speaker"], ci
    for i, t in enumerate(
        turns[:-1]
    ):  # "Sarah, can you ...?"  -> next speaker takes it
        if REQUEST.search(t["text"]) and turns[i + 1]["speaker"] != t["speaker"]:
            return turns[i + 1]["speaker"], i + 1
    return "NULL", None


def link_action(turns, ci):
    """-> (action_text, source_turn_index). 'NULL'/None when nothing could be extracted."""
    n = len(turns)
    order = (
        sorted(range(n), key=lambda i: abs(i - ci))
        if ci is not None
        else list(range(n))
    )
    for i in order:
        a = extract_action(turns[i]["text"])
        if a:
            return a, i
    return "NULL", None


# ---------------------------------------------------------------- Stage 6: deadline
def deadline_in_turn(text):
    for m in TIME_RE.finditer(text):
        pre = text[max(0, m.start() - 25) : m.start()].lower()
        if re.search(r"\b(by|before|until|due|ready|than)\W*(?:the\s+)?$", pre):
            return m.group(1).strip()  # explicit deadline cue
        if not NEGDL.search(text) and (COMMIT.search(text) or OBLIG.search(text)):
            return m.group(1).strip()  # time attached to a commitment
    return None


def link_deadline(turns, ci):
    """-> (deadline_text, source_turn_index). 'NULL'/None when no deadline is justified."""
    n = len(turns)
    order = sorted(range(n), key=lambda i: abs(i - (ci if ci is not None else n - 1)))
    for i in order:
        d = deadline_in_turn(turns[i]["text"])
        if d:
            return d, i
    return "NULL", None


# ---------------------------------------------------------------- Stage 7: output
def extract_detail(turns, detector=rule_detect):
    """Full extraction WITH provenance, for component-level evaluation.

    Returns None when the detector says 'not an action item', otherwise a dict with the
    triplet plus the source turn of every field:
      commit_turn  = the turn the detector/commitment anchored on (None if none)
      person_turn  = turn the responsible speaker was taken from (= commit_turn / responder)
      action_turn  = turn the action phrase was taken from (may differ -> anaphora linking)
      deadline_turn= turn the time expression was taken from (may differ -> cross-turn link)
    """
    if not detector(turns):
        return None
    person, ci = link_person(turns)
    action, ai = link_action(turns, ci)
    deadline, di = link_deadline(turns, ci)
    return {
        "person": person,
        "action": action,
        "deadline": deadline,
        "commit_turn": ci,
        "person_turn": ci,
        "action_turn": ai,
        "deadline_turn": di,
    }


def extract(turns, detector=rule_detect):
    d = extract_detail(turns, detector)
    return None if d is None else (d["person"], d["action"], d["deadline"])


def run_on_transcript(turns, detector=rule_detect, win=3):
    """Sliding windows over a full meeting. Dedup key = (action, person); when the same task is
    visible from more than one window we keep the EARLIEST one UNLESS only a later window carries
    a deadline (otherwise 'have it done by Friday' spoken one turn later would be dropped).
    """
    best = {}
    for s in range(max(1, len(turns) - win + 1)):
        trip = extract(turns[s : s + win], detector)
        if not trip or trip[1] == "NULL":
            continue
        key = (trip[1].lower(), trip[0])
        has_dl = trip[2] != "NULL"
        prev = best.get(key)
        if prev is None or (has_dl and not prev[0]):
            best[key] = (has_dl, s, trip)
    return sorted((s, t) for _, s, t in best.values())


# ---------------------------------------------------------------- evaluation
def toks(s):
    return set(re.findall(r"\w+", s.lower()))


def tok_f1(a, b):
    A, B = toks(a), toks(b)
    if not A or not B:
        return float(A == B)
    ov = len(A & B)
    if ov == 0:
        return 0.0
    p, r = ov / len(B), ov / len(A)
    return 2 * p * r / (p + r)


def nd(d):
    return re.sub(r"^(by|before|until)\s+", "", d.lower().strip())


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["demo"])
    ap.add_argument("--file", required=True)
    a = ap.parse_args()
    pairs = [l.split(":", 1) for l in open(a.file, encoding="utf-8") if ":" in l]
    for i, (person, action, dl) in run_on_transcript(
        make_turns([(s.strip(), t) for s, t in pairs])
    ):
        print(f"turn {i}: ({person}, {action}, {dl})")


if __name__ == "__main__":
    main()
