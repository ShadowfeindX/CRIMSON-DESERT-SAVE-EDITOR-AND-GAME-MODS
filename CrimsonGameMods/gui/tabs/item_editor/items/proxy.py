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