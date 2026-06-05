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

from .proxy import ItemTableModelProxy

from .model import ItemTableModel

from .view import ItemEditorTableView
from ..helpers import ItemEditorInfo, ItemEditorInfoDetails
from ..dmm_types import ItemInfo

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


log = logging.getLogger(__name__)


class ItemTable(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui(parent)

    def _build_ui(self, parent):
        layout = QVBoxLayout(self)
        self.model = ItemTableModel(self)
        self.proxy = ItemTableModelProxy(self, self.model)
        self.table = ItemEditorTableView(parent, self.proxy)
        self.proxy.setFilterKeyColumn(-1)

        layout.addWidget(self.table)
        self.table.refresh_view()

    @Slot(ItemEditorInfo)
    def load(self, info: ItemEditorInfo):
        self.model.load(info)
        self.table.refresh_view()

    @Slot(str)
    def search(self, term: str):
        self.proxy.setFilterRegularExpression(
            QRegularExpression(
                term, QRegularExpression.PatternOption.CaseInsensitiveOption
            )
        )
        self.table.refresh_view()
