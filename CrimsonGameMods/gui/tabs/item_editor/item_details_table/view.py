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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import DetailsTableModel


from .roles import CustomItemDataRole, TypeRole

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

    def setModel(self, model):
        super().setModel(model)
        self._rebuild_spans()

    def rowsInserted(self, parent, start, end):
        super().rowsInserted(parent, start, end)
        self.rebuild_spans()

    def rowsRemoved(self, parent, start, end):
        super().rowsRemoved(parent, start, end)
        self.rebuild_spans()

    def refresh_view(self) -> None:
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._rebuild_spans()

    def contextMenuEvent(self, event: QContextMenuEvent):
        index = self.indexAt(event.pos())
        if index.isValid():
            log.info("showing context menu for: %s", index.data())
            return DetailsTableContextMenu.open(self, index, event.globalPos())

    def _rebuild_spans(self):
        self.setUpdatesEnabled(False)
        self.clearSpans()

        role: CustomItemDataRole.TypeRole = None
        model: DetailsTableModel = self.model()
        for row in range(model.rowCount()):
            role = model.data(model.index(row, 0), CustomItemDataRole.TypeRole)
            if role == TypeRole.Header:
                self.setSpan(row, 0, 1, model.columnCount())
            elif role == TypeRole.Stretch:
                self.setSpan(row, 0, 1, model.columnCount() - 1)

        self.setUpdatesEnabled(True)
