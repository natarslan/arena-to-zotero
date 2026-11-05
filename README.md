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

```bash
# Import everything from all your channels
python main.py

# Import specific channels by slug
python main.py my-channel-slug another-channel

# Interactive mode: browse blocks per channel and pick which to import
python main.py -i

# Interactive mode for a specific channel
python main.py -i my-channel-slug

# Only import certain block types (no prompt)
python main.py --type Link,Image

# Combine: interactive picker, but only show links
python main.py -i --type Link my-channel-slug
```

The channel slug is the last part of the Are.na URL:  
`https://www.are.na/username/my-channel-slug` → slug is `my-channel-slug`

### Interactive picker

When `-i` / `--interactive` is used, each channel shows a paged list of blocks:

```
────────────────────────────────────────────────────────────
  Channel: Research  (42 blocks)
  ✓ = already in Zotero (will be skipped even if selected)
────────────────────────────────────────────────────────────

  Blocks 1–20 of 42  (page 1/3)
  #     Type  Title
  ────  ─────  ──────────────────────────────────────────────────
     1  [LNK]  Some interesting article
     2  [IMG]  Diagram of a thing                           ✓
     3  [TXT]  Quick note to self
    ...

  Currently selected: 0 new block(s)
  Navigation: n=next, a=select all, c=clear, d=done, s=skip channel
  Enter numbers to toggle (e.g. 1,3,5-8  or  all  or  none):
  > 1,3,7-10
```

- Type numbers, ranges (`5-8`), or `all` / `none`
- Selecting a number again **deselects** it
- Blocks marked `✓` are already in Zotero and will be skipped regardless
- `d` / Enter with no input → confirm and move to next channel
- `s` → skip this channel entirely

### Block types for `--type`

| Value        | Are.na block type         |
|--------------|--------------------------|
| `Link`       | Web page / URL           |
| `Image`      | Image upload or embed    |
| `Text`       | Plain text / markdown    |
| `Media`      | Video, audio embed       |
| `Attachment` | File upload              |
| `Channel`    | Connected channel        |

## Notes

- Re-running is safe — blocks already in Zotero are skipped (tracked via Are.na block ID in the item's `extra` field).
- Zotero allows up to 50 items per API call; large channels are batched automatically.
- Are.na API rate limits are respected with small delays between requests.
