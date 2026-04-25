# Building the Unified Package

## Prerequisites

### CrimsonGameMods (Python/PySide6)
- Python 3.13+
- PySide6
- PyInstaller
- crimson_rs (PyO3 Rust extension)

### DMM (Tauri/Rust)
- Node.js 18+
- Rust toolchain (stable)
- npm

## Step-by-Step Build

### 1. Build CrimsonGameMods

```bash
cd CrimsonGameMods
python -m PyInstaller CrimsonSaveEditor.spec --noconfirm
# Output: dist/CrimsonSaveEditor.exe (~85MB)
```

### 2. Build DMM

```bash
cd CrimsonGameMods/DMMLoader
npm install
npx tauri build
# Output: src-tauri/target/release/definitive-mod-manager.exe (~13MB)
```

**Important**: DMM depends on crimson-rs. Two patches must be applied to
the vendored copy (see DMMLoader/command to build.txt):

1. `crimson-rs-main/Cargo.toml` → add `crate-type = ["cdylib", "rlib"]`
2. `crimson-rs-main/src/lib.rs` → make modules public: `pub mod binary; pub mod crypto; pub mod item_info;`

### 3. Bundle Together

```bash
cd CrimsonGameMods
python bundle_unified.py
# Output: dist/CrimsonDesktopSuite/
#   CrimsonGameMods.exe
#   dmm/definitive-mod-manager.exe
#   dmm/asi_loader.dll
#   dmm/mods/
#   editor_config.json
#   README.txt
# Also: dist/CrimsonDesktopSuite_full.zip
```

### 4. Distribution

Upload `CrimsonDesktopSuite_full.zip` to the release page.
Users unzip to any folder and run `CrimsonGameMods.exe`.
DMM is auto-detected from the `dmm/` subfolder — no separate download needed.

## Development Setup

For dev, you don't need to build — just run:

```bash
cd CrimsonGameMods
python main.py
```

The Mod Loader tab will auto-detect DMM if it's in a sibling folder
(`../DMMLoader/`, `../DMM/`, etc.) or if a built exe exists anywhere nearby.

For DMM dev mode (live reload):

```bash
cd DMMLoader
npx tauri dev
# Spawns Vite at localhost:5173 + Rust backend
```

## Architecture

```
CrimsonDesktopSuite/
├── CrimsonGameMods.exe          # Main application (PySide6)
├── editor_config.json           # Shared config (game path, DMM path)
├── dmm/
│   ├── definitive-mod-manager.exe  # DMM (Tauri)
│   ├── asi_loader.dll              # ASI plugin loader stub
│   ├── config.json                 # DMM config (synced game path)
│   ├── mods/                       # User's DMM mods
│   └── backups/                    # DMM vanilla backups
├── splash.png
├── icon.ico
└── knowledge_packs/
```

Both apps write to the same game directory using non-colliding overlay
groups. CrimsonGameMods owns 0058-0063, DMM owns dmmsa/dmmgen/etc.
The shared state file (`crimson_modding_state.json` in the game dir)
tracks who wrote what.
