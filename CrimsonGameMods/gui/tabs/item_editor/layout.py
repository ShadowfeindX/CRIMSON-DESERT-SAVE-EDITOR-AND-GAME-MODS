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

from PySide6.QtCore import QRegularExpression, Qt, QSize, QTimer, Signal
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

from .helpers import SIGNALS, log

from .item_details.table import ItemDetailsTable

from .items.table import ItemTable

from .ui.search_bar import SearchBar

from .ui.action_bar import ActionBar

from .ui.editor_controls import EditorControls
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


class ItemEditorLayout(QVBoxLayout):
    # s_config_save_requested = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._build_ui(parent)
        

        self.items_table.table.selectionModel().currentRowChanged.connect(
            self._load_details
        )

        self.search_bar.s_search.connect(self.items_table.search)
        # SIGNALS.s_status_message.connect(self.status_bar.setText)

    def _build_ui(self, parent: QWidget):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.action_bar = ActionBar(parent)
        self.search_bar = SearchBar(parent)
        self.items_table = ItemTable(parent)
        self.item_details_table = ItemDetailsTable(parent)
        self.editor_controls = EditorControls(parent)
        # self.status_bar = QLabel("")

        layout = QHBoxLayout()
        layout.addWidget(self.items_table)
        layout.addWidget(self.item_details_table)
        layout.addWidget(self.editor_controls)

        self.addWidget(self.action_bar)
        self.addWidget(self.search_bar)
        self.addLayout(layout, 1)
        # self.addWidget(self.status_bar)

    def _load_details(self, curr, _):
        i_model = self.items_table.model
        d_table = self.item_details_table

        details = i_model.data(curr, Qt.ItemDataRole.UserRole)
        d_table.load(details)
        log.info("Changing Selection...")
        SIGNALS.s_item_selected.emit(details)
    
    def closeEvent(self, event):
        self.editor_controls.closeEvent(event)
