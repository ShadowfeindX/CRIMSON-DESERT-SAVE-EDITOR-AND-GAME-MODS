from __future__ import annotations

import os
import json
import string
import subprocess
import logging

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from collections.abc import Sequence

from .dmm_types import ItemInfo
from enum import StrEnum, auto
from benedict import benedict

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .helpers import HistoryEntry, ItemEditorInfo, ItemEditorInfoDetails

    "STUB"

log = logging.getLogger(__name__)


def copy(obj):
    try:
        return json.loads(json.dumps(obj))
    except TypeError:
        return None


# type HistoryEntry = tuple[str, object, str]
class HistoryEntry:
    class EntryType(StrEnum):
        PRESET = auto()
        EDIT = auto()
        REPLACE = auto()
        # PENDING = "pending"
        # ACTIVE = "active"
        # auto() automatically assigns the lower-case member name ("completed")
        # COMPLETED = auto()

    def __init__(self, entry_type: EntryType, data: object, desc: str):
        self.type = entry_type
        self.entry_data = data
        self.description = desc

    def undo(self):
        match self.type:
            case self.EntryType.PRESET:
                "stub"

    # def data() ->


type HistoryRegistry = Sequence[HistoryEntry]


class ItemEditorInfo:
    def __init__(self, data: list[ItemInfo] = []):
        self._data = data

    def __len__(self):
        return len(self._data)

    def details(self, idx):
        if idx < 0 or idx > len(self._data):
            raise IndexError("Index not in range!")

        return ItemEditorInfoDetails(self._data[idx])


class ItemEditorInfoDetails:
    EDITABLE_ENTRIES = [
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
    ]

    REGISTRY = []

    def __init__(self, data: ItemInfo = {}):
        # self._item_info = data
        self._data: ItemInfo = benedict(data)
        self._history = []

    def __getitem__(self, key):
        return self._data.get(key, None)

    def items(self):
        return self._data.items()

    def update(self, key, new_value):
        if key not in self.EDITABLE_ENTRIES:
            raise KeyError("This data is not editable!")

        self._data[key] = new_value

    def update_with_history(self, key, new_value, desc=None):
        if key not in self.EDITABLE_ENTRIES:
            raise KeyError("This data is not editable!")

        old_value = copy(self._data.get(key))
        self.update(key, new_value)

        if desc is None:
            desc = f"Value of {key} changed: {old_value} -> {new_value}"

        entry = HistoryEntry(
            HistoryEntry.EntryType.EDIT, (key, old_value), desc
        )

        self._history.append(entry)
        self.REGISTRY.append(entry)
        _SIGNALS_INSTANCE.s_history_entry_added.emit(entry)

    def add_history_entry(self, entry: HistoryEntry):
        self._history.append(entry)
        self.REGISTRY.append(entry)
        _SIGNALS_INSTANCE.s_history_entry_added.emit(entry)

    def editable(self):
        return (
            [(key, self._data.get(key, None)) for key in self.EDITABLE_ENTRIES]
            if self._data
            else []
        )

    def get_history(self) -> HistoryRegistry:
        return self._history

    def get_registry(self) -> HistoryRegistry:
        return self.REGISTRY


class _Slots(QObject):
    @Slot(HistoryEntry)
    def log_history(entry: HistoryEntry):
        log.info(f"History entry added: ({entry.description})")


_SLOTS_INSTANCE: _Slots = None


class _Signals(QObject):
    s_status_message = Signal(str, int | None)
    s_iteminfo_extracted = Signal(ItemEditorInfo)
    s_item_selected = Signal(ItemEditorInfoDetails)
    s_history_entry_added = Signal(HistoryEntry)

    def __init__(self):
        super().__init__()

        log.info("Signals Created!")

        self.s_history_entry_added.connect(_SLOTS_INSTANCE.log_history)


_SIGNALS_INSTANCE: _Signals = None


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


_CONFIG_INSTANCE: _Config = None


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


_initialized = False


def _init_helpers():
    global _SIGNALS_INSTANCE, _SLOTS_INSTANCE, _CONFIG_INSTANCE
    _SIGNALS_INSTANCE, _SLOTS_INSTANCE, _CONFIG_INSTANCE = (
        _Signals(),
        _Slots(),
        _Config(),
    )


def __getattr__(name: str):
    """Intercepts module attribute access."""
    global _SIGNALS_INSTANCE, _SLOTS_INSTANCE, _CONFIG_INSTANCE
    if _initialized is False:
        _init_helpers()

    match name:
        case "SIGNALS":
            return _SIGNALS_INSTANCE
        case "SLOTS":
            return _SLOTS_INSTANCE
        case "CONFIG":
            return _CONFIG_INSTANCE
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# def __getattr__(name: str):
#     """Intercepts module attribute access."""
#     global _SIGNALS_INSTANCE, _CONFIG_INSTANCE
#     if name == "SIGNALS":
#         if _SIGNALS_INSTANCE is None:
#             _SIGNALS_INSTANCE = _Signals()
#         return _SIGNALS_INSTANCE
#     elif name == "CONFIG":
#         if _CONFIG_INSTANCE is None:
#             _CONFIG_INSTANCE = _Config()
#         return _CONFIG_INSTANCE
#     raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# # Wrap your dictionary
# data = benedict({
#     "sub_dict": {
#         "sub_dict": {
#             "a": "Found the value!"
#         }
#     }
# })

# # Access using the dot-separated string
# print(data["sub_dict.sub_dict.a"])

# NOT_FOUND = object()


# class HistoryRegistry:
#     """Manages transactional logging and maps proxy references across data trees."""

#     def __init__(self):
#         self.history = []
#         self.track = True

#     def log(self, container, action, key, old_value):
#         if self.track:
#             self.history.append((container, action, key, old_value))

#     def undo(self, root):
#         if not self.history:
#             print("No history to undo.")
#             return

#         self.track = False
#         try:
#             container, action, key, old_value = self.history.pop()

#             if isinstance(container, ReversibleDict):
#                 if action == "SET":
#                     if old_value is NOT_FOUND:
#                         if key in container.data:
#                             del container.data[key]
#                     else:
#                         container.data[key] = container._wrap(key, old_value)
#                 elif action == "DEL":
#                     container.data[key] = container._wrap(key, old_value)

#             elif isinstance(container, ReversibleList):
#                 if action == "SET":
#                     container.data[key] = container._wrap(key, old_value)
#                 elif action == "APPEND":
#                     container.data.pop()
#                 elif action == "POP":
#                     container.data.insert(key, container._wrap(key, old_value))
#         finally:
#             self.track = True


# class ReversibleList(UserList):
#     def __init__(self, initlist=None, registry=None):
#         super().__init__()
#         self._registry = (
#             registry if registry is not None else HistoryRegistry()
#         )
#         if initlist is not None:
#             # Populating raw items silently first
#             for item in initlist:
#                 self.data.append(self._wrap(len(self.data), item))

#     def _wrap(self, index, value):
#         if isinstance(value, dict) and not isinstance(value, ReversibleDict):
#             return ReversibleDict(value, registry=self._registry)
#         if isinstance(value, list) and not isinstance(value, ReversibleList):
#             return ReversibleList(value, registry=self._registry)
#         return value

#     def _unwrap(self, val):
#         return (
#             val.data
#             if isinstance(val, (ReversibleDict, ReversibleList))
#             else val
#         )

#     def __setitem__(self, index, value):
#         old_val = self.data[index]
#         value = self._wrap(index, value)
#         self._registry.log(
#             self, "SET", index, copy.deepcopy(self._unwrap(old_val))
#         )
#         super().__setitem__(index, value)

#     def append(self, value):
#         idx = len(self.data)
#         value = self._wrap(idx, value)
#         self._registry.log(self, "APPEND", idx, None)
#         super().append(value)

#     def pop(self, index=-1):
#         idx = index if index >= 0 else len(self.data) + index
#         old_val = self.data[idx]
#         self._registry.log(
#             self, "POP", idx, copy.deepcopy(self._unwrap(old_val))
#         )
#         return super().pop(idx)


# class ReversibleDict(UserDict):
#     def __init__(self, dict_data=None, registry=None):
#         self.data = {}
#         self._registry = (
#             registry if registry is not None else HistoryRegistry()
#         )
#         if dict_data:
#             for k, v in dict_data.items():
#                 self.data[k] = self._wrap(k, v)

#     def _wrap(self, key, value):
#         if isinstance(value, dict) and not isinstance(value, ReversibleDict):
#             return ReversibleDict(value, registry=self._registry)
#         if isinstance(value, list) and not isinstance(value, ReversibleList):
#             return ReversibleList(value, registry=self._registry)
#         return value

#     def _unwrap(self, val):
#         return (
#             val.data
#             if isinstance(val, (ReversibleDict, ReversibleList))
#             else val
#         )

#     def __setitem__(self, key, value):
#         old_value = self.data.get(key, NOT_FOUND)
#         value = self._wrap(key, value)
#         self._registry.log(
#             self, "SET", key, copy.deepcopy(self._unwrap(old_value))
#         )
#         super().__setitem__(key, value)

#     def __delitem__(self, key):
#         if key not in self.data:
#             raise KeyError(key)
#         old_value = self.data[key]
#         self._registry.log(
#             self, "DEL", key, copy.deepcopy(self._unwrap(old_value))
#         )
#         super().__delitem__(key)

#     def undo(self):
#         """Rolls back the global state using explicit container instance references."""
#         self._registry.undo(self)


# # Initialize data with nested structural variations
# user_data = ReversibleDict({
#     "username": "coder123",
#     "tasks": [
#         {"id": 1, "status": "pending"},
#         {"id": 2, "status": "completed"}
#     ]
# })

# print("Original Object:")
# print(user_data)

# # Mutation 1: Update an attribute inside a list item
# user_data['tasks'][0]['status'] = 'in_progress'

# # Mutation 2: Append a new element to the list
# user_data['tasks'].append({"id": 3, "status": "backlog"})

# print("\nMutated Object:")
# print(user_data)
# # {'username': 'coder123', 'tasks': [{'id': 1, 'status': 'in_progress'}, {'id': 2, 'status': 'completed'}, {'id': 3, 'status': 'backlog'}]}

# # Undo Mutation 2 (The Append)
# user_data.undo()
# print("\nAfter Undo 1 (Removes appended item):")
# print(user_data['tasks'])
# # [{'id': 1, 'status': 'in_progress'}, {'id': 2, 'status': 'completed'}]

# # Undo Mutation 1 (The Inner dict change)
# user_data.undo()
# print("\nAfter Undo 2 (Reverts status modification):")
# print(user_data['tasks'])
# # [{'id': 1, 'status': 'pending'}, {'id': 2, 'status': 'completed'}]
