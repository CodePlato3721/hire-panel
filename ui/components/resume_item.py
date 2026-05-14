import streamlit as st


def render_resume_item(resume: dict):
    """Single resume card rendered as an expander."""
    with st.expander(f"**{resume['filename']}** — {resume['total_score']} pts"):
        if resume["reason"]:
            st.markdown(f"*{resume['reason']}*")
        if resume["detail"]:
            st.divider()
            st.markdown(resume["detail"])
