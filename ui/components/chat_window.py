import streamlit as st


def render_chat_window(messages: list[dict], height: int = 440):
    """Scrollable chat bubble area."""
    with st.container(height=height):
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
