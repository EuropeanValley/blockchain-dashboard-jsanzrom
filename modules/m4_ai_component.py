from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_recent_blocks


def render() -> None:
    st.header("M4 · AI Component")
    st.write("Initial anomaly detection on Bitcoin block inter-arrival times.")

    st.subheader("Chosen AI Approach")
    st.write(
        "This project uses anomaly detection on Bitcoin block inter-arrival times. "
        "The goal is to identify blocks whose arrival times are unusually short or unusually long "
        "compared with the expected behaviour of the Bitcoin network."
    )

    st.subheader("Why this approach?")
    st.write(
        "Bitcoin block arrivals are stochastic and target an average of 600 seconds per block. "
        "Large deviations from typical values may be interesting for analysis, so anomaly detection "
        "is a suitable AI approach for this project."
    )

    sample_size = st.slider(
        "Number of recent blocks for anomaly detection",
        min_value=20,
        max_value=120,
        value=50,
        step=10,
    )

    z_threshold = st.slider(
        "Z-score threshold for anomaly detection",
        min_value=1.0,
        max_value=3.5,
        value=2.0,
        step=0.1,
    )

    if st.button("Run anomaly detection", key="m4_anomaly"):
        try:
            blocks = get_recent_blocks(sample_size)

            if len(blocks) < 3:
                st.warning("Not enough blocks to run anomaly detection.")
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

            mean_time = df["inter_arrival_seconds"].mean()
            std_time = df["inter_arrival_seconds"].std()

            if std_time == 0 or pd.isna(std_time):
                st.warning("Inter-arrival times do not vary enough to detect anomalies.")
                return

            df["z_score"] = (df["inter_arrival_seconds"] - mean_time) / std_time
            df["is_anomaly"] = df["z_score"].abs() > z_threshold
            df["anomaly_type"] = df["z_score"].apply(
                lambda z: "Fast block" if z < -z_threshold else (
                    "Slow block" if z > z_threshold else "Normal"
                )
            )

            anomaly_count = int(df["is_anomaly"].sum())
            anomaly_ratio = anomaly_count / len(df)

            st.success("Anomaly detection completed successfully")

            col1, col2, col3 = st.columns(3)
            col1.metric("Average block time", f"{mean_time:.2f} s")
            col2.metric("Std deviation", f"{std_time:.2f} s")
            col3.metric("Detected anomalies", f"{anomaly_count} / {len(df)}")

            st.subheader("Inter-arrival Time Series")
            fig = px.scatter(
                df,
                x="datetime",
                y="inter_arrival_seconds",
                color="anomaly_type",
                hover_data=["height", "z_score"],
                title="Block Inter-arrival Times with Detected Anomalies",
            )

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Inter-arrival time (seconds)",
            )

            st.plotly_chart(fig, width="stretch")

            st.subheader("Detected Anomalies")
            anomalies_df = df[df["is_anomaly"]].copy()

            if anomalies_df.empty:
                st.write("No anomalies detected with the selected threshold.")
            else:
                st.dataframe(
                    anomalies_df[
                        [
                            "height",
                            "datetime",
                            "inter_arrival_seconds",
                            "z_score",
                            "anomaly_type",
                        ]
                    ].reset_index(drop=True),
                    width="stretch",
                )

            st.subheader("Interpretation")
            st.write(
                f"In this sample, {anomaly_count} out of {len(df)} blocks "
                f"({anomaly_ratio:.2%}) were marked as anomalous using a z-score threshold of {z_threshold:.1f}."
            )

            st.info(
                "This is an initial anomaly detection baseline based on z-scores. "
                "A later version of the project may compare this simple statistical method "
                "with a more advanced machine learning model."
            )

        except Exception as exc:
            st.error(f"Error running anomaly detection: {exc}")