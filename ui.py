import streamlit as st

def metric_row(result):
    cols=st.columns(3)
    cols[0].metric("ATS Simulation Score", f"{result.overall_score}/100")
    cols[1].metric("Likely Screening Outcome", result.outcome)
    cols[2].metric("Prediction Confidence", result.confidence)
    st.caption("This is a transparent simulation—not a score produced by the employer or ATS vendor.")

def score_bars(scores):
    for k,v in scores.items():
        st.write(f"**{k}: {v}/100**")
        st.progress(v/100)
