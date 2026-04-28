from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_difficulty_adjustment_periods


def render() -> None:
    st.header("M3 · Difficulty History")
    st.write("Difficulty evolution over recent completed Bitcoin adjustment periods.")

    period_count = st.slider(
        "Number of completed adjustment periods",
        min_value=3,
        max_value=12,
        value=6,
        step=1,
    )

    if st.button("Load difficulty adjustment history", key="m3_adjustments"):
        try:
            periods = get_difficulty_adjustment_periods(period_count)

            if not periods:
                st.warning("No difficulty adjustment data was returned.")
                return

            df = pd.DataFrame(periods)

            df["start_datetime"] = df["start_timestamp"].apply(
                lambda ts: datetime.utcfromtimestamp(ts)
            )
            df["end_datetime"] = df["end_timestamp"].apply(
                lambda ts: datetime.utcfromtimestamp(ts)
            )

            df["period_label"] = df.apply(
                lambda row: f"{int(row['start_height'])}-{int(row['end_height'])}",
                axis=1,
            )

            df["avg_block_time_seconds"] = df["average_block_time"].round(2)
            df["ratio_vs_target"] = df["ratio_vs_target"].round(4)
            df["difficulty_change_direction"] = df["ratio_vs_target"].apply(
                lambda x: "Faster than target" if x < 1 else "Slower than target"
            )

            st.success("Difficulty adjustment history loaded successfully")

            latest_difficulty = df.iloc[-1]["difficulty"]
            latest_ratio = df.iloc[-1]["ratio_vs_target"]
            latest_avg_time = df.iloc[-1]["avg_block_time_seconds"]

            col1, col2, col3 = st.columns(3)
            col1.metric("Latest Period Difficulty", f"{latest_difficulty:,.2f}")
            col2.metric("Latest Avg Block Time", f"{latest_avg_time} s")
            col3.metric("Latest Ratio vs 600s", f"{latest_ratio:.4f}")

            st.subheader("Difficulty by Adjustment Period")

            fig = px.line(
                df,
                x="end_datetime",
                y="difficulty",
                markers=True,
                text="period_label",
                title="Bitcoin Difficulty Across Adjustment Periods",
            )

            fig.update_traces(textposition="top center")
            fig.update_layout(
                xaxis_title="Adjustment Date",
                yaxis_title="Difficulty",
            )

            st.plotly_chart(fig, width="stretch")

            st.subheader("Adjustment Event Summary")
            summary_df = df[
                [
                    "period_label",
                    "start_datetime",
                    "end_datetime",
                    "difficulty",
                    "avg_block_time_seconds",
                    "ratio_vs_target",
                    "difficulty_change_direction",
                ]
            ].copy()

            summary_df = summary_df.rename(
                columns={
                    "period_label": "Period (heights)",
                    "start_datetime": "Start",
                    "end_datetime": "Adjustment event",
                    "difficulty": "Difficulty",
                    "avg_block_time_seconds": "Avg block time (s)",
                    "ratio_vs_target": "Actual/600 ratio",
                    "difficulty_change_direction": "Interpretation",
                }
            )

            st.dataframe(summary_df, width="stretch")

            st.info(
                "Each point on the chart represents a Bitcoin difficulty adjustment event, "
                "which happens every 2016 blocks. "
                "The ratio compares the actual average block time in that period against "
                "the theoretical target of 600 seconds per block."
            )

        except Exception as exc:
            st.error(f"Error loading difficulty adjustment history: {exc}")