import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from ui.helpers import add_msg, read_file, stream_ai


def on_jd_submit(jd_text: str):
    add_msg("user", f"*[Job description — {len(jd_text)} chars]*")
    for m in stream_ai(
        st.session_state.jd_graph,
        {"messages": [], "job_requirements": jd_text, "scoring_criteria": []},
        st.session_state.jd_config,
    ):
        add_msg("assistant", m)
    st.session_state.stage = "awaiting_approval"


def on_jd_reply(reply: str):
    add_msg("user", reply)
    for m in stream_ai(
        st.session_state.jd_graph,
        Command(resume={"feedback": reply}),
        st.session_state.jd_config,
    ):
        add_msg("assistant", m)
    graph_state = st.session_state.jd_graph.get_state(st.session_state.jd_config)
    if graph_state.next:  # still in the approval revision loop
        st.session_state.stage = "awaiting_approval"
    else:
        st.session_state.criteria = graph_state.values["scoring_criteria"]
        st.session_state.stage = "ready_to_upload"


def on_resume_upload(files):
    st.session_state.resume_round += 1
    config = {"configurable": {"thread_id": f"resume-{st.session_state.resume_round}"}}
    resumes = [
        {"filename": f.name, "content": read_file(f), "total_score": None, "reason": "", "detail": ""}
        for f in files
    ]
    add_msg("user", f"*[{len(files)} resume(s) uploaded]*")
    for m in stream_ai(
        st.session_state.resume_graph,
        {
            "messages": [],
            "scoring_criteria": st.session_state.criteria,
            "resumes": resumes,
            "hr_memory": st.session_state.hr_memory,
        },
        config,
    ):
        add_msg("assistant", m)
    graph_state = st.session_state.resume_graph.get_state(config)
    st.session_state.resumes = graph_state.values["resumes"]
    st.session_state.stage = "awaiting_feedback"


def on_feedback(feedback: str):
    add_msg("user", feedback)
    st.session_state.feedback_round += 1
    config = {"configurable": {"thread_id": f"feedback-{st.session_state.feedback_round}"}}
    for m in stream_ai(
        st.session_state.feedback_graph,
        {
            "messages": [HumanMessage(content=feedback)],
            "scoring_criteria": st.session_state.criteria,
            "resumes": st.session_state.resumes,
            "hr_memory": st.session_state.hr_memory,
        },
        config,
    ):
        add_msg("assistant", m)
    graph_state = st.session_state.feedback_graph.get_state(config)
    st.session_state.resumes = graph_state.values["resumes"]
    st.session_state.hr_memory = graph_state.values["hr_memory"]
