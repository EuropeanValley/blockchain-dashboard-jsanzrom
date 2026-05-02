import hashlib
from datetime import datetime

import streamlit as st

from api.blockchain_client import get_latest_block


def bits_to_target(bits: int) -> int:
    """
    Convert Bitcoin compact 'bits' format into the full target integer.
    """
    exponent = bits >> 24
    coefficient = bits & 0xFFFFFF
    return coefficient * (1 << (8 * (exponent - 3)))


def serialize_header(
    version: int,
    prev_hash_hex: str,
    merkle_root_hex: str,
    timestamp: int,
    bits: int,
    nonce: int,
) -> bytes:
    """
    Build the 80-byte Bitcoin block header in the correct byte order.
    """
    version_bytes = version.to_bytes(4, byteorder="little", signed=False)
    prev_hash_bytes = bytes.fromhex(prev_hash_hex)[::-1]
    merkle_root_bytes = bytes.fromhex(merkle_root_hex)[::-1]
    timestamp_bytes = timestamp.to_bytes(4, byteorder="little", signed=False)
    bits_bytes = bits.to_bytes(4, byteorder="little", signed=False)
    nonce_bytes = nonce.to_bytes(4, byteorder="little", signed=False)

    return (
        version_bytes
        + prev_hash_bytes
        + merkle_root_bytes
        + timestamp_bytes
        + bits_bytes
        + nonce_bytes
    )


def double_sha256(data: bytes) -> bytes:
    """
    Compute SHA256(SHA256(data)).
    """
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def count_leading_zero_bits(hex_hash: str) -> int:
    """
    Count leading zero bits in a 256-bit hash represented as hex.
    """
    binary = bin(int(hex_hash, 16))[2:].zfill(256)
    return len(binary) - len(binary.lstrip("0"))


def render() -> None:
    st.header("M2 · Block Header Analyzer")
    st.write("Local verification of the latest Bitcoin block header and Proof of Work.")

    if st.button("Analyze latest block header", key="m2_analyze"):
        try:
            block = get_latest_block()

            version = block.get("version")
            prev_hash = block.get("previousblockhash")
            merkle_root = block.get("merkle_root")
            timestamp = block.get("timestamp")
            bits = block.get("bits")
            nonce = block.get("nonce")
            block_hash = block.get("id")
            height = block.get("height")

            if None in [version, prev_hash, merkle_root, timestamp, bits, nonce, block_hash, height]:
                st.error("Missing required block fields from API response.")
                return

            header_bytes = serialize_header(
                version=version,
                prev_hash_hex=prev_hash,
                merkle_root_hex=merkle_root,
                timestamp=timestamp,
                bits=bits,
                nonce=nonce,
            )

            calculated_hash_bytes = double_sha256(header_bytes)
            calculated_hash_hex = calculated_hash_bytes[::-1].hex()

            target = bits_to_target(bits)
            calculated_hash_int = int(calculated_hash_hex, 16)

            pow_valid = calculated_hash_int < target
            matches_api_hash = calculated_hash_hex == block_hash
            leading_zero_bits = count_leading_zero_bits(calculated_hash_hex)

            readable_time = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")

            st.success("Block header analyzed successfully")

            st.subheader("Block Identification")
            col1, col2, col3 = st.columns(3)
            col1.metric("Block Height", height)
            col2.metric("Header Length", f"{len(header_bytes)} bytes")
            col3.metric("Leading Zero Bits", leading_zero_bits)

            st.write(f"**Block Hash (API):** `{block_hash}`")
            st.write(f"**Timestamp:** {readable_time}")

            st.subheader("Header Fields")
            left_col, right_col = st.columns(2)

            with left_col:
                st.write(f"**Version:** {version}")
                st.write(f"**Previous Block Hash:** `{prev_hash}`")
                st.write(f"**Merkle Root:** `{merkle_root}`")

            with right_col:
                st.write(f"**Bits:** {bits}")
                st.write(f"**Nonce:** {nonce}")
                st.write(f"**Target (decimal):** {target}")

            st.subheader("Local Verification")
            col4, col5 = st.columns(2)
            col4.metric("Matches API Hash", "Yes" if matches_api_hash else "No")
            col5.metric("Hash < Target", "Yes" if pow_valid else "No")

            st.write(f"**Serialized Header (hex):** `{header_bytes.hex()}`")
            st.write(f"**Calculated Double SHA-256:** `{calculated_hash_hex}`")

            st.info(
                "This module rebuilds the 80-byte Bitcoin block header, applies double SHA-256 locally, "
                "and checks whether the resulting hash is below the target encoded by the bits field."
            )

        except Exception as exc:
            st.error(f"Error analyzing block header: {exc}")