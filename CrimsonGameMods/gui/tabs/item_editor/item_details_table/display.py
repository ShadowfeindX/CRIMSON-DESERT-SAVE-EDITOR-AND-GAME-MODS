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
from typing import Any, Callable, List, Optional, Tuple

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
    QStyledItemDelegate,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .roles import CustomItemDataRole, TypeRole


# from .view import ItemEditorTableView
from ..signals import SIGNALS, SLOTS

from ..helpers import *
from ..dmm_types import ItemInfo

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import DetailsTableModel

    "STUB"

Role = Qt.ItemDataRole
C_Role = CustomItemDataRole


class IntRangeDelegate(QStyledItemDelegate):
    def __init__(self, min_val, max_val, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setRange(self.min_val, self.max_val)
        return editor

    def setEditorData(self, editor, index):
        # Correctly using index.model().data() to fetch from the proxy
        model = index.model()
        value = model.data(index, Qt.ItemDataRole.EditRole)
        editor.setValue(int(value) if value is not None else self.min_val)

    def setModelData(self, editor, model, index):
        # Submits data safely back through the active model/proxy
        editor.interpretText()
        model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)

    def display(
        self, details: ItemEditorInfoDetails = None
    ) -> list[dict[Role | C_Role, tuple]]:

        if details is None:
            return self._display


_details: ItemEditorInfoDetails = None

COLUMNS = 1


def new_row(value):
    return tuple(value for _ in range(COLUMNS))


NOT_IMPLEMENTED = new_row(None)


def new_view(data={}):
    return (
        {role.value: NOT_IMPLEMENTED for role in Role}
        | {role.value: NOT_IMPLEMENTED for role in CustomItemDataRole}
        | data
    )


def passives_view():
    view = []

    view.append(
        new_view(
            {
                C_Role.TypeRole: new_row(TypeRole.Header),
                Role.DisplayRole: new_row("--- Passives ---"),
                Role.TextAlignmentRole: new_row(Qt.AlignmentFlag.AlignCenter),
            }
        )
    )

    view.extend(
        new_view(
            {
                C_Role.TypeRole: (TypeRole.Passive, i),
                Role.DisplayRole: (
                    passive["skill"],
                    STATE.skill_index[str(passive["skill"])]["string_key"],
                    passive["level"],
                ),
                Role.EditRole: new_row(passive["level"]),
            }
        )
        for i, passive in enumerate(_details.passives())
    )

    return view


def buffs_view():
    view = []
    # --- Buffs Header ---
    view.append(
        new_view(
            {
                C_Role.TypeRole: new_row(TypeRole.Header),
                Role.DisplayRole: new_row("--- Buffs ---"),
                Role.TextAlignmentRole: new_row(Qt.AlignmentFlag.AlignCenter),
            }
        )
    )

    # --- Buffs List ---
    view.extend(
        new_view(
            {
                C_Role.TypeRole: (TypeRole.Buff, i),
                Role.DisplayRole: (
                    buff["buff"],
                    STATE.buff_index[str(buff["buff"])]["string_key"],
                    buff["level"],
                ),
                Role.EditRole: new_row(buff["level"]),
            }
        )
        for i, buff in enumerate(_details.buffs())
    )

    return view

def stats_view():
    "STUB"

OTHER_HEADER = False


def other_view(key: str, value: Any):
    global OTHER_HEADER

    view = []
    if not OTHER_HEADER:
        # --- Other Header ---
        view.append(
            new_view(
                {
                    C_Role.TypeRole: new_row(TypeRole.Header),
                    Role.DisplayRole: new_row("--- Other ---"),
                    Role.TextAlignmentRole: new_row(
                        Qt.AlignmentFlag.AlignCenter
                    ),
                }
            )
        )

    match key:
        case "stack_size":
            view.append(
                new_view(
                    {
                        C_Role.TypeRole: new_row(TypeRole.Stretch),
                        Role.DisplayRole: ("Stack Size", None, value),
                        Role.EditRole: new_row(value),
                        Role.TextAlignmentRole: new_row(
                            Qt.AlignmentFlag.AlignCenter
                        ),
                    }
                )
            )
        case _:
            view.append(new_view({Role.DisplayRole: (None, key, value)}))

    return view


# # --- Other Data ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Buff, i),
#             Role.DisplayRole: (
#                 buff["buff"],
#                 STATE.buff_index[str(buff["buff"])]["string_key"],
#                 buff["level"],
#             ),
#             Role.EditRole: new_row(buff["level"]),
#         }
#     )
#     for i, buff in enumerate(_details.buffs())
# )


def build_view(key: str, value: Any):
    match key:
        case "passives":
            return passives_view()
        case "buffs":
            return buffs_view()
        case _:
            return other_view(key, value)


def display(self: DetailsTableModel, details: ItemEditorInfoDetails):
    global COLUMNS, NOT_IMPLEMENTED
    COLUMNS = self.columnCount()
    NOT_IMPLEMENTED = new_row(None)

    global _details
    _details = details

    views = []
    for key, value in details.editable():
        views.extend(build_view(key, value))

    return views

    # def display(
    #     self, details: ItemEditorInfoDetails = None
    # ) -> list[dict[Role | C_Role, tuple]]:

    #     if details is None:
    #         return self._display

    #     return _build_views(self, details)


# views = []
# for key, value in _details.editable():
#     views.extend(build_views(key, value))
# # map(views.extend, map(build_views, details.editable()))
# print(views)
# views.clear()

# # --- Passives Header ---
# views.append(
#     new_view(
#         {
#             # C_Role.HeaderRole: new_row(True),
#             C_Role.TypeRole: new_row(TypeRole.Header),
#             Role.DisplayRole: new_row("--- Passives ---"),
#         }
#     )
# )

# # --- Passives List ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Passive, i),
#             Role.DisplayRole: (
#                 passive["skill"],
#                 STATE.skill_index[str(passive["skill"])]["string_key"],
#                 passive["level"],
#             ),
#             Role.EditRole: new_row(passive["level"]),
#         }
#     )
#     for i, passive in enumerate(_details.passives())
# )

# # --- Buffs Header ---
# views.append(
#     new_view(
#         {
#             C_Role.TypeRole: new_row(TypeRole.Header),
#             Role.DisplayRole: new_row("--- Buffs ---"),
#         }
#     )
# )

# # --- Buffs List ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Buff, i),
#             Role.DisplayRole: (
#                 buff["buff"],
#                 STATE.buff_index[str(buff["buff"])]["string_key"],
#                 buff["level"],
#             ),
#             Role.EditRole: new_row(buff["level"]),
#         }
#     )
#     for i, buff in enumerate(_details.buffs())
# )

# # --- Other Header ---
# views.append(
#     new_view(
#         {
#             C_Role.TypeRole: new_row(TypeRole.Header),
#             Role.DisplayRole: new_row("--- Other ---"),
#         }
#     )
# )
# # --- Other Data ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Buff, i),
#             Role.DisplayRole: (
#                 buff["buff"],
#                 STATE.buff_index[str(buff["buff"])]["string_key"],
#                 buff["level"],
#             ),
#             Role.EditRole: new_row(buff["level"]),
#         }
#     )
#     for i, buff in enumerate(_details.buffs())
# )

# self._display = views
