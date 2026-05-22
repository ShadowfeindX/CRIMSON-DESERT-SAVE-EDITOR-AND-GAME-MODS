# CONTINUE.md - Crimson Desert Modding Utilities Guide

## 🌟 Project Overview

**Project Name:** Crimson Desert Save Editor & Game Mods
**Purpose:** This suite consists of two companion desktop utilities designed to enhance the player experience and functionality within "Crimson Desert." The tools allow users to non-invasively modify critical game data, such as inventory statistics, vendor pricing, quest progress, and creature spawns.
**Disclaimer:** *These tools are unofficial and non-commercial mods for Crimson Desert (© Pearl Abyss). Users must always back up their saves before making changes.*

### Key Technologies Used
*   **Primary Language:** Python (The core logic uses Python and PySide6 for the GUI/desktop application structure.)
*   **Dependencies:** Node.js (Used for managing dependencies, build tooling, or potentially front-end assets related to the utilities).
*   **Core Data Handling:** Specialized libraries handle game data structures, including custom serialization formats like `.pabgb` and proprietary save file formats (`save.save`).
*   **Architecture:** Modular design with distinct components for saving (Save Editor) and world/item manipulation (Game Mods).

### High-Level Architecture
The system is separated into two functional builds:
1.  **Save Editor:** Focuses on the local player data (`save.save` file). It acts as a comprehensive inventory, quest, and knowledge management tool.
2.  **Game Mods:** Focuses on modifying world parameters and database definitions (e.g., item stats, drop rates, vendor lists) by writing to PAZ overlay directories.

## 🚀 Getting Started

### Prerequisites
Before running the tools or contributing:
1.  **Python Environment:** Install Python (recommended version matching project requirements).
2.  **Dependencies:** Ensure `pip` is configured and required libraries are installed (e.g., `PySide6`, `lz4`, `cryptography`, `Pillow`).
3.  **Game Client:** Access to a local copy of the "Crimson Desert" game client for data extraction/context.

### Installation Instructions
Since this project is distributed as two standalone applications, installation involves following build instructions:

**For Local Development (Game Mods):**
1. Clone the repository into your workspace.
2. Navigate to `CrimsonGameMods/`.
3. Install Python dependencies: `pip install PySide6 lz4 cryptography Pillow pyinstaller crimson-rs`

**To Run:**
*   The easiest way is to use the pre-compiled executables (`.exe`) found in the official releases. These handle necessary configuration and backups automatically.

### Basic Usage Examples
*   **Editing Inventory (Save Editor):** Open `Save Editor`, load your save, select an item, and utilize the built-in tools for socket management or enchanting/stats modification.
*   **Modifying Drop Rates (Game Mods):** Point `Game Mods` to your game path. Navigate to the DropSets section, locate a desired enemy, and modify the drop rate or quantity of specific items within the `dropsetinfo.pabgb`.

### Running Tests
*(Needs verification - Assume standard Python testing)*
Run unit tests for core modules (e.g., parser logic, data validation) using:
```bash
# Assuming a standard test directory setup
pytest <module_name>
```

## 🏛️ Project Structure

The source code is primarily housed under `CrimsonGameMods/`.

*   **`package.json`, `node_modules/`:** Manages JavaScript/Node.js dependencies used by the tooling (e.g., asset compilation, utility scripts).
*   **`CrimsonGameMods/`:** **(Core Source)** Contains the main Python logic and GUI components for Game Mods.
    *   `main.py`: The primary entry point for the application.
    *   `gui/`: Directory containing various module GUIs (PySide6 packages). Each tab represents a core function (e.g., ItemBuffs, Stores).
    *   `data/`, `locale/`, `knowledge_packs/`: Directories holding structured game assets, localized strings, and knowledge databases that the tools read from or write to.
    *   `CrimsonGameMods.spec`: PyInstaller specification file used for bundling the application into a single executable.

## 🛠️ Development Workflow

### Coding Standards & Conventions
*   **Python:** Adhere strictly to PEP 8 guidelines. Type hinting should be utilized extensively across all modules (`gui/`).
*   **Data Integrity:** All write operations *must* include an auto-backup mechanism before execution and validate data structures against known schemas (using libraries like `zod` if applicable).

### Testing Approach
*   **Unit Tests:** Focus on isolated testing of parsers, serialization/deserialization logic, and business rules (e.g., checking if a crafted item adheres to defined limits).
*   **Integration Tests:** Test the end-to-end flow—from opening the GUI section (e.g., Stores) to successfully writing modified data back to the target `.pabgb` file format.

### Build and Deployment Process
The primary build process utilizes PyInstaller for generating standalone executables:
1.  Run the build command from within `CrimsonGameMods/`:
    ```bash
    pip install --upgrade pyinstaller
    python -m PyInstaller CrimsonGameMods.spec --noconfirm
    ```
2.  This generates the executable in the `dist/` directory.
3.  **Version Control:** Updates require updating the relevant manifest files (`editor_version_standalone.json`, etc.).

### Contribution Guidelines
*   All contributions must adhere to the **MPL-2.0 License**.
*   Feature additions or bug fixes should be accompanied by detailed documentation updates in `CONTINUE.md`.
*   Please ensure all new modules include proper error handling and validation for external file inputs.

## 🧠 Key Concepts (Domain Terminology)

| Term | Definition | Component |
| :--- | :--- | :--- |
| **PAZ Overlays** | A specific directory structure used to inject custom data definitions into the game client (e.g., `iteminfo.pabgb`, which holds item stats). Modifying these requires writing to them. | Game Mods |
| **`save.save`** | The primary, encrypted save file containing player progress, inventory, and quest state. Write access here is reserved for the Save Editor. | Save Editor |
| **`.pabgb`** | A proprietary or custom binary/compressed format used by the game to store structured data (e.g., item buffs, drop sets). Tools must correctly read and write this format. | Both |
| **MPL-2.0** | The Multi-Platform License v2.0; governs how the source code can be used and distributed. | Licensing |

## ⚙️ Common Tasks

### Task: Resetting a Quest
1. Navigate to the **Quest Editor** tab (Save Editor).
2. Select the relevant quest ID or objective.
3. Click 'Reset' or use batch filtering tools, ensuring you understand the impact on save integrity before proceeding.

### Task: Applying Item Buffs
1. Open `Game Mods` and select the **ItemBuffs** module.
2. Select a target item template/ID.
3. Use the stat selectors to define new buffs (e.g., +5 Crit Damage, +2 Stamina).
4. Apply changes and save the modified data back into the designated `.pabgb` file.

## 🐞 Troubleshooting

| Issue | Possible Cause(s) | Solution |
| :--- | :--- | :--- |
| **"Data Write Failed"** | Save file is corrupt, or required dependencies (like PAZ overlays) are missing/outdated. | Run the tool's internal diagnostics check. Ensure your game client version matches the expected format. |
| **GUI Crashes on Startup** | Missing Python dependency, especially in a new environment. | Re-run `pip install` and ensure all dependencies listed in the build instructions are installed. |
| **Changes Not Appearing In-Game** | The tool successfully wrote data, but the game client failed to load/read the overlay correctly. | Verify that the PAZ overlays directory is correctly located relative to the active game path. Restart the game after modification. |

## 📚 References
*   [Crimson Desert Game Wiki/Documentation](https://www.pearlabyss.com/) (External Link - Verification needed)
*   [Tooling License]: MPL-2.0
*   [Core Codebase Documentation]: `CrimsonGameMods/CREDITS.md` for original developers and tool insights.