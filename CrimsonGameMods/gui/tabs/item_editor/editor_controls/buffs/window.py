from __future__ import annotations

import json
import logging
import os
import re

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...helpers import CONFIG, ItemEditorInfoDetails, copy
from ...signals import SIGNALS

from .action_bar import ActionBar
from .bottom_bar import BottomBar
from .target_table import TargetBuffsTable
from .indexed_table import IndexedBuffsTable
from .selected_table import SelectedBuffsTable

log = logging.getLogger(__name__)

_CAMEL_SPLIT = re.compile(r"([a-z0-9])([A-Z])")
_ABBREV_SPLIT = re.compile(r"([A-Z]+)([A-Z][a-z])")


def _display_name(string_key: str) -> str:
    """Convert 'BuffLevel_CombatHigh' → 'Combat High'."""
    name = string_key.removeprefix("BuffLevel_")
    name = name.replace("_", " ")
    name = _CAMEL_SPLIT.sub(r"\1 \2", name)
    name = _ABBREV_SPLIT.sub(r"\1 \2", name)
    return name


class BuffWindow(QWidget):
    s_load_buff_index = Signal()

    _selected_item_indexes: list[int] = []
    _selected_buffs: dict[str, str] = {}

    def __init__(self, parent: QWidget):
        super().__init__()
        self.setWindowTitle("Buff Editor")

        self.buff_index: dict[str, str] = {}

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

        self.s_load_buff_index.emit()

    def closeEvent(self, event: QCloseEvent):
        del self.buff_index
        return super().closeEvent(event)

    def get_buff_name(self, key: str) -> str:
        return self.buff_index.get(key, "(unknown)")

    def get_buff_index(self):
        return self.buff_index

    def search_buffs(self, query: str):
        for table_widget in (
            self.indexed_buffs_table.table,
            self.selected_buffs_table.table,
            self.target_buffs_table.table,
        ):
            for row in range(table_widget.rowCount()):
                key_item = table_widget.item(row, 0)
                name_item = table_widget.item(row, 1)
                if key_item is None or name_item is None:
                    continue
                match = (
                    query in key_item.text().lower()
                    or query in name_item.text().lower()
                )
                table_widget.setRowHidden(row, not match)

    def _sync_from_table(self):
        """Sync _selected_buffs from the target table's current contents.

        Call this before any operation that reads _selected_buffs so it
        reflects edits made directly in the QSpinBox delegate.
        """
        self._selected_buffs = {
            str(key): str(level)
            for key, level in self.target_buffs_table.get_all_buffs()
        }

    def add_selected_buffs(self):
        self._sync_from_table()

        s_list = self.selected_buffs_table.selected_rows()
        i_list = self.indexed_buffs_table.selected_rows()

        # From indexed table: default level 1
        for index in i_list:
            key = index.data()
            if key not in self._selected_buffs:
                self._selected_buffs[key] = "1"

        # From selected table: carry over the existing level (or use 1)
        for index in s_list:
            key = index.data()
            level_item = index.siblingAtColumn(2)
            level = level_item.data() if level_item else "1"

            current_level = self._selected_buffs.get(key, "1")
            self._selected_buffs[key] = max(current_level, str(level))

        self.target_buffs_table.load_buffs(self._selected_buffs.items())

    def remove_selected_buffs(self):
        selected = self.target_buffs_table.selected_rows()
        keys_to_remove = [str(index.data()) for index in selected]

        # Sync from table to capture any spinbox edits, then remove
        self._sync_from_table()
        for key in keys_to_remove:
            self._selected_buffs.pop(key, None)

        self.target_buffs_table.load_buffs(self._selected_buffs.items())

    def add_targets_to_favorites(self):
        selected = self.target_buffs_table.selected_rows()
        keys_to_add = [index.data() for index in selected]

        favorites = CONFIG["favorite_buffs"] or []

        for key in keys_to_add:
            if key not in favorites:
                favorites.append(key)

        CONFIG["favorite_buffs"] = favorites
        CONFIG.save()

    def apply_buffs_to_items(self):
        # Read live values from the target table (includes spinbox edits)
        self._sync_from_table()
        live_buffs = self.target_buffs_table.get_all_buffs()
        new_buffs = [{"buff": key, "level": level} for key, level in live_buffs]

        for item in map(ItemEditorInfoDetails, self._selected_item_indexes):
            item.buffs(new=new_buffs, log=True)

    def remove_buffs_from_items(self):
        # Read live values from the target table (includes spinbox edits)
        self._sync_from_table()
        live_buffs = self.target_buffs_table.get_all_buffs()
        keys_to_remove = {key for key, _ in live_buffs}

        for item in map(ItemEditorInfoDetails, self._selected_item_indexes):
            current = item.buffs() or []
            filtered = [b for b in current if b["buff"] not in keys_to_remove]
            item.buffs(new=filtered, log=True)

    def clear_target_list(self):
        self.target_buffs_table.clear()
        self._selected_buffs.clear()

    def load_buff_index(self):
        """Load buffs.json from data/item_editor_database/."""
        try:
            # Search multiple plausible locations
            import sys

            _here = os.path.dirname(os.path.abspath(__file__))
            _root = os.path.dirname(os.path.dirname(_here))

            candidates = [
                os.path.join(_root, "data", "item_editor_database", "buffs.json"),
                os.path.join(
                    getattr(sys, "_MEIPASS", ""),
                    "data",
                    "item_editor_database",
                    "buffs.json",
                ),
                os.path.join(
                    os.getcwd(), "data", "item_editor_database", "buffs.json"
                ),
            ]

            for path in candidates:
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                    # raw format: list of { "key_str": { "key": int, "string_key": str } }
                    index = {}
                    for entry in raw:
                        for key_str, data in entry.items():
                            index[key_str] = _display_name(
                                data.get("string_key", key_str)
                            )
                    self.buff_index = index
                    log.info("Loaded %d buffs from %s", len(self.buff_index), path)
                    return
            else:
                log.warning("buffs.json not found in any candidate path")
        except Exception as e:
            log.error("Failed to load buffs.json: %s", e)

    def _ready_signals(self):
        pass

    def _connect_signals(self):
        SIGNALS.s_items_selected.connect(self._set_selected_items)
        self.s_load_buff_index.connect(self.load_buff_index)
        self.s_load_buff_index.connect(self.indexed_buffs_table.load_buffs)

        self.action_bar.s_add.connect(self.add_selected_buffs)
        self.action_bar.s_remove.connect(self.remove_selected_buffs)
        self.action_bar.s_search.connect(self.search_buffs)

        self.bottom_bar.s_apply.connect(self.apply_buffs_to_items)
        self.bottom_bar.s_remove.connect(self.remove_buffs_from_items)
        self.bottom_bar.s_clear.connect(self.clear_target_list)

        self.target_buffs_table.s_add_to_favorites.connect(
            self.add_targets_to_favorites
        )
        self.target_buffs_table.s_remove_selection.connect(
            self.remove_selected_buffs
        )

    def _build_ui(self, parent: QWidget):
        main_layout = QVBoxLayout(self)
        table_layout = QHBoxLayout()

        self.action_bar = ActionBar(self)
        self.selected_buffs_table = SelectedBuffsTable(self)
        self.indexed_buffs_table = IndexedBuffsTable(self)
        self.target_buffs_table = TargetBuffsTable(self)
        self.bottom_bar = BottomBar(self)

        table_layout.addWidget(self.selected_buffs_table)
        table_layout.addWidget(self.indexed_buffs_table)

        main_layout.addWidget(self.action_bar)
        main_layout.addLayout(table_layout)
        main_layout.addWidget(self.target_buffs_table)
        main_layout.addWidget(self.bottom_bar)

    def _set_selected_items(self, items: list[int]):
        self._selected_item_indexes[:] = items
        self.selected_buffs_table.load_buffs()
