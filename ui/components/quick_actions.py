import streamlit as st


def render_quick_actions():
    """Idle-state quick-action buttons: Fill JD and Upload Resumes."""
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 Fill JD", use_container_width=True, type="primary"):
            st.session_state.stage = "entering_jd"
            st.rerun()
    with c2:
        st.button("📁 Upload Resumes", use_container_width=True, disabled=True)
