# Crimson Game Mods v1.0.3 — Changelog

## What's New

### Universal Proficiency v2 (NEW)
- **All 3 player characters can now equip any weapon and armor**
  - Kliff, Damiane, and Oongka can use each other's equipment
  - Pirate King Hat, Mining Knuckledrill, Oongka blasters, Damiane rapiers — all cross-equippable
  - NPC weapons with no tribe restriction (Witch's Fan, Magic Scythe, etc.) still work for everyone
- **Targeted slot expansion** — only adds weapon hashes to weapon slots, armor to armor slots
  - No more items showing up in wrong equipment categories
  - Only the 3 player characters are modified (NPCs/mercenaries untouched)
- **Tribe_gender union** — adds the 12 known player tribe hashes to every restricted item
  - Items already open to all characters are left untouched
  - Never clears or removes existing hashes (prevents Batz_OneHandDagger crash)
- **Split overlay architecture** — iteminfo and equipslotinfo deploy to separate PAZ groups
  - Group 0058: iteminfo.pabgb (tribe_gender changes)
  - Group 0059: equipslotinfo.pabgb + .pabgh (slot expansion)
  - Prevents the game from rejecting the entire overlay
- Universal Proficiency v1 moved to dev mode (kept for research)
- CDUMM export warns when Universal Proficiency is active (not compatible)

### Mesh Swap — Make Rideable (NEW)
- **Inject rider bones into any skeleton** to make non-rideable mounts rideable
  - Confirmed working: Golden Star (golemdragon) rideable via Blackstar swap
  - B_Rider_01 bone injected with configurable rider height (Y offset)
- **Character scale override** — resize any mesh-swapped creature
  - Extracts original appearance XML from PAZ, modifies CharacterScale only
  - Deploys as separate overlay (group 0062)
- **"Make Rideable" checkbox** in mesh swap dialog with rider height spinbox
  - Warning popup explains this only works reliably for flying dragon-type mounts
- **PAB skeleton parser fully rewritten** (`Model/pab_skeleton_parser.py`)
  - Fixed: bone_count is u16 (was u8 — only read 18 of 274 bones)
  - Fixed: names are length-prefixed (was scanning for ASCII)
  - Added: `serialize_pab()` for writing skeletons back to binary
  - Added: `inject_bone()` for cross-skeleton bone transplant
  - Perfect round-trip on all tested skeletons

### 5 Sockets — Out of Dev Mode
- Socket extender row (Extend Sockets + All -> 5 Sockets) is now always visible
- No longer requires experimental/dev mode to access

### Apply to Game — PAPGT Fix
- Apply to Game no longer wipes other overlay group entries from PAPGT
- Previously: rebuilding from vanilla backup dropped 0059 (equipslotinfo), 0039 (field edits), 0062 (rider bone)
- Now: reads current PAPGT and only removes/re-adds its own group entry

### Bug Fixes
- Fixed `deepcopy` crash on Python 3.14 (crimson_rs Rust objects incompatible with new `copy.deepcopy`)
  - Falls back to JSON round-trip when deepcopy fails
- Fixed missing `wantedinfo_parser.py` causing JSON export crash
- Fixed `_find_skeleton_path` matching wrong skeleton (Golden Star matched Blackstar's skeleton due to fuzzy token matching)
- Fixed `_deploy_mount_overlays` failing because `parse_all_entries` uses field name `'name'` not `'internal_name'`

### New Files
- `rider_bone_injector.py` — standalone tool for injecting rider bones into any .pab skeleton
- `wantedinfo_parser.py` — copied from CrimsonSaveEditorGUI (was missing)

### Documentation
- `ResearchFolder/SKELETON_RIDING_BONE_RESEARCH.md` — full PAB format spec, rider bone injection, deployment rules
- `ResearchFolder/APPEARANCE_SCALE_OVERRIDE.md` — how to resize any creature via appearance XML
- `ResearchFolder/EQUIP_SYSTEM_DEEP_DIVE.md` — full equip system RE: 3 gates, character tribe mapping, slot categories
- `TODO_CROSS_CHARACTER_EQUIP_PROGRESS.md` — milestone tracker for cross-character equipment
