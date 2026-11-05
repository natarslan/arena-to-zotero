#!/usr/bin/env python3
"""
arena-to-zotero: Export Are.na channels into a Zotero library.

Usage:
    python main.py                              # sync all channels (import everything)
    python main.py my-channel other-channel     # sync specific channels
    python main.py -i                           # interactive: pick blocks per channel
    python main.py -i my-channel                # interactive picker for one channel
    python main.py --type Link,Image            # only import links and images
    python main.py -i --type Link my-channel    # combine: pick from links only
"""

import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
    parser = argparse.ArgumentParser(
        prog="arena-to-zotero",
        description="Export Are.na channels to a Zotero library.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Block types for --type:
  Image, Link, Text, Media, Attachment, Channel

Examples:
  python main.py                          Import everything from all channels
  python main.py research inspiration     Import two specific channels
  python main.py -i                       Pick blocks interactively per channel
  python main.py --type Link,Image        Only import links and images
  python main.py -i --type Link           Interactively pick from links only
        """,
    )
    parser.add_argument(
        "channels",
        nargs="*",
        metavar="CHANNEL_SLUG",
        help="Are.na channel slug(s) to sync (default: all your channels).",
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help=(
            "Show a block picker for each channel. "
            "Browse by page, select by number (e.g. 1,3,5-8), or type 'all'/'none'."
        ),
    )
    parser.add_argument(
        "--type",
        metavar="TYPES",
        help=(
            "Comma-separated block types to import. "
            "E.g. --type Link,Image  or  --type Text"
        ),
    )

    args = parser.parse_args()

    arena_token = _require("ARENA_ACCESS_TOKEN")
    zotero_key = _require("ZOTERO_API_KEY")
    zotero_library_id = _require("ZOTERO_LIBRARY_ID")
    zotero_library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user").strip()

    filter_types = [t.strip() for t in args.type.split(",")] if args.type else None
    channel_slugs = args.channels or None

    arena = ArenaClient(access_token=arena_token)
    zotero = ZoteroClient(
        api_key=zotero_key,
        library_id=zotero_library_id,
        library_type=zotero_library_type,
    )

    sync(
        arena,
        zotero,
        channel_slugs=channel_slugs,
        interactive=args.interactive,
        filter_types=filter_types,
        verbose=True,
    )


if __name__ == "__main__":
    main()
