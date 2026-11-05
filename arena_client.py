"""Are.na API client."""

import time
import requests

ARENA_BASE = "https://api.are.na/v2"


class ArenaClient:
    def __init__(self, access_token: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        })

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{ARENA_BASE}{path}"
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_user(self) -> dict:
        return self._get("/me")

    def get_channels(self, username: str) -> list[dict]:
        """Return all channels for a user (handles pagination)."""
        channels = []
        page = 1
        per_page = 100
        while True:
            data = self._get(
                f"/users/{username}/channels",
                params={"page": page, "per": per_page},
            )
            batch = data.get("channels", [])
            channels.extend(batch)
            if len(channels) >= data.get("length", 0) or len(batch) < per_page:
                break
            page += 1
            time.sleep(0.3)
        return channels

    def get_channel_blocks(self, channel_slug: str) -> list[dict]:
        """Return all blocks in a channel (handles pagination)."""
        blocks = []
        page = 1
        per_page = 100
        while True:
            data = self._get(
                f"/channels/{channel_slug}/contents",
                params={"page": page, "per": per_page},
            )
            batch = data.get("contents", [])
            blocks.extend(batch)
            total = data.get("length", 0)
            if len(blocks) >= total or len(batch) < per_page:
                break
            page += 1
            time.sleep(0.3)
        return blocks
