from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
)

from ..signals import SIGNALS, SLOTS

from .view import DetailsTableView

from .proxy import DetailsTableProxy

from .model import DetailsTableModel

from ..helpers import ItemEditorInfoDetails


class ItemDetailsTable(QFrame):
    s_data_changed = Signal(int)

    def __init__(self, parent):
        super().__init__(parent)

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()

    def _ready_signals(self):
        SIGNALS.s_data_changed = self.s_data_changed

    def _connect_signals(self):
        SIGNALS.s_item_selected.connect(self.load)
        SIGNALS.s_data_changed.connect(
            lambda idx: self.load(idx) if idx == SLOTS.last_selected() else None
        )

    def _build_ui(self, parent):
        layout = QVBoxLayout(self)
        self.model = DetailsTableModel(self)
        self.proxy = DetailsTableProxy(self, self.model)
        self.table = DetailsTableView(parent, self.proxy)

        layout.addWidget(self.table)
        self.table.refresh_view()

    def load(self, idx: Optional[int]):
        if idx is not None:
            self.model.load(idx)
            self.table.refresh_view()
