# Handover: Build Custom Item Creator

## CRITICAL TEST RESULTS (2026-04-17)

### What WORKS:
- **Swap existing item into store**: Modify an existing item's stats (e.g. max attack to 999k)
  and it shows up in the vendor with the game's existing name. CONFIRMED WORKING.
- Approach: edit iteminfo stats via crimson_rs → deploy 0058 overlay → vendor already sells it
- Store injection via StoreinfoParser.add_item() also works for adding existing keys to new vendors

### What WORKS (confirmed via save editor repurchase swap):
- **Brand new item key (999001+) via save editor**: Clone item, deploy iteminfo overlay (0058),
  swap item key in save via repurchase tab, buy back in-game = CUSTOM ITEM WORKS.
- Clone engine (echo key patching) produces valid binary
- crimson_rs extracts the overlay correctly from group 0058 (6025 items with key 999001)
- Game loads and recognizes the new item key from the overlay

### What DOESN'T work:
- **Store injection via storeinfo overlay (0060)**: Adding new key to storeinfo didn't show
  up in vendor. Likely a storeinfo binary format issue with our add_item() insertion.
- **Paloc overlay (0064)**: Untested whether the unencrypted paloc was loaded. The item
  may have shown with a blank name. Vanilla paloc uses flags=0x0032 (ChaCha20+LZ4).

### CONFIRMED PIPELINE (2026-04-17):
1. User picks a donor item from 6024 items (searchable, with icons)
2. User sets custom name, description, stats (attack/defense/HP/etc)
3. System clones item under new key (999001+), patches echo keys + stats
4. Deploy: 0058 overlay (iteminfo with 6025 items)
5. User opens save editor → Repurchase tab → swaps junk item to new key
6. Load game → buy back from vendor → CUSTOM ITEM IN HAND

Ideally steps 4-5 should be combined into one button.

### Future: True Custom Items
To make new item keys work, need to investigate:
- Whether the game validates pabgh entry count at load time
- Whether paloc overlays need encryption (flags=0x0032, ChaCha20 + LZ4)
- The paz_crypto.py tools at CrimsonSaveEditorGUI/Localization/tools/ have full encrypt/decrypt
- May need to use PackGroupBuilder with Compression.LZ4 + Crypto.CHACHA20 for paloc

---

## Context
Community contributor Benreuveni built `crimson-desert-add-item` — a CLI tool for cloning existing items under new IDs with custom stats and localization. We want to integrate this into CrimsonGameMods as a visual, "child-proof" item creator with live preview.

Source: `C:\Users\Coding\Desktop\New folder\crimson-desert-add-item-main\`

## What to Build

### 1. Clone Engine: `item_creator.py`

Port from Benreuveni's `lib/iteminfo.py` + `lib/paloc.py`:

**Core functions**:
- `clone_item(rust_items, donor_key, new_key, new_name)` — clone donor's binary blob, patch key + name + echo keys (0x07 0x70/0x71 markers)
- `find_next_free_key(rust_items, start=999001)` — auto-generate key that doesn't conflict with any existing item
- `compute_paloc_ids(item_key)` — `(key << 32) | 0x70` for name, `| 0x71` for description
- `build_modded_iteminfo(vanilla_body, vanilla_head, new_items)` — append cloned items, rebuild pabgh

**Echo key pattern** (critical for game name lookup):
```
byte 0x07 + u32 0x70 + u32 item_key  → name lookup
byte 0x07 + u32 0x71 + u32 item_key  → description lookup
```
These MUST be patched to the new key or the item shows as blank in-game.

**Stat modification** (reuse existing crimson_rs):
- Already have `crimson_rs.parse_iteminfo_from_bytes()` for field-level access
- Can modify `enchant_data_list[0].enchant_stat_data.stat_list_static` for flat stats
- Can modify `enchant_data_list[0].enchant_stat_data.stat_list_static_level` for rate stats

### 2. Dialog: `gui/dialogs/item_creator_dialog.py`

**Visual Design** — Match the existing item preview card style (buffs_v319.py:3951):

```
+--[ Create Custom Item ]--------------------------------------------+
|                                                                     |
|  [Donor Item: _________________ v]  [Icon 96x96]                   |
|                                                                     |
|  +--- LIVE PREVIEW CARD ---+  +--- EDIT FORM ----------------+    |
|  | [Icon]                   |  | Name: [________________]     |    |
|  | Bale's Sword             |  | Description: [__________]   |    |
|  | Legendary | Weapon       |  | Key: [999001] (auto)        |    |
|  |                          |  |                              |    |
|  | Attack         500       |  | --- Stats ---                |    |
|  | Defense        200       |  | Attack: [__500__]            |    |
|  | Critical Rate  Lv 10    |  | Defense: [__200__]           |    |
|  | Move Speed     Lv 5     |  | Crit Rate: [__10__]          |    |
|  |                          |  | Move Speed: [__5__]          |    |
|  | Passive: Shadow Dash     |  | HP: [__0__]                  |    |
|  |                          |  |                              |    |
|  | Enchant +0 of 10         |  | [+ Add Stat]                |    |
|  +--------------------------+  +------------------------------+    |
|                                                                     |
|  [Create Item]                                    [Cancel]          |
+---------------------------------------------------------------------+
```

**Key UI Elements**:
- **Donor selector**: Searchable QComboBox with icon thumbnails (reuse existing item list from ItemBuffs)
- **Live preview**: HTML card identical to `_buff_preview_item()` — updates in real-time as user edits
- **Auto-key**: Auto-assigns next available key >= 999001, with validation label ("Key 999001 is available")
- **Stat form**: Only shows stats the donor item already has. Each stat gets a labeled QSpinBox. Values shown in game units (attack/defense in thousands, rates as levels 0-15)
- **Add Stat button**: Dropdown to add a new stat from the known 28 hashes
- **Tier selector**: Dropdown for Common/Uncommon/Rare/Epic/Legendary
- **Create button**: Clones item, patches stats, adds to staged items, user deploys via Apply to Game

**Validation (child-proof)**:
- Key auto-generated, can't conflict
- Name required, max 100 chars
- Stats clamped to valid ranges (rate 0-15, flat values sane maximums)
- Donor must be selected
- Preview updates live so user sees exactly what they're creating
- Warning if creating a duplicate name

### 3. Integration Points

**In ItemBuffs tab** (`buffs_v319.py`):
- Add "Create Item" button in the toolbar (always visible)
- Opens the creator dialog
- On success: item gets added to `_buff_rust_items` list and staged for Apply to Game
- Item also gets registered in name DB so it appears in the item list immediately

**Localization**:
- User already has paloc patching at `CrimsonSaveEditorGUI - Copy/Localization/`
- For Apply to Game: we need to either:
  a) Bundle paloc in the overlay (0058), OR
  b) Show instructions for paloc patching, OR
  c) Port the 118-line paloc.py parser for direct patching

**Save editor integration**:
- Auto-generate `item_names.json` entry so the save editor can see the new item
- Auto-generate `item_templates.json` entry (clone donor template, patch key)

### 4. File Locations

| File | Purpose |
|------|---------|
| `item_creator.py` | Clone engine (clone_item, echo key patching, paloc IDs) |
| `gui/dialogs/item_creator_dialog.py` | Visual creator dialog |
| Integration in `gui/tabs/buffs_v319.py` | "Create Item" button + staging |

### 5. Key Data from Benreuveni's Code

**Echo key format**: `0x07` marker byte + `u32 tag (0x70=name, 0x71=desc)` + `u32 item_key`
**Paloc ID formula**: `name_id = (item_key << 32) | 0x70`, `desc_id = (item_key << 32) | 0x71`
**Paloc entry format**: `8-byte marker (07 00 00 00 00 00 00 00)` + `u32 key_len` + `key UTF-8` + `u32 val_len` + `value UTF-8`
**Recommended key range**: 999001+ to avoid vanilla collisions (6024 items, highest vanilla key ~200K)

### 6. What We Already Have

- `crimson_rs.parse_iteminfo_from_bytes()` — full item field parsing
- `crimson_rs.serialize_iteminfo()` — serialize back to pabgb
- `IconCache.get_pixmap(item_key)` — item icons
- `ItemNameDB.get_name(item_key)` — item display names
- Item preview HTML card (buffs_v319.py:3951-4160)
- PackGroupBuilder overlay deployment
- 28 stat hashes with human names
- Paloc patching tools at `CrimsonSaveEditorGUI - Copy/Localization/`

### 7. Benreuveni Source Reference

- `C:\Users\Coding\Desktop\New folder\crimson-desert-add-item-main\lib\iteminfo.py` — clone_item, echo key patching, pabgh rebuild
- `C:\Users\Coding\Desktop\New folder\crimson-desert-add-item-main\lib\paloc.py` — paloc parser (118 lines)
- `C:\Users\Coding\Desktop\New folder\crimson-desert-add-item-main\lib\stats.py` — stat array scanner
- `C:\Users\Coding\Desktop\New folder\crimson-desert-add-item-main\lib\savedb.py` — save editor extension builder
