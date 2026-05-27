# Option D: Full Integration Plan — CrimsonGameMods + DMM Merger

**Status: ALL PHASES IMPLEMENTED** (2026-04-23)

## Vision

One product. Two engines. Zero sacrifice.

CrimsonGameMods keeps ALL its game data editing tabs (ItemBuffs, Stores,
SkillTree, DropSets, Spawns, BagSpace, Stacker, FieldEdit).  DMM becomes
the **mod loading backbone** — handling everything we don't: DLL/ASI
plugins, texture mods, audio, language packs, ReShade, mod profiles, and
the full PAZ overlay mount/unmount lifecycle for third-party mods.

The user sees ONE tool that does everything.

---

## What Each Side Brings

### CrimsonGameMods (Python/PySide6)
- **Game data editors**: ItemBuffs, Stores, SkillTree, DropSets, Spawns,
  BagSpace — visual editors that modify specific PABGB tables
- **Stacker Tool**: field-level multi-mod iteminfo merger with inspector
  (SEM/RPD/STR modes via `crimson_rs.inspect_legacy_patches`)
- **FieldEdit**: browse and edit ANY pabgb file
- **Save Editor**: ChaCha20/HMAC/LZ4/PARC pipeline (separate concern,
  stays separate)
- **crimson_rs**: Python bindings (PyO3) for iteminfo parsing, serialization,
  legacy patch inspection, PAZ packing

### DMM (Rust/Tauri/React)
- **Mod loader**: DLL/ASI with PE security scanning, texture injection,
  audio (WEM), language/font replacement, ReShade preset management
- **Mod manager UI**: drag-reorder, profiles, import/export, mod packs,
  conflict detection, Nexus integration
- **Semantic merge engine**: 105-field iteminfo parser, three-way merge,
  field-level conflict resolution with persistent user choices
- **PAZ overlay pipeline**: build overlays, register PAPGT, backup/restore
  vanilla, foreign entry preservation
- **Save engine** (v1.3): crypto primitives (prep for future save-mod features)

---

## Architecture: Three Phases

### Phase 1: Smart Wrapper (NOW — shipped with this commit)

**What**: A "Mod Loader" tab in CrimsonGameMods that integrates with DMM
as a co-process.

**How it works**:
```
┌──────────────────────────────────┐
│     CrimsonGameMods (PySide6)    │
│                                  │
│  ┌──────────┐  ┌──────────────┐  │
│  │ ItemBuffs│  │ Stacker Tool │  │
│  │ Stores   │  │ FieldEdit    │  │
│  │ DropSets │  │ BagSpace     │  │
│  │ SkillTree│  │ SpawnEdit    │  │
│  └──────────┘  └──────────────┘  │
│         │               │        │
│         ▼               ▼        │
│  ┌─────────────────────────────┐ │
│  │  Overlay Writer (0058-0063) │ │
│  └────────────┬────────────────┘ │
│               │                  │
│  ┌────────────▼────────────────┐ │
│  │  Mod Loader Tab             │ │
│  │  • Detects DMM exe          │ │
│  │  • Launches DMM             │ │
│  │  • Reads DMM config.json    │ │
│  │  • Shows active mods        │ │
│  │  • Syncs game path          │ │
│  │  • Overlay status panel     │ │
│  └────────────┬────────────────┘ │
│               │                  │
└───────────────┼──────────────────┘
                │ subprocess.Popen
                ▼
┌──────────────────────────────────┐
│     DMM (Tauri/Rust)             │
│                                  │
│  • DLL/ASI loading               │
│  • Texture/audio injection       │
│  • Language/font mods            │
│  • JSON byte-patch mods          │
│  • Mod profiles & conflict UI    │
│  • PAZ overlay mount (dmmsa/etc) │
│  • PAPGT rebuild (preserves ours)│
│                                  │
└──────────────────────────────────┘
```

**Coexistence rules**:
- Our overlays: 0058 (iteminfo buffs), 0059 (equipslotinfo), 0060 (stores),
  0062 (stacker iteminfo), 0063 (stacker equipslotinfo)
- DMM overlays: dmmsa, dmmgen, dmmequ, dmmlang (non-numeric by design)
- PAPGT: DMM v1.2.4+ preserves foreign entries on rebuild.  We preserve
  DMM entries via `_rebuild_papgt_without` which only touches our groups.
- Config sync: Mod Loader tab reads DMM's `config.json` to display status,
  can write `gamePath` into it to keep both tools pointed at same game.

**Deliverables** (this commit):
- [x] `gui/tabs/mod_loader.py` — ModLoaderTab
- [x] DMM auto-detection (sibling dirs, common install paths)
- [x] Launch DMM as subprocess, track running state
- [x] Read DMM config.json, display active mod list
- [x] Game path sync (write our path into DMM config)
- [x] Overlay status panel (classify groups by owner)
- [x] Wired into main_window.py with game_path propagation

---

### Phase 2: Deep Config Integration

**Goal**: Bidirectional awareness.  Each tool knows what the other has
active, and they coordinate without user intervention.

#### 2A. Shared State File

Create a `crimson_modding_state.json` in the game directory that BOTH
tools read/write:

```json
{
  "version": 1,
  "last_updated": "2026-04-23T...",
  "overlays": {
    "0058": { "owner": "CrimsonGameMods", "content": "iteminfo buffs", "updated": "..." },
    "0062": { "owner": "CrimsonGameMods", "content": "stacker merge", "updated": "..." },
    "dmmsa": { "owner": "DMM", "content": "mixed JSON mods", "updated": "..." }
  },
  "active_game_path": "D:\\Games\\CrimsonDesert",
  "cgm_version": "1.0.9",
  "dmm_version": "1.3.0"
}
```

Benefits:
- DMM can show "CrimsonGameMods has 3 overlays active" without reading our config
- We can show "DMM has 2 overlays + 3 ASI mods active" without launching it
- Third-party tools (JMM etc.) could adopt this and stop wiping each other

#### 2B. Stacker → DMM Conversion Pipeline

When a user has legacy JSON byte-patch mods in DMM that target iteminfo:

1. Our Mod Loader tab detects them (reads DMM's mods folder)
2. Offers "Convert to semantic patches" button
3. Runs `inspect_legacy_patches` on each mod
4. Exports converted mods back to DMM's mods folder in a DMM-compatible
   format (either as standalone overlay or as an enhanced JSON with
   field-level metadata)

This is the #1 feature DMM/Cracker wanted from the merger.

#### 2C. DMM → Our Stacker Import

Add a "Pull from DMM" button in Stacker that:
1. Scans DMM's mods folder for enabled iteminfo mods
2. Imports them into the Stacker's mod list
3. Merges them field-level alongside our ItemBuffs/Store edits
4. Produces ONE merged overlay instead of DMM + us fighting

This eliminates the "who applies last wins" problem entirely.

---

### Phase 3: Unified Build (Future)

**Goal**: Ship ONE exe that contains both CrimsonGameMods and DMM.

Two paths to get there:

#### Path A: Embed DMM's Rust engine as a Python extension

- Build DMM's core (mod scanning, overlay building, PAPGT, ASI management)
  as a Rust library with PyO3 bindings (like crimson_rs already is)
- Strip the Tauri frontend; replace with PySide6 tabs in our app
- Our app gains native mod loader capability

**Effort**: High.  DMM's commands.rs is 20K lines.  Would need to extract
the core logic into a clean library, separate from Tauri IPC concerns.

**Risk**: Cracker loses his React UI and Tauri build pipeline.  He'd need
to learn PySide6 or accept that we own the UI layer.

#### Path B: Embed our Python engine in DMM's Tauri shell

- Port our game data editors to React components in DMM's frontend
- Our Python logic (crimson_rs already ships as Rust) moves to Rust modules
  in DMM's backend
- DMM becomes the single shell for everything

**Effort**: Very high.  9 PySide6 tabs → React components.  ItemBuffs alone
is ~3K lines of Qt widget code.

**Risk**: We lose rapid iteration speed of Python.  Every game data change
requires Rust recompile.

#### Path C: Two processes, one launcher (RECOMMENDED)

- Ship a single launcher exe that unpacks both CrimsonGameMods.exe and
  DMM.exe into a shared directory
- Launcher manages lifecycle: starts CGM as primary, DMM launches on demand
- Shared config directory for cross-tool state
- From user perspective: one download, one install, one tool

**Effort**: Low-medium.  Both tools stay in their native stacks.  Cracker
keeps shipping Tauri updates.  We keep shipping PySide6 updates.  Launcher
is a thin shim (~200 lines).

**Benefit**: Zero rewrite.  Both teams keep their dev velocity.  Integration
deepens over time through the shared state protocol (Phase 2A).

---

## Overlay Group Allocation

To prevent collisions, reserved group assignments:

| Group     | Owner          | Content                |
|-----------|----------------|------------------------|
| 0000-0035 | Vanilla        | Game data (read-only)  |
| 0036      | JMM / DMM      | Legacy mod loader      |
| 0037-0057 | Reserved       | Future loaders         |
| 0058      | CrimsonGameMods| ItemBuffs (iteminfo)   |
| 0059      | CrimsonGameMods| Equipslot buffs        |
| 0060      | CrimsonGameMods| Store edits            |
| 0061      | Reserved       | Future CGM use         |
| 0062      | CrimsonGameMods| Stacker (merged items) |
| 0063      | CrimsonGameMods| Stacker (equipslot)    |
| 0064-0099 | Reserved       | Future CGM use         |
| dmmsa     | DMM            | Smart-merge overlay    |
| dmmgen    | DMM            | General overlay        |
| dmmequ    | DMM            | Equip overlay          |
| dmmlang   | DMM            | Language overlay        |

---

## Mod Type Coverage Map

| Mod Type            | CrimsonGameMods | DMM  | After Merger |
|---------------------|:-:|:-:|:-:|
| ItemInfo editing    | Stacker + Buffs | Semantic merge | Both — Stacker primary, DMM imports |
| StoreInfo editing   | Stores tab      | —    | CrimsonGameMods |
| SkillTree editing   | SkillTree tab   | —    | CrimsonGameMods |
| DropSet editing     | DropSets tab    | —    | CrimsonGameMods |
| Spawn editing       | SpawnEdit tab   | —    | CrimsonGameMods |
| BagSpace editing    | BagSpace tab    | —    | CrimsonGameMods |
| Any PABGB editing   | FieldEdit tab   | —    | CrimsonGameMods |
| JSON byte patches   | Inspector only  | Full load | DMM |
| DLL / ASI plugins   | —               | Full | DMM |
| Texture (.dds)      | —               | Full | DMM |
| Audio (.wem)        | —               | Full | DMM |
| Language / fonts    | —               | Full | DMM |
| ReShade presets     | —               | Full | DMM |
| Mod profiles        | —               | Full | DMM |
| Standalone overlays | Export          | Import + mount | Both |
| Save editing        | Full            | Crypto only | CrimsonGameMods |

---

## Data Flow: How Mods Get Applied

```
User wants to mod their game
         │
         ├── Game data change? (stats, items, stores, drops, skills)
         │   └── Use CrimsonGameMods tabs
         │       └── Writes overlay to 0058-0063
         │           └── PAPGT updated (preserves DMM entries)
         │
         ├── Third-party mod? (DLL, texture, JSON, audio)
         │   └── Use DMM (via Mod Loader tab → Launch)
         │       └── Writes overlay to dmmsa/dmmgen/etc
         │           └── PAPGT updated (preserves CGM entries)
         │
         ├── Legacy JSON mod that needs conversion?
         │   └── Phase 2B: Convert via Stacker Inspector
         │       └── SEM/RPD translation → field-level patch
         │           └── Can be merged in Stacker or re-exported to DMM
         │
         └── Multiple iteminfo mods need merging?
             └── Phase 2C: Pull all into Stacker
                 └── Field-level merge with conflict resolution
                     └── ONE overlay in 0062 (no conflicts)
```

---

## Implementation Priority

1. **Phase 1** — Smart Wrapper (THIS COMMIT)
   - ModLoaderTab built and wired
   - DMM detection, launch, config read, overlay scan

2. **Phase 2A** — Shared state file
   - Both tools write `crimson_modding_state.json`
   - Coordinate without process communication

3. **Phase 2B** — Stacker conversion export
   - "Convert DMM mods" button in Mod Loader
   - Runs inspector, exports semantic patches

4. **Phase 2C** — Stacker DMM import
   - "Pull from DMM" in Stacker
   - Unified field-level merge across all sources

5. **Phase 3C** — Unified launcher
   - Single download, one install, both tools
   - Shared config directory

---

## What Cracker Needs To Do

1. **Keep PAPGT foreign-entry preservation** (already in v1.2.4+) — this is
   the foundation of coexistence
2. **Expose mod list as readable JSON** — DMM already stores `config.json`
   next to exe with `activeMods`, so this is done
3. **Adopt shared state file** (Phase 2A) — write
   `crimson_modding_state.json` on mount, read on scan
4. **Accept standalone overlays from us** — already works (DMM detects
   `0036/0.paz + 0.pamt` standalone format)

---

## What We Do NOT Sacrifice

- All 9 game mod tabs remain fully functional
- Stacker's field-level merge stays in our codebase
- crimson_rs Python bindings stay ours
- Save editor stays separate and independent
- PySide6 development velocity stays intact
- Users who don't want DMM can ignore the Mod Loader tab entirely
- Users who only want DMM can use it standalone — our overlays survive
