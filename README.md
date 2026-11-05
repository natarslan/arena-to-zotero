# arena-to-zotero

Export your [Are.na](https://www.are.na) channels into a [Zotero](https://www.zotero.org) library.

## What it creates

```
Zotero Library
└── Arena                    ← top-level collection (created automatically)
    ├── My Channel           ← one sub-collection per Are.na channel
    │   ├── Some Link        ← webpage item
    │   ├── An Image         ← artwork item
    │   └── A Note           ← note item
    └── Another Channel
        └── …
```

Are.na block types map to Zotero item types:

| Are.na block | Zotero type  |
|--------------|--------------|
| Link         | Webpage      |
| Image        | Artwork      |
| Text         | Note         |
| Media        | Webpage      |
| Attachment   | Document     |
| Channel      | Webpage      |

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env`:

```
ARENA_ACCESS_TOKEN=...   # from https://dev.are.na/oauth/applications
ZOTERO_API_KEY=...       # from https://www.zotero.org/settings/keys
ZOTERO_LIBRARY_ID=...    # your numeric user ID (in your profile URL)
ZOTERO_LIBRARY_TYPE=user # "user" or "group"
```

**Are.na token**: Go to [https://dev.are.na/oauth/applications](https://dev.are.na/oauth/applications), create an application, then generate a personal access token.

**Zotero API key**: Go to [https://www.zotero.org/settings/keys](https://www.zotero.org/settings/keys) and create a key with read/write access to your library. Your library ID is the number in your Zotero profile URL (`zotero.org/users/<ID>`).

### 3. Run

Sync all your channels:
```bash
python main.py
```

Sync specific channels by slug:
```bash
python main.py my-channel-slug another-channel
```

The channel slug is the last part of the Are.na URL:  
`https://www.are.na/username/my-channel-slug` → slug is `my-channel-slug`

## Notes

- Re-running the script is safe — it skips blocks already in Zotero (tracked via Are.na block ID stored in the item's `extra` field).
- Zotero allows up to 50 items per API call; large channels are batched automatically.
- Are.na API rate limits are respected with small delays between requests.
