from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QVBoxLayout,
)

from ..signals import SIGNALS

from .view import DetailsTableView

from .proxy import DetailsTableProxy

from .model import DetailsTableModel

from ..helpers import ItemEditorInfoDetails

class ItemDetailsTable(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        SIGNALS.s_item_selected.connect(self.load)

        self._build_ui(parent)

    def _build_ui(self, parent):
        layout = QVBoxLayout(self)
        self.model = DetailsTableModel(self)
        self.proxy = DetailsTableProxy(self, self.model)
        self.table = DetailsTableView(parent, self.proxy)

        layout.addWidget(self.table)
        self.table.refresh_view()

    def load(self, details: ItemEditorInfoDetails):
        self.model.load(details)
        self.table.refresh_view()
