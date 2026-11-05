"""Map Are.na blocks to Zotero item payloads."""

from datetime import datetime

# Are.na class → Zotero item type
BLOCK_TYPE_MAP = {
    "Image": "artwork",
    "Link": "webpage",
    "Text": "note",
    "Media": "webpage",
    "Attachment": "document",
    "Channel": "webpage",
}


def _safe_date(date_str: str | None) -> str:
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return date_str[:10] if date_str else ""


def block_to_zotero_item(block: dict, collection_key: str) -> dict:
    """Convert an Are.na block dict to a Zotero item payload."""
    block_class = block.get("class", "Link")
    item_type = BLOCK_TYPE_MAP.get(block_class, "webpage")

    title = (
        block.get("title")
        or block.get("generated_title")
        or f"Are.na block {block.get('id', '')}"
    ).strip()

    date_added = _safe_date(block.get("created_at"))
    description = block.get("description") or block.get("description_html") or ""
    arena_url = f"https://www.are.na/block/{block.get('id')}"

    base = {
        "itemType": item_type,
        "title": title,
        "date": date_added,
        "extra": f"Are.na block ID: {block.get('id')}\nBlock class: {block_class}",
        "collections": [collection_key],
        "tags": [{"tag": t.get("name", "")} for t in block.get("connection_data", {}).get("tags", [])],
    }

    if item_type == "note":
        # For text blocks use the note content
        content = block.get("content") or block.get("content_html") or title
        return {
            "itemType": "note",
            "note": f"<p><strong>{title}</strong></p>{content}",
            "collections": [collection_key],
            "tags": base["tags"],
        }

    elif item_type == "artwork":
        source = block.get("source") or {}
        url = source.get("url") or block.get("image", {}).get("original", {}).get("url", arena_url)
        base["url"] = url
        base["artworkMedium"] = "Digital image"
        if description:
            base["extra"] += f"\n{description}"

    elif item_type == "webpage":
        source = block.get("source") or {}
        url = source.get("url") or arena_url
        base["url"] = url
        base["websiteTitle"] = source.get("title") or ""
        if description:
            base["abstractNote"] = description

    elif item_type == "document":
        source = block.get("source") or {}
        attachment = block.get("attachment") or {}
        base["url"] = attachment.get("url") or source.get("url") or arena_url
        if description:
            base["abstractNote"] = description

    return base


def channel_to_collection_name(channel: dict) -> str:
    return channel.get("title") or channel.get("slug") or f"channel-{channel.get('id')}"
