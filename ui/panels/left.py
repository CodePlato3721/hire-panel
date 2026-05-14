import streamlit as st

from ui.components.criteria_list import render_criteria_list
from ui.components.resume_list import render_resume_list


def render_left_panel():
    st.subheader("Job Requirements")
    render_criteria_list(st.session_state.criteria)

    st.divider()

    st.subheader("Resume Scores")
    render_resume_list(st.session_state.resumes)
