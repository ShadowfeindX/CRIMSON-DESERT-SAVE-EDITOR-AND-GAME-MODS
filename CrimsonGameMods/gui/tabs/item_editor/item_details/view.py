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
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QContextMenuEvent,
    QFont,
    QIcon,
)
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

from .context_menu import DetailsTableContextMenu

from ..helpers import ItemEditorInfoDetails, log

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


class DetailsTableView(QTableView):
    def __init__(self, parent, model):
        super().__init__(
            parent, sortingEnabled=False, cornerButtonEnabled=True
        )

        self.setModel(model)
        self.setMinimumWidth(120)
        self.setColumnWidth(1, 180)
        self.verticalHeader().setVisible(False)
        # self.setSortingEnabled(True)
        # self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.customContextMenuRequested.connect(self._show_context_menu)

    def refresh_view(self: QTableView) -> None:
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        # self.horizontalHeader().setSectionResizeMode(
        #     2, QHeaderView.ResizeMode.ResizeToContents
        # )

    def contextMenuEvent(self, event: QContextMenuEvent):
        index = self.indexAt(event.pos())
        if index.isValid():
            log.info("showing context menu for: %s", index.data())
            return DetailsTableContextMenu.open(self, index, event.globalPos())
