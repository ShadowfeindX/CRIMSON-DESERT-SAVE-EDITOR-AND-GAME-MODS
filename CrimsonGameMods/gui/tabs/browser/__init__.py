from __future__ import annotations

import logging
from i18n import tr
import dmm_parser as dmm
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHeaderView,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from gui.tabs.browser.vfs_node import VirtualNode
from gui.tabs.browser.vfs_model import VirtualFileSystemModel

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


class GameBrowserTab(QWidget):
    """Tab for viewing and extracting files from game PAZ archives"""

    status_message = Signal(str)
    game_path_changed = Signal(str)
    config_save_requested = Signal()

    def __init__(
        self,
        config: dict,
        parent: Optional[QWidget] = None,
        show_guide_fn=None,
        path="",
    ):
        super().__init__(parent)

        self._config = config
        self._show_guide = show_guide_fn
        self._game_path = path or self._config.get("game_install_path", "")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        btn = QPushButton("Load Game Data")
        btn.clicked.connect(self.reload_model)
        layout.addWidget(btn)

        tree_view = QTreeView()
        tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(tree_view)

        tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree_view.customContextMenuRequested.connect(self.show_context_menu)

        self._tree_view = tree_view

    def set_game_path(self, path: str):
        self._game_path = path

    def reload_model(self):
        if not self._game_path:
            QMessageBox.warning(
                self,
                tr("No Game Path"),
                tr(
                    "Set the game install path using the Browse button at the top."
                ),
            )
            return

        model = VirtualFileSystemModel(dir=self._game_path)
        self._tree_view.setModel(model)
        self._tree_view.header().setStretchLastSection(False)
        self._tree_view.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._tree_view.header().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )

    def show_context_menu(self, position):
        index = self._tree_view.indexAt(position)
        if not index.isValid():
            return

        node: VirtualNode = index.internalPointer()
        if node.is_dir:
            return

        menu = QMenu()
        found_match = None

        first_dot_index = node.name.find(".") + 1
        if first_dot_index != 0:
            found_match = node.name[first_dot_index:]

        if found_match and found_match in VirtualNode.KNOWN_FORMATS:
            custom_type = VirtualNode.KNOWN_FORMATS[found_match]
            action = QAction(f"Extract as {custom_type}", self._tree_view)
            menu.addAction(action)

        if found_match and menu.actions():

            def handle_action(_):
                print(f"Extract requested: {node.absolute_path}")
                segments = [
                    s for s in node.absolute_path.split("/") if s != node.name
                ]
                try:
                    file_data = dmm.extract_file(
                        game_dir=self._game_path,
                        group_name=segments.pop(0),
                        dir_path="/".join(segments),
                        file_name=node.name,
                    )
                except IOError:
                    log.error("Error: The PAZ file cannot be read!")
                except ValueError:
                    log.error("Error: File not found in PAMT!")
                except Exception as e:
                    log.error(f"Error: {e}")
                else:
                    with open(f"data/{node.name}", "wb") as f:
                        f.write(file_data)
                    QMessageBox.information(
                        self._tree_view,
                        "File Extracted",
                        f"{node.name} was successfully extracted to the data folder.",
                    )

            menu.triggered.connect(handle_action)
            menu.exec(self._tree_view.mapToGlobal(position))
