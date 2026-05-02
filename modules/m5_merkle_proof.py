import hashlib

import pandas as pd
import streamlit as st

from api.blockchain_client import (
    get_block_txids,
    get_latest_block,
    get_tx_merkle_proof,
)


def double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def merkle_parent(left_hex: str, right_hex: str) -> str:
    """
    Compute parent hash from two child hashes.
    Input hashes are displayed in standard big-endian hex.
    """
    left_bytes = bytes.fromhex(left_hex)[::-1]
    right_bytes = bytes.fromhex(right_hex)[::-1]
    parent = double_sha256(left_bytes + right_bytes)
    return parent[::-1].hex()


def render() -> None:
    st.header("M5 · Merkle Proof Verifier")
    st.write("Verify a Bitcoin transaction Merkle proof step by step.")

    try:
        block = get_latest_block()
        block_hash = block.get("id")
        block_height = block.get("height")
        merkle_root = block.get("merkle_root")
        tx_count = block.get("tx_count")

        if not block_hash or not merkle_root:
            st.error("Missing required block data.")
            return

        st.subheader("Selected Block")
        col1, col2, col3 = st.columns(3)
        col1.metric("Block Height", block_height)
        col2.metric("Transactions", tx_count)
        col3.metric("Merkle Root", merkle_root[:16] + "...")

        txids = get_block_txids(block_hash)

        if not txids:
            st.warning("No transactions found for this block.")
            return

        tx_index = st.slider(
            "Transaction index in block",
            min_value=0,
            max_value=len(txids) - 1,
            value=min(1, len(txids) - 1),
            step=1,
        )

        selected_txid = txids[tx_index]
        st.write(f"**Selected TXID:** `{selected_txid}`")

        if st.button("Verify Merkle proof", key="m5_verify"):
            proof = get_tx_merkle_proof(selected_txid)

            merkle_path = proof.get("merkle", [])
            position = proof.get("pos")

            if position is None:
                st.error("Merkle proof response does not contain a valid position.")
                return

            current_hash = selected_txid
            current_pos = position
            steps = []

            for level, sibling_hash in enumerate(merkle_path, start=1):
                if current_pos % 2 == 0:
                    left_hash = current_hash
                    right_hash = sibling_hash
                    direction = "current hash on LEFT"
                else:
                    left_hash = sibling_hash
                    right_hash = current_hash
                    direction = "current hash on RIGHT"

                parent_hash = merkle_parent(left_hash, right_hash)

                steps.append(
                    {
                        "level": level,
                        "position": current_pos,
                        "direction": direction,
                        "left_hash": left_hash,
                        "right_hash": right_hash,
                        "parent_hash": parent_hash,
                    }
                )

                current_hash = parent_hash
                current_pos //= 2

            calculated_root = current_hash
            proof_valid = calculated_root == merkle_root

            st.success("Merkle proof processed successfully")

            st.subheader("Verification Result")
            st.write(f"**Block Merkle Root:** `{merkle_root}`")
            st.write(f"**Calculated Root from Proof:** `{calculated_root}`")
            st.write(f"**Proof Valid:** {proof_valid}")

            st.subheader("Step-by-Step Hash Computation")
            df = pd.DataFrame(steps)
            st.dataframe(df, width="stretch")

            st.info(
                "Starting from the selected transaction ID, this module combines the hash "
                "with each sibling hash in the Merkle proof and applies double SHA-256 "
                "at every level until reaching the final Merkle root."
            )

    except Exception as exc:
        st.error(f"Error verifying Merkle proof: {exc}")