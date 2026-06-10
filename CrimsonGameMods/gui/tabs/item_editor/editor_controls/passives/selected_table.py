from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...helpers import ItemEditorInfoDetails

if TYPE_CHECKING:
    from .window import PassiveWindow


class SelectedPassivesTable(QWidget):
    def __init__(self, parent: PassiveWindow):
        super().__init__(parent)

        self.get_skill_name = parent.get_skill_name
        self.get_skill_index = parent.get_skill_index
        self._selected_item_indexes = parent._selected_item_indexes

        self._build_ui()

    def _build_ui(self):
        table = QTableWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            [
                "Key",
                "Name",
                "Level",
            ]
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda: table.clearSelection()
        )

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(24)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        table.setSortingEnabled(True)

        self.table = table

        layout.addWidget(QLabel("Passives on Selected Items:"))
        layout.addWidget(table)

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def load_passives(self):
        skills = self.get_skill_index()
        
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(0)

        skill_levels: dict[int, int] = {}
        for item in map(ItemEditorInfoDetails, self._selected_item_indexes):
            passives = item.passives() or []

            for passive in passives:
                skill_key = passive["skill"]
                level = passive["level"]
                if skill_key not in skill_levels or level > skill_levels[skill_key]:
                    skill_levels[skill_key] = level

        self.table.setRowCount(len(skill_levels))
        for row, (skill_key, level) in enumerate(skill_levels.items()):
            self.table.setItem(
                row, 0, QTableWidgetItem(str(skill_key))
            )
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    skills.get(str(skill_key), "(unknown)")
                ),
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(str(level))
            )
        
        self.table.setSortingEnabled(True)
        self.table.setUpdatesEnabled(True)
