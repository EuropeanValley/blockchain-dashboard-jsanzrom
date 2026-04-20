import streamlit as st
from datetime import datetime

from api.blockchain_client import get_latest_block


def render():
    st.subheader("M1 · Proof of Work Monitor")
    st.write("Live Bitcoin block data from Mempool.space")

    if st.button("Fetch latest block"):
        try:
            block = get_latest_block()

            block_hash = block.get("id", "N/A")
            height = block.get("height", "N/A")
            difficulty = block.get("difficulty", "N/A")
            nonce = block.get("nonce", "N/A")
            tx_count = block.get("tx_count", "N/A")
            bits = block.get("bits", "N/A")
            timestamp = block.get("timestamp")

            if timestamp:
                block_time = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                block_time = "N/A"

            st.success("Latest block fetched successfully")

            col1, col2 = st.columns(2)
            col1.metric("Block Height", height)
            col2.metric("Transactions", tx_count)

            st.write(f"**Block Hash:** `{block_hash}`")
            st.write(f"**Difficulty:** {difficulty}")
            st.write(f"**Nonce:** {nonce}")
            st.write(f"**Bits:** {bits}")
            st.write(f"**Timestamp:** {block_time}")

            st.info(
                "Observation: the block hash is the result of the Proof-of-Work process. "
                "Its leading zeros reflect how small the hash is relative to the mining target. "
                "The bits field compactly encodes that target."
            )

        except Exception as e:
            st.error(f"API error: {e}")