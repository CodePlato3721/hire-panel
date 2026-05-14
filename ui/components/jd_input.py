import streamlit as st

from ui.handlers import on_jd_submit, on_jd_reply


def render_jd_input():
    """JD paste area with Extract Criteria button (entering_jd stage)."""
    jd = st.text_area("Paste job description:", height=180, key="jd_text")
    if st.button("Extract Criteria", type="primary"):
        if jd.strip():
            with st.spinner("Extracting criteria…"):
                on_jd_submit(jd.strip())
            st.rerun()


def render_approval_input():
    """Chat input for HR to approve or revise criteria (awaiting_approval stage)."""
    reply = st.chat_input("Reply 'ok' to confirm, or tell me what to adjust")
    if reply:
        with st.spinner("Updating criteria…"):
            on_jd_reply(reply)
        st.rerun()
