# CrimsonGameMods v1.0.4 — Pre-Release

## New Features

### Custom Item Creator
- **Create Item** button in ItemBuffs tab opens a full visual item editor
- Pick any of 6,000+ game items as a donor template
- Edit all stats per enchant level (+0 through +10) with live preview
- Add/remove passive skills with searchable dropdown (all known skills)
- Add/remove equip buffs with searchable dropdown (all known buffs)
- Edit gimmick info, socket count, sharpness/refinement
- **Two deploy modes**:
  - **Swap to Vendor** — replaces an existing vendor item with your custom stats. Visit the vendor in-game and buy it. Proven working.
  - **Apply to Game (New Item)** — creates a brand new item key (999001+) with custom name via localization patching. Use Save Editor Repurchase tab to acquire.
- Save/Load item configs as shareable JSON files
- Live preview card shows stats, skills, buffs, tier with game-style formatting
- Credit: Item cloning based on [Benreuveni/crimson-desert-add-item](https://github.com/Benreuveni/crimson-desert-add-item)

### SkillTree Editor Tab
- New tab in Game Mods for cross-character skill tree swapping
- Extracts skilltreeinfo + skilltreegroupinfo from live game
- Shows all 31 skill trees with localized names
- Per-character preset buttons (Kliff/Damiane/Oongka) with hover tooltips
- Discovered `_characterInfo` gate field — patches character binding on trees
- Group redirect system for loading another character's skill tree
- Root package swap for animation/moveset changes

### Export Button Gating
- All "Export as Mod / CDUMM / JSON" buttons now hidden by default
- Visible only in Advanced/Dev mode with disclaimer popup
- Apply to Game remains the primary supported deployment method
- Import JSON/configs still fully supported

## Bug Fixes
- Fixed PAPGT management to preserve other overlay groups when applying
- Added custom key input to Save Editor Repurchase tab swap dialog

## Notes
- This is a pre-release. The custom item creator is functional but some item fields are not yet editable in the UI.
- Using quest/story items as donors may result in "damaged" items — use endgame gear with 10+ enchant levels as donors for best results.
- SkillTree cross-character swap is experimental — "Arm Combat" confirmed showing on Kliff, weapon trees need further testing.
