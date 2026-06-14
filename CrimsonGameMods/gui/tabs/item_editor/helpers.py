from __future__ import annotations

import inspect
import os
import json
import string
import subprocess
import logging
import json

from PySide6.QtCore import (
    QObject,
    QPoint,
    Qt,
)

from collections.abc import Sequence
from typing import Any, Optional, Self, TypedDict

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .signals import SIGNALS


from .dmm_types import EquipmentBuff, ItemInfo, PassiveSkillLevel
from collections import UserDict, UserList
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


class _State(TypedDict):
    "stub"


STATE: _State = benedict(keyattr_dynamic=True)


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


# type HistoryRegistry = Sequence[HistoryEntry]


# class ItemEditorInfoDetails:
#     pass
# class ItemEditorInfo:
#     pass


class ItemEditorInfoDetails:
    EDITABLE_ENTRIES = {
        "cooltime",
        "docking_child_data",
        "drop_default_data",
        "enchant_data_list",
        "equip_passive_skill_list",
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
    _reference: list[ItemInfo] = []
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
            ItemEditorInfoDetails.data = ItemEditorInfoDetails._reference[idx]

    def __len__(self):
        return self.data.__len__()

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def items(self):
        return self.data.items()

    def history(self) -> Sequence[HistoryEntry]:
        return self._history

    def editable(self):
        return (
            (key, value)
            for key, value in self.data.items()
            if key in self.EDITABLE_ENTRIES
        )

    def passives(
        self, new: Optional[list[PassiveSkillLevel]] = None, log=True
    ) -> list[PassiveSkillLevel]:
        old = self.data["equip_passive_skill_list"]

        if new:
            old[:] = new

            if log:
                entry = POJO()
                entry.idx = self.idx
                entry.key = self.data["key"]
                entry.old = copy(old)
                entry.new = copy(new)
                entry = HistoryEntry(
                    HistoryEntry.EntryType.REPLACE,
                    entry,
                    "Update Passive List",
                )

                self._history.append(entry)
                SIGNALS.s_history_entry_added.emit(entry)

        return old

    def buffs(
        self, new: Optional[list[EquipmentBuff]] = None, log: bool = True
    ) -> list[EquipmentBuff]:
        """Get or set equip_buffs across all enchant levels.

        All levels in ``enchant_data_list`` share the same buff data object,
        so we read from the first entry and write to every entry.

        If *new* is ``None`` and the item has no ``enchant_data_list`` the
        method simply returns an empty list.  If *new* is provided but
        ``enchant_data_list`` does not yet exist a single baseline entry is
        bootstrapped so the buff list has somewhere to live.
        """
        enchant_data_list = self.data.get("enchant_data_list", []) or []

        # --- read-only path: nothing to do if the structure is absent ---
        if new is None:
            if not enchant_data_list:
                return []
            return enchant_data_list[0].get("equip_buffs", [])

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

        return old


class ItemEditorInfo:
    def __init__(self, data: list[ItemInfo] = []):
        self._data = data
        ItemEditorInfoDetails._reference = data

    def __len__(self):
        return len(self._data)

    def details(self, idx: int) -> ItemEditorInfoDetails:
        return ItemEditorInfoDetails(idx)


# class ItemEditorInfo:
#     """Central data store for all items with cached proxy creation.

#     Stores raw item data and history. Creates lightweight proxy objects
#     (ItemEditorInfoDetails) on-demand and caches them to prevent duplicate
#     object creation.
#     """

#     EDITABLE_ENTRIES = [
#         "cooltime",
#         "docking_child_data",
#         "drop_default_data",
#         "enchant_data_list",
#         "equip_passive_skill_list",
#         "gimmick_info",
#         "gimmick_visual_prefab_data_list",
#         "is_dyeable",
#         "item_charge_type",
#         "item_tier",
#         "max_charged_useable_count",
#         "max_endurance",
#         "max_stack_count",
#         "price_list",
#     ]

#     # Global history across all items
#     HISTORY_REGISTRY = []

#     def __init__(self, data: list[ItemInfo] = None):
#         self._data: list[ItemInfo] = data if data is not None else []
#         # Per-item history: { item_key: [HistoryEntry, ...] }
#         self._history: dict[int, list[HistoryEntry]] = {}
#         # Cache of proxy objects: { index: ItemEditorInfoDetails }
#         self._proxies: dict[int, ItemEditorInfoDetails] = {}

#     def __len__(self):
#         return len(self._data)

#     def get_item(self, idx: int) -> ItemInfo:
#         """Get raw item dict by index (no object creation)."""
#         if idx < 0 or idx >= len(self._data):
#             raise IndexError("Index not in range!")
#         return self._data[idx]

#     def get_item_key(self, item: ItemInfo) -> int:
#         """Get the unique key for an item."""
#         return item.get("key", -1)

#     def get_history(self, item_key: int) -> list[HistoryEntry]:
#         """Get history for a specific item key."""
#         if item_key not in self._history:
#             self._history[item_key] = []
#         return self._history[item_key]

#     def add_history_entry(self, item_key: int, entry: HistoryEntry):
#         """Add a history entry for a specific item key."""
#         if item_key not in self._history:
#             self._history[item_key] = []
#         self._history[item_key].append(entry)
#         self.HISTORY_REGISTRY.append(entry)
#         SIGNALS.s_history_entry_added.emit(entry)

#     def update_item(self, item: ItemInfo, key: str, new_value):
#         """Update an item field."""
#         if key not in self.EDITABLE_ENTRIES:
#             raise KeyError("This data is not editable!")
#         item[key] = new_value

#     def update_item_with_history(self, item: ItemInfo, key: str, new_value, desc=None):
#         """Update an item field and record history."""
#         if key not in self.EDITABLE_ENTRIES:
#             raise KeyError("This data is not editable!")

#         old_value = copy(item.get(key))
#         self.update_item(item, key, new_value)

#         if desc is None:
#             desc = f"Value of {key} changed: {old_value} -> {new_value}"

#         entry = HistoryEntry(
#             HistoryEntry.EntryType.EDIT, (key, old_value), desc
#         )

#         item_key = self.get_item_key(item)
#         self.add_history_entry(item_key, entry)

#     @classmethod
#     def bulk_update_with_history(
#         cls,
#         items: list[ItemEditorInfoDetails],
#         key: str,
#         new_value,
#         desc: str = None,
#     ):
#         """Update a field across multiple items as a single bulk history entry.

#         Args:
#             items: List of item proxies to update.
#             key: The field name to update (must be in EDITABLE_ENTRIES).
#             new_value: Either a single value applied to all items,
#                        or a callable (item_proxy) -> value for per-item values.
#             desc: Optional description for the history entry.
#         """
#         if key not in cls.EDITABLE_ENTRIES:
#             raise KeyError("This data is not editable!")

#         if not items:
#             return

#         parent = items[0]._parent
#         snapshots: list[tuple[int, str, Any]] = []

#         for proxy in items:
#             item = proxy._data
#             item_key = parent.get_item_key(item)
#             old_value = copy(item.get(key))
#             snapshots.append((item_key, key, old_value))

#             resolved = new_value(proxy) if callable(new_value) else new_value
#             parent.update_item(item, key, resolved)

#         if desc is None:
#             desc = f"Bulk update of {key} on {len(items)} item(s)"

#         entry = HistoryEntry(
#             HistoryEntry.EntryType.BULK, snapshots, desc
#         )

#         for item_key, _, _ in snapshots:
#             if item_key not in parent._history:
#                 parent._history[item_key] = []
#             parent._history[item_key].append(entry)

#         cls.HISTORY_REGISTRY.append(entry)
#         SIGNALS.s_history_entry_added.emit(entry)

#     def get_editable_fields(self, item: ItemInfo) -> list[tuple[str, Any]]:
#         """Get list of editable field names and their current values."""
#         return [(key, item.get(key, None)) for key in self.EDITABLE_ENTRIES] if item else []

#     def get_passives(self, item: ItemInfo, new_list: list[PassiveSkillLevel] = None) -> list[PassiveSkillLevel] | None:
#         """Get or set passive skills for an item."""
#         if new_list is not None:
#             item["equip_passive_skill_list"] = new_list
#         return item.get("equip_passive_skill_list", None)

#     def details(self, idx: int) -> ItemEditorInfoDetails:
#         """Get or create a cached proxy for the item at the given index.

#         Proxies are cached, so requesting the same index multiple times
#         returns the same proxy object (no duplicate creation).
#         """
#         if idx < 0 or idx >= len(self._data):
#             raise IndexError("Index not in range!")

#         if idx not in self._proxies:
#             self._proxies[idx] = ItemEditorInfoDetails(self, idx)
#         return self._proxies[idx]


# class ItemEditorInfoDetails:
#     """Lightweight proxy for a single item's data.

#     Holds only (parent_ref, index, item_key) - 3 attributes.
#     Delegates all operations to the parent ItemEditorInfo store.
#     Multiple proxies can exist simultaneously, each pointing to a different item.
#     Proxies are cached by ItemEditorInfo to prevent duplicate creation.
#     """

#     def __init__(self, parent: ItemEditorInfo, idx: int):
#         self._parent = parent
#         self._idx = idx
#         self._item_key = parent.get_item_key(parent.get_item(idx))

#     @property
#     def _data(self) -> ItemInfo:
#         """Get the underlying item data from parent (no copy, just reference)."""
#         return self._parent.get_item(self._idx)

#     def __getitem__(self, key):
#         return self._data.get(key, None)

#     def items(self):
#         return self._data.items()

#     def update(self, key, new_value):
#         if key not in self._parent.EDITABLE_ENTRIES:
#             raise KeyError("This data is not editable!")
#         self._data[key] = new_value

#     def update_with_history(self, key, new_value, desc=None):
#         if key not in self._parent.EDITABLE_ENTRIES:
#             raise KeyError("This data is not editable!")

#         old_value = copy(self._data.get(key))
#         self.update(key, new_value)

#         if desc is None:
#             desc = f"Value of {key} changed: {old_value} -> {new_value}"

#         entry = HistoryEntry(
#             HistoryEntry.EntryType.EDIT, (key, old_value), desc
#         )

#         self._parent.add_history_entry(self._item_key, entry)

#     def add_history_entry(self, entry: HistoryEntry):
#         self._parent.add_history_entry(self._item_key, entry)

#     def editable(self):
#         data = self._data
#         return (
#             [(key, data.get(key, None)) for key in self._parent.EDITABLE_ENTRIES]
#             if data
#             else []
#         )

#     def get_history(self) -> HistoryRegistry:
#         return self._parent.get_history(self._item_key)

#     def get_registry(self) -> HistoryRegistry:
#         return self._parent.HISTORY_REGISTRY

#     def passives(
#         self, new_list: list[PassiveSkillLevel] = None
#     ) -> list[PassiveSkillLevel] | None:
#         if new_list is not None:
#             self._data["equip_passive_skill_list"] = new_list
#         return self._data.get("equip_passive_skill_list", None)


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
