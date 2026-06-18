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
from ..helpers import log, ItemEditorInfo, ItemEditorInfoDetails
from ..dmm_types import ItemInfo

# from gui.theme import COLORS, CATEGORY_COLORS


class ItemTableModelProxy(QSortFilterProxyModel):
    def __init__(self, parent, model):
        super().__init__(parent)

        self._search_term = ""

        if model:
            self.setSourceModel(model)

    def lessThan(self, left: QModelIndex, right: QModelIndex):
        i = self.sourceModel().details
        # left: ItemInfo = self.sourceModel().display(left_index)
        # right: ItemInfo = self.sourceModel().display(right_index)

        match left.column():
            case 0:
                return i(left, "key") < i(right, "key")
            case 1:
                return i(left, "string_key") < i(right, "string_key")
            case 2:
                return i(left, "item_tier") < i(right, "item_tier")
            case _:
                log.warning(
                    "Warning: Sorting unidentified column id: %s",
                    left.column(),
                )
                return super().lessThan(left, right)

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
            val0 = model.details(idx0, "key")
            if val0 is not None and self._search_term in str(val0):
                return True

        idx1 = model.index(source_row, 1, source_parent)
        val1 = model.details(idx1, "string_key")
        if val1 is not None and self._search_term in str(val1).lower():
            return True

        idx2 = model.index(source_row, 2, source_parent)
        val2 = model.details(idx2, "item_tier")
        tier = model.ITEM_TIERS_INDEX.get(self._search_term.capitalize(), None)
        if tier is not None and val2 == tier:
            return True

        # No match found across any of the 3 columns
        return False
