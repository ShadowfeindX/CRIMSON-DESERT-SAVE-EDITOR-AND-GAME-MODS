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

from .model import ItemTableModel

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

        self._search_term = ""

        if model:
            self.setSourceModel(model)

    def lessThan(self, left_index: QModelIndex, right_index: QModelIndex):
        left: ItemInfo = self.sourceModel().display(left_index)
        right: ItemInfo = self.sourceModel().display(right_index)

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

    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        return super().sort(column, order)

    def apply_filter_text(self, text: str):
        self._search_term = text.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._search_term:
            return True

        model: ItemTableModel = self.sourceModel()

        if self._search_term.isdigit():
            idx0 = model.index(source_row, 0, source_parent)
            val0 = model.display(idx0, "key")
            if val0 is not None and self._search_term in str(val0):
                return True

        idx1 = model.index(source_row, 1, source_parent)
        val1 = model.display(idx1, "string_key")
        if val1 is not None and self._search_term in str(val1).lower():
            return True

        idx2 = model.index(source_row, 2, source_parent)
        val2 = model.display(idx2, "item_tier")
        tier = model.ITEM_TIERS_INDEX.get(self._search_term.capitalize(), None)
        if tier is not None and val2 == tier:
            return True

        # No match found across any of the 3 columns
        return False
