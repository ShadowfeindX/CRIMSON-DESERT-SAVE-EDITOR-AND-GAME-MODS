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
    def __init__(self, parent):
        super().__init__(parent)

        self.addWidget(self.action_bar())
        self.addWidget(self.search_bar())
        self.addWidget(QFrame())
        self.addStretch(1)

        """
        Action Bar
            Extract
            Extract Vanilla
            Reset
            Apply to Game
            Import
            Export
            Transmog
            Custom Items
            Other
        Search Bar
            Favorites Quick Filter
            Search
            Category Filter
            Save Filter
            Icons
        Main Frame
            Item List
            Item Details
            Editor Tabs
                Presets
                Quick Edit Options
                Passives/Effects
                Stats/Buffs
                Imbue
                Global OPtions
                Bulk Options
                Raw Edit Json
        """

    def search_bar(self):
        bar = QWidget()
        layout = QHBoxLayout(bar)
        # layout.setSpacing(4)

        search = QLineEdit()
        search.setPlaceholderText(
            "Item name (e.g. Earring, Sword, Necklace)..."
        )

        search_btn = QPushButton("Search")

        fav_btn = QPushButton("⭐")
        fav_btn.setToolTip("Show favorited items only")

        # Category filter (populated after extract — empty until then)
        category_filter = QComboBox()
        category_filter.setToolTip(
            "Restrict results to items in a specific category.\n"
            "Populated from live iteminfo after Extract."
        )
        category_filter.setMinimumWidth(180)
        category_filter.addItem("All categories", None)

        inv_btn = QPushButton("My Inventory")
        inv_btn.setToolTip(
            "Show only items from your loaded save that exist in iteminfo"
        )

        icons_btn = QPushButton("Icons")
        icons_btn.setToolTip("Toggle item icons in the items list")

        layout.addWidget(icons_btn)
        layout.addWidget(fav_btn)
        layout.addWidget(QLabel("Search:"))
        layout.addWidget(search, 1)
        layout.addWidget(search_btn)
        layout.addWidget(category_filter)
        layout.addWidget(inv_btn)
        return bar

    def action_bar(self):
        bar = QWidget()
        layout = QHBoxLayout(bar)

        extract_btn = QPushButton("Extract")
        extract_menu = QMenu(extract_btn)
        extract_btn.setMenu(extract_menu)
        extract_menu.addAction("Extract from Overlay")
        extract_menu.addAction("Extract Vanilla")

        import_btn = QPushButton("Import")
        import_menu = QMenu(import_btn)
        import_btn.setMenu(import_menu)
        import_menu.addAction("Import Config")
        import_menu.addAction("Import v3 Mod")
        import_menu.addAction("Import Mod Folder")

        export_btn = QPushButton("Export")
        export_menu = QMenu(export_btn)
        export_btn.setMenu(export_menu)
        export_menu.addAction("Export Config")
        export_menu.addAction("Export v3 Mod")
        export_menu.addAction("Export Mod Folder")

        apply_btn = QPushButton("Apply to Game")
        reset_btn = QPushButton("Reset")

        layout.addWidget(extract_btn)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)
        layout.addWidget(apply_btn)
        layout.addWidget(reset_btn)
        layout.addStretch(1)
        return bar

    def items_table(self):
        
        "STUB"
