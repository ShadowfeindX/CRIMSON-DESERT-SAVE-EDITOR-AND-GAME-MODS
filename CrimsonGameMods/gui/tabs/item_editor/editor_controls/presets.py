from __future__ import annotations

import json
from pathlib import Path

from gui.tabs.item_editor.helpers import (
    HistoryEntry,
    ItemEditorInfoDetails,
    copy,
    log,
)
from gui.tabs.item_editor.signals import SIGNALS


class Presets:
    Standard: dict[str, dict[str, dict]] = {
        "open_sockets": {
            "name": "5 Sockets",
            "description": "Adds 5 open sockets to all newly obtained versions of this item.",
            "warning": "Embedding abyss gears in-game on items that do not normally have socket slots can cause crashing.",
            "key": 0,
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
            "description": (
                "Apply Potter's Shadow Boots config to selected item:\n"
                "Skills: Shadow Dash (7201) + Breeze Step (7055) + Swimming (7202)\n"
                "Gimmick: 1004431 (boots gimmick — activates the skills)"
            ),
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
            "description": (
                "Apply lightning weapon config (Potter's Hwando recipe):\n"
                "Skills: Lightning (91101) + Fire (91105) + Ice (91104) affinity\n"
                "Gimmick: 1001961 (weapon gimmick)"
            ),
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
    }

    Dev = {
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

    Special = {
        "god_mode": {},
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

    Custom: dict[str, dict[str, object]] = {}

    _presets = None
    _current_item: ItemEditorInfoDetails = None

    def __init__(self):
        # self._set_current_item(ItemEditorInfoDetails._last_created_item)
        SIGNALS.s_item_selected.connect(self._set_current_item)

        custom_path = Path("custom_presets.json")

        custom_path.touch(exist_ok=True)

        try:
            with open(custom_path, "r", encoding="utf-8") as f:
                self.Custom = json.load(f)
        except BaseException as e:
            log.error(f"Error loading Custom Presets: {e}")
        else:
            self.Custom = {}

    def _set_current_item(self, item):
        self._current_item = item
        if item:
            log.info(f"Item Loaded: {item['key']}")

    def apply_std_preset(
        self, preset: str, skip: bool = False, warn: str = ""
    ):
        log.info("Applying Preset: %s", preset)

        preset_data: dict = copy(self.Standard[preset])
        # log.info(f"Testing Data Dump: {preset_data}")
        preset_data.pop("name", "")
        preset_data.pop("description", "")
        preset_data.pop("warning", "")

        original_values = {
            key: copy(self._current_item[key]) for key in preset_data.keys()
        }

        self._current_item.add_history_entry(
            HistoryEntry(
                HistoryEntry.EntryType.PRESET,
                {"id": preset, "old_values": original_values},
                f"Applied Preset: {preset}",
            )
        )

        SIGNALS.s_status_message.emit(f"Applying Preset: {preset}")

    def apply_dev_preset(
        self, preset: str, skip: bool = False, warn: str = ""
    ):
        log.info("Applying Dev Preset: %s", preset)

    def apply_custom_preset(
        self, preset: str, skip: bool = False, warn: str = ""
    ):
        log.info("Applying Custom Preset: %s", preset)

    @classmethod
    def get_presets(cls) -> Presets:
        if cls._presets is None:
            cls._presets = cls()
        return cls._presets
