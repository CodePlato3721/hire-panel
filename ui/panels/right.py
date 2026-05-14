import streamlit as st

from ui.components.chat_window import render_chat_window
from ui.components.quick_actions import render_quick_actions
from ui.components.jd_input import render_jd_input, render_approval_input
from ui.components.file_uploader import render_upload_confirmed, render_file_uploader
from ui.components.feedback_input import render_feedback_input

_STAGE_RENDERERS = {
    "idle":              render_quick_actions,
    "entering_jd":       render_jd_input,
    "awaiting_approval": render_approval_input,
    "ready_to_upload":   render_upload_confirmed,
    "uploading":         render_file_uploader,
    "awaiting_feedback": render_feedback_input,
}


def render_right_panel():
    st.subheader("Chat")
    render_chat_window(st.session_state.chat)

    renderer = _STAGE_RENDERERS.get(st.session_state.stage)
    if renderer:
        renderer()
