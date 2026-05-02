"""
Blockchain API client for Mempool.space.

Provides helper functions to fetch live Bitcoin block data.
"""

from __future__ import annotations

import requests

BASE_URL = "https://mempool.space/api"


def _get(endpoint: str):
    """Perform a GET request and return the parsed response."""
    response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return response.json()

    return response.text


def get_tip_height() -> int:
    """Return the height of the latest Bitcoin block."""
    return int(_get("/blocks/tip/height"))


def get_tip_hash() -> str:
    """Return the hash of the latest Bitcoin block."""
    return str(_get("/blocks/tip/hash")).strip()


def get_block(block_hash: str) -> dict:
    """Return details for a block identified by its hash."""
    return _get(f"/block/{block_hash}")


def get_latest_block() -> dict:
    """Return the latest block details from Mempool.space."""
    tip_hash = get_tip_hash()
    return get_block(tip_hash)

def get_block_hash_by_height(height: int) -> str:
    """Return the block hash for a given block height."""
    return str(_get(f"/block-height/{height}")).strip()


def get_recent_blocks(count: int = 20) -> list[dict]:
    """
    Return a list with the most recent `count` blocks.
    Builds the history by walking backwards from the current tip.
    """
    blocks = []
    current_hash = get_tip_hash()

    while len(blocks) < count:
        block = get_block(current_hash)
        blocks.append(block)

        previous_hash = block.get("previousblockhash")
        if not previous_hash:
            break

        current_hash = previous_hash

    return blocks


def get_block_by_height(height: int) -> dict:
    """Return full block data for a given block height."""
    block_hash = get_block_hash_by_height(height)
    return get_block(block_hash)


def get_difficulty_adjustment_periods(period_count: int = 6) -> list[dict]:
    """
    Return summary data for the latest completed Bitcoin difficulty adjustment periods.

    Each period spans 2016 blocks. For every completed period, this function returns:
    - start and end heights
    - start and end timestamps
    - end difficulty
    - actual average block time
    - ratio vs the 600-second target
    """
    tip_height = get_tip_height()

    # Last completed adjustment boundary
    last_completed_boundary = (tip_height // 2016) * 2016

    periods = []

    for i in range(period_count):
        end_height = last_completed_boundary - (i * 2016)
        start_height = end_height - 2016

        if start_height < 0:
            break

        start_block = get_block_by_height(start_height)
        end_block = get_block_by_height(end_height)

        start_ts = start_block.get("timestamp")
        end_ts = end_block.get("timestamp")
        difficulty = end_block.get("difficulty")

        if start_ts is None or end_ts is None or difficulty is None:
            continue

        total_seconds = end_ts - start_ts
        average_block_time = total_seconds / 2016
        ratio_vs_target = average_block_time / 600

        periods.append(
            {
                "start_height": start_height,
                "end_height": end_height,
                "start_timestamp": start_ts,
                "end_timestamp": end_ts,
                "difficulty": difficulty,
                "total_seconds": total_seconds,
                "average_block_time": average_block_time,
                "ratio_vs_target": ratio_vs_target,
            }
        )

    periods.reverse()
    return periods

def get_block_txids(block_hash: str) -> list[str]:
    """Return all transaction IDs for a given block hash."""
    return _get(f"/block/{block_hash}/txids")


def get_tx_merkle_proof(txid: str) -> dict:
    """Return the Merkle inclusion proof for a transaction."""
    return _get(f"/tx/{txid}/merkle-proof")

def get_recent_block_times(count: int = 20) -> list[dict]:
    """
    Return recent blocks with enough data to analyze inter-arrival times.
    """
    blocks = get_recent_blocks(count)
    blocks = [b for b in blocks if b.get("height") is not None and b.get("timestamp") is not None]
    return sorted(blocks, key=lambda b: b["height"])