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

from .ui.models import ItemEditorInfo

from .ui.dmm_types import ItemInfo
from gui.theme import COLORS, CATEGORY_COLORS
from gui.iteminfo_index import IteminfoIndex


def _safe_iv(v, default=0):
    """Safely extract int from plain int, float, or dmm_parser nested dict.
    dmm_parser returns numeric structs as {'a': int, 'b': int, 'c': int}.
    """
    if v is None:
        return default
    if isinstance(v, (int, float, bool)):
        return int(v)
    if isinstance(v, dict):
        for k in ("a", "value", "_v", "v", "val", "n", "data"):
            if k in v:
                sub = v[k]
                if isinstance(sub, (int, float, bool)):
                    return int(sub)
                if sub is None:
                    return default
        return default
    try:
        return int(v)
    except Exception:
        return default


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


def _can_write_game_dir(game_path: str) -> bool:
    try:
        _t = os.path.join(game_path, ".se_write_test")
        with open(_t, "w") as _f:
            _f.write("t")
        os.remove(_t)
        return True
    except Exception:
        return False


def _is_game_running() -> bool:
    try:
        out = subprocess.check_output(
            [
                "tasklist",
                "/FI",
                "IMAGENAME eq CrimsonDesert.exe",
                "/FO",
                "CSV",
                "/NH",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return "CrimsonDesert.exe" in out
    except Exception:
        return False


from gui.tabs.item_editor.ui import ItemEditorLayout
from gui.tabs.item_editor.ui.helpers import find_game_path
import dmm_parser as dmm


class ItemEditorTab(QWidget):
    s_status_message = Signal()
    s_config_save_requested = Signal()
    s_iteminfo_extracted = Signal(ItemEditorInfo)

    def __init__(self, path="", config: Optional[dict] = None, parent=None):
        super().__init__(parent)

        ui = ItemEditorLayout(self)
        ui.action_bar.s_extract.connect(self._extract)

        self.s_iteminfo_extracted.connect(ui.items_table.load)

        self._game_path = (
            path or config["game_install_path"] or find_game_path()
        )

    @Slot(str)
    def set_game_path(self, path: str):
        self.game_path = path

    @Slot(str)
    def _extract(self, type: str = "overlay"):
        match type:
            case "overlay":
                log.info("extracting...")

                data = ItemEditorInfo([{"item_name": "Test Item", "key": 100}])
                self.s_iteminfo_extracted.emit(data)
                "stub"

            case "vanilla":
                log.info("extracting vanilla...")

                pabgb = dmm.extract_file(
                    game_dir=self._game_path,
                    group_name="0008",
                    dir_path="gamedata/binary__/client/bin",
                    file_name="iteminfo.pabgb",
                )
                data = dmm.parse_table("iteminfo", pabgb, shape="v3.1")

                iteminfo = ItemEditorInfo(data)
                self.s_iteminfo_extracted.emit(iteminfo)

                with open("./data/sample.json", "w") as f:
                    json.dump(data[0], f)

                log.info(f"extracted {len(data)} items from vanilla pabgb...")
                log.info(f"sample item data written to data/sample.json")
            case _:
                log.critical("Invalid extract type: %s", type)
