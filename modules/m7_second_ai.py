from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_recent_blocks


def render() -> None:
    st.header("M7 · Second AI Approach")
    st.write("Alternative AI approach based on quantile classification of Bitcoin block inter-arrival times.")

    st.subheader("Approach")
    st.write(
        "This module applies a second analytical approach different from M4. "
        "Instead of using z-scores, it classifies block inter-arrival times using lower and upper quantiles."
    )

    sample_size = st.slider(
        "Number of recent blocks for second AI approach",
        min_value=20,
        max_value=150,
        value=60,
        step=10,
    )

    low_quantile = st.slider(
        "Lower quantile threshold",
        min_value=0.01,
        max_value=0.40,
        value=0.10,
        step=0.01,
    )

    high_quantile = st.slider(
        "Upper quantile threshold",
        min_value=0.60,
        max_value=0.99,
        value=0.90,
        step=0.01,
    )

    if st.button("Run second AI approach", key="m7_run"):
        try:
            if low_quantile >= high_quantile:
                st.error("Lower quantile must be smaller than upper quantile.")
                return

            blocks = get_recent_blocks(sample_size)

            if len(blocks) < 3:
                st.warning("Not enough blocks to run the second AI approach.")
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
            df = df.dropna().reset_index(drop=True)

            low_threshold = df["inter_arrival_seconds"].quantile(low_quantile)
            high_threshold = df["inter_arrival_seconds"].quantile(high_quantile)

            def classify_block(value: float) -> str:
                if value <= low_threshold:
                    return "Fast block"
                if value >= high_threshold:
                    return "Slow block"
                return "Normal"

            df["classification"] = df["inter_arrival_seconds"].apply(classify_block)

            fast_count = int((df["classification"] == "Fast block").sum())
            slow_count = int((df["classification"] == "Slow block").sum())
            normal_count = int((df["classification"] == "Normal").sum())

            st.success("Second AI approach completed successfully")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Fast blocks", fast_count)
            col2.metric("Slow blocks", slow_count)
            col3.metric("Normal blocks", normal_count)
            col4.metric("Sample size", len(df))

            st.subheader("Quantile Thresholds")
            st.write(f"**Lower threshold ({low_quantile:.2f}):** {low_threshold:.2f} seconds")
            st.write(f"**Upper threshold ({high_quantile:.2f}):** {high_threshold:.2f} seconds")

            st.subheader("Classification Result")
            fig = px.scatter(
                df,
                x="datetime",
                y="inter_arrival_seconds",
                color="classification",
                hover_data=["height", "difficulty"],
                title="Quantile-Based Classification of Block Inter-arrival Times",
            )

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Inter-arrival time (seconds)",
            )

            st.plotly_chart(fig, width="stretch")

            st.subheader("Classified Blocks")
            st.dataframe(
                df[
                    [
                        "height",
                        "datetime",
                        "difficulty",
                        "inter_arrival_seconds",
                        "classification",
                    ]
                ].reset_index(drop=True),
                width="stretch",
            )

            st.info(
                "This second AI approach differs from M4 because it does not use z-scores. "
                "Instead, it classifies blocks according to empirical quantile thresholds. "
                "This makes it useful for comparing two different anomaly-detection styles."
            )

        except Exception as exc:
            st.error(f"Error running second AI approach: {exc}")