# Item Editor — Technical Memo

> Last updated: 2026-06-10
> Scope: `CrimsonGameMods/gui/tabs/item_editor/` and all subdirectories

---

## 1. High-Level Architecture

The Item Editor is a **PySide6 (Qt6) GUI** for viewing, searching, and modifying
item data from the game *Crimson Desert*. It lives inside the larger
`CrimsonGameMods` application and is one of several tabs in the main window.

```
ItemEditorTab  (tab.py — top-level QWidget, owns signals & extraction logic)
 └── ItemEditorLayout  (layout.py — QVBoxLayout)
      ├── ActionBar       (action_bar.py — Extract/Import/Export/Apply/Reset/Undo)
      ├── SearchBar       (search_bar.py — text search + category/favorites/inventory filters)
      └── HBoxLayout (main content area — 3 side-by-side panels)
           ├── ItemTable            (items_table/ — left: all items list)
           ├── ItemDetailsTable     (item_details_table/ — center: editable fields of selected item)
           └── EditorControls       (editor_controls/ — right: tool buttons that open sub-windows)
```

---

## 2. Directory Map

```
item_editor/
├── tab.py                       # ItemEditorTab — root widget, owns signals + extraction
├── layout.py                    # ItemEditorLayout — wires together action bar, search, 3 panels
├── signals.py                   # SIGNALS / SLOTS global registries (benedict-based)
├── helpers.py                   # Shared data classes, config, utilities
├── dmm_types.py                 # TypedDict definitions for every iteminfo sub-struct
├── action_bar.py                # ActionBar widget (Extract, Import, Export, Apply, Reset, Undo)
├── search_bar.py                # SearchBar widget (text search, category filter, favorites, etc.)
├── editor_config.json           # Persistent config (which collapsible sections are open)
│
├── items_table/                 # LEFT PANEL — master list of all items
│   ├── table.py                 #   ItemTable (QFrame) — orchestrator, wires model/proxy/view
│   ├── model.py                 #   ItemTableModel (QAbstractTableModel) — 3 columns: Key, Name, Tier
│   ├── proxy.py                 #   ItemTableModelProxy (QSortFilterProxyModel) — text/tier filtering + sorting
│   ├── view.py                  #   ItemEditorTableView (QTableView) — visual config, context menu hook
│   └── context_menu.py          #   ItemTableContextMenu — right-click menu (currently stub/placeholder)
│
├── item_details_table/          # CENTER PANEL — editable fields of the currently selected item
│   ├── table.py                 #   ItemDetailsTable (QFrame) — orchestrator
│   ├── model.py                 #   DetailsTableModel — 2 columns: Key, Details (JSON-serialized)
│   ├── proxy.py                 #   DetailsTableProxy — minimal sort proxy
│   ├── view.py                  #   DetailsTableView — visual config, context menu hook
│   ├── context_menu.py          #   DetailsTableContextMenu — shows history/registry diff popup
│   └── display.py               #   Unused/legacy helpers
│
└── editor_controls/             # RIGHT PANEL — tool buttons + sub-windows  ← PRIMARY WORK AREA
    ├── __init__.py              #   EditorControls (QFrame) — main widget with 3 collapsible grids
    ├── window_template.py       #   Window (QWidget) — base template for sub-windows
    ├── json_window.py           #   JSONWindow — raw JSON viewer/editor (QTextEdit, currently stub)
    ├── history_window.py        #   HistoryWindow — read-only viewer for the global history registry
    ├── presets.py               #   Presets — data class with Standard/Dev/Special/Custom preset dicts
    ├── presets_window.py        #   PresetsWindow — grid UI for one-click preset application
    │
    └── passives/                #   PASSIVE SKILL EDITOR sub-window
        ├── window.py            #     PassiveWindow — main passives editor window
        ├── action_bar.py        #     ActionBar — search, add, remove, favorites toggle
        ├── bottom_bar.py        #     BottomBar — apply to items, remove from items, clear
        ├── indexed_table.py     #     IndexedPassivesTable — all known skills from catalog
        ├── selected_table.py    #     SelectedPassivesTable — passives on currently selected items
        └── target_table.py      #     TargetPassivesTable — staging area for passives to apply
```

---

## 3. Signal System

Signals are the backbone of inter-component communication. Defined in `signals.py`
using a `benedict` (dict with attribute access) singleton:

```python
SIGNALS: _Signals = benedict(keyattr_dynamic=True)
```

### Key Signals

| Signal                               | Type                              | Emitter              | Consumer(s)                          |
|--------------------------------------|-----------------------------------|----------------------|--------------------------------------|
| `SIGNALS.s_status_message`           | `Signal(str, int\|None)`          | Various              | Main window status bar               |
| `SIGNALS.s_iteminfo_extracted`       | `Signal(ItemEditorInfo)`          | `ItemEditorTab`      | `ItemTable.load()`                   |
| `SIGNALS.s_item_selected`            | `Signal(int)`                     | `ItemTable`          | `ItemDetailsTable`, `EditorControls`, `PassiveWindow` |
| `SIGNALS.s_items_selected`           | `Signal(list[int])`               | `ItemTable`          | `PassiveWindow` (multi-select)       |
| `SIGNALS.s_history_entry_added`      | `Signal(HistoryEntry)`            | Various              | `ItemEditorTab.log_history()`        |
| `SIGNALS.ActionBar.s_extract`        | `Signal(str)`                     | `ActionBar`          | `ItemEditorTab._extract()`           |
| `SIGNALS.SearchBar.s_search`         | `Signal(str)`                     | `SearchBar`          | `ItemTable.search()`                 |
| `SIGNALS.SearchBar.s_filter`         | `Signal(str)`                     | `SearchBar`          | (wired but consumer logic pending)   |
| `SIGNALS.SearchBar.s_toggle_icons`   | `Signal()`                        | `SearchBar`          | (wired but consumer logic pending)   |

### Signal Readiness Pattern

Each widget that owns signals follows a `_ready_signals()` method that wires
its local `Signal` instances onto the global `SIGNALS` benedict, e.g.:

```python
def _ready_signals(self):
    SIGNALS.s_item_selected = self.s_item_selected
    SIGNALS.s_items_selected = self.s_items_selected
```

The root `ItemEditorTab` calls `_ready_signals()` first in `__init__()` before
`_build_ui()` so children can connect during construction.

---

## 4. Data Model

### 4.1 Item Data (dmm_types.py)

`ItemInfo` is a **TypedDict** with ~100+ fields representing a single game item.
Key fields include:

- `key` (u32) — unique item ID
- `string_key` — internal name (e.g. `"Pyeonjeon_Arrow"`)
- `item_name` — `LocalizableString` with category/index/default
- `equip_passive_skill_list` — `list[PassiveSkillLevel]` (skill + level)
- `enchant_data_list` — `list[EnchantData]` (per-level stats + buffs)
- `drop_default_data` — `DropDefaultData` (sockets, enchant level, sub-items)
- `docking_child_data` — `DockingChildData | None` (gimmick attachment)
- `cooltime` — `CoolTimeData` (a/b/c slot cooldowns, ADDED PROPERTY)
- `price_list`, `gimmick_info`, `item_tier`, `max_stack_count`, etc.

Helper types: `PassiveSkillLevel`, `EnchantStatData`, `EquipmentBuff`,
`LocalizableString`, `DockingChildData`, `DropDefaultData`, `SealableItemInfo`, etc.

### 4.2 ItemEditorInfo & ItemEditorInfoDetails (helpers.py)

**`ItemEditorInfo`** — Wrapper around `list[ItemInfo]`:
- Constructed after extraction (`_extract()` in tab.py)
- Sets `ItemEditorInfoDetails._reference` to the raw data list
- `.details(idx)` creates a singleton proxy for the item at index `idx`

**`ItemEditorInfoDetails`** — Singleton proxy for viewing/editing a single item:
- Uses `__new__` to enforce singleton (only one instance at a time)
- `.data` — the raw `ItemInfo` dict
- `.editable()` — generator of `(key, value)` for fields in `EDITABLE_ENTRIES`
- `.passives(new, log)` — get/set `equip_passive_skill_list` with optional history logging
- `.EDITABLE_ENTRIES` — set of 15 field names that can be edited:
  `cooltime`, `docking_child_data`, `drop_default_data`, `enchant_data_list`,
  `equip_passive_skill_list`, `gimmick_info`, `gimmick_visual_prefab_data_list`,
  `is_dyeable`, `item_charge_type`, `item_tier`, `max_charged_useable_count`,
  `max_endurance`, `max_stack_count`, `price_list`

### 4.3 History System

`HistoryEntry` records undo-able changes:
- `EntryType` enum: `PRESET`, `EDIT`, `REPLACE`, `BULK`
- `.entry_data` — arbitrary payload (old values, snapshots, etc.)
- `.description` — human-readable label
- `.undo()` — currently only stubs for `PRESET` and `BULK`

The history registry (`ItemEditorInfoDetails._history`) is a class-level list shared
by all detail proxies. It serves as a **global sequential log of all edits** across
all items. Its sole purpose is to support **rollback and replay** of changes. Entries
are not timestamped; insertion order alone is the meaningful data.

History entries are emitted via `SIGNALS.s_history_entry_added` and logged
in `ItemEditorTab.log_history()`.

### 4.4 Config (helpers.py)

`_Config` class wraps `editor_config.json` in the item_editor directory:
- Supports dict-like access (`CONFIG["key"]`)
- `.save()` commits to disk
- Used for collapsible section states (`itemeditor_standard`, etc.)
- Also stores `favorite_passives`, `game_install_path`, `custom_preset_ask`

### 4.5 safe_iv() Utility

The `dmm_parser` Rust extension returns some integers as nested dicts
(`{'a': int, 'b': int, 'c': int}`). `safe_iv()` safely extracts a plain int
from various formats.

---

## 5. EditorControls — Tool Buttons & Sub-Windows

This is the **primary extensibility point** — where new editor tools are added.

### 5.1 Layout (editor_controls/__init__.py)

`EditorControls` is a `QFrame` with three collapsible sections:

| Section           | Buttons                                     | Status          |
|-------------------|---------------------------------------------|-----------------|
| **Standard**      | Presets, Show Preview, Transmog, Custom Item, Bulk Options, Global Options | Presets ✅, others stub |
| **Advanced**      | Edit Passives, Edit Buffs, Edit Stats, Edit Drop Data, Edit Gimmick, Edit VFX | Passives ✅, others stub |
| **Dev**           | Edit JSON, View History, Dump ITEMINFO, Show Item Diff | JSON ✅ (viewer only), History ✅, others stub |

### 5.2 Window Registry Pattern

Sub-windows are opened via a **registry + factory**:

```python
WINDOW_REGISTRY = {
    "preset":  PresetsWindow,
    "passive": PassiveWindow,
    "json":    JSONWindow,
    "history": HistoryWindow,
}
```

`open_window(id)` looks up the class, checks if already open (re-focuses if so),
otherwise instantiates, hooks `destroyed` → cleanup, stores in `self._windows[id]`,
shows and centers. Windows are auto-cleaned from `_windows` on close via `gc.collect()`.

**To add a new editor tool:**
1. Create a new window class (extend `QWidget`, follow `window_template.py` pattern)
2. Register it in `WINDOW_REGISTRY` with a unique string key
3. Add a button in the appropriate `_build_*_grid()` method
4. Connect the button: `btn.clicked.connect(self._open_window("your_key"))`

### 5.3 Existing Sub-Windows

#### PresetsWindow (`presets_window.py` + `presets.py`)

`Presets` class holds four preset dictionaries:

- **Standard** — user-facing one-click presets:
  - `open_sockets` — 5 sockets with material costs
  - `max_enchant` — level 10 refine
  - `no_cooldown` — 1s cooldown, no recharge restriction
  - `max_charges` — 100 charges
  - `max_stacks` — 999999 stack size
  - `shadow_boots` — Potter's Shadow Boots (skills 7201+7055+7202, gimmick 1004431)
  - `lightning_weapon` — Potter's Lightning (skills 91101+91105+91104, gimmick 1001961)

- **Dev** — dev ring presets:
  - `immune`, `str_hp`, `def_hp`, `mp_stam`, `speed`, `all`
  - `elemental_weapon`, `jump_boots`

- **Special** — situational presets:
  - `god_mode` (empty), `great_thief`, `great_thief_all`, `crime_mask`

- **Custom** — loaded from `custom_presets.json` (user-editable)

Preset application flow:
1. User clicks button → `PresetsWindow.apply_std_preset()` → confirmation dialog
2. → `Presets.apply_std_preset()` → strips metadata keys, snapshots old values,
   creates `HistoryEntry(PRESET, ...)`, emits `s_history_entry_added`
3. **NOTE**: The actual mutation of item data is currently incomplete —
   `apply_std_preset()` records history but doesn't yet iterate over preset_data
   to modify `self._current_item` fields. This needs implementation.

#### PassiveWindow (`passives/window.py` + sub-files)

A full-featured passive skill editor with:

- **IndexedPassivesTable** — all skills from `data/passive_skill_catalog.json`
- **SelectedPassivesTable** — passives currently on selected items (merged, highest level wins)
- **TargetPassivesTable** — staging area ("passives to apply") with context menu (add to favorites, remove)
- **ActionBar** — favorites toggle, search, add/remove buttons
- **BottomBar** — apply to selected items, remove from selected items, clear target list

Application flow:
1. User selects items in ItemTable (multi-select supported)
2. `SIGNALS.s_items_selected` → `PassiveWindow._set_selected_items()`
3. User browses indexed table, adds skills → they appear in target table
4. User clicks "Apply Passives" → `apply_passives_to_items()` iterates selected items,
   calls `item.passives(new=..., log=True)` which mutates the data and logs history

#### JSONWindow (`json_window.py`)

Simple raw JSON viewer. On `s_item_selected`, dumps `details._data` as indented JSON
into a `QTextEdit`. Currently read-only (no save/apply button).

#### HistoryWindow (`editor_controls/history_window.py`)

Read-only viewer for the global history registry (`ItemEditorInfoDetails._history`).

- **Top bar** — entry count label + "Clear History" button
- **Table** (`QTableWidget`) — 2 columns: **Type** (entry type, uppercase) and
  **Description**. Row numbering is handled by the vertical header.
- **Detail pane** (`QTextEdit` via `setHtml`) — shows `json.dumps(entry_data)` for the
  selected row as formatted rich text inside a monospace `<pre>` block. Uses a module-level
  `_to_dict()` helper to recursively unpack POJOs and other non-JSON-native objects into
  plain dicts/lists before serialization.
- **Splitter** — table and detail pane are separated by a `QSplitter` with no min/max
  constraints on either pane, allowing the user full freedom to resize.

Behavior:
1. On open: populates the table from all existing entries in the class-level `_history`.
2. Connects to `SIGNALS.s_history_entry_added` → appends new rows live as edits occur.
3. Row selection → serializes the selected entry's `entry_data` into the detail pane.
4. "Clear History" clears the class-level list and resets the table and pane.

The window follows the standard build pattern (`_ready_signals` → `_build_ui` →
`_connect_signals`) and does not itself produce any `HistoryEntry` objects — it is a
purely observational/dev tool. It does not depend on `SIGNALS.s_item_selected` since
the registry is global and not item-scoped.

---

## 6. Extraction Flow

Two extraction modes in `ActionBar`:

1. **Extract from Overlay** — loads `data/sample.json` (test data for development)
2. **Extract Vanilla** — uses `dmm_parser` to extract `iteminfo.pabgb` from game files:
   ```python
   pabgb = dmm.extract_file(game_dir, group_name="0008",
       dir_path="gamedata/binary__/client/bin", file_name="iteminfo.pabgb")
   data = dmm.parse_table("iteminfo", pabgb)
   ```
   Wraps result in `ItemEditorInfo`, saves sample to `data/sample.json`,
   emits `s_iteminfo_extracted` → `ItemTable.load()`.

---

## 7. ItemTable (Left Panel)

- **Model**: `ItemTableModel` — `QAbstractTableModel` with 3 columns (Key, Name/`string_key`, Tier)
- **Proxy**: `ItemTableModelProxy` — custom `QSortFilterProxyModel`:
  - `filterAcceptsRow()` filters by key (digit match), string_key (substring), or tier name
  - `lessThan()` delegates sorting per-column
  - `.apply_filter_text()` triggers `invalidateFilter()`
- **View**: `ItemEditorTableView` — `QTableView` with row selection, stretch on column 1
- **Selection**: On selection change, emits `SIGNALS.s_item_selected(row_index)` with
  the proxy-mapped-to-source row, and `SIGNALS.s_items_selected(list[row_indices])`

---

## 8. ItemDetailsTable (Center Panel)

- Shows only the 15 **editable** fields from `ItemEditorInfoDetails.EDITABLE_ENTRIES`
- 2 columns: Key (field name) and Details (JSON-dumped value)
- Context menu: "hello darling" placeholder. The `test()` handler body is
  neutralized with `pass` (prior implementation referenced `.get_history()` /
  `.get_registry()` methods that no longer exist on `ItemEditorInfoDetails`)

---

## 9. Key Patterns & Conventions

### 9.1 Build Pattern

Every widget follows the same `__init__` structure:
```python
def __init__(self, parent):
    super().__init__(parent)
    self._ready_signals()    # Wire local signals onto SIGNALS global
    self._build_ui(parent)   # Construct and lay out child widgets
    self._connect_signals()  # Connect signals to slots
```

### 9.2 _open_window() Partial Binding

Because `clicked.connect(lambda: self.open_window(id))` captures `id` by reference,
`_open_window` returns a `functools.partial`:
```python
def _open_window(self, id: str):
    return partial(self.open_window, id)
```

### 9.3 make_collapsible() Helper

Wraps any widget in a collapsible section with a toggle button.
Persists open/closed state via `CONFIG[config_key]`.

### 9.4 center_window_in_parent()

Positions sub-windows centered relative to the parent, supporting both
embedded (within parent geometry) and standalone (absolute coordinates) modes.

### 9.5 copy() Deep-Copy Utility

Uses JSON round-trip (`json.loads(json.dumps(obj))`) for deep copies.
Returns `None` on TypeError rather than raising.

---

## 10. Known Gaps & Stubs

These are areas that exist in the UI but lack implementation:

| Feature                          | Location                          | Status                              |
|----------------------------------|-----------------------------------|-------------------------------------|
| **Show Preview**                 | Standard grid button              | No click handler                    |
| **Transmog**                     | Standard grid button              | No click handler                    |
| **Custom Item**                  | Standard grid button              | No click handler                    |
| **Bulk Options**                 | Standard grid button              | No click handler                    |
| **Global Options**               | Standard grid button              | No click handler                    |
| **Edit Buffs**                   | Advanced grid button              | No window in registry               |
| **Edit Stats**                   | Advanced grid button              | No window in registry               |
| **Edit Drop Data**               | Advanced grid button              | No window in registry               |
| **Edit Gimmick**                 | Advanced grid button              | No window in registry               |
| **Edit VFX**                     | Advanced grid button              | No click handler                    |
| **Dump ITEMINFO**                | Dev grid button                   | No click handler                    |
| **Show Item Diff**               | Dev grid button                   | No click handler                    |
| **JSON Editor save/apply**       | `json_window.py`                  | View-only QTextEdit, no save button |
| **Preset actual data mutation**  | `presets.py` → `apply_std_preset` | Records history but doesn't mutate  |
| **Dev preset apply**             | `presets.py` → `apply_dev_preset` | Stub (just logs)                    |
| **Custom preset apply**          | `presets.py` → `apply_custom_preset` | Stub (just logs)                 |
| **Undo**                         | ActionBar button + `HistoryEntry.undo()` | Stubs only                  |
| **Import/Export**                | ActionBar menu items              | No consumer for emitted signals     |
| **Apply to Game**                | ActionBar button                  | No consumer for emitted signal      |
| **ItemTable context menu**       | `items_table/context_menu.py`     | Shows "hello darling" placeholder; `test()` handler neutralized with `pass` |
| **`display.py`**                 | `item_details_table/display.py`   | Unused legacy file                  |

---

## 11. Adding a New Editor Tool — Checklist

To add a new tool button + window to the `editor_controls` panel:

1. **Create the window module**: `editor_controls/your_tool/window.py`
   - Extend `QWidget` (or use `window_template.py` as base)
   - Implement `_ready_signals()`, `_build_ui()`, `_connect_signals()`
   - Listen to `SIGNALS.s_item_selected` for the current item
   - Use `parent.get_current_item()` to access `ItemEditorInfoDetails`

2. **Register in WINDOW_REGISTRY** (`editor_controls/__init__.py`):
   ```python
   from .your_tool.window import YourToolWindow
   WINDOW_REGISTRY["your_tool"] = YourToolWindow
   ```

3. **Add button** to appropriate grid method (`_build_standard_grid`,
   `_build_advanced_grid`, or `_build_dev_grid`):
   ```python
   btns["your_tool"] = QPushButton("Your Tool Name")
   btns["your_tool"].clicked.connect(self._open_window("your_tool"))
   ```

4. **Wire signals** — if your tool produces changes:
   - Create `HistoryEntry` objects and emit `SIGNALS.s_history_entry_added`
   - Use `SIGNALS.s_status_message` for status bar feedback
   - Use `ItemEditorInfoDetails.passives()` or direct dict mutation for data changes

5. **Persist state** (optional) — use `CONFIG["your_key"]` for settings
   and `CONFIG.save()` to persist to `editor_config.json`.

---

## 12. External Dependencies

| Module                    | Purpose                                       |
|---------------------------|-----------------------------------------------|
| `dmm_parser` (Rust ext)   | Parse game binary tables (.pabgb files)       |
| `PySide6`                 | Qt6 GUI framework                             |
| `benedict`                | Dict with attribute access (for SIGNALS)      |
| `models`                  | `SaveItem`, `SaveData`, `UndoEntry`           |
| `item_db`                 | `ItemNameDB` — item name lookups              |
| `equipment_sets`          | `SetManager`, `EquipmentSet`, `StatOperation` |
| `paz_patcher`             | `PazPatchManager`, `ItemBuffPatcher`, etc.    |
| `icon_cache`              | `IconCache`, `ICON_SIZE`                      |
| `gui.theme`               | `COLORS`, `CATEGORY_COLORS` — theming         |
| `gui.iteminfo_index`      | `IteminfoIndex` — analytics over item data    |
| `gui.utils`               | `make_help_btn` (graceful fallback exists)    |

---

## 13. File Sizes & Complexity Notes

- **tab.py** — Large file (~200 lines), but most is imports. The actual `ItemEditorTab`
  class is compact: init, build UI, ready/connect signals, extraction, close event.
- **helpers.py** — Largest file (~400+ lines). Contains `ItemEditorInfoDetails`,
  `ItemEditorInfo`, `_Config`, `HistoryEntry`, utility functions, and a commented-out
  alternative proxy-based architecture (the "ItemEditorInfo as central store" pattern).
  The active code uses the singleton proxy pattern instead.
- **presets.py** — Large data file (~280 lines), mostly preset dict definitions.
- **presets_window.py** — Large UI file (~450 lines), contains two copies of
  `_build_standard_grid` (one with `__` prefix, currently unused). Has some commented-out
  logic for equippability checks and charge/stack warnings.
- **editor_controls/__init__.py** — Moderate (~180 lines), the main `EditorControls` class.
- Most other files are small and focused.

---

## 14. Game Data Paths

- **Game install**: Auto-detected via `find_game_path()` (checks Steam/Epic directories)
- **iteminfo.pabgb**: `{game_dir}/0008/0.pamt` → extracted via `dmm_parser`
- **Passive skill catalog**: `data/passive_skill_catalog.json`
- **Sample data**: `data/sample.json` (overlay extraction test data)
- **Custom presets**: `custom_presets.json` (root-level)
