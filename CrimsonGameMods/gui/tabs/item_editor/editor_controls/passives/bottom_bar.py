from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
)


class BottomBar(QWidget):
    s_apply = Signal()
    s_remove = Signal()
    s_clear = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        apply_btn = QPushButton("Apply Passives to Selected Items")
        apply_btn.clicked.connect(self.s_apply)
        remove_btn = QPushButton("Remove Passives from Selected Items")
        remove_btn.clicked.connect(self.s_remove)
        clear_btn = QPushButton("Clear Target List")
        clear_btn.clicked.connect(self.s_clear)

        layout.addWidget(apply_btn)
        layout.addWidget(remove_btn)
        layout.addWidget(clear_btn)

        return layout
