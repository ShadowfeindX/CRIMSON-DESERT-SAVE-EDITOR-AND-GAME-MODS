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
from typing import Callable, List, Optional, Self, Tuple, TYPE_CHECKING, cast

from PySide6.QtCore import (
    QAbstractListModel,
    QAbstractTableModel,
    QPoint,
    QRegularExpression,
    QSortFilterProxyModel,
    Qt,
    QSize,
    QTimer,
    Signal,
    Slot,
    QModelIndex,
)
from PySide6.QtGui import QAction, QBrush, QCloseEvent, QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QCompleter,
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

from data.item_editor_database.database_entry import Skill, Stat
import gui.tabs.item_editor.editor_controls.quick.stats as stats_row
import gui.tabs.item_editor.editor_controls.quick.passives as passives_row
import gui.tabs.item_editor.editor_controls.quick.buffs as buffs_row
from .data_row import DataRow
from ...dmm_types import EnchantStatChange

from ...helpers import STATE
from ...signals import SIGNALS, SLOTS

from ...helpers import *


class QuickWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setWindowTitle("Quick Item Editor")

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

    def closeEvent(self, event: QCloseEvent):
        return super().closeEvent(event)

    def _ready_signals(self):
        "STUB"

    def _connect_signals(self):
        "STUB"

    def _build_ui(self, parent: QWidget):
        """
        edit stack size
        edit sockets
        edit default enchant level
        edit charges
        edit cooldown
        edit gimmick
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.passive_editor = passives_row.new()
        self.buff_editor = buffs_row.new()
        self.stat_editor = stats_row.new()
        self.stack_size_editor = self._build_stack_row()

        layout.addWidget(self.passive_editor)
        layout.addWidget(self.buff_editor)
        layout.addWidget(self.stat_editor)
        layout.addWidget(self.stack_size_editor)

    def _build_stack_row(self):
        stack = QWidget()
        row = QHBoxLayout(stack)

        spin = QSpinBox(minimum=1, maximum=999999)

        def add(self):
            if self._data is None or self._add_fn is None:
                return

            return self._add_fn(
                SLOTS.current_selection(),
                self._data[self._list.currentIndex()],
                self._value.value(),
            )

        def remove(self):
            if self._data is None or self._remove_fn is None:
                return

            return self._remove_fn(
                SLOTS.current_selection(),
                self._data[self._list.currentIndex()],
            )

        def _set():
            for idx in SLOTS.current_selection():
                item = ItemEditorInfoDetails(idx)
                if spin.value() != item.stack_size():
                    item.stack_size(spin.value())

        def _reset():
            "STUB"

        set = QPushButton("Set Stack Size")
        set.clicked.connect(_set)
        # reset = QPushButton("Reset")
        # reset.clicked.connect(_reset)

        row.addWidget(spin)
        row.addWidget(set)
        # row.addWidget(reset)
        row.addStretch(1)
        return stack
