from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_recent_blocks


def render() -> None:
    st.header("M3 · Difficulty History")
    st.write("Recent historical view of Bitcoin block difficulty.")

    block_count = st.slider(
        "Number of recent blocks to load",
        min_value=10,
        max_value=100,
        value=30,
        step=10,
    )

    if st.button("Load difficulty history", key="m3_load"):
        try:
            blocks = get_recent_blocks(block_count)

            if not blocks:
                st.warning("No block history data was returned.")
                return

            rows = []
            for block in blocks:
                rows.append(
                    {
                        "height": block.get("height"),
                        "difficulty": block.get("difficulty"),
                        "timestamp": block.get("timestamp"),
                    }
                )

            df = pd.DataFrame(rows)
            df = df.dropna()
            df["datetime"] = df["timestamp"].apply(
                lambda ts: datetime.utcfromtimestamp(ts)
            )
            df = df.sort_values("height")

            st.success("Difficulty history loaded successfully")

            fig = px.line(
                df,
                x="datetime",
                y="difficulty",
                markers=True,
                title="Bitcoin Difficulty Over Recent Blocks",
            )

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Difficulty",
            )

            st.plotly_chart(fig, width="stretch")

            st.subheader("Recent Data")
            st.dataframe(
                df[["height", "datetime", "difficulty"]].reset_index(drop=True),
                width="stretch",
            )

            st.info(
                "This is a first working version of M3. "
                "The next step will be to identify difficulty adjustment periods "
                "and compare actual block timing against the 600-second target."
            )

        except Exception as exc:
            st.error(f"Error loading difficulty history: {exc}")