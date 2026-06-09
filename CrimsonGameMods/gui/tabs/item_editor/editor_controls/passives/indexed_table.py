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

if TYPE_CHECKING:
    from .window import PassiveWindow


class IndexedPassivesTable(QWidget):
    def __init__(self, parent: PassiveWindow):
        super().__init__(parent)

        self.get_skill_name = parent.get_skill_name
        self.get_skill_index = parent.get_skill_index

        self._build_ui()

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def _build_ui(self):
        table = QTableWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(
            [
                "Key",
                "Name",
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
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(24)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.table = table

        layout.addWidget(QLabel("Passive Skill Index:"))
        layout.addWidget(table)

    def load_passives(self):
        skills = self.get_skill_index().items()
        self.table.setRowCount(len(skills))

        for row, (key, name) in enumerate(skills):
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(name))
