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
from typing import Callable, List, Optional, Self, Tuple, TYPE_CHECKING

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

from data.item_editor_database.database_entry import Skill

from ..helpers import (
    load_buff_list,
    load_skill_index,
    load_skill_list,
)
from ..signals import SIGNALS, SLOTS

from ..helpers import *


class QuickWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__()

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
        edit stats
        edit default enchant level
        edit charges
        edit cooldown
        edit gimmick
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.passive_editor = self._build_passive_row()
        self.buff_editor = self._build_buff_row()
        self.stack_size_editor = self._build_stack_row()

        layout.addWidget(self.passive_editor)
        layout.addWidget(self.buff_editor)
        layout.addWidget(self.stack_size_editor)

        "STUB"

    def _build_passive_row(self):
        passives = QWidget()
        row = QHBoxLayout(passives)

        combo = QComboBox()
        combo.setUpdatesEnabled(False)
        combo.addItems(
            [
                f"{skill['key']} - {skill['string_key']}"
                for skill in STATE.skill_list
            ]
        )
        combo.setUpdatesEnabled(True)

        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.lineEdit().setPlaceholderText("Type to search passives...")
        combo.completer().setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        spin = QSpinBox(minimum=1, maximum=10)

        def _add():
            indexes = SLOTS.current_selection()
            selected = STATE.skill_list[combo.currentIndex()]
            level = spin.value()

            for idx in indexes:
                item = ItemEditorInfoDetails(idx)
                new = None

                passives = [
                    skill
                    for skill in item.passives()
                    if skill["skill"] != selected["key"]
                    or (new := skill["level"] == level) is None
                ]

                if not new:
                    passives.append({"skill": selected["key"], "level": level})
                    item.passives(passives)

        def _remove():
            indexes = SLOTS.current_selection()
            selected = STATE.skill_list[combo.currentIndex()]

            for idx in indexes:
                item = ItemEditorInfoDetails(idx)

                passives = [
                    skill
                    for skill in item.passives()
                    if skill["skill"] != selected["key"]
                ]

                if len(item.passives()) != len(passives):
                    item.passives(passives)

        add = QPushButton("Add Passive")
        add.clicked.connect(_add)

        remove = QPushButton("Remove Passive")
        remove.clicked.connect(_remove)

        row.addWidget(spin)
        row.addWidget(combo)
        row.addWidget(add)
        row.addWidget(remove)

        return passives

    def _build_buff_row(self):
        buffs = QWidget()
        row = QHBoxLayout(buffs)

        combo = QComboBox()
        combo.setUpdatesEnabled(False)
        combo.addItems(
            [
                f"{skill['key']} - {skill['string_key']}"
                for skill in STATE.buff_list
            ]
        )
        combo.setUpdatesEnabled(True)

        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.lineEdit().setPlaceholderText("Type to search buffs...")
        combo.completer().setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        spin = QSpinBox(minimum=1, maximum=50)

        def _add():
            indexes = SLOTS.current_selection()
            selected = STATE.buff_list[combo.currentIndex()]
            level = spin.value()

            for idx in indexes:
                item = ItemEditorInfoDetails(idx)
                new = None

                buffs = [
                    buff
                    for buff in item.buffs()
                    if buff["buff"] != selected["key"]
                    or (new := buff["level"] == level) is None
                ]

                if not new:
                    buffs.append({"buff": selected["key"], "level": level})
                    item.buffs(buffs)

        def _remove():
            indexes = SLOTS.current_selection()
            selected = STATE.buff_list[combo.currentIndex()]

            for idx in indexes:
                item = ItemEditorInfoDetails(idx)

                buffs = [
                    buff
                    for buff in item.buffs()
                    if buff["buff"] != selected["key"]
                ]

                if len(item.buffs()) != len(buffs):
                    item.buffs(buffs)

        add = QPushButton("Add Buff")
        add.clicked.connect(_add)

        remove = QPushButton("Remove Buff")
        remove.clicked.connect(_remove)

        row.addWidget(spin)
        row.addWidget(combo)
        row.addWidget(add)
        row.addWidget(remove)

        return buffs

    def _build_stack_row(self):
        stack = QWidget()
        row = QHBoxLayout(stack)

        spin = QSpinBox(minimum=1, maximum=999999)

        def _set():
            "STUB"

        def _reset():
            "STUB"

        set = QPushButton("Set Stack Size")
        set.clicked.connect(_set)
        reset = QPushButton("Reset")
        reset.clicked.connect(_reset)

        row.addWidget(spin)
        row.addWidget(set)
        row.addWidget(reset)
        row.addStretch(1)
        return stack
