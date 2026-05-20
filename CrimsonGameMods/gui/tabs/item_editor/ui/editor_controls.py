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

from gui.tabs.item_editor.ui.helpers import make_collapsible
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

from gui.theme import COLORS, CATEGORY_COLORS
from gui.iteminfo_index import IteminfoIndex


class EditorControls(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui(parent)

    def _build_ui(self, parent: QWidget):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        grid = self._build_standard_grid()
        adv_grid = self._build_advanced_grid()
        adv_grid_collapsible = make_collapsible(
            "Advanced Options",
            adv_grid,
            start_open=False,
            config_key="itemeditor_advanced",
        )

        layout.addWidget(grid)
        layout.addWidget(adv_grid_collapsible)
        layout.addStretch(1)

    def _build_standard_grid(self):
        grid = QWidget()
        layout = QGridLayout(grid)
        layout.setSpacing(8)
        cols = 3
        btns: dict[str, QPushButton] = {}

        btns["preset"] = QPushButton("Presets")
        btns["preview"] = QPushButton("Show Preview")
        btns["passive"] = QPushButton("Edit Passives")
        btns["buff"] = QPushButton("Edit Buffs")
        btns["stat"] = QPushButton("Edit Stats")
        btns["drop"] = QPushButton("Edit Drop Data")
        btns["effect"] = QPushButton("Edit Effects")
        btns["imbue"] = QPushButton("Edit Imbues")
        btns["transmog"] = QPushButton("Transmog")
        btns["custom"] = QPushButton("Custom Item")
        btns["bulk"] = QPushButton("Bulk Options")
        btns["global"] = QPushButton("Global Options")

        self._standard_controls = btns

        for i, btn in enumerate(btns.values()):
            # bc,fc = styles[i % len(styles)]
            r, c = divmod(i, cols)
            # btn.setStyleSheet(gen_styles(fc,bc))
            layout.addWidget(btn, r, c)

        return grid

    def _build_advanced_grid(self):
        grid = QWidget()
        layout = QGridLayout(grid)
        layout.setSpacing(8)
        cols = 3
        btns = {}

        btns["json"] = QPushButton("Edit JSON")
        btns["dump"] = QPushButton("Dump ITEMINFO")
        btns["diff"] = QPushButton("Show Item Diff")

        self._advanced_controls = btns

        for i, btn in enumerate(btns.values()):
            # bc,fc = styles[i % len(styles)]
            r, c = divmod(i, cols)
            # btn.setStyleSheet(gen_styles(fc,bc))
            layout.addWidget(btn, r, c)

        return grid
