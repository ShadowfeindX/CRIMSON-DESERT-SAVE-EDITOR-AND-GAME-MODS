from __future__ import annotations

from collections.abc import ItemsView
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from .window import PassiveWindow


class TargetPassivesTable(QWidget):
    s_add_to_favorites = Signal()
    s_remove_selection = Signal()

    def __init__(self, parent: PassiveWindow):
        super().__init__(parent)

        self.get_skill_name = parent.get_skill_name
        self._selected_item_indexes = parent._selected_item_indexes

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table = QTableWidget()
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
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_context_menu)

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

        layout.addWidget(QLabel("Passives to Apply:"))
        layout.addWidget(table)

    def clear(self):
        self.table.clear()
        self.table.setRowCount(0)

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def load_passives(self, passives: ItemsView[str, str]):
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(len(passives))
        for row, (key, level) in enumerate(passives):
            name = self.get_skill_name(key)

            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(level))
        
        self.table.setSortingEnabled(True)
        self.table.setUpdatesEnabled(True)

    def _show_context_menu(self, pos):
        if not self.table.selectedItems():
            return

        menu = QMenu(self)
        menu.addAction("Add to Favorites", self.s_add_to_favorites.emit)
        menu.addAction("Remove", self.s_remove_selection.emit)
        menu.exec(self.table.viewport().mapToGlobal(pos))
