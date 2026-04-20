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