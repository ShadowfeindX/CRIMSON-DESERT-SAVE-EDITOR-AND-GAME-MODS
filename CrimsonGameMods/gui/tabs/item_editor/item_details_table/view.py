from __future__ import annotations

from PySide6.QtGui import (
    QContextMenuEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QSizePolicy,
    QTableView,
)

from ..helpers import log
from .context_menu import DetailsTableContextMenu


class DetailsTableView(QTableView):
    def __init__(self, parent, model):
        super().__init__(
            parent, sortingEnabled=False, cornerButtonEnabled=True
        )

        self.setModel(model)
        self.setMinimumWidth(120)
        self.setColumnWidth(1, 180)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

    def refresh_view(self: QTableView) -> None:
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )

    def contextMenuEvent(self, event: QContextMenuEvent):
        index = self.indexAt(event.pos())
        if index.isValid():
            log.info("showing context menu for: %s", index.data())
            return DetailsTableContextMenu.open(self, index, event.globalPos())
