from __future__ import annotations
from dataclasses import dataclass


from benedict import benedict
from PySide6.QtCore import Signal, SignalInstance


from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .helpers import HistoryEntry, ItemEditorInfo, ItemEditorInfoDetails
    # from .helpers import HistoryEntry, ItemEditorInfoDetails


# @dataclass
class _ActionBarSignals:
    s_extract: SignalInstance[str]
    s_import: SignalInstance[str]
    s_export: SignalInstance[str]
    s_reset: SignalInstance
    s_undo: SignalInstance
    s_apply_to_game: SignalInstance


# @dataclass
class _SearchBarSignals:
    s_search: SignalInstance[str]
    s_filter: SignalInstance[str]
    s_toggle_icons: SignalInstance


# @dataclass
class _Signals:
    s_status_message: SignalInstance[str, int | None]
    s_iteminfo_extracted: SignalInstance[ItemEditorInfo]
    s_item_selected: SignalInstance[int]
    s_items_selected: SignalInstance[list[int]]
    s_history_entry_added: SignalInstance[HistoryEntry]
    ActionBar: _ActionBarSignals
    SearchBar: _SearchBarSignals


class _Slots(TypedDict):
    def log_history(entry: HistoryEntry, is_remove: bool = False) -> None:
        """Log change to history registry

        Args:
            entry: History Entry being logged
            is_remove: Whether this entry is being removed or added
        """


SIGNALS: _Signals = benedict(keyattr_dynamic=True)
SLOTS: _Slots = benedict(keyattr_dynamic=True)

__all__ = ["SIGNALS", "SLOTS"]