import math

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import get_latest_block


def estimate_network_hashrate(difficulty: float) -> float:
    """
    Estimate Bitcoin network hash rate in hashes per second.
    Approximation: hashrate = difficulty * 2^32 / 600
    """
    return difficulty * (2**32) / 600


def format_hashrate(hashes_per_second: float) -> str:
    """
    Format hash rate into human-readable units.
    """
    units = ["H/s", "KH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s", "ZH/s"]
    value = float(hashes_per_second)
    unit_index = 0

    while value >= 1000 and unit_index < len(units) - 1:
        value /= 1000
        unit_index += 1

    return f"{value:,.2f} {units[unit_index]}"


def simple_attack_success_probability(confirmations: int) -> float:
    """
    Simple illustrative risk model:
    more confirmations -> lower approximate attack success probability.
    """
    return math.exp(-0.5 * confirmations)


def render() -> None:
    st.header("M6 · Security Score")
    st.write("Estimate the economic cost of a 51% attack using live Bitcoin network data.")

    try:
        block = get_latest_block()
        difficulty = block.get("difficulty")
        height = block.get("height")
        block_hash = block.get("id")

        if difficulty is None:
            st.error("Difficulty data is missing from the latest block.")
            return

        network_hashrate = estimate_network_hashrate(difficulty)
        attack_hashrate = 0.51 * network_hashrate
        attack_hashrate_th = attack_hashrate / 1e12

        st.subheader("Live Network Security Metrics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Block Height", f"{height}")
        col2.metric("Estimated Network Hash Rate", format_hashrate(network_hashrate))
        col3.metric("Estimated 51% Attack Hash Rate", format_hashrate(attack_hashrate))

        st.write(f"**Latest Block Hash:** `{block_hash}`")
        st.write(f"**Difficulty:** {difficulty:,.2f}")

        st.subheader("Attack Cost Estimation")

        cost_per_th_per_hour = st.number_input(
            "Estimated rental cost per TH/s per hour (USD)",
            min_value=0.001,
            max_value=100.0,
            value=0.02,
            step=0.001,
            format="%.3f",
        )

        attack_cost_per_hour = attack_hashrate_th * cost_per_th_per_hour

        col4, col5 = st.columns(2)
        col4.metric("Attack Hash Rate Needed", f"{attack_hashrate_th:,.2f} TH/s")
        col5.metric("Estimated Attack Cost", f"${attack_cost_per_hour:,.2f} / hour")

        st.subheader("Attack Cost Sensitivity")

        price_values = [0.005, 0.01, 0.02, 0.05, 0.10]
        cost_df = pd.DataFrame(
            {
                "cost_per_th_per_hour": price_values,
                "attack_cost_per_hour_usd": [
                    attack_hashrate_th * price for price in price_values
                ],
            }
        )

        fig1 = px.bar(
            cost_df,
            x="cost_per_th_per_hour",
            y="attack_cost_per_hour_usd",
            title="Estimated 51% Attack Cost for Different Market Rental Prices",
        )
        fig1.update_layout(
            xaxis_title="Rental cost per TH/s per hour (USD)",
            yaxis_title="Estimated attack cost per hour (USD)",
        )
        st.plotly_chart(fig1, width="stretch")

        st.subheader("Security vs Confirmations")

        confirmation_values = list(range(1, 11))
        risk_values = [
            simple_attack_success_probability(c) for c in confirmation_values
        ]

        risk_df = pd.DataFrame(
            {
                "confirmations": confirmation_values,
                "attack_success_probability": risk_values,
            }
        )

        fig2 = px.line(
            risk_df,
            x="confirmations",
            y="attack_success_probability",
            markers=True,
            title="Illustrative Attack Success Probability vs Confirmations",
        )
        fig2.update_layout(
            xaxis_title="Number of Confirmations",
            yaxis_title="Approximate attack success probability",
        )
        st.plotly_chart(fig2, width="stretch")

        st.subheader("Security Summary Table")

        summary_df = risk_df.copy()
        summary_df["attack_success_probability"] = summary_df[
            "attack_success_probability"
        ].round(6)

        st.dataframe(summary_df, width="stretch")

        st.info(
            "This module estimates network hash rate from Bitcoin difficulty and uses a "
            "user-defined market cost per TH/s to approximate the hourly cost of a 51% attack. "
            "The confirmations chart is an illustrative security model showing that the risk "
            "of attack decreases as transaction confirmations increase."
        )

    except Exception as exc:
        st.error(f"Error calculating security score: {exc}")