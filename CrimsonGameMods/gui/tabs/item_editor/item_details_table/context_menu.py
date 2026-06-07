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
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from ..helpers import ItemEditorInfo, ItemEditorInfoDetails
from ..dmm_types import ItemInfo

# if TYPE_CHECKING:
    

# from gui.theme import COLORS, CATEGORY_COLORS



try:
    from gui.utils import make_help_btn
except Exception:

    def make_help_btn(topic, fn=None):
        btn = QPushButton("?")
        btn.setFixedSize(22, 22)
        if fn:
            btn.clicked.connect(lambda: fn(topic))
        return btn

class DetailsTableContextMenu(QMenu):
    instance: Self | None = None

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    @classmethod
    def open(cls, parent: QWidget, index: QModelIndex, position: QPoint, blocking=True):
        if cls.instance is None:
            cls.instance = cls(parent, toolTipsVisible=True)

        def get_table(parent, entries):
            table = QTableWidget(parent)

            table.setColumnCount(2)
            table.setHorizontalHeaderLabels([
                "Key", "Change Description",
            ])
            table.setRowCount(len(entries))
            for i, (key, old_value, desc) in enumerate(entries):
                table.setItem(i, 0, QTableWidgetItem(key))
                table.setItem(i, 1, QTableWidgetItem(desc))

            hdr_stats = table.horizontalHeader()
            # hdr_stats.setSectionResizeMode(0, QHeaderView.Interactive)
            # table.setColumnWidth(0, 240)
            # hdr_stats.setSectionResizeMode(1, QHeaderView.Interactive)
            # table.setColumnWidth(1, 100)
            hdr_stats.setStretchLastSection(True)
            table.verticalHeader().setDefaultSectionSize(24)
            # table.setMinimumHeight(100)
            return table

        def test():
            details: ItemEditorInfoDetails = index.data(Qt.ItemDataRole.UserRole)
            popup = QDialog(parent)
            layout = QHBoxLayout(popup)
            layout.addWidget(get_table(popup, details.get_history()))
            layout.addWidget(get_table(popup, details.get_registry()))

            popup.exec()


        menu = cls.instance
        menu.clear()
        act_test = QAction("hello darling", menu)
        act_test.triggered.connect(test)

        menu.addAction(act_test)
        return menu.exec(position) if blocking else menu.popup(position)
