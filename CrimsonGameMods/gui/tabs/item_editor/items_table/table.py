from __future__ import annotations

from PySide6.QtCore import (
    QItemSelection,
    QModelIndex,
    QRegularExpression,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
)

from ..helpers import ItemEditorInfo, ItemEditorInfoDetails
from ..signals import SIGNALS, SLOTS
from .model import ItemTableModel
from .proxy import ItemTableModelProxy
from .view import ItemEditorTableView

# from gui.theme import COLORS, CATEGORY_COLORS


class ItemTable(QFrame):
    s_item_selected = Signal(ItemEditorInfoDetails)
    s_items_selected = Signal(list)

    def __init__(self, parent):
        super().__init__(parent)

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

    def _ready_signals(self):
        SIGNALS.s_item_selected = self.s_item_selected
        SIGNALS.s_items_selected = self.s_items_selected

        # SLOTS.current_selection = self.current_selection

    def _connect_signals(self):
        SIGNALS.s_iteminfo_extracted.connect(self.load)
        self.table.selectionModel().selectionChanged.connect(
            self._selection_changed
        )

        SIGNALS.s_item_selected.connect(SLOTS.current_selection)

    @Slot(QItemSelection, QItemSelection)
    def _selection_changed(
        self, selected: QItemSelection, deselected: QItemSelection
    ):
        print("Selection changed...")

        if not selected.isEmpty():
            SIGNALS.s_item_selected.emit(
                self.proxy.mapToSource(selected.indexes()[0]).row()
            )
        else:
            SIGNALS.s_item_selected.emit(None)

        SIGNALS.s_items_selected.emit(
            [
                self.proxy.mapToSource(index).row()
                for index in self.table.selectionModel().selectedRows()
            ]
        )

    def _build_ui(self, parent):
        layout = QVBoxLayout(self)
        self.model = ItemTableModel(self)
        self.proxy = ItemTableModelProxy(self, self.model)
        self.table = ItemEditorTableView(parent, self.proxy)
        self.proxy.setFilterKeyColumn(-1)

        layout.addWidget(self.table)
        self.table.refresh_view()

    @Slot(ItemEditorInfo)
    def load(self, info: ItemEditorInfo):
        self.table.setUpdatesEnabled(False)
        self.proxy.setDynamicSortFilter(False)
        self.model.load(info)
        self.table.refresh_view()
        self.proxy.setDynamicSortFilter(True)
        self.table.setUpdatesEnabled(True)

    @Slot(str)
    def search(self, term: str):
        self.proxy.apply_filter_text(term)
