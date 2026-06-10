from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class ActionBar(QWidget):
    s_add = Signal()
    s_remove = Signal()
    s_search = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.fav_btn = QPushButton("⭐")
        self.fav_btn.setCheckable(True)
        self.fav_btn.setToolTip("Show favorited passives only")
        search_btn = QPushButton("Search")
        search_box = QLineEdit()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.s_add)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.s_remove)

        search_btn.clicked.connect(
            lambda: self.s_search.emit(search_box.text().strip().lower())
        )
        search_box.returnPressed.connect(
            lambda: self.s_search.emit(search_box.text().strip().lower())
        )

        layout.addWidget(self.fav_btn)
        layout.addWidget(search_btn)
        layout.addWidget(search_box)
        layout.addWidget(add_btn)
        layout.addWidget(remove_btn)

        self.search_box = search_box

        return layout
