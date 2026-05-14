import streamlit as st
from pipeline import build_jd_graph, build_resume_graph, build_feedback_graph


def init_session():
    if "initialized" in st.session_state:
        return
    st.session_state.initialized = True
    st.session_state.stage = "idle"       # idle | entering_jd | awaiting_approval |
                                           # ready_to_upload | uploading | awaiting_feedback
    st.session_state.chat = []            # [{"role": "user"|"assistant", "content": str}]
    st.session_state.criteria = []        # list[ScoringCriteria]
    st.session_state.resumes = []         # list[Resume]
    st.session_state.hr_memory = {"scoring_preferences": [], "adjustment_history": []}
    st.session_state.resume_round = 0
    st.session_state.feedback_round = 0
    st.session_state.jd_graph = build_jd_graph()
    st.session_state.jd_config = {"configurable": {"thread_id": "jd"}}
    st.session_state.resume_graph = build_resume_graph()
    st.session_state.feedback_graph = build_feedback_graph()
