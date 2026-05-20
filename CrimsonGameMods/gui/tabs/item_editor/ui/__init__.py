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

from PySide6.QtCore import Qt, QSize, QTimer, Signal
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
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .item_details_table import ItemDetailsTable

from .item_table import ItemTable

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


class ItemEditorLayout(QVBoxLayout):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._build_ui(parent)

        def load_details(curr, prev):
            i_model = self.items_table.model
            d_table = self.item_details_table

            details = i_model.data(curr, Qt.ItemDataRole.UserRole)
            d_table.load(details)

        self.items_table.table.selectionModel().currentRowChanged.connect(
            load_details
        )

    def _build_ui(self, parent: QWidget):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.action_bar = ActionBar(parent)
        self.search_bar = SearchBar(parent)
        self.items_table = ItemTable(parent)
        self.item_details_table = ItemDetailsTable(parent)
        self.editor_controls = EditorControls(parent)

        layout = QHBoxLayout()
        layout.addWidget(self.items_table)
        layout.addWidget(self.item_details_table)
        layout.addWidget(self.editor_controls)

        self.addWidget(self.action_bar)
        self.addWidget(self.search_bar)
        self.addLayout(layout, 1)
