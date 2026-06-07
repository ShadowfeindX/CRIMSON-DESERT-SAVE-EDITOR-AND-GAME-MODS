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

from .view import ItemEditorTableView
from ..helpers import ItemEditorInfo, ItemEditorInfoDetails
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
    ITEM_TIERS_INDEX = {
        "-": 0,
        "Common": 1,
        "Uncommon": 2,
        "Rare": 3,
        "Epic": 4,
        "Legendary": 5,
    }

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

    def display(self, index: QModelIndex, key=None):
        if not index.isValid():
            return None

        data = self._items._data[index.row()]
        return data[key] if key else data

    def data(self, index: QModelIndex, role):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.UserRole:
            return self.details(index)

        match role:
            case Qt.ItemDataRole.DisplayRole:
                match index.column():
                    case 0:
                        return self.details(index, "key")
                    case 1:
                        return self.details(index, "string_key")
                    case 2:
                        return self.ITEM_TIERS[
                            self.details(index, "item_tier")
                        ]
                    case _:
                        return self.details(index, "item_name")

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
