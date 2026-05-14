import streamlit as st

from ui.handlers import on_resume_upload


def render_upload_confirmed():
    """Success banner + button to enter uploading stage (ready_to_upload stage)."""
    st.success("Criteria confirmed!")
    if st.button("📁 Upload Resumes", type="primary"):
        st.session_state.stage = "uploading"
        st.rerun()


def render_file_uploader():
    """File upload widget with Score button (uploading stage)."""
    files = st.file_uploader(
        "Upload resumes (PDF or TXT):",
        accept_multiple_files=True,
        type=["pdf", "txt"],
    )
    if files and st.button("Score Resumes", type="primary"):
        with st.spinner(f"Scoring {len(files)} resume(s)…"):
            on_resume_upload(files)
        st.rerun()
