from __future__ import annotations

import os
import json
import string
import subprocess
import logging

from PySide6.QtCore import (
    QPoint,
    Qt,
)

from collections.abc import Sequence
from typing import Optional

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from data.item_editor_database.database_entry import Buff, Skill

from .signals import SIGNALS, SLOTS


from .dmm_types import EquipmentBuff, ItemInfo, PassiveSkillLevel
from enum import StrEnum, auto
from benedict import benedict

from typing import TYPE_CHECKING

from ...theme import COLORS


if TYPE_CHECKING:
    #     from .helpers import HistoryEntry, ItemEditorInfoDetails

    "STUB"

log = logging.getLogger(__name__)

__all__ = [
    "CONFIG",
    "COLORS",
    "STATE",
    "POJO",
    "HistoryEntry",
    "ItemEditorInfo",
    "ItemEditorInfoDetails",
    "copy",
    "can_write_game_dir",
    "is_game_running",
    "find_game_path",
    "safe_iv",
    "load_passive_skill_index",
    "load_skill_index",
    "load_skill_list",
    "load_buff_index",
    "load_buff_list",
    "log",
]


class POJO:
    def __str__(self) -> str:
        return json.dumps(
            {k: v for k, v in vars(self).items()},
            indent=2,
            ensure_ascii=False,
            default=str,
        )


class _State(benedict):
    skill_index: dict[str, Skill]
    skill_list: list[Skill]
    buff_index: dict[str, Buff]
    buff_list: list[Buff]


STATE: _State = benedict(keyattr_dynamic=True)


def load_buff_list(force=False) -> list[Buff]:
    """Load the buff list from the buffs database file.

    Returns:
        list[Buff]: A list of Buff objects.
            Returns empty list if loading fails.
    """
    if force and STATE.buff_list:
        old = STATE.pop("buff_list")
        del old

    if not STATE.buff_list:
        print("recreating buff list")
        try:
            with open(
                "data/item_editor_database/buffs_list.json",
                "r",
                encoding="utf-8",
            ) as f:
                # print(catalog)
                STATE.buff_list = json.load(f) or [0]
                # buff_list = copy(catalog) or {}
                STATE.buff_list.pop(0)
        except BaseException as e:
            log.error(f"An error occurred while loading the buff index!\n{e}")
            return []

    return STATE.buff_list


def load_skill_list(force=False) -> list[Skill]:
    """Load the passive skill list from the skills database file.

    Returns:
        list[Skill]: A list of Skill objects.
            Returns empty list if loading fails.
    """
    if force and STATE.skill_list:
        old = STATE.pop("skill_list")
        del old

    if not STATE.skill_list:
        print("recreating skill list")
        try:
            with open(
                "data/item_editor_database/skills_list.json",
                "r",
                encoding="utf-8",
            ) as f:
                # print(catalog)
                STATE.skill_list = json.load(f) or [0]
                # skill_list = copy(catalog) or {}
                STATE.skill_list.pop(0)
        except BaseException as e:
            log.error(f"An error occurred while loading the skill index!\n{e}")
            return []

    return STATE.skill_list


def load_buff_index(force=False) -> dict[str, Skill]:
    """Load the buff index from the buffs database file.

    Returns:
        dict[str, Buff]: A dictionary mapping buff IDs to Buff objects.
            Returns empty dict if loading fails.
    """
    if force and STATE.buff_index:
        old = STATE.pop("buff_index")
        del old

    if not STATE.buff_index:
        print("recreating buff index")
        try:
            with open(
                "data/item_editor_database/buffs.json", "r", encoding="utf-8"
            ) as f:
                STATE.buff_index = json.load(f) or {}
                STATE.buff_index.pop("999999", None)
        except BaseException as e:
            log.error(f"An error occurred while loading the buff index!\n{e}")
            return {}

    return STATE.buff_index


def load_skill_index(force=False) -> dict[str, Skill]:
    """Load the passive skill index from the skills database file.

    Returns:
        dict[str, Skill]: A dictionary mapping skill IDs to Skill objects.
            Returns empty dict if loading fails.
    """
    if force and STATE.skill_index:
        old = STATE.pop("skill_index")
        del old

    if not STATE.skill_index:
        print("recreating skill index")
        try:
            with open(
                "data/item_editor_database/skills.json", "r", encoding="utf-8"
            ) as f:
                # catalog = json.load(f)
                # print(catalog)
                STATE.skill_index = json.load(f) or {}
                # skill_index = copy(catalog) or {}
                STATE.skill_index.pop("999999", None)
        except BaseException as e:
            log.error(f"An error occurred while loading the skill index!\n{e}")
            return {}

    return STATE.skill_index


def load_state(force=True):
    load_buff_index(force)
    load_buff_list(force)
    load_skill_index(force)
    load_skill_list(force)


class HistoryEntry:
    class EntryType(StrEnum):
        PRESET = auto()
        EDIT = auto()
        REPLACE = auto()
        BULK = auto()

    def __init__(self, entry_type: EntryType, data: object, desc: str):
        self.type = entry_type
        self.entry_data = data
        self.description = desc

    def undo(self):
        match self.type:
            case self.EntryType.PRESET:
                "stub"
            case self.EntryType.BULK:
                "stub"


class ItemEditorInfoDetails:
    EDITABLE_ENTRIES = {
        "equip_passive_skill_list",
        "cooltime",
        "docking_child_data",
        "drop_default_data",
        "enchant_data_list",
        "gimmick_info",
        "gimmick_visual_prefab_data_list",
        "is_dyeable",
        "item_charge_type",
        "item_tier",
        "max_charged_useable_count",
        "max_endurance",
        "max_stack_count",
        "price_list",
    }

    data: ItemInfo = {}

    _instance = None
    _reference: ItemEditorInfo = None
    _history: list[HistoryEntry] = []

    def __new__(cls, idx: int):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.idx = -1

        if idx < 0 or idx >= len(cls._reference):
            raise IndexError("Index not in range!")

        return cls._instance

    def __init__(self, idx: int):
        if idx != self.idx:
            self.idx = idx
            ItemEditorInfoDetails.data = (
                ItemEditorInfoDetails._reference._data[idx]
            )

    def __len__(self):
        return self.data.__len__()

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def items(self):
        return (
            (key, value)
            for key, value in (
                ("passives", self.passives()),
                ("buffs", self.buffs()),
                ("stack_size", self.stack_size()),
            )
            if value is not None
        )
        return self.data.items()

    def history(self) -> Sequence[HistoryEntry]:
        return self._history

    def editable(self):
        return self.items()
        return (
            (key, value)
            for key, value in self.items()
            if key in self.EDITABLE_ENTRIES
        )

    def passives(
        self,
        new: Optional[list[PassiveSkillLevel]] = None,
        log=True,
        refresh=True,
    ) -> list[PassiveSkillLevel]:
        old = self.data["equip_passive_skill_list"]

        if new is None:
            return old

        self._reference.dirty(self)
        snapshot = copy(old) if log else None

        old[:] = new

        if log:
            entry = POJO()
            entry.idx = self.idx
            entry.key = self.data["key"]
            entry.old = snapshot
            entry.new = copy(new)
            entry = HistoryEntry(
                HistoryEntry.EntryType.REPLACE,
                entry,
                "Update Passive List",
            )

            self._history.append(entry)
            SIGNALS.s_history_entry_added.emit(entry)

        # Reset view if changing currently selected item
        if refresh and self.idx == SLOTS.last_selected():
            SIGNALS.s_item_selected.emit(self.idx)

        return old

    def buffs(
        self,
        new: Optional[list[EquipmentBuff]] = None,
        log: bool = True,
        refresh: bool = True,
    ) -> list[EquipmentBuff]:
        """Get or set equip_buffs across all enchant levels.

        All levels in ``enchant_data_list`` share the same buff data object,
        so we read from the first entry and write to every entry.

        If *new* is ``None`` and the item has no ``enchant_data_list`` the
        method simply returns an empty list.  If *new* is provided but
        ``enchant_data_list`` does not yet exist a single baseline entry is
        bootstrapped so the buff list has somewhere to live.
        """
        enchant_data_list = self.data.get("enchant_data_list", [])

        # --- read-only path: nothing to do if the structure is absent ---
        if new is None:
            return (
                []
                if not enchant_data_list
                else enchant_data_list[0].get("equip_buffs", [])
            )

        # --- write path ---
        if not enchant_data_list:
            # Bootstrap a single EnchantData entry so equip_buffs has a home.
            baseline = {
                "level": 0,
                "enchant_stat_data": {
                    "max_stat_list": [],
                    "regen_stat_list": [],
                    "stat_list_static": [],
                    "stat_list_static_level": [],
                },
                "buy_price_list": [],
                "equip_buffs": [],
            }
            enchant_data_list = [baseline]
            self.data["enchant_data_list"] = enchant_data_list

        old = enchant_data_list[0].get("equip_buffs", [])
        snapshot = copy(old) if log else None

        # Write to every enchant level entry
        for entry in enchant_data_list:
            entry["equip_buffs"] = new

        if log:
            hist_entry = POJO()
            hist_entry.idx = self.idx
            hist_entry.key = self.data["key"]
            hist_entry.old = snapshot
            hist_entry.new = copy(new)
            hist = HistoryEntry(
                HistoryEntry.EntryType.REPLACE,
                hist_entry,
                "Update Buff List",
            )
            self._history.append(hist)
            SIGNALS.s_history_entry_added.emit(hist)

        # Reset view if changing currently selected item
        if refresh and self.idx == SLOTS.last_selected():
            SIGNALS.s_item_selected.emit(self.idx)

        return old

    def stats(
        self,
        new: Optional[list[EquipmentBuff]] = None,
        log: bool = True,
        refresh: bool = True,
    ) -> list[EquipmentBuff]:
        enchant_data_list = self.data.get("enchant_data_list", [])

        # --- read-only path: nothing to do if the structure is absent ---
        if new is None:
            return enchant_data_list

        # --- write path ---
        if not enchant_data_list:
            # Bootstrap a single EnchantData entry so equip_buffs has a home.
            baseline = {
                "level": 0,
                "enchant_stat_data": {
                    "max_stat_list": [],
                    "regen_stat_list": [],
                    "stat_list_static": [],
                    "stat_list_static_level": [],
                },
                "buy_price_list": [],
                "equip_buffs": [],
            }
            enchant_data_list = [baseline]
            self.data["enchant_data_list"] = enchant_data_list

        old = enchant_data_list[0].get("equip_buffs", [])
        snapshot = copy(old) if log else None

        # Write to every enchant level entry
        for entry in enchant_data_list:
            entry["equip_buffs"] = new

        if log:
            hist_entry = POJO()
            hist_entry.idx = self.idx
            hist_entry.key = self.data["key"]
            hist_entry.old = snapshot
            hist_entry.new = copy(new)
            hist = HistoryEntry(
                HistoryEntry.EntryType.REPLACE,
                hist_entry,
                "Update Buff List",
            )
            self._history.append(hist)
            SIGNALS.s_history_entry_added.emit(hist)

        # Reset view if changing currently selected item
        if refresh and self.idx == SLOTS.last_selected():
            SIGNALS.s_item_selected.emit(self.idx)

        return old

    def stack_size(
        self,
        new: int = None,
        log: bool = True,
        refresh: bool = True,
    ) -> int:
        if new is None:
            return self.data["max_stack_count"]

        self.data["max_stack_count"] = new


class ItemEditorInfo:
    def __init__(self, data: list[ItemInfo] = []):
        self._data = data
        self._backup = {}
        ItemEditorInfoDetails._reference = self

    def __len__(self):
        return len(self._data)

    def details(self, idx: int) -> ItemEditorInfoDetails:
        return ItemEditorInfoDetails(idx)

    def dirty(self, item: ItemEditorInfoDetails, mark=False) -> bool:
        idx = item.idx

        if mark:
            self._backup[idx] = copy(item.data)
            return True

        return True if self._backup.get(idx) else False


class _Config:
    _CONFIG_FILE = "editor_config.json"

    def __init__(self):
        self._config: dict = self.load()

    def path(self) -> str:
        import sys

        if getattr(sys, "frozen", False):
            return os.path.join(
                os.path.dirname(os.path.abspath(sys.executable)),
                self._CONFIG_FILE,
            )
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)), self._CONFIG_FILE
        )

    def load(self) -> dict:
        path = self.path()
        if os.path.isfile(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def save(self) -> None:
        try:
            with open(self.path(), "w") as f:
                json.dump(self._config, f, indent=2)
        except OSError:
            pass

    def __len__(self) -> int:
        return len(self._config)

    def __getitem__(self, key):
        return self._config.get(key)

    def __setitem__(self, key, value):
        self._config[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._config


CONFIG = _Config()


def copy(obj):
    try:
        return json.loads(json.dumps(obj))
    except TypeError:
        return None


def can_write_game_dir(game_path: str) -> bool:
    try:
        _t = os.path.join(game_path, ".se_write_test")
        with open(_t, "w") as _f:
            _f.write("t")
        os.remove(_t)
        return True
    except Exception:
        return False


def is_game_running() -> bool:
    try:
        out = subprocess.check_output(
            [
                "tasklist",
                "/FI",
                "IMAGENAME eq CrimsonDesert.exe",
                "/FO",
                "CSV",
                "/NH",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return "CrimsonDesert.exe" in out
    except Exception:
        return False


def find_game_path() -> str:
    candidates = []

    for letter in string.ascii_uppercase:
        candidates.append(
            f"{letter}:\\SteamLibrary\\steamapps\\common\\Crimson Desert"
        )

    candidates.extend(
        [
            r"C:\Program Files (x86)\Steam\steamapps\common\Crimson Desert",
            r"C:\Program Files\Steam\steamapps\common\Crimson Desert",
            r"C:\Program Files\Epic Games\CrimsonDesert",
        ]
    )

    for path in candidates:
        papgt = os.path.join(path, "meta", "0.papgt")
        if os.path.isfile(papgt):
            return path

    return ""


def safe_iv(v, default=0):
    """Safely extract int from plain int, float, or dmm_parser nested dict.
    dmm_parser returns numeric structs as {'a': int, 'b': int, 'c': int}.
    """
    if v is None:
        return default
    if isinstance(v, (int, float, bool)):
        return int(v)
    if isinstance(v, dict):
        for k in ("a", "value", "_v", "v", "val", "n", "data"):
            if k in v:
                sub = v[k]
                if isinstance(sub, (int, float, bool)):
                    return int(sub)
                if sub is None:
                    return default
        return default
    try:
        return int(v)
    except Exception:
        return default


def load_passive_skill_index() -> dict[str, str]:
    """Load the passive skill index from the catalog file.

    Returns:
        dict[str, str]: A dictionary mapping skill IDs to skill names.
                       Returns empty dict if loading fails.
    """
    try:
        with open(
            "data/passive_skill_catalog.json", "r", encoding="utf-8"
        ) as f:
            catalog = json.load(f)
            skill_index = copy(catalog["full_skill_index"]) or {}
            skill_index.pop("999999", None)
            return skill_index
    except BaseException as e:
        log.error(f"An error occurred while loading the skill index!\n{e}")
        return {}


def make_collapsible(
    label: str,
    content: QWidget,
    start_open: bool = True,
    config_key: str = None,
) -> QWidget:
    cfg = CONFIG
    accent = COLORS.get("accent", "#daa850")

    if config_key and cfg[config_key] is not None:
        start_open = cfg[config_key]
    wrapper = QWidget()
    vbox = QVBoxLayout(wrapper)
    vbox.setContentsMargins(0, 0, 0, 0)
    vbox.setSpacing(0)

    toggle = QPushButton(("▾ " if start_open else "▸ ") + label)
    toggle.setStyleSheet(
        f"QPushButton {{ text-align: left; font-weight: bold; font-size: 11px;"
        f" padding: 3px 8px; background: transparent;"
        f" color: {accent}; border: none; border-bottom: 1px solid {accent}; }}"
        f"QPushButton:hover {{ background: rgba(218,168,80,0.10); }}"
    )
    toggle.setCursor(Qt.PointingHandCursor)
    toggle.setFixedHeight(22)

    content.setVisible(start_open)

    def _on_toggle():
        vis = not content.isVisible()
        content.setVisible(vis)
        toggle.setText(("▾ " if vis else "▸ ") + label)
        if config_key:
            cfg[config_key] = vis
            CONFIG.save()

    toggle.clicked.connect(_on_toggle)

    vbox.addWidget(toggle)
    vbox.addWidget(content)
    return wrapper


def center_window_in_parent(window: QWidget, parent: QWidget, embedded=False):
    # --- CENTERING LOGIC START ---
    # Get dimensions of the main window
    main_geo = parent.geometry()
    # Get dimensions of the sub-window
    sub_geo = window.geometry()
    # Get absolute position of main window
    abs_geo = parent.mapToGlobal(QPoint(0, 0))

    (x, y) = (
        (abs_geo.x(), abs_geo.y())
        if embedded
        else (main_geo.x(), main_geo.y())
    )

    # Calculate the new X and Y coordinates to perfectly center it
    new_x = x + (main_geo.width() - sub_geo.width()) // 2
    new_y = y + (main_geo.height() - sub_geo.height()) // 2

    # Move the window to the calculated position
    window.move(new_x, new_y)
