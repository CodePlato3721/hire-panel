import streamlit as st

from ui.handlers import on_feedback


def render_feedback_input():
    """Feedback chat input + Upload More button (awaiting_feedback stage)."""
    fb = st.chat_input("Give feedback on the scores…")
    if fb:
        with st.spinner("Re-scoring with your feedback…"):
            on_feedback(fb)
        st.rerun()
    if st.button("📁 Upload More Resumes"):
        st.session_state.stage = "uploading"
        st.rerun()
