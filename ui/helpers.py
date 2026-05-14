import io

import pdfplumber
import streamlit as st


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
