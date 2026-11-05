#!/usr/bin/env python3
"""
arena-to-zotero: Export Are.na channels into a Zotero library.

Usage:
    python main.py                          # sync all your channels
    python main.py my-channel other-channel # sync specific channels by slug
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env loading is optional; fall back to real env vars

from arena_client import ArenaClient
from zotero_client import ZoteroClient
from sync import sync


def _require(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        print(f"Error: environment variable {name} is not set.")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)
    return val


def main() -> None:
    arena_token = _require("ARENA_ACCESS_TOKEN")
    zotero_key = _require("ZOTERO_API_KEY")
    zotero_library_id = _require("ZOTERO_LIBRARY_ID")
    zotero_library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user").strip()

    channel_slugs = sys.argv[1:] or None  # None → sync all

    arena = ArenaClient(access_token=arena_token)
    zotero = ZoteroClient(
        api_key=zotero_key,
        library_id=zotero_library_id,
        library_type=zotero_library_type,
    )

    sync(arena, zotero, channel_slugs=channel_slugs, verbose=True)


if __name__ == "__main__":
    main()
