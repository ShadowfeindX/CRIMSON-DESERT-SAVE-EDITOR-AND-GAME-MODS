from __future__ import annotations

from collections.abc import ItemsView
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QAbstractItemDelegate,
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QMenu,
    QSpinBox,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from .window import BuffWindow


class _LevelSpinBoxDelegate(QStyledItemDelegate):
    """Provides a QSpinBox editor for the Level column (col 2)."""

    def createEditor(self, parent, option, index):
        spin = QSpinBox(parent)
        spin.setRange(1, 99)
        spin.setFrame(False)
        return spin

    def setEditorData(self, editor, index):
        try:
            editor.setValue(int(index.data()))
        except (TypeError, ValueError):
            editor.setValue(1)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class TargetBuffsTable(QWidget):
    s_add_to_favorites = Signal()
    s_remove_selection = Signal()

    def __init__(self, parent: BuffWindow):
        super().__init__(parent)
        self.get_buff_name = parent.get_buff_name
        self._selected_item_indexes = parent._selected_item_indexes
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Key", "Name", "Level"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
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

        # Delegate for editable Level column
        table.setItemDelegateForColumn(2, _LevelSpinBoxDelegate(table))

        self.table = table

        layout.addWidget(QLabel("Buffs to Apply:"))
        layout.addWidget(table)

    def clear(self):
        self.table.clear()
        self.table.setRowCount(0)
        # Re-apply header labels after clear()
        self.table.setHorizontalHeaderLabels(["Key", "Name", "Level"])
        self.table.setItemDelegateForColumn(2, _LevelSpinBoxDelegate(self.table))

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def _show_context_menu(self, pos):
        if not self.table.selectedItems():
            return
        menu = QMenu(self)
        menu.addAction("Add to Favorites", self.s_add_to_favorites.emit)
        menu.addAction("Remove", self.s_remove_selection.emit)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def load_buffs(self, buffs: ItemsView[str, str]):
        """Populate the target table from {(key_str): level_str} pairs."""
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)

        self.table.setRowCount(len(buffs))
        for row, (key, level) in enumerate(buffs):
            name = self.get_buff_name(key)

            key_item = QTableWidgetItem(key)
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)

            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)

            level_item = QTableWidgetItem(str(level))
            level_item.setFlags(level_item.flags() | Qt.ItemIsEditable)

            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, level_item)

        self.table.setSortingEnabled(True)
        self.table.setUpdatesEnabled(True)

    def get_all_buffs(self) -> list[tuple[int, int]]:
        """Return list of (buff_key, level) from the current table contents."""
        result = []
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            level_item = self.table.item(row, 2)
            if key_item is None or level_item is None:
                continue
            try:
                result.append((int(key_item.text()), int(level_item.text())))
            except (TypeError, ValueError):
                pass
        return result
