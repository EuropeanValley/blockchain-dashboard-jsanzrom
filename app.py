import streamlit as st

from modules.m1_pow_monitor import render as render_m1
from modules.m2_block_header import render as render_m2
from modules.m3_difficulty_history import render as render_m3
from modules.m4_ai_component import render as render_m4
from modules.m5_merkle_proof import render as render_m5
from modules.m6_security_score import render as render_m6
from modules.m7_second_ai import render as render_m7

st.set_page_config(
    page_title="CryptoChain Analyzer Dashboard",
    layout="wide",
)

st.title("CryptoChain Analyzer Dashboard")
st.markdown(
    """
    Real-time Bitcoin dashboard for cryptographic analysis, blockchain monitoring,
    and AI-based interpretation of live network data.
    """
)

st.info(
    "This project combines Proof of Work monitoring, block header verification, "
    "difficulty history analysis, AI-based anomaly detection, Merkle proof validation, "
    "and Bitcoin security estimation."
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "M1 · PoW Monitor",
        "M2 · Block Header",
        "M3 · Difficulty History",
        "M4 · AI Anomaly Detection",
        "M5 · Merkle Proof",
        "M6 · Security Score",
        "M7 · Second AI Approach",
    ]
)

with tab1:
    render_m1()

with tab2:
    render_m2()

with tab3:
    render_m3()

with tab4:
    render_m4()

with tab5:
    render_m5()

with tab6:
    render_m6()

with tab7:
    render_m7()