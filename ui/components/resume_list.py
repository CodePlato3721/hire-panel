import streamlit as st

from ui.components.resume_item import render_resume_item


def render_resume_list(resumes: list[dict]):
    """Display all scored resumes, sorted by score descending."""
    if resumes:
        for r in sorted(resumes, key=lambda r: r["total_score"] or 0, reverse=True):
            render_resume_item(r)
    else:
        st.caption("No resumes scored yet.")
