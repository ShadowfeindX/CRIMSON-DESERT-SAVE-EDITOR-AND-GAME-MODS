# Crimson Game Mods — v1.0.1

A standalone Windows PAZ/pabgb modding toolkit for Crimson Desert. Edits the game's data tables directly (iteminfo, skill, equipslotinfo, storeinfo, fieldinfo, spawninfo, dropsetinfo) and deploys overlays that don't touch vanilla files. Works alongside CDUMM/DMM; exports to their formats too.

**Download:** `CrimsonGameMods.exe` (~73 MB, single exe, no installer). Drop anywhere. First launch asks for your Crimson Desert install path.

---

## What's new in v1.0.1

- **Universal Proficiency** — one-click: every character can equip every weapon and armor type.
- **Import Mod Folder** — reverse-engineer any `.pabgb` mod folder back into an editable config. See exactly what other mods do, tweak, re-export.
- **Enable All QoL** — one-click: no cooldown + max charges + 999999 stacks + infinity durability.
- **Searchable Imbue dropdown** — find any Equip_Passive skill by key, name, or internal name; three-tier markers show which passives actually render a visual vs stat-only.
- **Fixed bulk imbue corruption** — was dropping 13+ class hashes when rebuilding skill.pabgb.
- **Import/Load auto-detects QoL flags** — Max Stacks and Infinity Durability checkboxes now tick themselves if an imported mod had them.
- **Apply to Game is public** — no longer dev-mode gated.
- **Auto-version splash** + misc tooltip/UX cleanups.

---

## Full feature list

### ItemBuffs tab (weapons, armor, accessories)

**Top toolbar**
- **Extract** — parse the game's iteminfo.pabgb (6,000+ items) via Potter's Rust parser. Entry point for everything else in this tab.
- **Search by Description** — free-text search across item descriptions (English localization included).
- **JSON Edit** — raw JSON editor for a single item's full iteminfo record.
- **Transmog / Visual Swap** — swap one item's mesh for another's (looks like X, stats of Y).
- **Item Diff** — byte-level diff between two items in the table.
- **Inspect Item** — full field dump for the selected item.
- **My Inventory** — filter the table to items in your current save.
- **Icons** — toggle icon rendering in the table (faster scroll without icons).
- **Preview Item** — preview the modded item's final tooltip.

**Stats / effects panel**
- **Apply Preset** — apply a named stat preset (e.g. "Max God Mode weapon", "Bismuth spear", dev-ring presets).
- **Suggest from Cluster** — auto-suggest stats based on similar items.
- **Add / Remove Stat** — add or remove individual stat fields on an item.
- **Apply to Stat** — edit a selected stat value.
- **Reset** — revert all edits on the selected item.

**Passives / skills**
- **Add Passive** — add an Equip_Passive skill (searchable dropdown with 176 skills).
- **Remove** — remove a passive from the selected item.
- **God Mode** — inject full God-Mode stat preset (the dev-debug ring layout).
- **Copy Effect** — copy the full effect set from one item to another.
- **Shadow Boots / Lightning Weapon / Great Thief** — one-click famous presets.
- **Apply Gimmick** — attach a VFX gimmick (searchable combo of 12,000+ gimmicks).
- **Extend Sockets / All → 5 Sockets** — raise socket count on items that support sockets.

**Equip buffs / enchant-level buffs**
- **Add Buff** — add an equip_buff at a chosen enchant level.
- **Remove Buff** — remove one.
- **Copy Selected Item's Buffs → All Weapons** — broadcast the currently-selected item's equip_buffs onto every weapon (DMM-clone; merges dupes, higher level wins).

**Utility row**
- **No Cooldown (All Items)** — cooltime → 1 on everything.
- **Max Charges (All Items)** — set max_charged_useable_count to chosen value on charged items.
- **Max Stacks checkbox + spinner** — tick to include stack-size edits in export (default 9999, raise to 999999 if wanted).
- **Infinity Durability** — when checked, every export sets max_endurance=65535 + is_destroy_when_broken=0.
- **Enable All QoL** ✨ — one click: all of the above with sensible defaults (999999 stacks, 99 charges, 65535 durability, cooltime=1). Auto-ticks the checkboxes too.

**Bulk actions row**
- **Copy Selected Item's Buffs → All Weapons** (red) — see above.
- **Imbue All Weapons** (purple) — apply the selected Imbue passive (Lightning/Fire/Ice/Bismuth/etc) to every weapon. Single-pass batched editor; safe for large class-hash lists.
- **Make All Equipment Dyeable** (blue) — flip `is_dyeable + is_editable_grime` on every equipment item. (Items whose mesh doesn't author a dye material slot still won't render dye changes — asset-level gate.)
- **Universal Proficiency** ✨ (orange) — removes the character→weapon filter. Two things happen:
  1. `equipslotinfo.pabgb` — every character's equip slots get every weapon hash that canonically belongs in that slot type (melee→melee, ranged→ranged, armor→armor).
  2. `iteminfo.pabgb` — player-tribe hashes are unioned into every item's `tribe_gender_list` (originals preserved — empty lists are left alone so NPC defaults still work).
  - Animation caveat: weapons without a character's native animation set (e.g. muskets on Kliff) will equip but won't fire/reload correctly.

**Imbue row**
- **Imbue dropdown** — searchable; three-tier markers:
  - 🎆 **Visual** — vanilla item uses this passive with a bone-attached gimmick → real VFX renders
  - ⚙ **Functional** — gimmick exists but socket is empty → invisible (stealth, immunity, faction filters)
  - · **Stat-only** — no vanilla gimmick reference → skill filter edit only, no visual
- **Add to Selected** — apply the imbue to one item (adds passive + gimmick + docking + cooltime config + skill.pabgb filter patch).
- **Coverage Report** — show exactly how many weapons currently allow this imbue, how many would be unlocked, per-weapon-class breakdown.

**Bottom bar**
- **Export JSON Patch** — value-only edits (cooldowns, stats at existing offsets). Pldada/DMM format.
- **Export as Mod** — full PAZ mod folder (iteminfo.pabgb + modinfo.json). Structural edits (new buffs, passives, god mode).
- **Export as CDUMM Mod** — proper 0036/0.paz + 0.pamt + meta/0.papgt. Direct import into CDUMM.
- **Apply to Game** — deploy a PAZ overlay directly (no mod manager required). Requires admin. Restart game after.
- **Import Community JSON** — import a Pldada/DMM-format byte patch.
- **Sync Buff Names** — refresh buff name database.
- **Save Config / Load Config** — save current edits to JSON; load later to re-apply on fresh vanilla data.
- **Import Mod Folder** ✨ — reverse-engineer any CDUMM/PAZ mod folder back into an editable config. Auto-ticks Max Stacks / Infinity Durability if the mod used them.
- **Restore Original** — remove the ItemBuffs PAZ overlay + PAPGT entry (preserves other overlays).
- **Reset to Vanilla PAPGT** — nuclear recovery if the game won't launch.

---

### FieldEdit tab (world rules)
- **Load FieldInfo** — parse the field/region data.
- **Enable Mounts Everywhere** — remove the "can't summon here" checks across regions.
- **Make All NPCs Killable** — flip killable flags on faction NPCs.
- **Invincible Mounts** — godmode your mounts.
- **Mesh Swap** — character appearance swap (swap Kliff's model to Damian's, etc.).
- **Wipe Ally Lists** — clear faction ally lists (makes more NPCs attack each other).
- **Intruder Flag (slot 2)** — flip slot-2 flag.
- **Apply to Game / Export as Mod / Export as CDUMM Mod / Export as JSON / Export Mesh Swap as JSON Mod / Restore** — same deployment options as ItemBuffs.

---

### Stores tab (vendors / shops)
- **Load Store Data** — parse storeinfo.pabgb (254 stores, 9 with populated item lists).
- **Swap Selected** — swap one store's inventory for another's.
- **Apply Limit / Set ALL Limits** — edit per-item or global stock limits.
- **Import/Export JSON Patch** — trade configs.
- **Apply to Game / Restore** — deploy.

---

### DropSets tab (loot tables)
- **Load DropSets** — parse dropsetinfo.pabgb.
- **+Add / Remove / Swap** — edit loot table entries.
- **Add Pack to Selected** — bulk-add a pack of items.
- **5x Drop Rates / Max Drop Rates / Zero Cooldowns** — one-click bulk buffs.
- **Apply to Chest Tiers / Apply to Selected** — targeted application.
- **Save/Load Config, Apply to Game, Export as Mod, Restore**.

---

### SpawnEdit tab (NPC spawn density)
- **Load Spawn Data** — parse the 7 spawn pabgb tables.
- **Increase ALL Spawns / Increase ALL Life** — world-wide density/HP boost.
- **Halve Respawn Timers / Halve Sub Times** — faster respawns.
- **x Camp Max / x Camp Min / x World Rates / x Sub-Slots** — multiplier presets.
- **Apply to Game / Export Mod / Restore Vanilla / Reset Edits**.

---

### Game Data tab (raw PABGB editor)
- **Load** — open any .pabgb/.pabgh pair.
- **Patch Bytes** — hex-level patching.
- **Export Record** — dump an individual record.
- **Apply to Game / Restore** — deploy.

---

### Database / Items tabs
- **Scan PAZ / Load File** — database tooling.
- **Refresh / Restore Selected / Open Backup Folder / Delete Selected** — backup manager.

---

## Notes & limitations

- **Skeleton/rig binding is asset-level.** The engine's equip-decision path has a third gate (beyond equipslotinfo and iteminfo.tribe_gender) that checks whether the weapon's `.pab` mesh binds cleanly to the character's skeleton. Oongka-specific axes and character-tied meshes still refuse to equip on Kliff even after Universal Proficiency. Not fixable from data — requires editing the `.pab` appearance asset itself.
- **Dye-material is asset-level too.** `Make All Equipment Dyeable` flips the flag correctly but the game's dye UI checks whether the mesh has a dye-enabled material slot. Items whose mesh wasn't authored with a dye channel will still refuse to open the dye dialog. Not fixable from iteminfo.
- **Muskets on non-native characters equip but don't animate.** The animation graph is per-character; unlocking the slot doesn't give Kliff Damian's fire/reload animations.
- **Saves aren't touched.** This tool edits game data (PAZ overlays), not your save file. Your existing items keep their current state — new drops use the modded values.
- **Admin required for Apply to Game.** The game is in Program Files; writing to the overlay folder needs elevation. Mod export paths don't need admin.
- **Auto-updater** — checks the manifest on each launch. In-app "Check for Updates" pulls the latest exe.

## Credits

Uses Potter's crimson-rs for PAZ packing and iteminfo parse/serialize.
