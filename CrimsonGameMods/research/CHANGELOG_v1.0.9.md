# CrimsonGameMods v1.0.9 Changelog

## Game Update Support
- Updated to crimson_rs v1.0.4.1 (Potter's latest wheel) — new iteminfo fields: `inherit_summoner`, `summon_tag_name_hash`, `PatternDescriptionData`, `extract_additional_drop_set_info`, `minimum_extract_enchant_level`, `is_housing_only`, `unk_texture_path`, `usable_alert_type`, `pattern_description_data_list`, `is_preserved_on_extract`
- Saved vanilla baselines for both 1.0.0.3 and 1.0.0.4 game versions (iteminfo + skill)

## New: Field JSON v3 Export Format
- **Replaced all legacy export formats** (Export JSON Patch, Export as Mod, Export CDUMM) with a single "Export as Field JSON v3" button
- Field JSON uses field names instead of byte offsets — mods survive game updates automatically
- Published `FIELD_JSON_V3_SPEC.md` technical spec for mod manager developers (JMM, CDUMM, DMM)
- Dev mode prompt updated to explain the format change and current mod manager compatibility

## New: Export Field JSON on All Tabs
- **ItemBuffs** — Export as Field JSON v3 (diffing against vanilla)
- **MercPets** — Export + Import Field JSON for mercenary/pet/vehicle caps
- **DropSets** — Export + Import Field JSON for drop table edits
- **BagSpace** — Export + Import Field JSON for inventory slot changes

## New: Stacker Multi-Version Support
- Stacker now discovers ALL baselines in `game_baselines/` (1.0.0.3, 1.0.0.4, future versions)
- Auto-detects which baseline a legacy mod targets by scoring `original` byte matches
- Correct parser per baseline (current crimson_rs for 1.0.0.4, legacy parser for 1.0.0.3)
- Hex string offsets (`"31AF6C"`) now parsed correctly
- Insert patches applied in reverse offset order to prevent corruption
- Path A (preview diff) now preferred over Path B (baseline translation) — handles all mod types including inserts

## New: Skill Editor (skill.pabgb)
- **100% roundtrip skill.pabgb parser** (`skillinfo_parser.py`) — 1952 entries on 1.0.0.4
- 17 named fields decoded from fixed header (isBlocked, cooltime, applyType, skillGroupKey, uiType, damageType, useBatteryStat, etc.)
- Tail section fully parsed (max_level, skill_group_key_list, buff_sustain_flag, dev names, video hash)
- **Stamina Presets** — one-click buttons: 10%, 25%, 50%, 75%, Infinite stamina
- In-place value patching — no cross-version blob transfer, works on current game data directly
- **Cooltime and MaxLevel editable** in the skill table (double-click to edit)
- Import Legacy Mod — loads legacy skill JSON mods, auto-detects baseline
- Export Field JSON — exports as Format 3 JSON targeting `skill.pabgb`
- Apply to Game — packs into overlay (shared with skill tree swaps)
- Bundled stamina presets in `stamina_presets/`

## New: ItemBuffs Features (ported from community dev)
- **Favorites** — right-click to add/remove items, star button to filter
- **Drop enchant level selector** — change enchant level on drop per item
- **Socket display** in stats table — shows socket items when selecting equipment
- **Individual socket extender** — set socket count + pre-unlocked count per item
- **Drop data saved in config** — enhance level and socket changes persist in config export/import
- **Item diff & inspect** — restored in advanced right-click menu

## Overlay Spinners
- **SpawnEdit** — was hardcoded `0037`, now configurable (default 37)
- **BagSpace** — was hardcoded `0062`, now configurable (default 61, avoids Stacker conflict)
- All active tabs now have unique non-conflicting overlay defaults

## Bug Fixes
- **No Cooldown** rewritten to use Rust dict approach — no longer depends on fragile byte-marker scanning
- **Great Thief** preset disabled (broken after game update)
- **Stores tab** disabled (broken after game update)
- **Mod Manager tab** disabled (not functional yet)
- **Shared state startup audit** disabled (was producing false "unknown owner" warnings)
- Fixed duplicate `_eb_extend_sockets` method from port
- Fixed socket display `(none)` branch using correct variable (`si_c` not `c1`)

## Disabled / Removed
- Legacy export buttons removed (Export JSON Patch, Export as Mod, Export CDUMM, Export All Formats)
- Great Thief preset button commented out
- Stores tab commented out
- Mod Manager (DMM WebView) tab commented out

## TODO
- **BuffLevelData full decode** — 120 buff types, 38 unique subclasses. Common base mapped from IDA but subclass-specific fields not yet decoded. Needed for per-field stamina editing and granular Field JSON export for skills
- Stores tab update for new game version
- Great Thief preset fix for new game version
