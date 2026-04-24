# Crimson Game Mods v1.0.8 — April 2026 Game Update Compatibility

## Game Update (37GB patch)
The April 22, 2026 game update changed the internal item data format (`iteminfo.pabgb`). This release updates the Rust parser to handle the new format.

## What Works
- **ItemBuffs Tab** — Extract, view, and edit stats for ~94% of items (5982/6339)
- **Infinite Durability** — works
- **Max Stacks** — works
- **No Cooldowns** — works
- **Field Edit Tab** — Mount unlocks, vehicle/region edits, all QoL features
- **Stores Tab** — fully working
- **SkillTree Tab** — fully working
- **Apply to Game** — works (uses byte buffer fallback)
- **Export buttons** — now always visible; prompts for Dev Mode on first use instead of being hidden

## Known Issues (being fixed in v1.0.9)
- **~357 equipment items** (legendary weapons, shields, armor helms, boots, cloaks, necklaces, lanterns, fishing rods) fail to parse due to a sub-struct change in the game update. These items can't have their stats viewed/edited yet.
- **Transmog** — broken for equipment items that fail to parse (targets not found in catalog)
- **Enchant editing** (e.g. Lightning Weapon) — may not apply correctly due to serialize fallback
- **5-Socket Mod (Universal Proficiency)** — socket regeneration broken pending parser fix
- **QFont warning** — cosmetic Qt warning about font size, does not affect functionality

## Technical Changes
- Updated `crimson-rs` ItemInfo struct with 10 new fields from the game update
- Added `PatternDescriptionData` struct, `DockingChildData` new fields
- Implemented per-entry parsing fallback using pabgh schema boundaries
- Restructured `crimson_rs` as a Python package (enums, pack_mod, create_pack)
- Export buttons now prompt for Dev Mode instead of being hidden
- New Damiane equip slots (TwoHandWeapon_Axe/WarHammer/Hammer) detected in equipslotinfo — no parser changes needed
