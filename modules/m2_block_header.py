import streamlit as st
from datetime import datetime

from api.blockchain_client import get_latest_block


def render() -> None:
    st.header("M2 · Block Header Analyzer")
    st.write("Inspect the main fields of the latest Bitcoin block header.")

    if st.button("Load latest block header", key="m2_load"):
        try:
            block = get_latest_block()

            version = block.get("version", "N/A")
            prev_hash = block.get("previousblockhash", "N/A")
            merkle_root = block.get("merkle_root", "N/A")
            timestamp = block.get("timestamp")
            bits = block.get("bits", "N/A")
            nonce = block.get("nonce", "N/A")
            block_hash = block.get("id", "N/A")
            height = block.get("height", "N/A")

            if timestamp:
                readable_time = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                readable_time = "N/A"

            st.success("Latest block header loaded successfully")

            st.write(f"**Block Height:** {height}")
            st.write(f"**Block Hash:** `{block_hash}`")

            st.subheader("Header Fields")
            st.write(f"**Version:** {version}")
            st.write(f"**Previous Block Hash:** `{prev_hash}`")
            st.write(f"**Merkle Root:** `{merkle_root}`")
            st.write(f"**Timestamp:** {readable_time}")
            st.write(f"**Bits:** {bits}")
            st.write(f"**Nonce:** {nonce}")

            st.info(
                "These are the six main fields used to build the 80-byte Bitcoin block header. "
                "In the next phase, this module will serialize the header and verify Proof of Work locally."
            )

        except Exception as exc:
            st.error(f"Error fetching block header: {exc}")