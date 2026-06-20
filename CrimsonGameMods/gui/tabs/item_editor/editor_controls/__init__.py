from __future__ import annotations

import datetime
from functools import partial, partialmethod
import gc
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

from PySide6 import QtCore
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QAction, QBrush, QCloseEvent, QColor, QFont, QIcon
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

from .quick.window import QuickWindow

from .json_window import JSONWindow
from .history_window import HistoryWindow

from .passives.window import PassiveWindow
from .buffs.window import BuffWindow
from gui.tabs.item_editor.helpers import ItemEditorInfoDetails, HistoryEntry, log
from gui.tabs.item_editor.signals import SIGNALS


from .presets_window import PresetsWindow
from gui.tabs.item_editor.helpers import (
    center_window_in_parent,
    make_collapsible,
)
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


log = logging.getLogger(__name__)

from gui.theme import COLORS, CATEGORY_COLORS
from gui.iteminfo_index import IteminfoIndex


class EditorControls(QFrame):
    WINDOW_REGISTRY = {
        "preset": PresetsWindow,
        "quick": QuickWindow,
        "passive": PassiveWindow,
        "json": JSONWindow,
        "history": HistoryWindow,
        "buff": BuffWindow,
    }

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._windows: dict[str, QWidget] = {}
        self._build_ui(parent)
        self._current_item = None
        SIGNALS.s_item_selected.connect(self._set_current_item)

    def get_current_item(self) -> ItemEditorInfoDetails | None:
        return self._current_item

    def open_window(self, id: str):
        # Look up the class from the dictionary
        cls = self.WINDOW_REGISTRY.get(id)

        # Log error and return if class not found
        if not cls:
            log.error(f"Error: '{id}' Window not found in registry.")
            return

        # Check if the window is already open and active
        if id in self._windows:
            center_window_in_parent(self._windows[id], self, True)
            self._windows[id].raise_()
            self._windows[id].activateWindow()
            return


        def cleanup():
            self._windows.pop(id, None)
            gc.collect()

        # Instantiate the class dynamically
        new_window: QWidget = cls(self)

        # Hook into the close event to clean up memory when closed
        new_window.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.Window)
        new_window.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        new_window.destroyed.connect(cleanup)

        # Store reference in the active dictionary using the ID as the key
        self._windows[id] = new_window
        new_window.show()
        center_window_in_parent(self._windows[id], self, True)

    def closeEvent(self, event: QCloseEvent):
        active_instances = list(self._windows.values())
        for sub_window in active_instances:
            if sub_window.isVisible():
                sub_window.close()
        event.accept()

    def _build_ui(self, parent: QWidget):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        std_grid = self._build_standard_grid()
        adv_grid = self._build_advanced_grid()
        dev_grid = self._build_dev_grid()
        std_grid_collapsible = make_collapsible(
            "Standard Options",
            std_grid,
            start_open=False,
            config_key="itemeditor_standard",
        )
        adv_grid_collapsible = make_collapsible(
            "Advanced Options",
            adv_grid,
            start_open=False,
            config_key="itemeditor_advanced",
        )
        dev_grid_collapsible = make_collapsible(
            "Dev Options",
            dev_grid,
            start_open=False,
            config_key="itemeditor_dev",
        )

        layout.addWidget(std_grid_collapsible)
        layout.addWidget(adv_grid_collapsible)
        layout.addWidget(dev_grid_collapsible)
        layout.addStretch(1)

    def _build_standard_grid(self):
        grid = QWidget()
        layout = QGridLayout(grid)
        layout.setSpacing(8)
        cols = 3
        btns: dict[str, QPushButton] = {}

        btns["preset"] = QPushButton("Presets")
        btns["preset"].clicked.connect(self._open_window("preset"))
        btns["quick"] = QPushButton("Quick Edit")
        btns["quick"].clicked.connect(self._open_window("quick"))

        # btns["preview"] = QPushButton("Show Preview")
        # btns["transmog"] = QPushButton("Transmog")
        # btns["custom"] = QPushButton("Custom Item")

        btns["bulk"] = QPushButton("Bulk Options")
        btns["global"] = QPushButton("Global Options")

        self._standard_controls = btns

        for i, (id, btn) in enumerate(btns.items()):
            # bc,fc = styles[i % len(styles)]
            r, c = divmod(i, cols)
            # btn.setStyleSheet(gen_styles(fc,bc))
            # if id == "presets":
            #     btn.clicked.connect(lambda: self._open_window(id))
            layout.addWidget(btn, r, c)

        return grid

    def _build_advanced_grid(self):
        grid = QWidget()
        layout = QGridLayout(grid)
        layout.setSpacing(8)
        cols = 3
        btns = {}

        btns["passive"] = QPushButton("Edit Passives")
        btns["passive"].clicked.connect(self._open_window("passive"))

        btns["buff"] = QPushButton("Edit Buffs")
        btns["buff"].clicked.connect(self._open_window("buff"))
        btns["stat"] = QPushButton("Edit Stats")
        btns["drop"] = QPushButton("Edit Drop Data")
        btns["effect"] = QPushButton("Edit Gimmick")
        btns["imbue"] = QPushButton("Edit VFX")

        self._advanced_controls = btns

        for i, btn in enumerate(btns.values()):
            # bc,fc = styles[i % len(styles)]
            r, c = divmod(i, cols)
            # btn.setStyleSheet(gen_styles(fc,bc))
            layout.addWidget(btn, r, c)

        return grid

    def _build_dev_grid(self):
        grid = QWidget()
        layout = QGridLayout(grid)
        layout.setSpacing(8)
        cols = 3
        btns = {}

        btns["json"] = QPushButton("Edit JSON")
        btns["json"].clicked.connect(self._open_window("json"))
        btns["history"] = QPushButton("View History")
        btns["history"].clicked.connect(self._open_window("history"))
        btns["dump"] = QPushButton("Dump ITEMINFO")
        btns["diff"] = QPushButton("Show Item Diff")
        btns["inspect"] = QPushButton("Inspect Item")

        self._dev_controls = btns

        for i, btn in enumerate(btns.values()):
            # bc,fc = styles[i % len(styles)]
            r, c = divmod(i, cols)
            # btn.setStyleSheet(gen_styles(fc,bc))
            layout.addWidget(btn, r, c)

        return grid

    def _open_window(self, id: str):
        return partial(self.open_window, id)

    def _set_current_item(self, item: ItemEditorInfoDetails):
        self._current_item = item
