import json
import sys
import textwrap
import logging
from typing import Any
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
)

from gui.theme import COLORS, CATEGORY_COLORS


log = logging.getLogger(__name__)


class PresetsWindow(QWidget):
    _PRESETS = {
        "open_sockets": {
            "name": "5 Sockets",
            "description": "Adds 5 open sockets to all newly obtained versions of this item.",
            "warning": "Embedding abyss gears in-game on items that do not normally have socket slots can cause crashing.",
            "drop_default_data": {
                "add_socket_material_item_list": [
                    {"item": 1, "value": 500},
                    {"item": 1, "value": 1000},
                    {"item": 1, "value": 2000},
                    {"item": 1, "value": 3000},
                    {"item": 1, "value": 4000},
                ],
                "socket_valid_count": 5,
                "use_socket": 1,
            },
        },
        "max_enchant": {
            "name": "Max Refine",
            "description": "All newly obtained copies of this item will be lvl 10 be default.",
            "drop_default_data": {"drop_enchant_level": 10},
        },
        "no_cooldown": {
            "name": "No Cooldown",
            "description": "Set cooldown of item ability to 1s and remove recharge restrictions.",
            "cooltime": 1000,  # wire unit is milliseconds; 1000 = 1 second (minimum safe value)
            "item_charge_type": 0,
            "respawn_time_seconds": 0,
        },
        "max_charges": {
            "name": "Max Charges",
            "description": "Set charges of item ability to 100.",
            "max_charged_useable_count": 100,
        },
        "max_stacks": {
            "name": "Max Stacks",
            "description": "Set the max stack size of an item to 999999.",
            "max_stack_count": 999999,
        },
        "shadow_boots": {
            "name": "Shadow Boots",
            "passives": [
                {"skill": 7201, "level": 1},
                {"skill": 7055, "level": 1},
                {"skill": 7202, "level": 1},
            ],
            "gimmick_info": 1004431,
            "cooltime": 1000,  # ms; 1000 = 1s
            "item_charge_type": 0,
            "max_charged_useable_count": 100,
            "respawn_time_seconds": 0,
            "docking_child_data": {
                "gimmick_info_key": 1004431,
                "character_key": 0,
                "item_key": 0,
                "attach_parent_socket_name": "Bip01 Footsteps",
                "attach_child_socket_name": "",
                "docking_tag_name_hash": [247236102, 0, 0, 0],
                "docking_equip_slot_no": 65535,
                "spawn_distance_level": 4294967295,
                "is_item_equip_docking_gimmick": 0,
                "send_damage_to_parent": 0,
                "is_body_part": 0,
                "docking_type": 0,
                "is_summoner_team": 0,
                "is_player_only": 0,
                "is_npc_only": 0,
                "is_sync_break_parent": 0,
                "hit_part": 0,
                "detected_by_npc": 0,
                "is_bag_docking": 0,
                "enable_collision": 0,
                "disable_collision_with_other_gimmick": 1,
                "docking_slot_key": "",
                "inherit_summoner": 0,
                "summon_tag_name_hash": [0, 0, 0, 0],
            },
        },
        "lightning_weapon": {
            "name": "Lightning Weapon",
            "passives": [
                {"skill": 91101, "level": 3},
                {"skill": 91104, "level": 3},
                {"skill": 91105, "level": 3},
            ],
            "gimmick_info": 1001961,
            "cooltime": 1000,  # ms; 1000 = 1s
            "item_charge_type": 0,
            "max_charged_useable_count": 100,
            "respawn_time_seconds": 0,
            "docking_child_data": {
                "gimmick_info_key": 1001961,
                "character_key": 0,
                "item_key": 0,
                "attach_parent_socket_name": "Gimmick_Weapon_00_Socket",
                "attach_child_socket_name": "",
                "docking_tag_name_hash": [3365725887, 0, 0, 0],
                "docking_equip_slot_no": 65535,
                "spawn_distance_level": 4294967295,
                "is_item_equip_docking_gimmick": 1,
                "send_damage_to_parent": 0,
                "is_body_part": 0,
                "docking_type": 0,
                "is_summoner_team": 0,
                "is_player_only": 0,
                "is_npc_only": 0,
                "is_sync_break_parent": 0,
                "hit_part": 0,
                "detected_by_npc": 0,
                "is_bag_docking": 0,
                "enable_collision": 0,
                "disable_collision_with_other_gimmick": 1,
                "docking_slot_key": "",
                "inherit_summoner": 0,
                "summon_tag_name_hash": [0, 0, 0, 0],
            },
        },
        "great_thief": {
            "name": "Great Thief (Block Theft only)",
            "passives": [
                {"skill": 9128, "level": 1},
                {"skill": 76009, "level": 1},
            ],
            "gimmick_info": 1002041,
            "cooltime": 1800,
            "item_charge_type": 0,
            "max_charged_useable_count": 1,
            "respawn_time_seconds": 0,
            "docking_child_data": {
                "gimmick_info_key": 1002041,
                "character_key": 0,
                "item_key": 0,
                "attach_parent_socket_name": "Gimmick_Hand_L_00_Socket",
                "attach_child_socket_name": "",
                "docking_tag_name_hash": [0, 0, 0, 0],
                "docking_equip_slot_no": 65535,
                "spawn_distance_level": 4294967295,
                "is_item_equip_docking_gimmick": 0,
                "send_damage_to_parent": 0,
                "is_body_part": 0,
                "docking_type": 0,
                "is_summoner_team": 0,
                "is_player_only": 0,
                "is_npc_only": 0,
                "is_sync_break_parent": 0,
                "hit_part": 0,
                "detected_by_npc": 0,
                "is_bag_docking": 0,
                "enable_collision": 0,
                "disable_collision_with_other_gimmick": 1,
                "docking_slot_key": "",
                "inherit_summoner": 0,
                "summon_tag_name_hash": [0, 0, 0, 0],
            },
        },
        "great_thief_all": {
            "name": "Great Thief (Block ALL crime)",
            "passives": [
                {"skill": 9128, "level": 1},
                {"skill": 76009, "level": 1},
                {"skill": 76011, "level": 1},
                {"skill": 76012, "level": 1},
            ],
            "gimmick_info": 1002041,
            "cooltime": 1800,
            "item_charge_type": 0,
            "max_charged_useable_count": 1,
            "respawn_time_seconds": 0,
            "docking_child_data": {
                "gimmick_info_key": 1002041,
                "character_key": 0,
                "item_key": 0,
                "attach_parent_socket_name": "Gimmick_Hand_L_00_Socket",
                "attach_child_socket_name": "",
                "docking_tag_name_hash": [0, 0, 0, 0],
                "docking_equip_slot_no": 65535,
                "spawn_distance_level": 4294967295,
                "is_item_equip_docking_gimmick": 0,
                "send_damage_to_parent": 0,
                "is_body_part": 0,
                "docking_type": 0,
                "is_summoner_team": 0,
                "is_player_only": 0,
                "is_npc_only": 0,
                "is_sync_break_parent": 0,
                "hit_part": 0,
                "detected_by_npc": 0,
                "is_bag_docking": 0,
                "enable_collision": 0,
                "disable_collision_with_other_gimmick": 1,
                "docking_slot_key": "",
                "inherit_summoner": 0,
                "summon_tag_name_hash": [0, 0, 0, 0],
            },
        },
        "crime_mask": {
            "name": "Crime Mask (Steal / Threaten)",
            "passives": [
                {"skill": 709, "level": 1},
            ],
        },
    }

    _DEV_PRESETS = {
        "immune": {
            "label": "Immune Ring",
            "passives": [{"skill": 70994, "level": 1}],
            "regen_stat_list": [{"stat": 1000000, "change_mb": 1000000}],
            "stat_list_static": [{"stat": 1000002, "change_mb": 1000000}],
        },
        "str_hp": {
            "label": "Str+HP Ring",
            "passives": [],
            "regen_stat_list": [{"stat": 1000000, "change_mb": 1000000}],
            "stat_list_static": [{"stat": 1000002, "change_mb": 1000000}],
        },
        "def_hp": {
            "label": "Def+HP Ring",
            "passives": [],
            "regen_stat_list": [{"stat": 1000000, "change_mb": 1000000}],
            "stat_list_static": [{"stat": 1000003, "change_mb": 1000000}],
        },
        "mp_stam": {
            "label": "MP+Stamina Ring",
            "passives": [],
            "regen_stat_list": [
                {"stat": 1000026, "change_mb": 100000},
                {"stat": 1000027, "change_mb": 100000},
            ],
            "stat_list_static": [
                {"stat": 1000037, "change_mb": 100000000},
            ],
        },
        "speed": {
            "label": "Speed Ring",
            "passives": [],
            "regen_stat_list": [],
            "stat_list_static": [],
            "stat_list_static_level": [
                {"stat": 1000010, "change_mb": 15},
                {"stat": 1000011, "change_mb": 15},
                {"stat": 1000007, "change_mb": 15},
            ],
        },
        "all": {
            "label": "All Dev Rings",
            "passives": [{"skill": 70994, "level": 1}],
            "regen_stat_list": [
                {"stat": 1000000, "change_mb": 1000000},
                {"stat": 1000026, "change_mb": 100000},
                {"stat": 1000027, "change_mb": 100000},
            ],
            "stat_list_static": [
                {"stat": 1000002, "change_mb": 1000000},
                {"stat": 1000003, "change_mb": 1000000},
                {"stat": 1000037, "change_mb": 100000000},
            ],
            "stat_list_static_level": [
                {"stat": 1000010, "change_mb": 15},
                {"stat": 1000011, "change_mb": 15},
                {"stat": 1000007, "change_mb": 15},
            ],
        },
        "elemental_weapon": {
            "label": "Elemental Weapon (Lightning+Ice+Fire)",
            "passives": [
                {"skill": 91101, "level": 3},
                {"skill": 91104, "level": 3},
                {"skill": 91105, "level": 3},
            ],
            "gimmick_info": 1001961,
            "cooltime": 1000,  # ms; 1000 = 1s
            "item_charge_type": 0,
            "max_charged_useable_count": 100,
            "respawn_time_seconds": 0,
            "docking_child_data": {
                "gimmick_info_key": 1001961,
                "character_key": 0,
                "item_key": 0,
                "attach_parent_socket_name": "Gimmick_Weapon_00_Socket",
                "attach_child_socket_name": "",
                "docking_tag_name_hash": [3365725887, 0, 0, 0],
                "docking_equip_slot_no": 65535,
                "spawn_distance_level": 4294967295,
                "is_item_equip_docking_gimmick": 1,
                "send_damage_to_parent": 0,
                "is_body_part": 0,
                "docking_type": 0,
                "is_summoner_team": 0,
                "is_player_only": 0,
                "is_npc_only": 0,
                "is_sync_break_parent": 0,
                "hit_part": 0,
                "detected_by_npc": 0,
                "is_bag_docking": 0,
                "enable_collision": 0,
                "disable_collision_with_other_gimmick": 1,
                "docking_slot_key": "",
                "inherit_summoner": 0,
                "summon_tag_name_hash": [0, 0, 0, 0],
            },
        },
        "jump_boots": {
            "label": "Jump Boots (Dash+Breeze+Swimming)",
            "passives": [
                {"skill": 7201, "level": 1},
                {"skill": 7055, "level": 1},
                {"skill": 7202, "level": 1},
            ],
            "gimmick_info": 1004431,
            "cooltime": 1000,  # ms; 1000 = 1s
            "item_charge_type": 0,
            "max_charged_useable_count": 100,
            "respawn_time_seconds": 0,
            "docking_child_data": {
                "gimmick_info_key": 1004431,
                "character_key": 0,
                "item_key": 0,
                "attach_parent_socket_name": "Bip01 Footsteps",
                "attach_child_socket_name": "",
                "docking_tag_name_hash": [247236102, 0, 0, 0],
                "docking_equip_slot_no": 65535,
                "spawn_distance_level": 4294967295,
                "is_item_equip_docking_gimmick": 0,
                "send_damage_to_parent": 0,
                "is_body_part": 0,
                "docking_type": 0,
                "is_summoner_team": 0,
                "is_player_only": 0,
                "is_npc_only": 0,
                "is_sync_break_parent": 0,
                "hit_part": 0,
                "detected_by_npc": 0,
                "is_bag_docking": 0,
                "enable_collision": 0,
                "disable_collision_with_other_gimmick": 1,
                "docking_slot_key": "",
                "inherit_summoner": 0,
                "summon_tag_name_hash": [0, 0, 0, 0],
            },
        },
    }

    _CUSTOM_PRESETS: dict[str, dict[str, Any]] = {}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Presets")

        self._config = {}

        try:
            with open("custom_presets.json", "r+", encoding="utf-8") as f:
                self._CUSTOM_PRESETS = json.load(f)
        except BaseException as e:
            log.error(e)

        self._build_ui()

    def _build_ui(self) -> QWidget:
        """Hero Presets Window — grid rows of 3 large colored buttons."""

        # TEMP styles array
        styles = [
            ("#4682B4", "White"),
            ("#FFFFFF", "Black"),
            ("#00FF7F", "Black"),
            ("#00BFFF", "Black"),
            ("#9370DB", "Black"),
            ("#DC143C", "White"),
            ("#778899", "Black"),
            ("#FFD700", "Black"),
            ("#FF69B4", "Black"),
            ("#FF8C00", "Black"),
            ("#00FFFF", "Black"),
            ("#7FFF00", "Black"),
            ("#DDA0DD", "Black"),
            ("#2E8B57", "White"),
        ]

        def gen_styles(font_color: str, bkg_color: str):
            return f"""
            QPushButton, QToolTip {{
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton {{
                color: {font_color};
                background-color: {bkg_color};
                padding: 16px 24px;
            }}
            
            QToolTip {{
                color: black;
                background-color: white;
                border: 1px solid black;
            }}
            """

        pl = QVBoxLayout(self)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(8)
        grid_columns = 3

        grid = QGridLayout()
        grid_buttons: list[QPushButton] = []
        grid_label = QLabel(
            "One-Click Presets. Click an item in the list, "
            "then choose a preset below to apply."
        )
        self._build_standard_grid(grid_buttons)

        dev_grid = QGridLayout()
        dev_grid_buttons: list[QPushButton] = []
        dev_grid_label = QLabel(
            "DEV Ring Presets. Click an item in the list, "
            "then choose a preset below to apply."
        )
        self._build_dev_grid(dev_grid_buttons)

        custom_grid = QGridLayout()
        custom_grid_buttons: list[QPushButton] = []
        custom_grid_label = QLabel(
            "Custom Saved Presets. "
            "Choose a preset below to apply. "
            "Click the plus button to add a new custom preset."
        )
        self._build_custom_grid(custom_grid_buttons)

        # Apply Layout and Styles to all grid buttons
        # i = 0
        grid.setSpacing(8)
        for i, btn in enumerate(grid_buttons):
            bc, fc = styles[i % len(styles)]
            r, c = divmod(i, grid_columns)
            btn.setStyleSheet(gen_styles(fc, bc))
            grid.addWidget(btn, r, c)
            # i += 1

        # i = 0
        dev_grid.setSpacing(8)
        for i, btn in enumerate(dev_grid_buttons):
            bc, fc = styles[~(i % len(styles))]
            r, c = divmod(i, grid_columns)
            btn.setStyleSheet(gen_styles(fc, bc))
            dev_grid.addWidget(btn, r, c)
            # i += 1

        # i = 0
        custom_grid.setSpacing(8)
        for i, btn in enumerate(custom_grid_buttons):
            bc, fc = styles[i % len(styles)]
            r, c = divmod(i, grid_columns)
            btn.setStyleSheet(gen_styles(fc, bc))
            custom_grid.addWidget(btn, r, c)
            # i += 1

        pl.addWidget(grid_label)
        pl.addLayout(grid)
        pl.addWidget(dev_grid_label)
        pl.addLayout(dev_grid)
        pl.addWidget(custom_grid_label)
        pl.addLayout(custom_grid)
        pl.addStretch(1)

    def _build_standard_grid(self, grid_buttons: list[QPushButton]):
        "───────────────────── Standard Presets ──────────────────────────────"

        godmode_desc = textwrap.dedent("""
            - No Cooldown   
            - Max Charges
            - Max Sockets
            - Max Enchant
            - Invincible
            - Great Thief (All Crimes)
            - Max Attack/Defense
            - Max Attack/Move Speed
            - Max Regen
            - Max Crit/Resist
            - 8 Equipment Buffs at level 10
        """).strip()

        def apply_godmode():
            if (
                not hasattr(self, "_buff_rust_items")
                or self._buff_rust_items is None
            ):
                QMessageBox.warning(
                    self, "God Mode", "Extract with Rust parser first."
                )
                return
            if (
                not hasattr(self, "_buff_current_item")
                or self._buff_current_item is None
            ):
                QMessageBox.warning(self, "God Mode", "Select an item first.")
                return

            rust_info = self._buff_rust_lookup.get(
                self._buff_current_item.item_key
            )
            if rust_info is None:
                QMessageBox.warning(
                    self, "God Mode", "Item not found in Rust data."
                )
                return

            edl = rust_info.get("enchant_data_list", [])
            if not edl:
                _eq = rust_info.get(
                    "equip_type", rust_info.get("equipment_type", 0)
                )
                if isinstance(_eq, dict):
                    _eq = _eq.get("a", 0)
                _it = rust_info.get("item_type", rust_info.get("type", 0))
                if isinstance(_it, dict):
                    _it = _it.get("a", 0)
                _is_equippable = bool(_eq) or int(_it or 0) in {
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                }
                if not _is_equippable:
                    QMessageBox.warning(
                        self,
                        "God Mode",
                        "This item has no enchant data.\n"
                        "Only equippable items (weapons, armor, accessories) can have buffs.",
                    )
                    return
                edl = []

            display_name = self._name_db.get_name(
                self._buff_current_item.item_key
            )

            reply = QMessageBox.warning(
                self,
                "Potter's God Mode",
                f"Apply God Mode to {display_name}?\n\n"
                f"This will inject into ALL enchant levels:\n"
                f"{godmode_desc}\n\n"
                f"Click 'Export Field JSON v3' after to write.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            self.apply_preset("god_mod", True)
            self.apply_preset("great_thief_all", True)
            self.apply_preset("open_sockets", True)
            self.apply_preset("max_charges", True)
            self.apply_preset("max_enchant", True)
            self.apply_preset("no_cooldown", True)

        def apply_great_thief(self) -> None:
            # from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

            dlg = QDialog(self)
            dlg.setWindowTitle("Great Thief — Pick Variant")
            dlg.resize(480, 220)
            dl = QVBoxLayout(dlg)

            info = QLabel(
                "Pick which variant of Great Thief to apply.\n\n"
                "Block Theft only: skills 9128 + 76009. Suppresses pickpocket crime detection.\n"
                "Other crimes (vandalism, assault) will still flag you.\n\n"
                "Block ALL crime: also adds 76011 + 76012. Full crime immunity —\n"
                "theft, vandalism, and all other crime types.\n\n"
                "Passives stack with existing; gimmick replaces."
            )
            info.setWordWrap(True)
            info.setStyleSheet(f"color: {COLORS['text_dim']}; padding: 4px;")
            dl.addWidget(info)

            btn_row = QHBoxLayout()
            b1 = QPushButton("Block Theft only")
            b1.clicked.connect(
                lambda: (dlg.accept(), self._eb_apply_preset("great_thief"))
            )
            btn_row.addWidget(b1)

            b2 = QPushButton("Block ALL crime")
            b2.setObjectName("accentBtn")
            b2.clicked.connect(
                lambda: (
                    dlg.accept(),
                    self._eb_apply_preset("great_thief_all"),
                )
            )
            btn_row.addWidget(b2)

            cancel = QPushButton("Cancel")
            cancel.clicked.connect(dlg.reject)
            btn_row.addWidget(cancel)
            dl.addLayout(btn_row)

            dlg.exec()

        sockets_btn = QPushButton("5 Sockets")
        sockets_btn.setToolTip(
            "Item will drop with 5 open sockets by default."
        )
        sockets_btn.clicked.connect(lambda: self.apply_preset("open_sockets"))
        grid_buttons.append(sockets_btn)

        enchant_btn = QPushButton("Max Refine")
        enchant_btn.setToolTip("Item will drop at lvl 10 by default.")
        enchant_btn.clicked.connect(lambda: self.apply_preset("max_enchant"))
        grid_buttons.append(enchant_btn)

        cooldown_btn = QPushButton("No Cooldown")
        cooldown_btn.setToolTip("Item will have 1s cooldown by default.")
        cooldown_btn.clicked.connect(lambda: self.apply_preset("no_cooldown"))
        grid_buttons.append(cooldown_btn)

        charges_btn = QPushButton("Max Charges")
        charges_btn.setToolTip("Item will have 100 charges by default.")
        charges_btn.clicked.connect(lambda: self.apply_preset("max_charges"))
        grid_buttons.append(charges_btn)
        stacks_btn = QPushButton("Max Stacks")
        stacks_btn.setToolTip("Item will have a max stack size of 999999.")
        stacks_btn.clicked.connect(lambda: self.apply_preset("max_stacks"))
        grid_buttons.append(stacks_btn)

        abyss_socket_btn = QPushButton("Abyss + 5 Sockets")
        abyss_socket_btn.setToolTip(
            "Unlock abyss restriction (equipable_hash = 0) AND\n"
            "extend to 5 sockets on the selected item."
        )
        # abyss_socket_btn.clicked.connect(self._eb_abyss_plus_sockets)
        grid_buttons.append(abyss_socket_btn)

        godmode_btn = QPushButton("God Mode")
        godmode_btn.setToolTip(f"Inject full God Mode stats:\n{godmode_desc}")
        godmode_btn.clicked.connect(apply_godmode)
        grid_buttons.append(godmode_btn)

        shadow_boots_btn = QPushButton("Shadow Boots")
        shadow_boots_btn.setToolTip(
            "Apply Potter's Shadow Boots config to selected item:\n"
            "Skills: Shadow Dash (7201) + Breeze Step (7055) + Swimming (7202)\n"
            "Gimmick: 1004431 (boots gimmick — activates the skills)"
        )
        shadow_boots_btn.clicked.connect(
            lambda: self.apply_preset("shadow_boots")
        )
        grid_buttons.append(shadow_boots_btn)

        lightning_btn = QPushButton("Lightning Weapon")
        lightning_btn.setToolTip(
            "Apply lightning weapon config (Potter's Hwando recipe):\n"
            "Skills: Lightning (91101) + Fire (91105) + Ice (91104) affinity\n"
            "Gimmick: 1001961 (weapon gimmick)"
        )
        lightning_btn.clicked.connect(
            lambda: self.apply_preset("lightning_weapon")
        )
        grid_buttons.append(lightning_btn)

        great_thief_btn = QPushButton("Great Thief")
        great_thief_btn.setToolTip(
            "Apply Great Thief activated skill (works on ANY item).\n"
            "Opens a picker: Block Theft only, or Block ALL crime.\n"
            "Gimmick: 1002041, 1 charge, 30-min cooldown."
        )
        great_thief_btn.clicked.connect(apply_great_thief)
        grid_buttons.append(great_thief_btn)

        no_fall_btn = QPushButton("No Fall Damage")
        no_fall_btn.setToolTip(
            "Adds fall damage reduction buff to the selected item.\n"
            "Sets equip_buffs: BuffLevel_Food_FallDamageReduce (1000185) level 10\n"
            "on all enchant levels, and stages buffinfo changes so the reduction\n"
            "values export correctly via Export Field JSON v3."
        )
        # no_fall_btn.clicked.connect(self._eb_apply_no_fall_damage)
        grid_buttons.append(no_fall_btn)

    def _build_dev_grid(self, grid_buttons: list[QPushButton]):
        "───────────────────── DEV Ring Presets ──────────────────────────────"

        immunity_btn = QPushButton("Immunity")
        immunity_btn.setToolTip("Adds DEV Immune Ring buff to item.")
        immunity_btn.clicked.connect(lambda: self.apply_dev_preset("immune"))
        grid_buttons.append(immunity_btn)

        str_hp_btn = QPushButton("STR/HP")
        str_hp_btn.setToolTip(
            "Inject DEV STR/HP Ring stats:\n- Max DDD (Damage)\n- Max HP Regen"
        )
        str_hp_btn.clicked.connect(lambda: self.apply_dev_preset("str_hp"))
        grid_buttons.append(str_hp_btn)

        dev_def_hp_btn = QPushButton("DEF/HP")
        dev_def_hp_btn.setToolTip(
            "Inject DEV DEF/HP Ring stats:\n"
            "- Max DPV (Defense)\n"
            "- Max HP Regen"
        )
        dev_def_hp_btn.clicked.connect(lambda: self.apply_dev_preset("def_hp"))
        grid_buttons.append(dev_def_hp_btn)

        dev_mp_stam_btn = QPushButton("MP/Stamina")
        dev_mp_stam_btn.setToolTip(
            "Inject DEV MP/Stamina Ring stats:\n"
            "- Max Spirit Regen\n"
            "- Max Stamina Regen\n"
            "- Max Stamina Cost Reduction"
        )
        dev_mp_stam_btn.clicked.connect(
            lambda: self.apply_dev_preset("mp_stam")
        )
        grid_buttons.append(dev_mp_stam_btn)

        speed = QPushButton("Speed")
        speed.setToolTip(
            "Inject DEV Speed Ring stats:\n"
            "- Max Attack Speed\n"
            "- Max Move Speed\n"
            "- Max Crit Rate"
        )
        speed.clicked.connect(lambda: self.apply_dev_preset("speed"))
        grid_buttons.append(speed)

        dev_mode_desc = textwrap.dedent("""
            Inject ALL DEV Ring stats:
            - Immunity
            - Max DDD (Damage)
            - Max DPV (Defense)
            - Max Attack Speed
            - Max Move Speed
            - Max Crit Rate
            - Max HP Regen
            - Max Spirit Regen
            - Max Stamina Regen
            - Max Stamina Cost Reduction
        """).strip()
        all = QPushButton("All")
        all.setToolTip(dev_mode_desc)
        all.clicked.connect(lambda: self.apply_dev_preset("all"))
        grid_buttons.append(all)

    def _build_custom_grid(self, grid_buttons: list[QPushButton]):
        "─────────────────────── Custom Presets ──────────────────────────────"

        def add_custom_preset():
            dlg = QDialog(self)
            dlg.setWindowTitle("Create a new preset?")
            layout = QVBoxLayout(dlg)
            buttons = QHBoxLayout()

            layout.addWidget(
                QLabel("Would you like to create a new Custom Preset?")
            )

            yes_btn = QPushButton("Yes")
            no_btn = QPushButton("No")
            no_more_btn = QPushButton("Don't Ask Again")
            no_more_btn.setObjectName("btnDestructive")

            buttons.addWidget(yes_btn)
            buttons.addWidget(no_btn)
            buttons.addWidget(no_more_btn)
            layout.addLayout(buttons)

            def set_no_ask():
                self._config["custom_preset_ask"] = False
                # self.config_save_requested.emit()
                dlg.close()

            def show_mod_details_editor():
                _dlg = QDialog(dlg)
                _dlg.setWindowTitle("Mod Details")

                _layout = QVBoxLayout(_dlg)

                title = QLineEdit()
                title.setPlaceholderText("Merged Stack")
                author = QLineEdit()
                author.setPlaceholderText("CrimsonGameMods Stacker")
                version = QDoubleSpinBox()
                version.setValue(1.0)
                version.setSingleStep(0.01)
                version.setRange(0.01, 100)
                description = QTextEdit()
                description.setPlaceholderText("Mod Description")
                note = QTextEdit()
                note.setPlaceholderText("Author Notes")
                _buttons = QHBoxLayout()
                save_btn = QPushButton("Save")
                discard_btn = QPushButton("Discard Changes")
                _buttons.addWidget(save_btn)
                _buttons.addWidget(discard_btn)

                details = self._config.get("last_mod_details")
                if details:
                    title.setText(details["title"])
                    author.setText(details["author"])
                    title.setText(details["title"])
                    version.setValue(float(details["version"]))
                    description.setText(details["description"])
                    note.setText(details["note"])

                _layout.addWidget(QLabel("Title"))
                _layout.addWidget(title)
                _layout.addWidget(QLabel("Author"))
                _layout.addWidget(author)
                _layout.addWidget(QLabel("Version"))
                _layout.addWidget(version)
                _layout.addWidget(description)
                _layout.addWidget(note)
                _layout.addLayout(_buttons)
                _dlg.setLayout(_layout)

                def save_mod_details():
                    self._config["last_mod_details"] = {
                        "title": title.text(),
                        "version": version.text(),
                        "author": author.text(),
                        "description": description.toPlainText(),
                        "note": note.toPlainText(),
                    }
                    self.config_save_requested.emit()
                    _dlg.close()

                save_btn.clicked.connect(save_mod_details)
                discard_btn.clicked.connect(_dlg.close)
                _dlg.exec()
                dlg.close()

            yes_btn.clicked.connect(show_mod_details_editor)
            no_btn.clicked.connect(dlg.close)
            no_more_btn.clicked.connect(set_no_ask)
            dlg.exec()

        for i, (key, preset) in enumerate(self._CUSTOM_PRESETS.items()):
            try:
                name = preset["name"]
                desc = preset["description"]
                # warning = preset.pop("warning", None)

                btn = QPushButton(name)
                btn.setToolTip(desc)
                btn.clicked.connect(lambda: self.apply_custom_preset(key))

            except KeyError:
                QMessageBox.warning(
                    self,
                    "Invalid Preset",
                    f"Preset {key} is in an invalid format!",
                )
                continue

        custom_add = QPushButton("+")
        custom_add.setToolTip("Create a new Custom Preset")
        custom_add.clicked.connect(add_custom_preset)
        grid_buttons.append(custom_add)

    def apply_preset(self, preset: str):
        log.info("Applying Preset: %s", preset)

    def apply_dev_preset(self, preset: str):
        log.info("Applying Dev Preset: %s", preset)

    def apply_custom_preset(self, preset: str):
        log.info("Applying Custom Preset: %s", preset)
