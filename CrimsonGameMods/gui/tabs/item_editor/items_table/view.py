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
    QEvent,
    QRegularExpression,
    QSortFilterProxyModel,
    Qt,
    QSize,
    QTimer,
    Signal,
    Slot,
    QModelIndex,
)
from PySide6.QtGui import QAction, QBrush, QColor, QContextMenuEvent, QFont, QIcon
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

from ..signals import SIGNALS

# from gui.theme import COLORS, CATEGORY_COLORS

from .context_menu import ItemTableContextMenu

log = logging.getLogger(__name__)

class ItemEditorTableView(QTableView):
    def __init__(self, parent, model):
        super().__init__(parent, sortingEnabled=True, cornerButtonEnabled=False)

        self.setModel(model)
        self.setMinimumWidth(120)
        self.setColumnWidth(1, 180)
        self.verticalHeader().setVisible(False)
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        # self.setSortingEnabled(True)
        # self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        # self.setWordWrap(False)
        
        
        # SIGNALS
        # self.selectionModel().currentRowChanged.connect(lambda: )

        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.customContextMenuRequested.connect(self._show_context_menu)

    def refresh_view(self: QTableView) -> None:
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        return ItemTableContextMenu.open(self, event.globalPos())