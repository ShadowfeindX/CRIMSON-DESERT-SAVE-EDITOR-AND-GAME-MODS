from __future__ import annotations

import datetime
import json
import logging
import os
import re
import shutil
import struct
import sys
import tempfile
import traceback
import textwrap
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import Qt, QSize, QTimer, Signal, Slot
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
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .ui.helpers import CONFIG

from .models import ItemEditorInfo

from .dmm_types import ItemInfo
from gui.theme import COLORS, CATEGORY_COLORS
from gui.iteminfo_index import IteminfoIndex


from models import SaveItem, SaveData, UndoEntry
from item_db import ItemNameDB
from equipment_sets import SetManager, EquipmentSet, SetItem, StatOperation
from paz_patcher import (
    PazPatchManager,
    PazPatch,
    ItemBuffPatcher,
    ItemRecord,
    StatTriplet,
    BUFF_HASHES,
    BUFF_NAMES,
    ItemEffectPatcher,
)
from icon_cache import IconCache, ICON_SIZE

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


from gui.tabs.item_editor.ui import ItemEditorLayout
from gui.tabs.item_editor.helpers import find_game_path
import dmm_parser as dmm


class ItemEditorTab(QWidget):
    s_status_message = Signal()
    # s_config_save_requested = Signal()
    s_iteminfo_extracted = Signal(ItemEditorInfo)

    def __init__(self, path="", parent=None):
        super().__init__(parent)

        ui = ItemEditorLayout(self)
        # ui.s_config_save_requested.connect(self.s_config_save_requested.emit)

        ui.action_bar.s_extract.connect(self._extract)

        self.s_iteminfo_extracted.connect(ui.items_table.load)

        self._game_path = (
            path or CONFIG["game_install_path"] or find_game_path()
        )

        self._ui = ui

    @Slot(str)
    def set_game_path(self, path: str):
        self.game_path = path

    @Slot(str)
    def _extract(self, type: str = "overlay"):
        match type:
            case "overlay":
                log.info("extracting...")

                try:
                    with open("data/sample.json", "r+", encoding="utf-8") as f:
                        data = ItemEditorInfo(
                            [
                                json.load(f)
                                # {
                                #     "item_name": "Test Item",
                                #     "string_key": "test_item",
                                #     "cooltime": {"a": 1, "b": 1, "c": 1},
                                #     "gimmick_info": 0,
                                #     "item_tier": 1,
                                #     "key": 100,
                                # }
                            ]
                        )
                        self.s_iteminfo_extracted.emit(data)
                except BaseException as e:
                    print(e)
                    log.critical(
                        "Error: Failed to load test data!\n"
                        "Please provite a sample.json in your data folder!"
                    )

            case "vanilla":
                log.info("extracting vanilla...")

                pabgb = dmm.extract_file(
                    game_dir=self._game_path,
                    group_name="0008",
                    dir_path="gamedata/binary__/client/bin",
                    file_name="iteminfo.pabgb",
                )
                data = dmm.parse_table("iteminfo", pabgb)

                iteminfo = ItemEditorInfo(data)
                self.s_iteminfo_extracted.emit(iteminfo)

                with open("./data/sample.json", "w") as f:
                    json.dump(data[0], f)

                log.info(f"extracted {len(data)} items from vanilla pabgb...")
                log.info("sample item data written to data/sample.json")
            case _:
                log.critical("Invalid extract type: %s", type)

    def closeEvent(self, event):
        self._ui.closeEvent(event)
        return super().closeEvent(event)
