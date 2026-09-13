# WhaPa-ITA

WhatsApp Parser Toolset — forensic analysis of WhatsApp on **Android** and **iOS**.

This tree is the Italian-oriented edition of [WhaPa](https://github.com/B16f00t/whapa) by Ivan Moreno (B16f00t).  
**Clone this edition from Medvjed80:**

```bash
git clone https://github.com/Medvjed80/whapa-ita.git
cd whapa-ita
```

Upstream project: `https://github.com/B16f00t/whapa.git`

Written in Python 3.11 and tested on Windows, Linux and macOS.

It can parse **end-to-end encrypted WhatsApp backups** (`crypt12` / `crypt14` / `crypt15`) after they are obtained from the device. The backup can be copied by hand; the better route is the free **[Avilla Forensics](https://github.com/AvillaDaniel/AvillaForensics)** toolkit, using **Avilla Universal Whatsapp Extraction**. From the same suite, **Miscellaneous Collections** exports `Contatos.txt`, and the `com.whatsapp` media folder can be collected forensically so reports and single-chat packages include real attachments.

**This version** also lets you export **a single chat forensically** as `.html` or `.pdf`, with the related media, packed in a compressed **`tar.gz`** folder, plus a **`.txt` log** that reports the main information (chat name, phone, JID, message count, size, UTC) and the **SHA-256** hash of the archive.

---

## <u>Newest features (WhaPa-ITA)</u>

The items below are **new in this edition**. They are not in the original upstream toolset.

### <u>E2E encrypted backups and Avilla Forensics</u>

- Parses WhatsApp **end-to-end encrypted backups** (crypt12, crypt14, crypt15) once the file and the device key are available (Whacipher decrypts, then WhaPa reads the SQLite).
- The encrypted backup can be downloaded **manually** from the phone.
- **Better solution:** acquire it with the free **Avilla Forensics** tool, feature **Avilla Universal Whatsapp Extraction**.
- **`Contatos.txt`** is exportable from Avilla Forensics → **Miscellaneous Collections**. Load that file here to resolve display names.
- The **`com.whatsapp` media folder** (images, audio, video, documents) is also downloadable forensically with Avilla Forensics. Point WhaPa at that folder (`-mp` / media field) so reports and exported chats open the real attachments.

### <u>Italian reports and interface</u>

- Interactive report language **ITA** in the GUI dropdown (next to ES and EN).
- Italian terminology throughout the generated HTML report when ITA is selected (buttons, filters, badges, types, printable headings).
- GUI default language is Italian (IT), switchable to English and Spanish.

### <u>Address book from Contatos.txt</u>

- Upload a phone address-book dump (`Contatos.txt`, including UTF-16 LE Avilla/coleta files).
- **Export `Contatos.txt` with Avilla Forensics** from the **Miscellaneous Collections** toolset, then load it in this app.
- Rows such as `display_name=Simone Tarantino` and `data1=3312802146` are matched to WhatsApp JIDs.
- Names appear in chats and group senders even when `wa.db` is missing.

### <u>Name and phone together</u>

- Reports show **contact name and phone number**: `Simone Tarantino (393312802146)`.
- Chat list, message senders, printable tables and exported packages all keep both identifiers.

### <u>Forensic export of a single chat (HTML or PDF + media + tar.gz + TXT log)</u>

- **This version** can export **one selected chat forensically** in **HTML** (`.html`) or **PDF** (`.pdf`).
- The transcript is attached to the **related media** (images, audio, video, documents) inside a compressed **`tar.gz`** folder.
- Next to that folder a **`.txt` log** reports the main information — chat name, phone number, JID, number of messages, archive file name and size, UTC — and the **SHA-256** hash of the compressed archive.
- Archive and log are named from the chat: `Name_Phone.tar.gz` and `Name_Phone.sha256.txt`.
- Inside the `tar.gz`: `chat.html` (always, so media can be opened), optional `chat.pdf`, `attachments/` with the related files, `attachments/index.html`, `MANIFEST.txt`.

**From the interactive report:** select the chat in the left list → **Esporta chat** → HTML or PDF. If the report is a local file, choose the report `media` folder or `WhatsApp/Media` in the dialog so attachments are copied.

**From the GUI:** Messaggi → Ambito **Utente** or **Gruppo** → type the number or name in **Numero o gruppo** → **Esporta chat selezionata** → HTML or PDF. Set the WhatsApp media folder.

**From the command line:**

```text
python libs/whapa.py msgstore.db -m -u 393312802146 -z html -mp "C:\path\to\WhatsApp" -o out
python libs/whapa.py msgstore.db -m -u 393312802146 -z pdf  -mp "C:\path\to\WhatsApp" -o out -r ITA
```

### <u>Working multimedia in the exported chat</u>

- After extracting the `tar.gz`, open `chat.html` (do not open it from inside the compressed file).
- Images, audio and video have players and an **Apri allegato** link into `attachments/`.
- `attachments/index.html` lists every copied file.
- PDF packages also include `chat.html` so media can be opened the same way.

### <u>Report viewer reliability</u>

- Large interactive reports are generated with a single data script so the viewer actually starts (previously thousands of `<script>` tags left a blank page).

---

## Toolset

| Tool | Role |
|------|------|
| `whapa-gui.py` | Graphical interface (launches the tools in `libs/`) |
| `libs/whapa.py` | Database parser — query, filter, reports, single-chat pack |
| `libs/whacipher.py` | Decrypt / encrypt `crypt12`, `crypt14`, **crypt15** |
| `libs/whamerge.py` | Merge several databases into one |
| `libs/whachat.py` | Parse chats exported from the WhatsApp app |
| `libs/whagodri.py` | Download WhatsApp backups from Google Drive |
| `libs/whacloud.py` | Download WhatsApp backups from iCloud |
| `libs/whareader.py` | Read Android (current and legacy) and iOS (`ChatStorage.sqlite`) |
| `libs/whareport.py` | Filters, interactive / printable reports, CSV, KML, chat archive |
| `libs/whacodes.py` | Catalogue of native message-type codes |
| `cfg/settings.cfg` | Case details and cloud credentials |

---

## Install

```bash
git clone https://github.com/Medvjed80/whapa-ita.git
cd whapa-ita
```

Linux or macOS:

```bash
pip3 install --upgrade -r ./doc/requirements.txt
```

Windows:

```text
pip install --upgrade -r .\doc\requirements.txt
```

Start the GUI:

```text
python whapa-gui.py
```

Or run the tools directly from `libs/`.

---

## Existing features (upstream WhaPa)

These come from the original WhaPa project and remain available.

### Database parser (`whapa.py`)

- Autodetects **Android** (current `message` schema and legacy `messages`) and **iOS** (`ChatStorage.sqlite`).
- Message mode (`-m`): list and filter conversations.
- Info mode (`-i`): status (1), call log (2), active chats (3), uncatalogued types (4).
- Extract mode (`-e`): list media paths from the database.
- Carving (`-c`): recover residual records from the file.
- Recipients: one user (`-u`), one group (`-g`), all messages from a number (`-ua`), all chats (`-a`), broadcasts (`-b`).
- Contact names from `wa.db` / `ContactsV2.sqlite` (`-wa`) and, in this edition, from `Contatos.txt` (`--contacts_txt`).
- Media folder (`-mp`) so reports can show images and play audio/video; optional copy into the report (`-cm`). Prefer the `com.whatsapp` media folder collected with Avilla Forensics.
- Static maps downloaded once into the report (`-gm`), no live third-party map calls when the report is opened.

### Filters

- Text search, regular expression, case sensitive, whole word.
- Date range, sender, direction (sent / received / system).
- Native type codes and per-kind flags (text, image, audio, video, contact, location, call, document, GIF, deleted, live location, sticker, system, poll, view-once, note, event).
- Only deleted, starred, forwarded, edited, with attachment, with coordinates, read / unread.
- WhatsApp Web messages.

### Reports

- **Interactive HTML** (`-r ES|EN|ITA`): chat list, lazy-loaded pages, in-chat and global search, filters, print chat, CSV export from the viewer, summary and SHA-256 of the sources.
- **Printable HTML** (`-p`): static table for paper or PDF, cover, applied criteria, source verification.
- **CSV** (`-x`) of the selected messages.
- **KML** (`-k`) of locations for Google Earth / QGIS.
- Single-file interactive report (`-1`).
- LID identifiers are not shown as if they were phone numbers; they are resolved through `lid_jid_map` when possible.
- Delivery / read status, reactions, quotes, system actions, group subjects.

### Whacipher

- Decrypt or encrypt **end-to-end encrypted** WhatsApp backups with the phone key (`.key`, `encrypted_backup.key`, or 64 hex characters of the root key).
- crypt12, crypt14 and crypt15.
- File or folder of encrypted databases.
- Obtain the backup manually, or preferably with **Avilla Forensics → Avilla Universal Whatsapp Extraction**.

### Whamerge

- Merge several `msgstore` databases from a folder into one SQLite file.

### Whachat

- Build an interactive or printable report from a chat exported by the WhatsApp application (with optional media folder).

### Whagodri / Whacloud

- List and download Android backups from Google Drive.
- List and synchronise iCloud backups.
- Credentials in `cfg/settings.cfg` (`[google-auth]`, `[icloud-auth]`).
- Optional filters (images, video, audio, documents, databases only), thread count, dry run.

### Graphical interface

- Tabs for WhaPa, WhaCipher, WhaMerge, WhaGoDri, WhaChat, WhaCloud.
- Language switch (IT / EN / ES).
- Settings editor, dependency installer, log pane.
- Case metadata (company, record, examiner) written into reports.

---

## Typical workflow

1. **Acquire the evidence** (manual copy, or preferably **Avilla Forensics**):
   - Encrypted WhatsApp backup → **Avilla Universal Whatsapp Extraction** (or a manual download of the `crypt12` / `crypt14` / `crypt15` file and key).
   - Address book → **Miscellaneous Collections** → `Contatos.txt`.
   - Attachments → forensic download of the **`com.whatsapp` media folder**.
2. Decrypt the backup with Whacipher if it is still encrypted, then open the resulting `msgstore.db` in WhaPa.
3. Load `Contatos.txt` and/or `wa.db`, and set the media folder (`-mp`) to the Avilla `com.whatsapp` collection so images and audio open in the report.
4. Generate an interactive report (`-r ITA`) and/or a printable report (`-p`).
5. To deliver **one chat forensically**: set Ambito to Utente/Gruppo (or `-u` / `-g`) and export HTML or PDF (`-z`). The package is a `tar.gz` with the transcript and related media; keep the `.txt` log (main information + SHA-256) with it.
6. Extract the `tar.gz` and open `chat.html` to play or open the attachments.

---

## Project layout

```text
whapa-gui.py          GUI
libs/                 command-line tools and libraries
cfg/settings.cfg      case data and cloud credentials
doc/                  licence, requirements, changelog
```

---

## Credits and licence

- Original WhaPa: Ivan Moreno (B16f00t) — [github.com/B16f00t/whapa](https://github.com/B16f00t/whapa)
- This edition (Italian reports, Contatos.txt, name+phone, single-chat export): clone from **[Medvjed80/whapa-ita](https://github.com/Medvjed80/whapa-ita)**

See `doc/` for licence and third-party dependencies. Use only on material you are legally entitled to examine.
