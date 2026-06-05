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

from ..helpers import SIGNALS, ItemEditorInfoDetails, log

from ..dmm_types import ItemInfo
from ..ui.search_bar import SearchBar

from ..ui.action_bar import ActionBar

from ..ui.editor_controls import EditorControls
from gui.theme import COLORS, CATEGORY_COLORS
from gui.iteminfo_index import IteminfoIndex


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


class DetailsTableModel(QAbstractTableModel):
    def __init__(
        self, parent, data: ItemEditorInfoDetails = ItemEditorInfoDetails()
    ):
        super().__init__(parent)

        self.load(data)

    def load(self, details: ItemEditorInfoDetails):
        self.beginResetModel()

        # data = [(key, detail) for key, detail in details._data.items()]
        display_data = [
            (
                key,
                json.dumps(detail),
            )
            for key, detail in details.editable()
        ]

        self._data = details
        self._display = display_data

        self.endResetModel()

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.UserRole:
            return self._data

        match role:
            case Qt.ItemDataRole.DisplayRole:
                key, detail = self._display[index.row()]
                match index.column():
                    case 0:
                        return key
                    case 1:
                        return detail
                    case _:
                        log.info(
                            "Item Details Table: Invalid index column %s",
                            index.column(),
                        )
                # return self._data[index.row()]

    def display(self, key: str):
        "stub"

    def headerData(self, idx, orientation, role):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            match idx:
                case 0:
                    return "Key"
                case 1:
                    return "Details"

        return None

    def rowCount(self, _):
        return len(self._display)

    def columnCount(self, _):
        return 2
