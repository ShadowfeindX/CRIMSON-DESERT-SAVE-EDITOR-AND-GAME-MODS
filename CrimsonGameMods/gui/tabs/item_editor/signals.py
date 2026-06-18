from __future__ import annotations
from dataclasses import dataclass
import logging

from benedict import benedict
from PySide6.QtCore import Signal, SignalInstance


from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    from .helpers import HistoryEntry, ItemEditorInfo, ItemEditorInfoDetails
    # from .helpers import HistoryEntry, ItemEditorInfoDetails

log = logging.getLogger(__name__)


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
    s_data_changed: SignalInstance[int]
    s_history_entry_added: SignalInstance[HistoryEntry]
    ActionBar: _ActionBarSignals
    SearchBar: _SearchBarSignals


class _Slots:
    _last_idx: int = -1
    _idx: list[int] = []

    def _log_history(
        self, entry: HistoryEntry, is_remove: bool = False
    ) -> None:
        """Log change to history registry

        Args:
            entry: History Entry being logged
            is_remove: Whether this entry is being removed or added
        """

        log.info(
            f"History entry removed: ({entry.description})"
            if is_remove
            else f"History entry added: ({entry.description})"
        )

    def last_selected(self, idx: int = None) -> int:
        """Set or Retrieve last selected item index

        Args:
            idx: Index of last selected item (Optional)
        Returns:
            int: Index of last selected item
        """

        if idx is not None:
            self._last_idx = idx
        return self._last_idx

    def current_selection(self, idx: list[int] = None) -> list[int]:
        """Set or Retrieve currently selected item indexes

        Args:
            idx: Indexes of currently selected items (Optional)
        Returns:
            list[int]: Indexs of currently selected items
        """

        if idx is not None:
            self._idx[:] = idx
        return self._idx


SIGNALS: _Signals = benedict(keyattr_dynamic=True)
SLOTS: _Slots = _Slots()

__all__ = ["SIGNALS", "SLOTS"]
