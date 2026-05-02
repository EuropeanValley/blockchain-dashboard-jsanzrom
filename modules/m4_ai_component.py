from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_recent_blocks


def render() -> None:
    st.header("M4 · AI Component")
    st.write("Anomaly detection on Bitcoin block inter-arrival times.")

    st.subheader("Model Idea")
    st.write(
        "This module applies a statistical anomaly detection baseline using z-scores "
        "on Bitcoin block inter-arrival times. Blocks with unusually short or long "
        "arrival times are flagged as potential anomalies."
    )

    sample_size = st.slider(
        "Number of recent blocks for anomaly detection",
        min_value=20,
        max_value=120,
        value=50,
        step=10,
    )

    z_threshold = st.slider(
        "Z-score threshold",
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
            fast_count = int((df["anomaly_type"] == "Fast block").sum())
            slow_count = int((df["anomaly_type"] == "Slow block").sum())
            anomaly_ratio = anomaly_count / len(df)

            st.success("Anomaly detection completed successfully")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average block time", f"{mean_time:.2f} s")
            col2.metric("Std deviation", f"{std_time:.2f} s")
            col3.metric("Detected anomalies", f"{anomaly_count} / {len(df)}")
            col4.metric("Threshold", f"{z_threshold:.1f}")

            col5, col6 = st.columns(2)
            col5.metric("Fast anomalies", fast_count)
            col6.metric("Slow anomalies", slow_count)

            st.subheader("Anomaly Detection Result")
            fig = px.scatter(
                df,
                x="datetime",
                y="inter_arrival_seconds",
                color="anomaly_type",
                hover_data=["height", "z_score", "difficulty"],
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
                            "difficulty",
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
                f"({anomaly_ratio:.2%}) were classified as anomalous using a z-score "
                f"threshold of {z_threshold:.1f}."
            )

            st.info(
                "This is a baseline anomaly detector. It is simple and interpretable, "
                "but later it can be compared with a more advanced machine learning method."
            )

        except Exception as exc:
            st.error(f"Error running anomaly detection: {exc}")