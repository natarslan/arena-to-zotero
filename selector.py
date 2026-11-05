"""Interactive block selector for the CLI."""

from mapper import BLOCK_TYPE_MAP

# Type label shown in the picker
TYPE_ICONS = {
    "Image": "[IMG]",
    "Link":  "[LNK]",
    "Text":  "[TXT]",
    "Media": "[MED]",
    "Attachment": "[ATT]",
    "Channel": "[CHN]",
}


def _parse_selection(raw: str, max_index: int) -> set[int]:
    """
    Parse a selection string like "1,3,5-8,12" into a set of 0-based indices.
    Accepts 1-based numbers from the user.
    """
    selected = set()
    raw = raw.strip()
    if not raw or raw.lower() == "none":
        return selected
    if raw.lower() == "all":
        return set(range(max_index))
    for part in raw.replace(" ", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, _, end_s = part.partition("-")
            try:
                start = int(start_s.strip()) - 1
                end = int(end_s.strip()) - 1
                for i in range(max(0, start), min(max_index, end + 1)):
                    selected.add(i)
            except ValueError:
                print(f"  Skipping unrecognised range: '{part}'")
        else:
            try:
                idx = int(part) - 1
                if 0 <= idx < max_index:
                    selected.add(idx)
                else:
                    print(f"  Number out of range: {part}")
            except ValueError:
                print(f"  Skipping unrecognised input: '{part}'")
    return selected


def _display_blocks(blocks: list[dict], page: int, page_size: int, existing_ids: set[str]) -> None:
    start = page * page_size
    end = min(start + page_size, len(blocks))
    total_pages = (len(blocks) + page_size - 1) // page_size
    print(f"\n  Blocks {start + 1}–{end} of {len(blocks)}  (page {page + 1}/{total_pages})")
    print(f"  {'#':>4}  {'Type':>5}  Title")
    print(f"  {'─'*4}  {'─'*5}  {'─'*50}")
    for i, block in enumerate(blocks[start:end], start=start):
        block_class = block.get("class", "Link")
        icon = TYPE_ICONS.get(block_class, "[???]")
        title = (
            block.get("title") or block.get("generated_title") or f"block {block.get('id')}"
        )[:60]
        already = " ✓" if str(block.get("id")) in existing_ids else ""
        print(f"  {i + 1:>4}  {icon}  {title}{already}")


def select_blocks_interactive(
    blocks: list[dict],
    channel_name: str,
    existing_ids: set[str],
    page_size: int = 20,
) -> list[dict]:
    """
    Show blocks in pages and let the user pick which to import.
    Returns the selected list of block dicts.
    """
    if not blocks:
        return []

    total = len(blocks)
    total_pages = (total + page_size - 1) // page_size
    selected_indices: set[int] = set()
    page = 0

    print(f'\n{"─" * 60}')
    print(f'  Channel: {channel_name}  ({total} blocks)')
    print(f'  ✓ = already in Zotero (will be skipped even if selected)')
    print(f'{"─" * 60}')

    while True:
        _display_blocks(blocks, page, page_size, existing_ids)

        # Show currently selected count
        new_selected = selected_indices - {
            i for i, b in enumerate(blocks) if str(b.get("id")) in existing_ids
        }
        print(f"\n  Currently selected: {len(new_selected)} new block(s)")

        nav = []
        if page > 0:
            nav.append("p=prev")
        if page < total_pages - 1:
            nav.append("n=next")
        nav += ["a=select all", "c=clear", "d=done", "s=skip channel"]
        print(f"  Navigation: {', '.join(nav)}")
        print(f"  Enter numbers to toggle (e.g. 1,3,5-8  or  all  or  none):")

        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Skipping channel.")
            return []

        if raw.lower() in ("d", "done", ""):
            break
        elif raw.lower() in ("s", "skip"):
            return []
        elif raw.lower() in ("n", "next") and page < total_pages - 1:
            page += 1
        elif raw.lower() in ("p", "prev") and page > 0:
            page -= 1
        elif raw.lower() in ("a", "all"):
            selected_indices = set(range(total))
        elif raw.lower() in ("c", "clear"):
            selected_indices.clear()
        else:
            start_offset = page * page_size
            # Allow page-relative or absolute numbers
            toggled = _parse_selection(raw, total)
            # If user typed small numbers (≤ page_size) treat as page-relative
            if toggled and max(toggled) < page_size and total > page_size:
                toggled = {i + start_offset for i in toggled}
            # Toggle: selecting an already-selected index deselects it
            for idx in toggled:
                if idx in selected_indices:
                    selected_indices.discard(idx)
                else:
                    selected_indices.add(idx)

    return [blocks[i] for i in sorted(selected_indices)]


def filter_blocks_by_type(blocks: list[dict], types: list[str]) -> list[dict]:
    """Return only blocks whose class matches one of the given type names (case-insensitive)."""
    normalised = {t.strip().title() for t in types}
    valid = set(BLOCK_TYPE_MAP.keys())
    unknown = normalised - valid
    if unknown:
        print(f"  Warning: unknown block type(s): {', '.join(unknown)}")
        print(f"  Valid types: {', '.join(sorted(valid))}")
    return [b for b in blocks if b.get("class", "Link") in normalised]
