from __future__ import annotations

import string
import os

from PySide6.QtCore import Qt
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
    # cfg = self._config

    def _on_toggle():
        vis = not content.isVisible()
        content.setVisible(vis)
        toggle.setText(("▾ " if vis else "▸ ") + label)
        # if config_key:
        #     cfg[config_key] = vis
        #     self.config_save_requested.emit()

    toggle.clicked.connect(_on_toggle)

    vbox.addWidget(toggle)
    vbox.addWidget(content)
    return wrapper


def find_game_path() -> str:
    candidates = []

    for letter in string.ascii_uppercase:
        candidates.append(
            f"{letter}:\\SteamLibrary\\steamapps\\common\\Crimson Desert"
        )

    candidates.extend(
        [
            r"C:\Program Files (x86)\Steam\steamapps\common\Crimson Desert",
            r"C:\Program Files\Steam\steamapps\common\Crimson Desert",
            r"C:\Program Files\Epic Games\CrimsonDesert",
        ]
    )

    for path in candidates:
        papgt = os.path.join(path, "meta", "0.papgt")
        if os.path.isfile(papgt):
            return path

    return ""
