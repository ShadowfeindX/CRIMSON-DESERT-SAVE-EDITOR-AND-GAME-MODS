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
    QSortFilterProxyModel,
    Qt,
    QSize,
    QTimer,
    Signal,
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

from .dmm_types import ItemInfo
from .search_bar import SearchBar

from .action_bar import ActionBar

from .editor_controls import EditorControls
from gui.theme import COLORS, CATEGORY_COLORS
from gui.iteminfo_index import IteminfoIndex


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


from models import SaveItem, SaveData, UndoEntry
from item_db import ItemNameDB
from equipment_sets import SetManager, EquipmentSet, SetItem, StatOperation
from paz_patcher import (
    PazPatchManager,
    PazPatch,
    ItemBuffPatcher,
    ItemRecord,
    StatTriplet,
    BUFF_HASHES,
    BUFF_NAMES,
    ItemEffectPatcher,
)
from icon_cache import IconCache, ICON_SIZE

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


class ItemDetailsTableModel(QAbstractTableModel):
    def __init__(self, parent, data: list[ItemInfo] = []):
        super().__init__(parent)

        self._data = data

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


class ItemDetailsTableModelProxy(QSortFilterProxyModel):
    def __init__(self, parent, model):
        super().__init__(parent)

        if model:
            self.setSourceModel(model)


class ItemDetailsTable(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui(parent)

    def _build_ui(self, parent):
        layout = QVBoxLayout(self)
        table = QTableView()
        model = ItemDetailsTableModel(self)
        proxy = ItemDetailsTableModelProxy(self, model)
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

    def load(self, data):
        self.model.beginResetModel()
        self.model.data = data
        self.model.endResetModel()
