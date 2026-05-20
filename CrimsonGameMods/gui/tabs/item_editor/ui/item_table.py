from __future__ import annotations

import logging

from PySide6.QtCore import (
    QAbstractTableModel,
    QSortFilterProxyModel,
    Qt,
)
from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QTableView,
    QVBoxLayout,
)

from .models import ItemEditorInfo

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

        self._data = info._data

    def data(self, index, role):
        match role:
            case Qt.ItemDataRole.DisplayRole:
                return self._data[index.row()]["item_name"]
            case Qt.ItemDataRole.UserRole:
                return self._data[index.row()]

    def headerData(self, idx, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            match orientation:
                case Qt.Orientation.Horizontal:
                    return "Name"
                case Qt.Orientation.Vertical:
                    return self._data[idx]["key"]

        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return 1


class ItemTableModelProxy(QSortFilterProxyModel):
    def __init__(self, parent, model):
        super().__init__(parent)

        if model:
            self.setSourceModel(model)


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
        table.setSortingEnabled(True)
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
        self.model._data = info._data
        self.model.layoutChanged.emit()



    # def load(self, info: ItemEditorInfo):
    #     self.model = ItemTableModel(self, info)
    #     self.proxy = ItemTableModelProxy(self, self.model)
    #     self.table.setModel(self.proxy)