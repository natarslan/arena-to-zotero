"""
Core sync logic: Are.na → Zotero.

Structure created in Zotero:
  Arena (collection)
  └── <channel title> (sub-collection)
      └── <block> (item)
      ...
"""

import time
from arena_client import ArenaClient
from zotero_client import ZoteroClient
from mapper import block_to_zotero_item, channel_to_collection_name
from selector import select_blocks_interactive, filter_blocks_by_type

ARENA_ROOT_COLLECTION = "Arena"
ZOTERO_ITEM_BATCH = 50  # Zotero API max per request


def _chunk(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def sync(
    arena: ArenaClient,
    zotero: ZoteroClient,
    channel_slugs: list[str] | None = None,
    interactive: bool = False,
    filter_types: list[str] | None = None,
    verbose: bool = True,
) -> None:
    """
    Sync Are.na channels to Zotero.

    Args:
        arena:          Configured ArenaClient.
        zotero:         Configured ZoteroClient.
        channel_slugs:  Specific channel slugs to sync; None → all channels.
        interactive:    If True, show a picker for each channel so you can
                        choose which blocks to import.
        filter_types:   Only import blocks of these types, e.g. ["Link", "Image"].
                        Valid values: Image, Link, Text, Media, Attachment, Channel.
        verbose:        Print progress to stdout.
    """
    log = print if verbose else lambda *a, **k: None

    # ── 1. Resolve channels to sync ──────────────────────────────────────────
    if channel_slugs:
        channels = []
        for slug in channel_slugs:
            try:
                ch = arena._get(f"/channels/{slug}")
                channels.append(ch)
                log(f"  Found channel: {ch.get('title')} ({slug})")
            except Exception as exc:
                log(f"  Warning: could not fetch channel '{slug}': {exc}")
    else:
        log("Fetching your Are.na profile…")
        me = arena.get_user()
        username = me.get("slug") or me.get("username")
        log(f"Logged in as: {me.get('full_name', username)}")
        log("Fetching all channels…")
        channels = arena.get_channels(username)
        log(f"Found {len(channels)} channel(s).")

    if not channels:
        log("No channels to sync. Done.")
        return

    # ── 2. Ensure top-level "Arena" collection exists ─────────────────────────
    log(f'\nEnsuring top-level "{ARENA_ROOT_COLLECTION}" collection in Zotero…')
    arena_col = zotero.get_or_create_collection(ARENA_ROOT_COLLECTION)
    arena_col_key = arena_col["data"]["key"] if "data" in arena_col else arena_col.get("key")
    log(f"  Collection key: {arena_col_key}")

    # ── 3. Sync each channel ──────────────────────────────────────────────────
    for channel in channels:
        slug = channel.get("slug") or str(channel.get("id"))
        col_name = channel_to_collection_name(channel)
        log(f'\nChannel: "{col_name}" ({slug})')

        # Create sub-collection under Arena
        sub_col = zotero.get_or_create_collection(col_name, parent_key=arena_col_key)
        sub_col_key = sub_col["data"]["key"] if "data" in sub_col else sub_col.get("key")

        # Fetch existing items to avoid duplicates
        existing_items = zotero.get_collection_items(sub_col_key)
        existing_arena_ids = set()
        for item in existing_items:
            extra = item.get("data", {}).get("extra", "")
            for line in extra.splitlines():
                if line.startswith("Are.na block ID:"):
                    existing_arena_ids.add(line.split(":", 1)[1].strip())

        # Fetch blocks from Are.na
        log(f"  Fetching blocks…")
        all_blocks = arena.get_channel_blocks(slug)
        log(f"  {len(all_blocks)} block(s) found, {len(existing_arena_ids)} already in Zotero.")

        # Strip already-imported blocks
        new_blocks = [b for b in all_blocks if str(b.get("id")) not in existing_arena_ids]

        # Apply type filter if requested
        if filter_types:
            before = len(new_blocks)
            new_blocks = filter_blocks_by_type(new_blocks, filter_types)
            log(f"  After type filter ({', '.join(filter_types)}): {len(new_blocks)} of {before} block(s).")

        if not new_blocks:
            log("  Nothing new to import.")
            continue

        # Interactive picker
        if interactive:
            new_blocks = select_blocks_interactive(
                new_blocks, col_name, existing_arena_ids
            )
            if not new_blocks:
                log("  Skipped.")
                continue
            log(f"  {len(new_blocks)} block(s) selected.")

        # Build Zotero item payloads and push in batches
        items_payload = []
        for block in new_blocks:
            try:
                items_payload.append(block_to_zotero_item(block, sub_col_key))
            except Exception as exc:
                log(f"  Warning: skipping block {block.get('id')}: {exc}")

        created = 0
        failed = 0
        for batch in _chunk(items_payload, ZOTERO_ITEM_BATCH):
            try:
                result = zotero.create_items(batch)
                created += len(result.get("successful", {}))
                failed += len(result.get("failed", {}))
                for key, err in result.get("failed", {}).items():
                    log(f"  Warning: item {key} failed: {err}")
            except Exception as exc:
                log(f"  Error creating batch: {exc}")
                failed += len(batch)
            time.sleep(0.5)

        log(f"  Created {created} item(s)" + (f", {failed} failed." if failed else "."))

    log("\nSync complete.")
