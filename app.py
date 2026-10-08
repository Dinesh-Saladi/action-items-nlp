"""Demo: streamlit run app.py   (pip install streamlit)"""

import streamlit as st, pandas as pd
from pipeline import make_turns, run_on_transcript

st.title("Meeting Action-Item Extractor")
txt = st.text_area(
    "Paste transcript (one 'Speaker: text' per line)",
    height=250,
    value="Bob: The documentation still needs to be updated.\nSarah: I'll handle that.\nBob: Great, by Friday would be good.\nBob: Our next meeting is on Monday.",
)
if st.button("Extract"):
    pairs = [l.split(":", 1) for l in txt.splitlines() if ":" in l]
    res = run_on_transcript(make_turns([(s.strip(), t) for s, t in pairs]))
    st.dataframe(
        pd.DataFrame(
            [
                {"Turn": i, "Person": p, "Action": a, "Deadline": d}
                for i, (p, a, d) in res
            ]
        )
    )
