"""Zotero Web API client."""

import time
import requests

ZOTERO_BASE = "https://api.zotero.org"


class ZoteroClient:
    def __init__(self, api_key: str, library_id: str, library_type: str = "user"):
        self.library_id = library_id
        self.library_type = library_type  # "user" or "group"
        self.session = requests.Session()
        self.session.headers.update({
            "Zotero-API-Key": api_key,
            "Zotero-API-Version": "3",
            "Content-Type": "application/json",
        })

    @property
    def _base(self) -> str:
        t = "users" if self.library_type == "user" else "groups"
        return f"{ZOTERO_BASE}/{t}/{self.library_id}"

    def _get(self, path: str, params: dict = None) -> requests.Response:
        resp = self.session.get(f"{self._base}{path}", params=params)
        resp.raise_for_status()
        return resp

    def _post(self, path: str, json: object) -> requests.Response:
        resp = self.session.post(f"{self._base}{path}", json=json)
        resp.raise_for_status()
        return resp

    # ── Collections ──────────────────────────────────────────────────────────

    def get_all_collections(self) -> list[dict]:
        """Return every collection in the library."""
        collections = []
        start = 0
        limit = 100
        while True:
            resp = self._get("/collections", params={"start": start, "limit": limit})
            batch = resp.json()
            collections.extend(batch)
            total = int(resp.headers.get("Total-Results", 0))
            start += limit
            if start >= total:
                break
            time.sleep(0.2)
        return collections

    def find_collection_by_name(self, name: str, parent_key: str = None) -> dict | None:
        """Find a collection by name (and optionally parent key)."""
        for col in self.get_all_collections():
            data = col.get("data", {})
            if data.get("name") == name:
                col_parent = data.get("parentCollection") or None
                if parent_key is None or col_parent == parent_key:
                    return col
        return None

    def create_collection(self, name: str, parent_key: str = None) -> dict:
        """Create a collection; return the created collection dict."""
        payload = [{"name": name}]
        if parent_key:
            payload[0]["parentCollection"] = parent_key
        resp = self._post("/collections", json=payload)
        result = resp.json()
        # Zotero returns {"successful": {"0": {...}}, ...}
        created = result.get("successful", {}).get("0", {})
        if not created:
            raise RuntimeError(f"Failed to create collection '{name}': {result}")
        return created

    def get_or_create_collection(self, name: str, parent_key: str = None) -> dict:
        existing = self.find_collection_by_name(name, parent_key)
        if existing:
            return existing
        return self.create_collection(name, parent_key)

    # ── Items ─────────────────────────────────────────────────────────────────

    def get_collection_items(self, collection_key: str) -> list[dict]:
        """Return all items in a collection."""
        items = []
        start = 0
        limit = 100
        while True:
            resp = self._get(
                f"/collections/{collection_key}/items",
                params={"start": start, "limit": limit},
            )
            batch = resp.json()
            items.extend(batch)
            total = int(resp.headers.get("Total-Results", 0))
            start += limit
            if start >= total:
                break
            time.sleep(0.2)
        return items

    def create_items(self, items: list[dict]) -> dict:
        """Create up to 50 items at once (Zotero limit)."""
        resp = self._post("/items", json=items)
        return resp.json()

    def item_template(self, item_type: str) -> dict:
        """Fetch a blank item template for the given type."""
        resp = self._get(f"/items/new", params={"itemType": item_type})
        return resp.json()
