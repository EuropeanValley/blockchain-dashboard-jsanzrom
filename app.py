import streamlit as st

from modules.m1_pow_monitor import render as render_m1
from modules.m2_block_header import render as render_m2

st.set_page_config(page_title="Blockchain Dashboard", layout="wide")

st.title("Blockchain Dashboard")

tab1, tab2 = st.tabs(["M1 - PoW Monitor", "M2 - Block Header"])

with tab1:
    render_m1()

with tab2:
    render_m2()