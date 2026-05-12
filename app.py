import io

import pdfplumber
import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from pipeline import build_jd_graph, build_resume_graph, build_feedback_graph

st.set_page_config(page_title="Hire Panel", layout="wide")
st.title("Hire Panel")


# ── Session state ─────────────────────────────────────────────────────────────
def _init():
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


_init()


# ── Helpers ───────────────────────────────────────────────────────────────────
def add_msg(role: str, content: str):
    st.session_state.chat.append({"role": role, "content": content})


def read_file(f) -> str:
    if f.name.lower().endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(f.read())) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    return f.read().decode("utf-8", errors="replace")


def stream_ai(graph, inputs, config) -> list[str]:
    """Run a graph stream and return all AI message contents in order."""
    msgs = []
    for event in graph.stream(inputs, config):
        for value in event.values():
            if value and "messages" in value:
                content = value["messages"][-1].content
                if content:
                    msgs.append(content)
    return msgs


# ── Flow handlers ─────────────────────────────────────────────────────────────
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


# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([2, 3])

with left:
    st.subheader("Job Requirements")
    if st.session_state.criteria:
        for c in st.session_state.criteria:
            st.markdown(f"**{c['name']}**: {c['description']}")
    else:
        st.caption("No criteria extracted yet.")

    st.divider()

    st.subheader("Resume Scores")
    if st.session_state.resumes:
        for r in st.session_state.resumes:
            with st.expander(f"**{r['filename']}** — {r['total_score']} pts"):
                if r["reason"]:
                    st.markdown(f"*{r['reason']}*")
                if r["detail"]:
                    st.divider()
                    st.markdown(r["detail"])
    else:
        st.caption("No resumes scored yet.")

with right:
    st.subheader("Chat")

    with st.container(height=440):
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    stage = st.session_state.stage

    # Idle: show quick-action buttons
    if stage == "idle":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 Fill JD", use_container_width=True, type="primary"):
                st.session_state.stage = "entering_jd"
                st.rerun()
        with c2:
            st.button("📁 Upload Resumes", use_container_width=True, disabled=True)

    # JD text input
    elif stage == "entering_jd":
        jd = st.text_area("Paste job description:", height=180, key="jd_text")
        if st.button("Extract Criteria", type="primary"):
            if jd.strip():
                with st.spinner("Extracting criteria…"):
                    on_jd_submit(jd.strip())
                st.rerun()

    # Waiting for HR to approve or revise criteria
    elif stage == "awaiting_approval":
        reply = st.chat_input("Reply 'ok' to confirm, or tell me what to adjust")
        if reply:
            with st.spinner("Updating criteria…"):
                on_jd_reply(reply)
            st.rerun()

    # Criteria confirmed, prompt to upload
    elif stage == "ready_to_upload":
        st.success("Criteria confirmed!")
        if st.button("📁 Upload Resumes", type="primary"):
            st.session_state.stage = "uploading"
            st.rerun()

    # File uploader
    elif stage == "uploading":
        files = st.file_uploader(
            "Upload resumes (PDF or TXT):",
            accept_multiple_files=True,
            type=["pdf", "txt"],
        )
        if files and st.button("Score Resumes", type="primary"):
            with st.spinner(f"Scoring {len(files)} resume(s)…"):
                on_resume_upload(files)
            st.rerun()

    # Resumes scored; HR can give feedback or upload more
    elif stage == "awaiting_feedback":
        fb = st.chat_input("Give feedback on the scores…")
        if fb:
            with st.spinner("Re-scoring with your feedback…"):
                on_feedback(fb)
            st.rerun()
        if st.button("📁 Upload More Resumes"):
            st.session_state.stage = "uploading"
            st.rerun()
