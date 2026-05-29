from __future__ import annotations
import json
import os


# from PySide6 import QtCore
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from gui.theme import COLORS


# def make_collapsible(
#     label: str,
#     content: QWidget,
#     start_open: bool = True,
#     config_key: str = None,
# ) -> QWidget:
#     accent = COLORS.get("accent", "#daa850")
#     if config_key and self._config.get(config_key) is not None:
#         start_open = self._config[config_key]
#     wrapper = QWidget()
#     vbox = QVBoxLayout(wrapper)
#     vbox.setContentsMargins(0, 0, 0, 0)
#     vbox.setSpacing(0)

#     toggle = QPushButton(("▾ " if start_open else "▸ ") + label)
#     toggle.setStyleSheet(
#         f"QPushButton {{ text-align: left; font-weight: bold; font-size: 11px;"
#         f" padding: 3px 8px; background: transparent;"
#         f" color: {accent}; border: none; border-bottom: 1px solid {accent}; }}"
#         f"QPushButton:hover {{ background: rgba(218,168,80,0.10); }}"
#     )
#     toggle.setCursor(Qt.PointingHandCursor)
#     toggle.setFixedHeight(22)

#     content.setVisible(start_open)
#     cfg = self._config

#     def _on_toggle():
#         vis = not content.isVisible()
#         content.setVisible(vis)
#         toggle.setText(("▾ " if vis else "▸ ") + label)
#         if config_key:
#             cfg[config_key] = vis
#             self.config_save_requested.emit()

#     toggle.clicked.connect(_on_toggle)

#     vbox.addWidget(toggle)
#     vbox.addWidget(content)
#     return wrapper

class _Config():
    _CONFIG_FILE = "editor_config.json"

    def __init__(self):
        self._config: dict = self.load()
    
    def path(self) -> str:
        import sys
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(os.path.abspath(sys.executable)), self._CONFIG_FILE)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), self._CONFIG_FILE)

    def load(self) -> dict:
        path = self.path()
        if os.path.isfile(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def save(self) -> None:
        try:
            with open(self.path(), "w") as f:
                json.dump(self._config, f, indent=2)
        except OSError:
            pass

    def __len__(self) -> int :
        return len(self._config)

    def __getitem__(self, key):
        return self._config.get(key)

    def __setitem__(self, key, value):
        self._config[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._config
    

CONFIG = _Config()

def make_collapsible(
    label: str,
    content: QWidget,
    start_open: bool = True,
    config_key: str = None,
) -> QWidget:
    accent = COLORS.get("accent", "#daa850")
    # if config_key and self._config.get(config_key) is not None:
    #     start_open = self._config[config_key]
    wrapper = QWidget()
    vbox = QVBoxLayout(wrapper)
    vbox.setContentsMargins(0, 0, 0, 0)
    vbox.setSpacing(0)

    toggle = QPushButton(("▾ " if start_open else "▸ ") + label)
    toggle.setStyleSheet(
        f"QPushButton {{ text-align: left; font-weight: bold; font-size: 11px;"
        f" padding: 3px 8px; background: transparent;"
        f" color: {accent}; border: none; border-bottom: 1px solid {accent}; }}"
        f"QPushButton:hover {{ background: rgba(218,168,80,0.10); }}"
    )
    toggle.setCursor(Qt.PointingHandCursor)
    toggle.setFixedHeight(22)

    content.setVisible(start_open)
    cfg = CONFIG

    def _on_toggle():
        vis = not content.isVisible()
        content.setVisible(vis)
        toggle.setText(("▾ " if vis else "▸ ") + label)
        if config_key:
            cfg[config_key] = vis
            CONFIG.save()

    toggle.clicked.connect(_on_toggle)

    vbox.addWidget(toggle)
    vbox.addWidget(content)
    return wrapper


def center_window_in_parent(window: QWidget, parent: QWidget, embedded = False):
    # --- CENTERING LOGIC START ---
    # Get dimensions of the main window
    main_geo = parent.geometry()
    # Get dimensions of the sub-window
    sub_geo = window.geometry()
    # Get absolute position of main window
    abs_geo = parent.mapToGlobal(QPoint(0, 0))

    (x, y) = (abs_geo.x(), abs_geo.y()) if embedded else (main_geo.x(), main_geo.y())

    # Calculate the new X and Y coordinates to perfectly center it
    new_x = x + (main_geo.width() - sub_geo.width()) // 2
    new_y = y + (main_geo.height() - sub_geo.height()) // 2

    # Move the window to the calculated position
    window.move(new_x, new_y)
    # --- CENTERING LOGIC END ---
