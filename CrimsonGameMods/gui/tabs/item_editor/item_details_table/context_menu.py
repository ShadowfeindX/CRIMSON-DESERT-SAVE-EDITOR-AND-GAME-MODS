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

class DetailsTableContextMenu(QMenu):
    instance: Self | None = None

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    @classmethod
    def open(cls, parent: QWidget, index: QModelIndex, position: QPoint, blocking=True):
        if cls.instance is None:
            cls.instance = cls(parent, toolTipsVisible=True)

        def test():
            pass


        menu = cls.instance
        menu.clear()
        act_test = QAction("hello darling", menu)
        act_test.triggered.connect(test)

        menu.addAction(act_test)
        return menu.exec(position) if blocking else menu.popup(position)
