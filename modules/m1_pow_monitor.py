from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_latest_block, get_recent_block_times


def render():
    st.header("M1 · Proof of Work Monitor")
    st.write("Live monitoring of the latest Bitcoin block and recent block timing behaviour.")

    try:
        block = get_latest_block()

        block_hash = block.get("id", "N/A")
        height = block.get("height", "N/A")
        difficulty = block.get("difficulty", 0)
        nonce = block.get("nonce", "N/A")
        tx_count = block.get("tx_count", "N/A")
        bits = block.get("bits", "N/A")
        timestamp = block.get("timestamp")

        if timestamp:
            block_time = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            block_time = "N/A"

        st.subheader("Latest Block Overview")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Block Height", height)
        col2.metric("Transactions", tx_count)
        col3.metric("Nonce", nonce)
        col4.metric("Bits", bits)

        col5, col6 = st.columns(2)
        col5.metric("Difficulty", f"{difficulty:,.2f}" if isinstance(difficulty, (int, float)) else difficulty)
        col6.metric("Timestamp", block_time)

        st.write(f"**Latest Block Hash:** `{block_hash}`")

        st.info(
            "The block hash is the output of the Proof-of-Work process. "
            "Its leading zeros reflect how small the hash is compared with the mining target. "
            "The bits field compactly encodes that target."
        )

        st.subheader("Recent Block Timing")

        block_count = st.slider(
            "Number of recent blocks to analyze",
            min_value=10,
            max_value=100,
            value=30,
            step=10,
            key="m1_block_count",
        )

        blocks = get_recent_block_times(block_count)

        rows = []
        for b in blocks:
            rows.append(
                {
                    "height": b.get("height"),
                    "timestamp": b.get("timestamp"),
                }
            )

        df = pd.DataFrame(rows).dropna()
        df["datetime"] = df["timestamp"].apply(lambda ts: datetime.utcfromtimestamp(ts))
        df["inter_arrival_seconds"] = df["timestamp"].diff()
        df = df.dropna().reset_index(drop=True)

        if not df.empty:
            avg_time = df["inter_arrival_seconds"].mean()
            min_time = df["inter_arrival_seconds"].min()
            max_time = df["inter_arrival_seconds"].max()

            col7, col8, col9 = st.columns(3)
            col7.metric("Average Block Time", f"{avg_time:.2f} s")
            col8.metric("Fastest Block", f"{min_time:.2f} s")
            col9.metric("Slowest Block", f"{max_time:.2f} s")

            fig = px.bar(
                df,
                x="height",
                y="inter_arrival_seconds",
                title="Inter-arrival Time Between Recent Bitcoin Blocks",
            )
            fig.update_layout(
                xaxis_title="Block Height",
                yaxis_title="Inter-arrival time (seconds)",
            )

            st.plotly_chart(fig, width="stretch")

            st.subheader("Recent Timing Data")
            st.dataframe(
                df[["height", "datetime", "inter_arrival_seconds"]].reset_index(drop=True),
                width="stretch",
            )

            st.write(
                "These values show how much the real time between blocks fluctuates around the "
                "Bitcoin target of 600 seconds."
            )

        else:
            st.warning("Not enough recent block data to compute inter-arrival times.")

    except Exception as e:
        st.error(f"API error: {e}")