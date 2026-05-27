# Session Status — 2026-04-23

## Shipped: CrimsonGameMods v1.0.9

Released to GitHub. Auto-updater live. Users get update notification on launch.

---

## What Works

### ItemBuffs Tab (v1.0.8 + v1.0.9 fixes)
- **All features stack**: Enable Everything, God Mode, presets, per-item edits, transmog, sockets, UP v2
- **Parser updated** for April 2026 game update (10 new fields, 6331/6339 items)
- **Mirror field sync** in all 7 code paths (cooltime ↔ unk_post_cooltime_a/b, max_charged ↔ unk_post_max_charged_a/b)
- **Rebuild uses vanilla ordering** — no more silent edit drops when extracting from overlay
- **Apply to Game fallback** tries serialize_iteminfo before dropping to raw bytes
- **Config load** uses per-entry fallback for housing items
- **Confirmed working in-game** by user

### Stacker Tool (v1.0.9)
- **Fixed**: vanilla parsing with per-entry PABGH fallback (was crashing on housing items)
- **Fixed**: serialize path uses vanilla-ordered rebuild (was corrupting 2.7M bytes via naive append)
- **Fixed**: uninstall NameError (`group_dir` → `group_dirs`)
- **Fixed**: pabgh uses pre-built index from rebuild, not sequential scan
- **NEW: Export Field JSON** — diffs merged result vs vanilla, outputs Format 3 semantic JSON
- **NEW: Import Field JSON** — drop `.field.json` into Stacker, applies by field-name lookup
- **NEW: Legacy Mod Translator** — old parser + old vanilla → reparse-diff → field-name intents
- **NEW: Per-item validation** — serialize→reparse each touched item, revert broken ones to vanilla
- **NEW: Apply Single Stack** — choose overlay folder # (e.g. 0058) instead of always 0062
- **Proven end-to-end**: Ultimate Lantern Reborn v1.1 legacy JSON → field JSON → import → apply → game runs

### Dropsets Tab
- **Fixed**: game added 1 new u32 field (`unk_post_cond`) after `unk_cond_flag` in each drop entry (64→68 bytes)
- **All 11,864 dropsets parse correctly** with sane rates and quantities
- Parser + serializer both updated

### Parser (crimson-rs)
- PR to Potter: https://github.com/potter420/crimson-rs/pull/1
- 10+ new ItemInfo fields mapped
- `parse_iteminfo_tracked` added for byte-level field attribution
- Legacy parser preserved at `crimson_rs/_legacy/crimson_rs.pyd`
- Old vanilla baseline bundled at `game_baselines/1.0.0.3/iteminfo.pabgb`

---

## What's Broken

### Stores Tab — NEEDS FIX (partial progress)

**IDA findings (from Mac 1.0.0.4 binary):**
- StoreItemData gained `_refreshFieldTime` (u64) — registered at runtime offset 40, before `_buyPrice` (48) and `_sellPrice` (56)
- StoreData (per-store header) gained `_lastPriceRefreshFieldTime` (u64) at offset 48
- StoreData also gained `_globalGameEventInfoKeyList` (array of GlobalGameEventInfoKey) and `_varyTradeItemPriceRateList` (array of ReflectObject)

**Binary analysis findings:**
- **Variable-length entries** — NOT fixed size. Two sizes found in Store_Her_General:
  - First 3 entries: **123 bytes** each
  - Remaining 34 entries: **110 bytes** each
  - Difference: 13 bytes (likely flag-dependent extra data, same pattern as dropset `unk4`)
- **Item count offset**: +0x2F from after_name (was +0x26)
- **Item key position**: +0x22 from entry start (confirmed via item_key/item_key_dup pairs)
- **Item key dup**: 63 bytes (0x3F) after item_key, so at +0x61 from entry start (was +0x5D - 0x22 = 0x3B = 59 bytes gap, now 63)
- **Header overhead**: 0x33 = 51 from after_name to first entry (same as old format)
- Every entry has two `1000000` (Health Amplification key) references at item_key - 0x20 and - 0x18 — likely `_itemInfoWrapper` fields

**What this means for the parser:**
- Cannot use fixed `ITEM_ENTRY_SIZE` — entries are variable length
- Need sequential parsing with flag-based size detection (like dropset parser's `unk4` branches)
- Must identify which byte/flag determines 123 vs 110 byte entries
- The old parser's `is_standard` check (fixed size * count == remaining) will only work for stores where ALL entries are the same size

**Current parser state:**
- `ITEM_ENTRY_SIZE = 113` — WRONG, entries are 110 or 123
- `HEADER_OVERHEAD = 55` — WRONG, actual is 51 (unchanged from old)
- Count at +0x2F — correct
- Field offsets within entry — partially mapped but need verification against variable-size entries
- Dropset parser fix is verified working (new `unk_post_cond` u32 field)

### 8 Housing Items — PENDING POTTER
- Keys: 1003774, 1003823-1003825, 1003976-1003979
- Extra u32 after `unk_post_max_charged_b` shifts all subsequent fields
- Hypothesis: add `unk_post_max_charged_c: u32` to ItemInfo struct
- Workaround: per-entry PABGH parsing stores them as raw bytes (round-tripped verbatim)
- PR #1 sent to Potter with full details

---

## Architecture Decisions Made This Session

### Overlay Priority
- **Confirmed**: higher-numbered overlay groups override lower-numbered ones for the same file
- 0062/ iteminfo overrides 0058/ iteminfo — game uses last-loaded
- Implication: Stacker output (0062) replaces ItemBuffs output (0058) for iteminfo
- Apply Single Stack lets user choose the target folder to avoid conflicts

### Field JSON Format (Format 3)
```json
{
  "format": 3,
  "target": "iteminfo.pabgb",
  "intents": [
    {"entry": "Lantern", "key": 10026, "field": "cooltime", "op": "set", "new": 1}
  ]
}
```
- Field names survive game updates (103/105 old fields have 1:1 match in new format)
- Only 2 field name changes: `unk_texture_path` → `default_texture_path`, `usable_alert` removed
- Translator auto-remaps renamed fields

### Legacy Mod Translation Pipeline
1. Load old vanilla `game_baselines/1.0.0.3/iteminfo.pabgb`
2. Load legacy parser `crimson_rs/_legacy/crimson_rs.pyd` (module-swap to avoid import collision)
3. Apply JSON v2 byte patches to old vanilla bytes
4. Reparse patched bytes with legacy parser
5. Diff old vs patched parsed dicts → field-name intents
6. Remap renamed fields, drop removed fields
7. Export as Format 3 JSON targeting current game version

### Dual Parser Coexistence
- Current parser: `crimson_rs/crimson_rs.pyd` (post-April 2026, 115 fields)
- Legacy parser: `crimson_rs/_legacy/crimson_rs.pyd` (pre-April 2026, 105 fields)
- Loaded via `importlib.util.spec_from_file_location` with `sys.modules` swap
- Both coexist in same process without collision
- Doc for Potter: `CRIMSON_RS_DUAL_PARSER_TECHNICAL_DOC.md`

---

## Files Changed This Session

### Modified
- `gui/tabs/buffs_v319.py` — rebuild fix, mirror sync (7 locations), fallback, config load
- `gui/tabs/stacker.py` — parse fallback, serialize rebuild, field JSON export/import, legacy translator, apply single, uninstall fix
- `dropset_editor.py` — new `unk_post_cond` field in drop entries
- `storeinfo_parser.py` — updated sizes and offsets (partial — needs more work)
- `updater.py` — version 1.0.9
- `editor_version_gamemods.json` — version 1.0.9
- `CrimsonGameMods.spec` — added `game_baselines` to bundled data
- `item_creator.py` — build_iteminfo_pabgh updates

### Added
- `game_baselines/1.0.0.3/iteminfo.pabgb` — old vanilla for legacy mod translation
- `CRIMSON_RS_DUAL_PARSER_TECHNICAL_DOC.md` — technical doc for Potter
- `Ultimate_Lantern_Reborn_v1.1.field.json` — proof-of-concept translated mod

### External
- PR #1 to `potter420/crimson-rs` — parser update for April 2026 game
- `editor_version_gamemods.json` updated on GitHub release repo
- Release `gamemods-v1.0.9` created on `NattKh/CRIMSON-DESERT-SAVE-EDITOR-AND-GAME-MODS`
