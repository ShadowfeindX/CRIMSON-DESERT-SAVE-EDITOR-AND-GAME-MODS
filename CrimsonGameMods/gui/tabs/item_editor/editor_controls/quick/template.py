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

from data.item_editor_database.database_entry import Skill, Stat, Buff
from .data_row import DataRow
from ...dmm_types import EnchantStatChange

from ...helpers import STATE
from ...signals import SIGNALS, SLOTS

from ...helpers import *


def _add(indexes: list[int], selected: Stat, value: int):
    pass

def _remove(indexes: list[int], selected: Stat):
    pass


def new():
    return DataRow(
        label="",
        load_fn=None,
        add_fn=_add,
        remove_fn=_remove,
        min_value=0,
        max_value=10,
    )
