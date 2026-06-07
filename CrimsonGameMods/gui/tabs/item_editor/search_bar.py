from __future__ import annotations


from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from .signals import SIGNALS

# from gui.theme import COLORS, CATEGORY_COLORS


class SearchBar(QWidget):
    s_search = Signal(str)
    s_filter = Signal(str)
    s_toggle_icons = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        SIGNALS.SearchBar.s_search = self.s_search
        SIGNALS.SearchBar.s_filter = self.s_filter
        SIGNALS.SearchBar.s_toggle_icons = self.s_toggle_icons

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        # layout.setSpacing(4)

        search = QLineEdit()
        search.setPlaceholderText(
            "Enter Item Name (e.g. Earring, Sword, Necklace)..."
        )
        search.returnPressed.connect(
            lambda: self.s_search.emit(search.text().strip().lower())
        )

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(
            lambda: self.s_search.emit(search.text().strip().lower())
        )

        fav_btn = QPushButton("⭐")
        fav_btn.setToolTip("Show favorited items only")
        fav_btn.clicked.connect(lambda: self.s_filter.emit("favorites"))

        # Category filter (populated after extract — empty until then)
        category_filter = QComboBox()
        category_filter.setToolTip(
            "Restrict results to items in a specific category.\n"
            "Populated from live iteminfo after Extract."
        )
        category_filter.setMinimumWidth(180)
        category_filter.addItem("All categories", None)
        category_filter.currentIndexChanged.connect(
            lambda: self.s_filter.emit(category_filter.currentData())
        )

        inv_btn = QPushButton("My Inventory")
        inv_btn.setToolTip(
            "Show only items from your loaded save that exist in iteminfo"
        )
        inv_btn.clicked.connect(lambda: self.s_filter.emit("inventory"))

        icons_btn = QPushButton("Icons")
        icons_btn.setToolTip("Toggle item icons in the items list")
        icons_btn.clicked.connect(lambda: self.s_toggle_icons.emit())

        self._category_filter = category_filter

        layout.addWidget(fav_btn)
        # layout.addWidget(QLabel("Search:"))
        layout.addWidget(search, 1)
        layout.addWidget(search_btn)
        layout.addWidget(category_filter)
        layout.addWidget(inv_btn)
        layout.addWidget(icons_btn)

    def update_categories(self, categories: list[tuple[int, str, int]]):
        combo = getattr(self, "_category_filter", None)
        if combo is None:
            return
        
        try:
            current = combo.currentData()
        except Exception:
            current = None

        combo.blockSignals(True)
        combo.clear()
        combo.addItem("All categories", None)
        for cat, label, count in categories:
            combo.addItem(f"{label} ({count})", cat)

        if current is not None:
            idx = combo.findData(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        combo.blockSignals(False)
