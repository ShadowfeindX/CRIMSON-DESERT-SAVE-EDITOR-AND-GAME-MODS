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

from ..dmm_types import PassiveSkillLevel

from ..signals import SIGNALS

from ..helpers import *


class PassiveWindow(QWidget):
    _selected_items: list[ItemEditorInfoDetails] = []

    def __init__(self, parent: QWidget):
        super().__init__()

        self.setWindowTitle("Passives Editor")

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

    def closeEvent(self, event: QCloseEvent):
        return super().closeEvent(event)

    def _ready_signals(self):
        "STUB"

    def _connect_signals(self):
        SIGNALS.s_items_selected.connect(self._set_selected_items)
        "STUB"

    def _build_ui(self, parent: QWidget):
        outer_layout = QVBoxLayout(self)
        table_layout = QHBoxLayout()

        top_bar = QFrame()
        left_table = QFrame()
        right_table = QFrame()
        target_list = QFrame()
        bottom_bar = QFrame()

        left_table_layout = QVBoxLayout(left_table)
        existing_passives = QTableWidget()
        existing_passives.setColumnCount(2)

        # left_table = None

        # left_table_layout.setContentsMargins(0, 0, 0, 0)
        # left_table_layout.setSpacing(2)
        # self._buff_selected_label = QLabel("No item selected — search and click an item on the left")
        # self._buff_selected_label.setStyleSheet(
        #     f"color: {COLORS['text_dim']}; font-weight: bold; padding: 2px 4px;"
        # )
        # left_table_layout.addWidget(self._buff_selected_label)
        # left_table_layout.addWidget(QLabel("Current Stats / Buffs:"))
        existing_passives.setHorizontalHeaderLabels(
            [
                "Key",
                "Level",
            ]
        )
        # existing_passives.setEditTriggers(QAbstractItemView.NoEditTriggers)
        existing_passives.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        # existing_passives.setSelectionMode(QAbstractItemView.SingleSelection)
        # existing_passives.setContextMenuPolicy(Qt.CustomContextMenu)
        # existing_passives.customContextMenuRequested.connect(self._buff_stats_context_menu)
        hdr_stats = existing_passives.horizontalHeader()
        # hdr_stats.setSectionResizeMode(0, QHeaderView.Interactive)
        # existing_passives.setColumnWidth(0, 240)
        # hdr_stats.setSectionResizeMode(1, QHeaderView.Interactive)
        # existing_passives.setColumnWidth(1, 100)
        hdr_stats.setStretchLastSection(True)
        existing_passives.verticalHeader().setDefaultSectionSize(24)
        # existing_passives.setMinimumHeight(100)
        # left_table_layout.addWidget(existing_passives, 1)
        # left_table.setMinimumHeight(120)
        # left_table.setMinimumWidth(120)

        """
        Get all currently selected items
        Get passive lists those items
        Combine into one list
        Clear table
        Add all passives from combined list to table
        """

        left_table_layout.addWidget(QLabel("Passives on selected items:"))
        left_table_layout.addWidget(existing_passives)

        table_layout.addWidget(left_table)
        table_layout.addWidget(right_table)

        outer_layout.addWidget(top_bar)
        outer_layout.addLayout(table_layout)
        outer_layout.addWidget(target_list)
        outer_layout.addWidget(bottom_bar)

        self.selected_passives_table = existing_passives

        "STUB"

    def _refresh_view(self):
        table: QTableWidget = self.selected_passives_table
        table.setRowCount(0)

        passive_list: list[PassiveSkillLevel] = []
        passives = None

        for i, item in enumerate(self._selected_items):
            passives = item.passives() or []
            row = len(passive_list)
            for j, passive in enumerate(passives):
                row += j
                table.setRowCount(row + 1)
                table.setItem(row, 0, QTableWidgetItem(f"{passive['skill']}"))
                table.setItem(row, 1, QTableWidgetItem(f"{passive['level']}"))

            passive_list.extend(passives)

    def _set_selected_items(self, items: list[ItemEditorInfoDetails]):
        self._selected_items[:] = items
        self._refresh_view()
