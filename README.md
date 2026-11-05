# arena-to-zotero

Export your [Are.na](https://www.are.na) channels into a [Zotero](https://www.zotero.org) library.

Each Are.na channel becomes a sub-collection in Zotero, and each block (link, image, text, attachment) becomes an item inside it — all nested under a top-level **Arena** collection.

```
Zotero Library
└── Arena
    ├── Research               ← Are.na channel
    │   ├── Some article       ← link block → Webpage item
    │   ├── A diagram          ← image block → Artwork item
    │   └── A quick note       ← text block  → Note item
    └── Inspiration
        └── …
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get your credentials

**Are.na access token**
1. Go to [dev.are.na/oauth/applications](https://dev.are.na/oauth/applications)
2. Create a new application (name it anything)
3. Copy the **Personal Access Token**

**Zotero API key and library ID**
1. Go to [zotero.org/settings/keys](https://www.zotero.org/settings/keys)
2. Click *Create new private key*
3. Give it **read/write** access to your personal library
4. Your **library ID** is the number in your Zotero profile URL:
   `zotero.org/users/1234567` → library ID is `1234567`

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and fill in:

```
ARENA_ACCESS_TOKEN=your_arena_token_here
ZOTERO_API_KEY=your_zotero_key_here
ZOTERO_LIBRARY_ID=1234567
ZOTERO_LIBRARY_TYPE=user
```

---

## Usage

### Import all your channels

Imports every channel you own into Zotero. Each channel becomes a sub-collection under **Arena**.

```bash
python main.py
```

---

### Import specific channels

Pass one or more channel slugs to only import those channels.

```bash
python main.py research-links
python main.py research-links my-inspiration visual-references
```

The **slug** is the last part of the channel URL:
`https://www.are.na/yourname/research-links` → slug is `research-links`

---

### Filter by block type

Use `--type` to only import certain kinds of blocks. Useful if you only want links, or only images, without everything else.

```bash
python main.py --type Link
python main.py --type Link,Image
python main.py --type Text,Attachment
```

| Type value   | What it imports                     |
|--------------|-------------------------------------|
| `Link`       | Web page links                      |
| `Image`      | Images (uploaded or embedded)       |
| `Text`       | Plain text / markdown notes         |
| `Media`      | Videos, audio embeds                |
| `Attachment` | File uploads (PDF, doc, etc.)       |
| `Channel`    | Connected channels (links to them)  |

You can also combine `--type` with specific channels:

```bash
python main.py --type Link research-links
```

---

### Interactive mode — pick blocks yourself

Use `-i` to browse each channel's blocks before importing and select only the ones you want.

```bash
python main.py -i
python main.py -i research-links
python main.py -i --type Link research-links
```

You'll see a paged list like this:

```
────────────────────────────────────────────────────────────
  Channel: Research  (42 blocks)
  ✓ = already in Zotero (will be skipped even if selected)
────────────────────────────────────────────────────────────

  Blocks 1–20 of 42  (page 1/3)
  #     Type  Title
  ────  ─────  ──────────────────────────────────────────
     1  [LNK]  How the internet works
     2  [IMG]  Diagram sketch                          ✓
     3  [TXT]  Note to self
     4  [LNK]  Another article
    ...

  Currently selected: 0 new block(s)
  Navigation: n=next, p=prev, a=select all, c=clear, d=done, s=skip channel
  Enter numbers to toggle (e.g. 1,3,5-8  or  all  or  none):
  > _
```

**How selection works:**

| Input      | What it does                              |
|------------|-------------------------------------------|
| `1,3,5`    | Select blocks 1, 3, and 5                 |
| `5-10`     | Select blocks 5 through 10               |
| `1,3,7-10` | Mix of individual numbers and ranges      |
| `all`      | Select every block on the current page    |
| `none`     | Deselect everything                       |
| A number already selected | Deselects it (toggle)   |
| `n`        | Next page                                 |
| `p`        | Previous page                             |
| `d` or Enter | Confirm selection and move on           |
| `s`        | Skip this channel entirely               |

Blocks marked `✓` are already in Zotero — they'll be skipped regardless of whether you select them.

---

## Common combinations

| Goal | Command |
|------|---------|
| Import everything | `python main.py` |
| Import one channel | `python main.py my-channel` |
| Import two channels | `python main.py channel-one channel-two` |
| Only import links from all channels | `python main.py --type Link` |
| Only import links from one channel | `python main.py --type Link my-channel` |
| Choose blocks yourself, all channels | `python main.py -i` |
| Choose blocks yourself, one channel | `python main.py -i my-channel` |
| Choose from links only, one channel | `python main.py -i --type Link my-channel` |

---

## Re-running safely

You can run the script as many times as you like. Blocks already imported into Zotero are automatically skipped — their Are.na block ID is stored in each Zotero item's `extra` field and checked on every run.

---

## How blocks map to Zotero item types

| Are.na block | Zotero item type |
|--------------|-----------------|
| Link         | Webpage         |
| Image        | Artwork         |
| Text         | Note            |
| Media        | Webpage         |
| Attachment   | Document        |
| Channel      | Webpage         |
