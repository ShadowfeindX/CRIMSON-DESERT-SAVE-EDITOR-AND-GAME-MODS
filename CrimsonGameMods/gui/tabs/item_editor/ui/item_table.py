from __future__ import annotations

import logging

from PySide6.QtCore import (
    QAbstractTableModel,
    QSortFilterProxyModel,
    Qt,
    QModelIndex,
)
from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QAbstractItemView,
)

from .models import ItemEditorInfo, ItemEditorInfoDetails
from .dmm_types import ItemInfo

# from gui.theme import COLORS, CATEGORY_COLORS


def _safe_iv(v, default=0):
    """Safely extract int from plain int, float, or dmm_parser nested dict.
    dmm_parser returns numeric structs as {'a': int, 'b': int, 'c': int}.
    """
    if v is None:
        return default
    if isinstance(v, (int, float, bool)):
        return int(v)
    if isinstance(v, dict):
        for k in ("a", "value", "_v", "v", "val", "n", "data"):
            if k in v:
                sub = v[k]
                if isinstance(sub, (int, float, bool)):
                    return int(sub)
                if sub is None:
                    return default
        return default
    try:
        return int(v)
    except Exception:
        return default


try:
    from gui.utils import make_help_btn
except Exception:

    def make_help_btn(topic, fn=None):
        btn = QPushButton("?")
        btn.setFixedSize(22, 22)
        if fn:
            btn.clicked.connect(lambda: fn(topic))
        return btn


log = logging.getLogger(__name__)


class ItemTableModel(QAbstractTableModel):
    def __init__(self, parent, info: ItemEditorInfo = ItemEditorInfo()):
        super().__init__(parent)

        self.load(info)

    def load(self, info: ItemEditorInfo):
        self._data = info._data

    def data(self, index: QModelIndex, role):
        match role:
            case Qt.ItemDataRole.UserRole:
                return ItemEditorInfoDetails(self._data[index.row()])
            case Qt.ItemDataRole.DisplayRole:
                match index.column():
                    case 0:
                        return self._data[index.row()]["_key"]
                    case 1:
                        return self._data[index.row()]["_stringKey"]
                return self._data[index.row()]["_itemName"]

    def headerData(self, idx, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            match idx:
                case 0:
                    return "Key"
                case 1:
                    return "Name"
                case _:
                    return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return 2


class ItemTableModelProxy(QSortFilterProxyModel):
    def __init__(self, parent, model):
        super().__init__(parent)

        if model:
            self.setSourceModel(model)

    def lessThan(self, left_index: QModelIndex, right_index: QModelIndex):
        left: ItemInfo = self.sourceModel().data(
            left_index, Qt.ItemDataRole.UserRole
        )._data
        right: ItemInfo = self.sourceModel().data(
            right_index, Qt.ItemDataRole.UserRole
        )._data

        match left_index.column():
            case 0:
                return left["_key"] < right["_key"]
            case 1:
                return left["_stringKey"] < right["_stringKey"]
            case _:
                print(left_index.column())
                return super().lessThan(left_index, right_index)

    def sort(self, column, /, order=...):
        print((column, order))
        return super().sort(column, order)


class ItemTable(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui(parent)

    def _build_ui(self, parent):
        layout = QVBoxLayout(self)
        table = QTableView()
        model = ItemTableModel(self)
        proxy = ItemTableModelProxy(self, model)
        table.setModel(proxy)

        table.setMinimumWidth(120)
        table.setColumnWidth(1, 180)
        table.verticalHeader().setVisible(False)
        table.setSortingEnabled(True)
        table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_context_menu)

        self.refresh_view()

        self.table = table
        self.model = model
        self.proxy = proxy

        layout.addWidget(table)

    def _show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if index.isValid():
            log.info("showing context menu for: %s", index.data())

    def refresh_view(self):
        "Stub"

    def load(self, info: ItemEditorInfo):
        self.model.load(info)
        self.model.layoutChanged.emit()
