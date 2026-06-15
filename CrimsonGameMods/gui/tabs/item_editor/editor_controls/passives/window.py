from __future__ import annotations

import json
import logging

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...helpers import (
    CONFIG,
    ItemEditorInfo,
    ItemEditorInfoDetails,
    copy,
    load_passive_skill_index,
)
from ...signals import SIGNALS

from .action_bar import ActionBar
from .bottom_bar import BottomBar
from .target_table import TargetPassivesTable
from .indexed_table import IndexedPassivesTable
from .selected_table import SelectedPassivesTable

log = logging.getLogger(__name__)


class PassiveWindow(QWidget):
    s_load_passive_skill_index = Signal()

    _selected_item_indexes: list[int] = []
    _selected_passives: dict[str, str] = {}

    def __init__(self, parent: QWidget):
        super().__init__()

        self.setWindowTitle("Passives Editor")

        self.skill_index: dict[str, str] = {}

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

        self.s_load_passive_skill_index.emit()

    def closeEvent(self, event: QCloseEvent):
        del self.skill_index
        return super().closeEvent(event)

    def get_skill_name(self, key: str) -> str:
        return self.skill_index.get(key, "(unknown)")

    def get_skill_index(self):
        return self.skill_index

    def search_passives(self, query: str):
        for table_widget in (
            self.indexed_passives_table.table,
            self.selected_passives_table.table,
            self.target_passives_table.table,
        ):
            for row in range(table_widget.rowCount()):
                key_item = table_widget.item(row, 0)
                name_item = table_widget.item(row, 1)
                match = (
                    query in key_item.text().lower()
                    or query in name_item.text().lower()
                )
                table_widget.setRowHidden(row, not match)

    def add_selected_passives(self):
        s_list = self.selected_passives_table.selected_rows()
        i_list = self.indexed_passives_table.selected_rows()

        for index in i_list:
            self._selected_passives.setdefault(index.data(), "1")

        for index in s_list:
            key = index.data()
            level = index.siblingAtColumn(2).data()

            current_level = self._selected_passives.get(key, "1")
            self._selected_passives[key] = max(current_level, level)

        self.target_passives_table.load_passives(
            self._selected_passives.items()
        )

    def remove_selected_passives(self):
        selected = self.target_passives_table.selected_rows()
        keys_to_remove = [index.data() for index in selected]

        for key in keys_to_remove:
            self._selected_passives.pop(key, None)

        self.target_passives_table.load_passives(
            self._selected_passives.items()
        )

    def add_targets_to_favorites(self):
        selected = self.target_passives_table.selected_rows()
        keys_to_add = [index.data() for index in selected]

        favorites = CONFIG["favorite_passives"] or []

        for key in keys_to_add:
            if key not in favorites:
                favorites.append(key)

        CONFIG["favorite_passives"] = favorites
        CONFIG.save()

    def apply_passives_to_items(self):
        new_passives = [
            {"skill": int(key), "level": int(level)}
            for key, level in self._selected_passives.items()
        ]

        for item in map(ItemEditorInfoDetails, self._selected_item_indexes):
            item.passives(new=new_passives, log=True)

        # ItemEditorInfo.bulk_update_with_history(
        #     self._selected_item_indexes,
        #     "equip_passive_skill_list",
        #     new_passives,
        #     f"Applied {len(new_passives)} passive(s) to {len(self._selected_item_indexes)} item(s)",
        # )

    def remove_passives_from_items(self):
        keys_to_remove = {int(k) for k in self._selected_passives}

        def make_filtered(item):
            current = item.passives() or []
            return [p for p in current if p["skill"] not in keys_to_remove]

        for item in map(ItemEditorInfoDetails, self._selected_item_indexes):
            item.passives(new=make_filtered(item), log=True)
            
        # ItemEditorInfo.bulk_update_with_history(
        #     self._selected_item_indexes,
        #     "equip_passive_skill_list",
        #     make_filtered,
        #     f"Removed passives from {len(self._selected_item_indexes)} item(s)",
        # )

    def clear_target_list(self):
        self.target_passives_table.clear()

    def load_skill_index(self):
        self.skill_index = load_passive_skill_index()

    def _ready_signals(self):
        pass

    def _connect_signals(self):
        SIGNALS.s_items_selected.connect(self._set_selected_items)
        self.s_load_passive_skill_index.connect(self.load_skill_index)
        self.s_load_passive_skill_index.connect(
            self.indexed_passives_table.load_passives
        )

        self.action_bar.s_add.connect(self.add_selected_passives)
        self.action_bar.s_remove.connect(self.remove_selected_passives)
        self.action_bar.s_search.connect(self.search_passives)

        self.bottom_bar.s_apply.connect(self.apply_passives_to_items)
        self.bottom_bar.s_remove.connect(self.remove_passives_from_items)
        self.bottom_bar.s_clear.connect(self.clear_target_list)

        self.target_passives_table.s_add_to_favorites.connect(
            self.add_targets_to_favorites
        )
        self.target_passives_table.s_remove_selection.connect(
            self.remove_selected_passives
        )

    def _build_ui(self, parent: QWidget):
        main_layout = QVBoxLayout(self)
        table_layout = QHBoxLayout()

        self.action_bar = ActionBar(self)
        self.selected_passives_table = SelectedPassivesTable(self)
        self.indexed_passives_table = IndexedPassivesTable(self)
        self.target_passives_table = TargetPassivesTable(self)
        self.bottom_bar = BottomBar(self)

        table_layout.addWidget(self.selected_passives_table)
        table_layout.addWidget(self.indexed_passives_table)

        main_layout.addWidget(self.action_bar)
        main_layout.addLayout(table_layout)
        main_layout.addWidget(self.target_passives_table)
        main_layout.addWidget(self.bottom_bar)

    def _refresh_view(self):
        self.target_passives_table.load_passives(
            self._selected_passives.items()
        )

    def _set_selected_items(self, items: list[int]):
        self._selected_item_indexes[:] = items
        self.selected_passives_table.load_passives()
