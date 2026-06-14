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
    from .window import BuffWindow


class SelectedBuffsTable(QWidget):
    def __init__(self, parent: BuffWindow):
        super().__init__(parent)
        self.get_buff_name = parent.get_buff_name
        self._selected_item_indexes = parent._selected_item_indexes
        self._build_ui()

    def _build_ui(self):
        table = QTableWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Key", "Name", "Level"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(lambda: table.clearSelection())

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

        layout.addWidget(QLabel("Buffs on Selected Items:"))
        layout.addWidget(table)

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def load_buffs(self):
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        # Merge buffs across all selected items (highest level wins)
        buff_levels: dict[int, int] = {}
        for item in map(ItemEditorInfoDetails, self._selected_item_indexes):
            buffs = item.buffs() or []
            for b in buffs:
                buff_key = b["buff"]
                level = b["level"]
                if buff_key not in buff_levels or level > buff_levels[buff_key]:
                    buff_levels[buff_key] = level

        self.table.setRowCount(len(buff_levels))
        for row, (buff_key, level) in enumerate(buff_levels.items()):
            key_item = QTableWidgetItem(str(buff_key))
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            name_item = QTableWidgetItem(self.get_buff_name(str(buff_key)))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            level_item = QTableWidgetItem(str(level))
            level_item.setFlags(level_item.flags() & ~Qt.ItemIsEditable)

            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, level_item)

        self.table.setSortingEnabled(True)
        self.table.setUpdatesEnabled(True)
