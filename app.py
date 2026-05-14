import streamlit as st

from ui.state import init_session
from ui.panels.left import render_left_panel
from ui.panels.right import render_right_panel

st.set_page_config(page_title="Hire Panel", layout="wide")
st.title("Hire Panel")

init_session()

left, right = st.columns([2, 3])

with left:
    render_left_panel()

with right:
    render_right_panel()
