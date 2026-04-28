from datetime import datetime

import pandas as pd
import streamlit as st

from api.blockchain_client import get_recent_blocks


def render() -> None:
    st.header("M4 · AI Component")
    st.write("Initial skeleton for the AI module based on anomaly detection.")

    st.subheader("Chosen AI Approach")
    st.write(
        "This project will use anomaly detection on Bitcoin block inter-arrival times. "
        "The idea is to identify blocks whose arrival time is unusually short or unusually long "
        "compared with the expected behaviour of the Bitcoin network."
    )

    st.subheader("Why this approach?")
    st.write(
        "Bitcoin block arrivals are expected to follow a probabilistic process with an average "
        "target of 600 seconds per block. Large deviations may be interesting for analysis, "
        "so anomaly detection is a suitable first AI approach for this project."
    )

    sample_size = st.slider(
        "Number of recent blocks for AI preview",
        min_value=20,
        max_value=120,
        value=40,
        step=10,
    )

    if st.button("Prepare AI preview data", key="m4_preview"):
        try:
            blocks = get_recent_blocks(sample_size)

            if len(blocks) < 2:
                st.warning("Not enough blocks to prepare AI preview data.")
                return

            rows = []
            for block in blocks:
                rows.append(
                    {
                        "height": block.get("height"),
                        "timestamp": block.get("timestamp"),
                        "difficulty": block.get("difficulty"),
                    }
                )

            df = pd.DataFrame(rows).dropna()
            df = df.sort_values("height").reset_index(drop=True)

            df["datetime"] = df["timestamp"].apply(
                lambda ts: datetime.utcfromtimestamp(ts)
            )
            df["inter_arrival_seconds"] = df["timestamp"].diff()

            preview_df = df[["height", "datetime", "difficulty", "inter_arrival_seconds"]].copy()

            st.success("AI preview data prepared successfully")

            st.subheader("Prepared Data Preview")
            st.dataframe(preview_df, width="stretch")

            mean_time = preview_df["inter_arrival_seconds"].dropna().mean()

            st.subheader("Initial Observation")
            st.write(f"Average inter-arrival time in this sample: **{mean_time:.2f} seconds**")

            st.info(
                "This is only the initial skeleton of M4. "
                "In the next phase, the module will apply an anomaly detection method "
                "to these inter-arrival times and highlight unusual blocks."
            )

        except Exception as exc:
            st.error(f"Error preparing AI preview data: {exc}")