# Handover: Next Session Tasks (after v1.0.4)

## Priority 1: Save Editor Updates (CrimsonSaveEditorGUI)

### 1a. Custom key support in Inventory tab swap
Same as the repurchase tab fix — add "Or enter custom key:" QSpinBox to the inventory
item swap dialog so users can type 999001+ directly.

File: `CrimsonSaveEditorGUI/gui.py`
Pattern: Search for the inventory swap function (similar to `_swap_repurch_item`)

### 1b. Version bump to 1.0.2
File: `CrimsonSaveEditorGUI/editor_version_standalone.json` or equivalent
Update APP_VERSION / internal version.

### 1c. "Open Game Mods" button in Save Editor
- Big button near the top tab bar
- Checks if CrimsonGameMods exe exists in the same folder as the save editor exe
- If found: launches it (subprocess or os.startfile)
- If not found: opens the GitHub releases page in browser for download
- Should check for `CrimsonGameMods.exe` or `CrimsonGameMods/` folder next to the save editor

### 1d. "Open Save Editor" button in Game Mods
- Same concept in reverse
- In CrimsonGameMods main_window.py, add button near tabs
- Checks for CrimsonSaveEditor.exe in same folder
- If found: launches it
- If not found: opens release page

## Priority 2: Item Creator Improvements

### 2a. Donor quality warning
When user selects a donor item with only 1 enchant level, show a warning:
"This item has only 1 enchant level — it may show as damaged in-game.
Use a multi-level item (10+ enchant levels) as donor for best results."

### 2b. Damaged item root cause
The "damaged" state comes from using quest/story items as donors.
These items have:
- Only 1 enchant level (vs 11 for real gear)
- No sockets (use_socket=0)
- No sharpness (max_sharpness=0)
- drop_enchant_level=0

Real wearable gear has 11 enchant levels, 3 sockets, sharpness 40+.
Example good donor: Samuel_PlateArmor_Armor (key=1000057)

## Priority 3: Damaged Item Investigation

The "damaged" state on custom items happens when the DONOR is a quest/story item.
Quest items (like Old_Kliff_PlateArmor_Armor key=1002366) have:
- Only 1 enchant level (real gear has 11)
- No sockets (use_socket=0)
- No sharpness (max_sharpness=0)
- drop_enchant_level=0

Real wearable gear (like Samuel_PlateArmor_Armor key=1000057) has:
- 11 enchant levels (+0 through +10)
- 3 sockets with socket items
- Sharpness 40
- drop_enchant_level=3

**Fix options:**
a) Add donor quality warning when <2 enchant levels
b) Auto-suggest a better donor of the same equip type
c) Let user pick "use as template but copy enchant structure from X"

## Priority 4: Item Creator Enhancements

### Expose ALL 105 fields
Currently exposing: Identity (8 fields), Stats (per level), Skills, Buffs, Gimmick, Sockets, Sharpness
Still missing as editable:
- Economy (price_list, repair costs)
- Restrictions (cooltime, sealable lists, hackable groups)  
- UI/Display (icon paths, inspect data)
- Prefab/tribe (equip slots, tribe_gender_list)
- Drop default data (socket items, socket materials)
- Multi change info list (14 entries on real gear)
- Item group info list

### Gimmick name lookup
Add searchable dropdown for gimmick_info IDs like skills/buffs have.
Need to build gimmick name database from game data.

## Session Summary (2026-04-17)

### Built This Session:
1. **SkillTree tab** — parser + group info + _characterInfo discovery + preset buttons
2. **Export buttons** — hidden by default, shown in dev mode with disclaimer
3. **Item Creator** — full dialog with 6 tabs (Identity, Stats, Skills, Buffs, Gimmick, Raw)
4. **Clone engine** — item_creator.py with echo key patching
5. **Paloc patching** — localization overlay for custom item names
6. **Two deploy modes** — "Swap to Vendor" (key swap) + "Apply to Game" (new item)
7. **Save/Load config** — shareable item configurations
8. **Custom key in Repurchase** — QSpinBox for typing any key
9. **Benreuveni credit** — tooltip + visible label

### Key Findings:
- SkillTree _characterInfo field (tail[1:3]) is the character gate
- "Arm Combat" showed on Kliff = overlay system works for skilltree
- Custom items (999001+) work via save editor repurchase
- Store injection via storeinfo doesn't work for new keys (format issue)
- Paloc overlay with unencrypted data WORKS for custom names
- Quest/story items as donors = "damaged" state (1 enchant level)
- JMM mod manager uses group 0036, wipes all other overlays
- Pldada's mod format: JSON hex patches at entry-anchored offsets
