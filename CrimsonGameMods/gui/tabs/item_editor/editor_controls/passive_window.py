from __future__ import annotations

from collections.abc import ItemsView
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
    s_load_passive_skill_index = Signal()

    _selected_items: list[ItemEditorInfoDetails] = []
    _selected_passives: dict[str, str] = {}

    def __init__(self, parent: QWidget):
        super().__init__()

        self.setWindowTitle("Passives Editor")

        self.skill_index: dict[str, str] = {}

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

        self.s_load_passive_skill_index.emit()

    def closeEvent(self, event: QCloseEvent):
        del self.skill_index
        return super().closeEvent(event)

    def _ready_signals(self):
        "STUB"

    def _connect_signals(self):
        SIGNALS.s_items_selected.connect(self._set_selected_items)
        self.s_load_passive_skill_index.connect(self.load_skill_index)
        self.s_load_passive_skill_index.connect(
            self._indexed_passives_table.load_passives
        )

        self.action_bar.s_add.connect(self.add_selected_passives)
        self.action_bar.s_remove.connect(self.remove_selected_passives)
        self._selected_passives.items()
        "STUB"

    def get_skill_name(self, key: str) -> str:
        return self.skill_index.get(key, "(unknown)")

    def get_skill_index(self):
        return self.skill_index

    def add_selected_passives(self):
        s_list = self._selected_passives_table.selected_rows()
        i_list = self._indexed_passives_table.selected_rows()

        for index in i_list:
            self._selected_passives.setdefault(index.data(), "1")

        for index in s_list:
            key = index.data()
            level = index.siblingAtColumn(2).data()

            current_level = self._selected_passives.get(key, "1")
            self._selected_passives[key] = max(current_level, level)

        self._target_passives_table.load_passives(
            self._selected_passives.items()
        )

    def remove_selected_passives(self):
        "STUB"

    def load_skill_index(self):
        try:
            with open(
                "data/passive_skill_catalog.json", "r", encoding="utf-8"
            ) as f:
                catalog = json.load(f)
                self.skill_index = copy(catalog["full_skill_index"]) or {}
                self.skill_index.pop("999999")
        except BaseException as e:
            log.error(f"An error occurred while loading the skill index!\n{e}")

    def _build_ui(self, parent: QWidget):
        main_layout = QVBoxLayout(self)
        table_layout = QHBoxLayout()

        self.action_bar = ActionBar(self)
        self._selected_passives_table = SelectedPassivesTable(self)
        self._indexed_passives_table = IndexedPassivesTable(self)
        self._target_passives_table = TargetPassivesTable(self)
        bottom_bar = self._build_bottom_bar()

        table_layout.addWidget(self._selected_passives_table)
        table_layout.addWidget(self._indexed_passives_table)

        main_layout.addWidget(self.action_bar)
        main_layout.addLayout(table_layout)
        main_layout.addWidget(self._target_passives_table)
        main_layout.addLayout(bottom_bar)

    def _build_bottom_bar(self):
        bar = QHBoxLayout()

        apply_btn = QPushButton("Apply Passives to Selected Items")
        remove_btn = QPushButton("Remove Passives from Selected Items")
        clear_btn = QPushButton("Clear Target List")

        bar.addWidget(apply_btn)
        bar.addWidget(remove_btn)
        bar.addWidget(clear_btn)

        return bar

    def _refresh_view(self):
        "stub"

    def _set_selected_items(self, items: list[ItemEditorInfoDetails]):
        PassiveWindow._selected_items[:] = items
        self._selected_passives_table.load_passives()


class ActionBar(QWidget):
    s_add = Signal()
    s_remove = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(2)

        fav_btn = QPushButton("⭐")
        search_btn = QPushButton("Search")
        search_box = QLineEdit()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.s_add)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.s_remove)

        layout.addWidget(fav_btn)
        layout.addWidget(search_btn)
        layout.addWidget(search_box)
        layout.addWidget(add_btn)
        layout.addWidget(remove_btn)

        return layout


class TargetPassivesTable(QWidget):
    def __init__(self, parent: PassiveWindow):
        super().__init__(parent)

        self.get_skill_name = parent.get_skill_name

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            [
                "Key",
                "Name",
                "Level",
            ]
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(24)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        """
        Get all currently selected rows
        Extract passive key and levels (use 1 as default level)
        Add all passives to selected passives dictionary
            Overrite key if level is higher
        Refresh target passives list

        Optional Optimizations:
            Mark list as stale when adding/removing passives. Only rebuild if stale
            Store change flag when selecion changes. Ignore add/remove signal if selection is unchanged
        """

        self.table = table

        layout.addWidget(QLabel("Passives to Apply:"))
        layout.addWidget(table)

    def load_passives(self, passives: ItemsView[str, str]):
        self.table.setRowCount(len(passives))
        for row, (key, level) in enumerate(passives):
            name = self.get_skill_name(key)

            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(level))


class IndexedPassivesTable(QWidget):
    def __init__(self, parent: PassiveWindow):
        super().__init__(parent)

        self.get_skill_name = parent.get_skill_name
        self.get_skill_index = parent.get_skill_index

        self._build_ui()

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def _build_ui(self):
        table = QTableWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(
            [
                "Key",
                "Name",
            ]
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda: table.clearSelection()
        )

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(24)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.table = table

        layout.addWidget(QLabel("Passive Skill Index:"))
        layout.addWidget(table)

    def load_passives(self):
        skills = self.get_skill_index().items()
        self.table.setRowCount(len(skills))

        for row, (key, name) in enumerate(skills):
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(name))


class SelectedPassivesTable(QWidget):
    def __init__(self, parent: PassiveWindow):
        super().__init__(parent)

        self.get_skill_name = parent.get_skill_name
        self.get_skill_index = parent.get_skill_index
        self._selected_items = parent._selected_items

        self._build_ui()

    def _build_ui(self):
        table = QTableWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            [
                "Key",
                "Name",
                "Level",
            ]
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda: table.clearSelection()
        )

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(24)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.table = table

        layout.addWidget(QLabel("Passives on Selected Items:"))
        layout.addWidget(table)

    def selected_rows(self):
        return self.table.selectionModel().selectedRows()

    def load_passives(self):
        skills = self.get_skill_index()
        self.table.setRowCount(0)

        # Collect highest level for each skill key
        skill_levels: dict[int, int] = {}
        for item in self._selected_items:
            passives = item.passives() or []

            for passive in passives:
                skill_key = passive["skill"]
                level = passive["level"]
                # Keep only the highest level
                if skill_key not in skill_levels or level > skill_levels[skill_key]:
                    skill_levels[skill_key] = level

        # Display unique skills with their highest level
        row = 0
        for skill_key, level in skill_levels.items():
            self.table.setRowCount(row + 1)
            self.table.setItem(
                row, 0, QTableWidgetItem(str(skill_key))
            )
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    skills.get(str(skill_key), "(unknown)")
                ),
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(str(level))
            )
            row += 1
