# TODO — Full cross-character equip for Oongka-class axes

## Status
Not fixed. Universal Proficiency covers ~95% of weapons (swords, rapiers, blasters,
cannons, spears, hammers, muskets — the hand-held neutral-rig items). Oongka-specific
axes (e.g. key 210080 Big_Horn_Tiger_OneHandAxe) still cannot be equipped by Kliff
even though both known gates are open.

## What we verified works
- `equipslotinfo.pabgb` has `0x9AA51C79` (OneHandAxe class hash) in Kliff's slot 0
  (it was there in vanilla — she never needed this hash added).
- Deployed `0058/iteminfo.pabgb` for the Silverwolf Axe has Kliff's tribe_gender
  (`0xFC66D914` / 4234598676) present in both prefab_data_list entries after
  Universal Proficiency's union pass.

## What we observed that's interesting
- **v5 (clear tribe_gender)**: Kliff COULD equip the axe. Clearing the two
  original tribes `[2278589063, 335227758]` made it work.
- **v5 crashed the game anyway** on `Batz_OneHandDagger` — but Batz had
  `tribe_gender_list=[]` in vanilla and our `if tg:` skipped empty lists,
  so we never touched Batz. Yet the game still blamed Batz.
  - Implication: universal proficiency's equipslotinfo edits may pull
    additional items into validation by adding them to NPC template records.
    Character 2 (player_4) may inherit from an NPC template we modified.
- **Union approach**: Kliff's tribe is now present on axes, but game silently
  refuses equip. Game doesn't crash or log an error.

## The remaining gate (theory — not verified)
Skeleton / rig compatibility at the asset level:
- Axe prefabs reference meshes built for Oongka's skeleton.
- Runtime `attach_weapon_to_hand` logic checks rig compat and silently fails
  for Kliff, even after item-level + slot-level filters pass.

These prefabs live in PAZ group `0009` (`character/appearance/...`) as `.pab`
asset bundles. No parser exists for them yet.

## What v5 might have hit that we haven't
v5's clear of `[2278589063, 335227758]` produced an empty list. Empty list
semantics may be "bypass rig check" rather than "any tribe". That would
explain why v5 worked even though the asset-level gate should still be
there. Worth testing: does a single-item targeted empty-list patch (only
on axes, leave everything else alone) reproduce v5's success without
crashing the game?

## Concrete next steps if revisited
1. Surgical test: make Silverwolf Axe's tribe_gender_list empty while leaving
   all other items untouched. Verify Kliff can equip AND game loads.
2. If (1) works: build a "targeted axe unlock" mode that clears tribe_gender
   only on items Kliff can't otherwise equip.
3. If (1) crashes: the rig check is real and we'd need a `.pab` parser in
   group 0009 to rebind skeletons — much bigger project.
4. Alternative: IDA trace of the actual equip-decision function (vtable method,
   not by name) via breakpoint-level RE when game is running.

---

## Sibling TODO — MercenaryInfo editor + Character unlock gates

### MercenaryInfo.pabgb — Pet / Summon Cap Editor (READY TO BUILD)

**Confirmed from community mod `Pet_Owned_Cap_999` by Codex + `Pet Power Overhaul`:**
- File is 297 bytes, 11 records — each record is a "summonable category" cap config.
- Each entry is ~27 bytes with layout: `key(u32) + flag(u8) + active(u32) + max(u32) + limit(u32) + flags(8 bytes)`.

**Confirmed category mapping (entry #4 = Pets):**
- Entry 4 at record offset 81: active=3, max=30 — matches in-game pet counts.
- **File offset 91** = max owned pets (30 vanilla, Codex patched to 999).
- Other entries hold caps for mercenaries, summons, etc. — 11 total.

**Fields from IDA decompile (still valid):**
- `_maxLimitHireCount` / `_defaultLimitHireCount` / `_defaultLimitSummonCount`
- `_isSellable`, `_isControllable`, `_applyEquipItemStat`
- `_learningStageInfo`, `_learningPosition`, `_mainMercenaryPerTribe`

**Concrete feature to build — "Pet & Summon Caps" mini-editor:**
1. Parse mercenaryinfo as 11 entries × 27 bytes (fixed-size records — unlike EquipInfoData).
2. Show entries with friendly labels (Pet, Mercenary, …) and editable spinboxes for active/max.
3. Bundle writes into an ItemBuffs-style overlay (0061 or shared with 0058).
4. Include preset shortcuts: "999 pets", "100 active pets", "All caps max".

**Related iteminfo offsets** (from Pet Power Overhaul):
- `AbyssGear_Companionship_I/II/III` rel_offset 8 → trust value (1/3/5 default)
- `AbyssGear_Companionship_Cap` rel_offset 4 → gear stack cap (10 default)
These would live in ItemBuffs tab as preset buff mods.

**Pets also live in character_catalog (via pet_catalog.json)** — 216 char_keys for 40 named breeds. Mesh Swap already uses this.

### Playable-character unlock gate (Oongka / Damian always playable)
Gate is NOT in any pabgb we control. Confirmed via IDA:
- `characterchange.pabgb` = menu labels / category grouping (Job_A/B/C, weapon types, gender lists).
- `CharacterChangeInfo` class has `_characterChangeFilter` but siblings (`_subCategoryIndex`, `_middleCategoryIndex`, `_groupAgeList`) show it's menu-organization metadata.
- `MissionInfo` has no character-lock field.
- `NotPlayableCharacter` UI string xrefs only to UI-rendering code.

Real gate lives in:
1. Save state — quest-completion flags (separate save-editor tool).
2. Cutscene/event triggers in `gameplaytrigger.pabgb` / event handlers — hardcoded story-beat forcing.
3. Runtime character manager state (in-memory, not in a data file).

Only fix that would work: **runtime DLL hook** of the "can switch to char X" function to always return true. Same class as the PAAC animation swap — asi/plugin territory, not data-file modding. Would need a new project.

---

## Files touched by Universal Proficiency
- `gui/tabs/buffs_v319.py` — `_eb_universal_proficiency` (union logic)
- `equipslotinfo_parser.py` — parse/serialize
- `imbue.py` — (unrelated, imbue system)

---

## Sibling TODO — dye-slot asset gate for "Make All Dyeable"

Same class of problem. `Make All Equipment Dyeable` correctly sets
`is_dyeable=1` and `is_editable_grime=1` in iteminfo. Verified in deployed
overlay. But the game UI still says "cannot be dyed" for items like
`Optionary_Demeniss_Spy_Cloak` (key 1000324, the Disguise Cloak).

### Proven: not an iteminfo field
Exhaustive comparison between a dyeable vanilla item (`Taorant_Fabric_Armor`)
and `Optionary_Demeniss_Spy_Cloak`:
- `is_dyeable`, `is_editable_grime`: both now 1 after our flip
- `material_key`, `material_match_info`: identical (947415234)
- No other field in iteminfo correlates with dyeability
- Vanilla has 530 dyeable items total; none of their prefab_name hashes
  match keys in `partprefabdyeslotinfo.pabgb` — so that table is keyed
  differently than we assumed (not per-item prefab)

### Actual gate
`prefab_data_list[0].prefab_names[0]` points to a `.pab` appearance asset
in PAZ group `0009/character/appearance/...`. The game checks whether
that mesh has a dye-enabled material slot; if not, UI refuses to open
the dye dialog. Taorant's prefab `2954220013` has the slot; Disguise
Cloak's `2448393756` doesn't.

### Concrete next steps if revisited
1. Parse `.pab` appearance files to find the dye-material bit.
2. Option A: patch dye bit in the .pab. Changes visual slot list.
3. Option B: swap `prefab_names[0]` to a dyeable prefab (visual change).
4. IDA: find the function that returns "can dye this item" and trace
   what it reads — confirm whether the .pab check is really the gate or
   if there's a third table we missed.
