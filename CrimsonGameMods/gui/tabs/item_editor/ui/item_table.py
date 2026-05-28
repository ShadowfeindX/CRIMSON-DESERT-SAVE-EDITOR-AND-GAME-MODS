from __future__ import annotations

import datetime
import json
import logging
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import traceback
import textwrap
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import (
    QAbstractTableModel,
    QRegularExpression,
    QSortFilterProxyModel,
    Qt,
    QSize,
    QTimer,
    Signal,
    Slot,
    QModelIndex,
)
from PySide6.QtGui import QAction, QBrush, QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from ..models import ItemEditorInfo, ItemEditorInfoDetails
from ..dmm_types import ItemInfo

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
    ITEM_TIERS = ["-", "Common", "Uncommon", "Rare", "Epic", "Legendary"]

    def __init__(self, parent, info: ItemEditorInfo = ItemEditorInfo()):
        super().__init__(parent)

        self.load(info)

    def load(self, info: ItemEditorInfo):
        self.beginResetModel()

        self._items = info

        self.endResetModel()

    def details(self, index: QModelIndex, key=None):
        if not index.isValid():
            return None

        data = self._items.details(index.row())
        return data[key] if key else data

    def data(self, index: QModelIndex, role):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.UserRole:
            return self.details(index)
            return self._items.details(index.row())

        match role:
            case Qt.ItemDataRole.DisplayRole:
                match index.column():
                    case 0:
                        return self.details(index, "key")
                        return self._items.details(index.row())["key"]
                    case 1:
                        return self.details(index, "string_key")
                        return self._items.details(index.row())["string_key"]
                    case 2:
                        return self.ITEM_TIERS[
                            self.details(index, "item_tier")
                        ]
                        return self._items.details(index.row())["item_tier"]
                    case _:
                        return self.details(index, "item_name")
                        return self._items.details(index.row())["item_name"]

    def headerData(self, idx, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            match idx:
                case 0:
                    return "Key"
                case 1:
                    return "Name"
                case 2:
                    return "Tier"
                case _:
                    return None

    def rowCount(self, index):
        return len(self._items)

    def columnCount(self, index):
        return 3


class ItemTableModelProxy(QSortFilterProxyModel):
    def __init__(self, parent, model):
        super().__init__(parent)

        if model:
            self.setSourceModel(model)

    def lessThan(self, left_index: QModelIndex, right_index: QModelIndex):
        left: ItemInfo = self.sourceModel().data(
            left_index, Qt.ItemDataRole.UserRole
        )
        right: ItemInfo = self.sourceModel().data(
            right_index, Qt.ItemDataRole.UserRole
        )

        match left_index.column():
            case 0:
                return left["key"] < right["key"]
            case 1:
                return left["string_key"] < right["string_key"]
            case 2:
                return left["item_tier"] < right["item_tier"]
            case _:
                log.warning(
                    "Warning: Sorting unidentified column id: %s",
                    left_index.column(),
                )
                return super().lessThan(left_index, right_index)

    def sort(self, column, /, order=...):
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
        proxy.setFilterKeyColumn(-1)
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

        self.table = table
        self.model = model
        self.proxy = proxy

        layout.addWidget(table)
        self.refresh_view()

    def _show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if index.isValid():
            log.info("showing context menu for: %s", index.data())

    def refresh_view(self):
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

    @Slot(ItemEditorInfo)
    def load(self, info: ItemEditorInfo):
        self.model.load(info)
        self.refresh_view()

    @Slot(str)
    def search(self, term: str):
        self.proxy.setFilterRegularExpression(
            QRegularExpression(
                term, QRegularExpression.PatternOption.CaseInsensitiveOption
            )
        )
        self.refresh_view()
