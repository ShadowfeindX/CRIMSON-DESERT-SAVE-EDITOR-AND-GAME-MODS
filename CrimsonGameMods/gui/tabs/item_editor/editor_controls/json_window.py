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

from ..signals import SIGNALS, SLOTS

from ..helpers import *


class JSONWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__()

        self.setWindowTitle("JSON Editor")

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

    def closeEvent(self, event: QCloseEvent):
        return super().closeEvent(event)

    def _ready_signals(self):
        "STUB"

    def _connect_signals(self):
        "STUB"

    def _render_details(self, idx: int):
        try:
            details = ItemEditorInfoDetails(idx)
        except Exception:
            details = None

        self.editor.setPlainText(
            json.dumps(details.data, indent=2, ensure_ascii=False, default=str)
            if details
            else ""
        )

    def _build_ui(self, parent: QWidget):
        layout = QHBoxLayout(self)
        self.editor = QTextEdit()
        layout.addWidget(self.editor)
        self._render_details(SLOTS.current_selection())

        SIGNALS.s_item_selected.connect(self._render_details)
