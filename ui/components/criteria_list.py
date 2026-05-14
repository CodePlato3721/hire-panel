import streamlit as st


def render_criteria_list(criteria: list[dict]):
    """Display the extracted JD scoring criteria."""
    if criteria:
        for c in criteria:
            st.markdown(f"**{c['name']}**: {c['description']}")
    else:
        st.caption("No criteria extracted yet.")
