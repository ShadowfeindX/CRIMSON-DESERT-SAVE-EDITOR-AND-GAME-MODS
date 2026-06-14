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
    from .window import BuffWindow


class IndexedBuffsTable(QWidget):
    def __init__(self, parent: BuffWindow):
        super().__init__(parent)
        self.get_buff_name = parent.get_buff_name
        self.get_buff_index = parent.get_buff_index

        self._build_ui()

    def _build_ui(self):
        table = QTableWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Key", "Name"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(lambda: table.clearSelection())

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(24)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        table.setSortingEnabled(True)
        self.table = table

        layout.addWidget(QLabel("Buff Index:"))
        layout.addWidget(table)

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def load_buffs(self, show_favorites_only: bool = False):
        from ...helpers import CONFIG

        buffs = self.get_buff_index().items()
        if show_favorites_only:
            favorites = CONFIG["favorite_buffs"]
            if not isinstance(favorites, list):
                favorites = []
            buffs = [(key, name) for key, name in buffs if key in favorites]

        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)

        self.table.setRowCount(len(buffs))
        for row, (key, name) in enumerate(buffs):
            key_item = QTableWidgetItem(key)
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, name_item)

        self.table.setSortingEnabled(True)
        self.table.setUpdatesEnabled(True)
