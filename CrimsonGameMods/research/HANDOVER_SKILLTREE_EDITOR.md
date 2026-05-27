# Handover: Build SkillTree Editor Tab

## Context
CrimsonGameMods v1.0.3 was just released. This session we built:
- Universal Proficiency v2 (cross-character equip — working)
- Rider bone injection (mount riding — working)
- PAB skeleton parser (fully decoded)
- Equip system deep dive (3 gates mapped, 12 player tribe hashes identified)

The **next feature** is a SkillTree Editor tab for cross-character skill/moveset swapping via `skilltreeinfo.pabgb`. Community dev crewny23 proved skill swaps work by patching root package IDs.

## What to Build

### 1. Parser: `skilltreeinfo_parser.py`

**File**: `skilltreeinfo.pabgb` (27,294 bytes) + `skilltreeinfo.pabgh` (250 bytes) in PAZ group 0008.

**pabgh format**:
```
u16 count (31 entries)
per entry: u32 key + u32 offset (8 bytes)
```

**pabgb record format** (from IDA decompile at `0x141066AF0`):
```
u32 key
u32 name_length  
char[N] name (ASCII)
... fields (see IDA decompile below)
```

Record sizes calculated by offset deltas. Last record ends at file end.

**Functions needed**:
- `parse_pabgh(data) -> list[(key, offset)]`
- `parse_record(data, offset, size) -> dict` 
- `parse_all(pabgh_data, pabgb_data) -> list[dict]`
- `serialize_all(records) -> (new_pabgh, new_pabgb)`

For the MVP, we don't need to parse every field — just enough to:
1. Read record key + name
2. Find and replace root package ID values (u32) at known offsets
3. Round-trip serialize without corruption

### 2. Tab: `gui/tabs/skill_tree.py`

**UI**:
- Extract button (loads from PAZ group 0008)
- Table with columns: Key, Name, Character, Type, Root Package
- For player characters (keys 50/51/52): editable root package dropdown
- Presets dropdown: "Kliff uses Damiane melee", "All characters share all skills"
- Apply to Game button → deploys to group 0063
- Restore button → removes 0063

**Follow existing patterns** from `gui/tabs/field_edit.py` and `gui/tabs/buffs_v319.py`:
- Use `crimson_rs.extract_file()` for PAZ extraction
- Use `PackGroupBuilder(NONE)` for overlay creation
- pabgb + pabgh MUST be in the SAME overlay group (paired)
- Read CURRENT papgt (not vanilla) to preserve other overlays
- One pabgb per overlay group rule

### 3. Register in `gui/main_window.py`

Add to the Game Mods tab group alongside Field Edits, ItemBuffs, etc.

## Key Data

### All 31 Entries
```
Player Weapon Trees:
  1: WeaponSkill_Kliff_Sword (1095B) — has root melee package 0x32C9
  2: WeaponSkill_Kliff_Shield (270B)
  3: WeaponSkill_Kliff_Bow (588B)
  4: WeaponSkill_Kliff_Spear (104B)
  8: MaterialArtSkill_Kliff (860B)
  9: SpecialSkill_Kliff (759B)
  10: SubSkill_Kliff (1148B)
  50: Skill_Kliff (5201B) — MAIN tree, has root melee ref at rel 0x4D and 0x1441
  51: Skill_Oongka (4319B) — MAIN tree
  11: WeaponSkill_Oongka_TwoHandAxe (191B)
  12: WeaponSkill_Oongka_HandCannon (110B)
  13: WeaponSkill_Oongka_Axe (103B)
  18: MaterialArtSkill_Oongka (266B)
  20: SubSkill_Oongka (96B)
  52: Skill_Damian (3743B) — MAIN tree, has root melee 0x332D
  21: WeaponSkill_Damian_Rapier (106B)
  22: WeaponSkill_Damian_Pistol (106B)
  23: WeaponSkill_Damian_TwoHandSword (112B)
  28: MaterialArtSkill_Damian (105B)
  30: SubSkill_Damian (97B)

NPC:
  31/38/40/53: Yahn (Dagger)

Factions:
  101-106: PororinVillage, ScholarStone, Urdavah, Gorthak, Delesyian, Dewhaven

Craft:
  201: CraftTree_Kuku_Pot
```

### Root Package IDs
- **Kliff melee**: 0x32C9 (13001) — at abs offsets 0x0057, 0x1325, 0x2719 in pabgb
- **Damiane melee**: 0x332D (13101) — at abs offsets 0x4184, 0x4995

### crewny23's Proven Swap
File: `root_package_test (1).json`
- Replaces 0x1325: 0x32C9 → 0x332D (Kliff ref A → Damiane)
- Replaces 0x274A: 0x32C9 → 0x332D (Kliff ref B → Damiane)
- Result: Kliff uses Damiane's melee moveset

## Critical Rules (from this session)
- pabgb + pabgh MUST be in the SAME overlay group
- NEVER bundle unrelated pabgb files in one group
- Read CURRENT papgt when deploying (not vanilla backup) — see `_buff_apply_to_game` PAPGT fix
- Use `PackGroupBuilder(Compression.NONE, Crypto.NONE)`
- `deepcopy` on crimson_rs objects may fail on Python 3.14 — use JSON round-trip fallback

## IDA Decompile Reference
SkillTreeInfo reader at `0x141066AF0`:
- Reads: key(u32), localization, flag(u8), 3 small fields(u16), 2 u32s, a hash read, 
  a skill tree node structure, array of 44-byte child nodes, then 3 more fields
- Error strings at 0x14498A5D0-0x14498AB58 (SkillTreeInfo variants)
- Manager class: `SkillTreeInfoManager` at 0x145B57840

## Files to Reference
- `ResearchFolder/SKILLTREEINFO_STRUCTURE.md` — full format spec
- `ResearchFolder/EQUIP_SYSTEM_DEEP_DIVE.md` — equip gates context
- `ResearchFolder/COMMUNITY_EQUIP_RE_NOTES.md` — crewny23 findings
- `gui/tabs/buffs_v319.py` — reference for Apply to Game pattern
- `gui/tabs/field_edit.py` — reference for tab structure
- `equipslotinfo_parser.py` — reference for pabgh+pabgb parser pattern
