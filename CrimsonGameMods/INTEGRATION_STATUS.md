# CrimsonGameMods + DMM Integration — Technical Status

## Before & After

### Before (two separate tools)

```
CrimsonGameMods (Python/PySide6)          DMM (Rust/Tauri/React)
├── ItemBuffs tab                         ├── JSON byte-patch loader
├── Stores tab                            ├── DLL/ASI plugin loader
├── SkillTree tab                         ├── Texture injection (DDS)
├── DropSets tab                          ├── Audio replacement (WEM)
├── Stacker Tool                          ├── Language/font mods
├── FieldEdit tab                         ├── ReShade preset manager
├── BagSpace tab                          ├── Mod profiles & packs
├── SpawnEdit tab                         ├── Conflict detection UI
└── MercPets tab                          ├── Semantic iteminfo merge
                                          └── 3-way merge engine

Problems:
- Users download and configure two separate tools
- Both write PAPGT independently — last writer wins, other's overlays vanish
- DMM revert restores vanilla PAPGT — wipes our overlay registrations
- DMM's file router can accidentally write into our overlay groups
- No way to know if the other tool has iteminfo changes active
- User has to manually avoid conflicts between tools
- Legacy JSON mods can't be merged field-level in DMM without our Inspector
```

### After (unified integration)

```
CrimsonGameMods (unified)
├── Game Mods tabs (all original tabs intact)
│   ├── ItemBuffs ─────── writes 0058/, conflict check before apply
│   ├── Stores ────────── writes 0060/, state tracked
│   ├── Stacker Tool ──── writes 0062/, Pull DMM button, conflict check
│   ├── SkillTree ─────── writes 0063/, state tracked
│   ├── BagSpace ──────── writes 0062/, state tracked
│   ├── DropSets ──────── state tracked
│   ├── SpawnEdit
│   ├── FieldEdit
│   ├── MercPets ──────── writes 0061/, state tracked
│   └── Mod Loader ────── DMM integration hub (3 sub-tabs)
│       ├── DMM Mods ──── reads DMM config, shows all mods
│       ├── Overlays ──── unified view of all overlay groups
│       └── Convert ───── byte-patch → semantic field conversion
│
├── Mod Manager tab (embedded DMM React UI via WebView)
│   └── Full DMM frontend with sidebar, mod cards, profiles
│       └── Python bridge handles IPC, launches DMM exe for heavy ops
│
├── Overlay Coordinator (workflow bible)
│   ├── pre_write() ──── blocks vanilla overwrites, blocks cross-tool
│   ├── post_write() ─── records overlay in shared state
│   ├── pre_restore() ── blocks deleting other tool's overlays
│   ├── post_restore() ─ cleans shared state
│   ├── safe_papgt_add/remove() ── always preserves foreign entries
│   ├── scan_for_iteminfo_conflicts() ── universal format scanner
│   └── audit() ──────── consistency check
│
├── Shared State (crimson_modding_state.json in game dir)
│   └── Both tools read/write — tracks who owns what overlay
│
└── Unified Launcher + Bundle
    └── One download, one install, both tools
```

---

## New Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `shared_state.py` | 336 | Cross-tool state file (`crimson_modding_state.json`). Tracks overlay ownership, DMM mod list, tool versions. Read/write by both tools. |
| `overlay_coordinator.py` | 643 | **The workflow bible.** Safety checks before every overlay write/restore. Universal conflict scanner. PAPGT operations that always preserve foreign entries. |
| `gui/tabs/mod_loader.py` | 1080 | Deep DMM integration tab. 3 sub-tabs: DMM Mods browser (reads DMM config + mods folder), Overlay status (classifies all groups by owner), Convert to Semantic (runs Inspector on byte-patch mods, exports Format 3 JSON). |
| `gui/tabs/dmm_webview.py` | 808 | Embeds DMM's full React UI in QWebEngineView. Custom `BridgePage` intercepts console.log IPC. `TauriBridge` with 42 command handlers + 88 plugin defaults/no-ops. Base64 response encoding. Local HTTP server for asset loading. |
| `launcher.py` | 134 | Unified launcher. Auto-detects bundled DMM, syncs game paths, manages lifecycle. |
| `bundle_unified.py` | 196 | Build script. Copies CGM.exe + DMM.exe + resources into `dist/CrimsonDesktopSuite/`, creates README, zips for distribution. |
| `BUILD_UNIFIED.md` | 68 | Step-by-step build instructions for the unified package. |
| `OPTION_D_INTEGRATION_PLAN.md` | 230 | Architecture plan, overlay allocation, mod type coverage matrix, phased rollout. |
| **Total new code** | **3,495** | |

---

## Existing Files Modified

### gui/main_window.py
- Added `ModLoaderTab` import and tab creation in Game Mods group
- Added `DmmWebViewTab` import (try/except guarded) and top-level "Mod Manager" tab
- Added `_mod_loader_tab.set_game_path()` to `_set_game_path()` propagation chain
- Total: ~20 lines added

### gui/tabs/buffs_v319.py
- **Apply path**: Added `check_iteminfo_conflicts_before_apply()` guard before `_buff_apply_to_game()` proceeds. Shows warning dialog listing all conflict sources, user can cancel or continue.
- **Post-write**: Added `record_overlay()` call after successful overlay write to 0058/. Tracks what files were written (iteminfo + staged skill/equip files).
- **Restore path**: Added `post_restore()` call inside `_buff_restore_original()` loop that deletes overlay directories. Cleans shared state for each removed group (0058, 0059, 0061, legacy 0038).

### gui/tabs/stacker.py
- **Pull DMM button**: Added "Pull DMM" button next to "Pull Buffs" in Sources panel. Reads DMM config, imports active iteminfo mods as `[DMM]`-prefixed stack sources.
- **`_pull_from_dmm()` method**: Reads DMM config via `get_dmm_iteminfo_mods()`, classifies each as legacy_json or field_json, appends to `self._mods` list.
- **DMM overlay warning**: After vanilla extraction in `_run_inner`, checks shared state for non-CGM iteminfo overlays. Logs warning if found, suggests using Pull DMM.
- **Pre-apply conflict check**: Added `check_iteminfo_conflicts_before_apply()` guard in `_run()`, only on install (not preview/export). Shows dialog, user can cancel.
- **Post-write**: Added `record_overlay()` calls after both iteminfo overlay write and equipslot overlay write.
- **DMM type tag**: Added `"dmm_json"` to `_TYPE_META` for visual distinction in Sources list.

### gui/tabs/world.py (Stores + DropSets)
- **Stores post-write**: Added `record_overlay()` after successful store overlay write.
- **Stores restore**: Added `post_restore()` after `shutil.rmtree(game_mod)` in `_store_restore()`.
- **DropSets post-write**: Added `record_overlay()` after successful dropset overlay write.
- **DropSets restore**: Added `post_restore()` after `shutil.rmtree(overlay)` in `_dropset_restore()`.

### gui/tabs/bagspace.py
- **Post-write**: Added `record_overlay()` after successful BagSpace overlay write.
- **Restore**: Added `post_restore()` after `shutil.rmtree(overlay_dir)` in `_restore_overlay()`.

### gui/tabs/skill_tree.py
- **Post-write**: Added `record_overlay()` after successful SkillTree overlay write.
- **Restore**: Added `post_restore()` after `shutil.rmtree(game_mod)` in `_on_restore()`.

### gui/tabs/mercpets.py
- **Post-write**: Added `record_overlay()` after successful MercPets overlay write.
- **Restore**: Added `post_restore()` after `shutil.rmtree(overlay)` in `_restore()`.

---

## DMM Codebase Changes

### DMMLoader/src-tauri/src/commands.rs

**New function: `is_foreign_overlay_group()`** (line 42)
```rust
pub fn is_foreign_overlay_group(name: &str) -> bool {
    matches!(name, "0058" | "0059" | "0060" | "0061" | "0062" | "0063" | "0064" | "0065")
}
```
Blocks DMM from routing file replacements into CrimsonGameMods overlay groups.

**Patched: 3 directory scan locations** (lines 2813, 17535, 18597)
Added `&& !is_foreign_overlay_group(&name)` to the filter predicate in `find_file_in_game()` and two other directory enumeration sites. Prevents DMM from ever reading our PAMT indexes or writing into our overlay PAZ files.

**Patched: `revert_mods()` PAPGT restore** (line 11011)
Before: restored `papgt_clean.bin` (vanilla backup) directly — wiped ALL overlay registrations including ours.
After: captures foreign overlay entries from live PAPGT before restoring backup, then re-adds them with refreshed CRCs via `build_papgt_with_overlay_named()`. Our overlays survive DMM revert.

---

## Architecture: How It All Connects

### Data Flow

```
User edits in CrimsonGameMods tabs
         │
         ▼
    overlay_coordinator.pre_write()
    ├── Blocks if vanilla group
    ├── Blocks if another tool owns the group
    └── Returns OK
         │
         ▼
    Tab writes PAZ overlay (0058-0063)
    Tab calls safe_papgt_add() for PAPGT
    ├── Removes ONLY our entry from PAPGT
    ├── Re-adds our entry with new CRC
    └── Preserves ALL other entries (DMM, JMM, unknown)
         │
         ▼
    overlay_coordinator.post_write()
    └── Records overlay in crimson_modding_state.json
         │
         ▼
    User clicks Restore
         │
         ▼
    overlay_coordinator.pre_restore()
    ├── Blocks if another tool owns the group
    └── Returns OK
         │
         ▼
    Tab deletes overlay directory
    Tab calls safe_papgt_remove()
    ├── Removes ONLY our entry from PAPGT
    └── Preserves ALL other entries
         │
         ▼
    overlay_coordinator.post_restore()
    └── Removes overlay from crimson_modding_state.json
```

### Conflict Detection Flow

```
User clicks Apply (ItemBuffs or Stacker Install)
         │
         ▼
    check_iteminfo_conflicts_before_apply()
         │
         ├── Scans game directory PAMT indexes
         │   (reads 0.pamt from every overlay group, checks for iteminfo)
         │
         ├── Scans DMM mods folder
         │   (parses JSON mods, checks game_file for iteminfo)
         │
         ├── Scans extra directories
         │   (walks folders for loose .pabgb files)
         │
         ├── Scans mod subfolder PAZ overlays
         │   (reads 0.pamt from 0036/ dirs inside mod folders)
         │
         ▼
    Conflicts found?
    ├── NO → proceed silently
    └── YES → show warning dialog:
              "Found 14 other source(s) with iteminfo.pabgb:
                0062/ (CrimsonGameMods: Stacker merge)
                Accessory & Cloak Sockets (411 patches)
                Super MOD/0036 (overlay)
                ...
              Use Stacker → Pull DMM to merge, or continue to override?"
              [Continue] [Cancel]
```

### WebView Bridge Flow

```
DMM React Frontend (built HTML/JS/CSS)
         │
         │  window.__TAURI_INTERNALS__.invoke("scan_mods", {...})
         ▼
    BRIDGE_SCRIPT (injected at DocumentCreation)
    └── console.log("__BRIDGE__:" + JSON.stringify({id, command, args}))
         │
         ▼
    BridgePage.javaScriptConsoleMessage()
    └── Intercepts __BRIDGE__ prefix messages
         │
         ▼
    TauriBridge._dispatch(command, args)
    ├── Plugin defaults (26) → return safe values
    ├── Plugin no-ops (62) → return null
    ├── File I/O commands (scan_mods, load_config, etc.) → Python handlers
    ├── Game detection (auto_detect_game_path, validate) → reuse our logic
    └── Heavy ops (apply_mods, revert_mods) → auto-launch DMM standalone
         │
         ▼
    Response encoded as base64, delivered via QTimer.singleShot(0):
    page.runJavaScript('window.__BRIDGE_RESPOND__(id, atob("..."))')
         │
         ▼
    Promise resolves in React → UI updates
```

---

## Shared State File Format

Written to `<game_dir>/crimson_modding_state.json`:

```json
{
  "version": 1,
  "last_updated": "2026-04-23T17:50:16",
  "cgm_version": "1.0.9",
  "dmm_version": "1.3.0",
  "game_path": "D:\\Games\\CrimsonDesert",
  "overlays": {
    "0058": {
      "owner": "CrimsonGameMods",
      "content": "ItemBuffs",
      "updated": "2026-04-23T17:50:16",
      "files": ["iteminfo.pabgb", "iteminfo.pabgh", "skill.pabgb"],
      "paz_size": 5367434,
      "pamt_size": 1024
    },
    "0062": {
      "owner": "CrimsonGameMods",
      "content": "Stacker merge",
      "files": ["iteminfo.pabgb", "iteminfo.pabgh"],
      ...
    },
    "dmmsa": {
      "owner": "DMM",
      "content": "DMM overlay (dmmsa)",
      ...
    }
  },
  "dmm_mods": [
    {
      "file_name": "AccessorySocketsMod.json",
      "title": "Accessory & Cloak Sockets",
      "author": "DennyBro",
      "patch_count": 411,
      "targets_iteminfo": true,
      ...
    }
  ],
  "dmm_asi_mods": ["script_extender.asi"],
  "dmm_texture_mods": [],
  "dmm_browser_mods": []
}
```

---

## Overlay Group Allocation

| Group | Owner | Content | Tracked |
|-------|-------|---------|---------|
| 0000-0035 | Vanilla | Game data | Never touched |
| 0036 | DMM/JMM | Legacy mod loader | DMM manages |
| 0058 | CrimsonGameMods | ItemBuffs (iteminfo) | record_overlay + post_restore |
| 0059 | CrimsonGameMods | ItemBuffs (equipslot) | record_overlay + post_restore |
| 0060 | CrimsonGameMods | Store edits | record_overlay + post_restore |
| 0061 | CrimsonGameMods | MercPets | record_overlay + post_restore |
| 0062 | CrimsonGameMods | Stacker merged items | record_overlay + post_restore |
| 0063 | CrimsonGameMods | Stacker equipslot / SkillTree | record_overlay + post_restore |
| 0064 | CrimsonGameMods | ItemBuffs localization | record_overlay |
| 0065 | CrimsonGameMods | Reserved | — |
| dmmsa | DMM | Smart-merge overlay | DMM manages |
| dmmgen | DMM | General overlay | DMM manages |
| dmmequ | DMM | Equip overlay | DMM manages |
| dmmlang | DMM | Language overlay | DMM manages |

---

## Universal Conflict Scanner Coverage

| Mod Format | Detection Method | Tested With |
|-----------|-----------------|-------------|
| JSON byte-patch (Format 1, absolute offset) | Parse JSON, check `game_file` | No Cooldown for all items.json (56 patches) |
| JSON byte-patch (Format 2, entry+rel_offset) | Parse JSON, check `game_file` | AccessorySocketsMod.json (411 patches) |
| JSON semantic (Format 3, field intents) | Parse JSON, check `game_file` | Stacker exports |
| Pre-built PAZ overlay (0036/0.paz + 0.pamt) | Read PAMT index, check file list | Super MOD, Lightning Aura, falldmg |
| Loose .pabgb file replacement | Walk folder tree, match filename | DMM_All_Melee_Weapon_Buffs |
| Browser mod (files/ subfolder) | Walk files/ tree, match filename | — |
| Active game overlay (any group) | Read live PAMT from game dir | 0062/ (our Stacker), dmmsa/ |

---

## Known Limitations

1. **WebView heavy operations**: `apply_mods` and `revert_mods` in the embedded DMM UI auto-launch DMM standalone instead of running in-process. DMM's mount pipeline is 20K lines of Rust that can't be replicated in Python. Users see a message explaining this.

2. **PAPGT 5-byte name table overhead**: After an add+remove cycle, the PAPGT file grows by 5 bytes (stale name-table entry from the removed group). This is cosmetic — the file is valid, parseable, and accepted by the game. Round-trip is stable (subsequent writes produce identical bytes).

3. **DMM changes are Rust source edits**: The `is_foreign_overlay_group()` and `revert_mods` fixes are in DMM's Rust source. They take effect when Cracker rebuilds DMM (`npx tauri build`). Until then, the live DMM exe doesn't have these fixes — but our overlay coordinator + shared state still protect against conflicts from our side.

4. **Shared state adoption by DMM**: DMM doesn't write `crimson_modding_state.json` yet. Our tool reads DMM's config.json directly as a fallback. Full bidirectional awareness requires Cracker to add state-file writes to DMM's mount/revert paths.

5. **QWebChannel not available in PySide6**: The WebView bridge uses console.log IPC instead of Qt's QWebChannel (PySide6 doesn't ship qwebchannel.js). This works but adds ~1ms latency per IPC round-trip due to the base64 encoding + QTimer deferral.

---

## Testing Status

| Test | Result |
|------|--------|
| All new modules import cleanly | PASS |
| Shared state round-trip (record + load + remove) | PASS |
| Coordinator safety (block vanilla, block cross-tool, clean restore) | PASS (7/7 checks) |
| PAPGT round-trip (add + remove + verify integrity) | PASS (all entries preserved) |
| PAPGT stability (write-read-write identical) | PASS |
| Foreign group detection (DMM overlay dirs) | PASS |
| Universal scanner — JSON byte-patch mods | PASS (8 mods found) |
| Universal scanner — pre-built PAZ overlays | PASS (4 found via PAMT) |
| Universal scanner — loose .pabgb files | PASS (1 found) |
| Universal scanner — no false positives on own group | PASS |
| Pre-apply warning message generation | PASS (716 chars) |
| ModLoaderTab creates with 3 sub-tabs | PASS |
| DmmWebViewTab loads DMM React UI (55KB HTML rendered) | PASS |
| TauriBridge invoke round-trip (get_app_dir) | PASS |
| TauriBridge scan_mods with real mod files | PASS (11 entries, correct shapes) |
| Stacker Pull DMM button exists + method works | PASS |
| DMM is_foreign_overlay_group defined + applied to 3 scan sites | PASS |
| DMM revert_mods preserves foreign entries | PASS (verified in Rust source) |
| Apply guard wired into ItemBuffs (before save prompt) | PASS |
| Apply guard wired into Stacker (only on install, before merge) | PASS |
| Post-restore wired into all 6 restore functions | PASS |
| Record_overlay wired into all 7 overlay write paths | PASS |
