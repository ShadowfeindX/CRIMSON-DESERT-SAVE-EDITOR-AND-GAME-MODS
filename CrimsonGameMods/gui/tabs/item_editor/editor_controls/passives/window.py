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

from ...helpers import ItemEditorInfoDetails, copy
from ...signals import SIGNALS

from .action_bar import ActionBar
from .bottom_bar import BottomBar
from .target_table import TargetPassivesTable
from .indexed_table import IndexedPassivesTable
from .selected_table import SelectedPassivesTable

log = logging.getLogger(__name__)


class PassiveWindow(QWidget):
    s_load_passive_skill_index = Signal()

    _selected_items: list[ItemEditorInfoDetails] = []
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

    def _ready_signals(self):
        pass

    def _connect_signals(self):
        SIGNALS.s_items_selected.connect(self._set_selected_items)
        self.s_load_passive_skill_index.connect(self.load_skill_index)
        self.s_load_passive_skill_index.connect(
            self._indexed_passives_table.load_passives
        )

        self.action_bar.s_add.connect(self.add_selected_passives)
        self.action_bar.s_remove.connect(self.remove_selected_passives)
        
        self.bottom_bar.s_apply.connect(self.apply_passives_to_items)
        self.bottom_bar.s_remove.connect(self.remove_passives_from_items)
        self.bottom_bar.s_clear.connect(self.clear_target_list)

    def get_skill_name(self, key: str) -> str:
        return self.skill_index.get(key, "(unknown)")

    def get_skill_index(self):
        return self.skill_index

    def add_selected_passives(self):
        s_list = self._selected_passives_table.selected_rows()
        i_list = self._indexed_passives_table.selected_rows()

        for index in i_list:
            self._selected_passives.setdefault(index.data(), "1")

        for index in s_list:
            key = index.data()
            level = index.siblingAtColumn(2).data()

            current_level = self._selected_passives.get(key, "1")
            self._selected_passives[key] = max(current_level, level)

        self._target_passives_table.load_passives(
            self._selected_passives.items()
        )

    def remove_selected_passives(self):
        selected = self._target_passives_table.table.selectionModel().selectedRows()
        keys_to_remove = [index.data() for index in selected]

        for key in keys_to_remove:
            self._selected_passives.pop(key, None)

        self._target_passives_table.load_passives(
            self._selected_passives.items()
        )

    def apply_passives_to_items(self):
        new_passives = [
            {"skill": int(key), "level": int(level)}
            for key, level in self._selected_passives.items()
        ]

        for item in self._selected_items:
            item.update_with_history(
                "equip_passive_skill_list",
                new_passives,
                f"Applied {len(new_passives)} passive(s)",
            )

    def remove_passives_from_items(self):
        keys_to_remove = {int(k) for k in self._selected_passives}

        for item in self._selected_items:
            current = item.passives() or []
            filtered = [p for p in current if p["skill"] not in keys_to_remove]
            item.update_with_history(
                "equip_passive_skill_list",
                filtered,
                f"Removed {len(current) - len(filtered)} passive(s)",
            )

    def clear_target_list(self):
        self._selected_passives.clear()
        self._target_passives_table.table.setRowCount(0)

    def load_skill_index(self):
        try:
            with open(
                "data/passive_skill_catalog.json", "r", encoding="utf-8"
            ) as f:
                catalog = json.load(f)
                self.skill_index = copy(catalog["full_skill_index"]) or {}
                self.skill_index.pop("999999")
        except BaseException as e:
            log.error(f"An error occurred while loading the skill index!\n{e}")

    def _build_ui(self, parent: QWidget):
        main_layout = QVBoxLayout(self)
        table_layout = QHBoxLayout()

        self.action_bar = ActionBar(self)
        self._selected_passives_table = SelectedPassivesTable(self)
        self._indexed_passives_table = IndexedPassivesTable(self)
        self._target_passives_table = TargetPassivesTable(self)
        self.bottom_bar = BottomBar(self)

        table_layout.addWidget(self._selected_passives_table)
        table_layout.addWidget(self._indexed_passives_table)

        main_layout.addWidget(self.action_bar)
        main_layout.addLayout(table_layout)
        main_layout.addWidget(self._target_passives_table)
        main_layout.addWidget(self.bottom_bar)

    def _refresh_view(self):
        self._target_passives_table.load_passives(
            self._selected_passives.items()
        )

    def _set_selected_items(self, items: list[ItemEditorInfoDetails]):
        PassiveWindow._selected_items[:] = items
        self._selected_passives_table.load_passives()
