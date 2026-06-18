from __future__ import annotations

from PySide6.QtGui import (
    QContextMenuEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QPushButton,
    QSizePolicy,
    QTableView,
)

from typing import TYPE_CHECKING

from ..signals import SIGNALS

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

        self.delegates: dict[int, bool] = {}

        self.setModel(model)
        self.setMinimumWidth(120)
        self.setColumnWidth(1, 180)
        self.verticalHeader().setVisible(False)
        # self.verticalHeader().setDefaultSectionSize(38)
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # SIGNALS.s_data_changed.connect(lambda idx: self.refresh_view() if idx == model.idx else None)

    def setModel(self, model):
        super().setModel(model)
        self._rebuild_spans()

    def rowsInserted(self, parent, start, end):
        super().rowsInserted(parent, start, end)
        self._rebuild_spans()

    def rowsRemoved(self, parent, start, end):
        super().rowsRemoved(parent, start, end)
        self._rebuild_spans()

    def refresh_view(self) -> None:
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setStretchLastSection(False)
        # self.horizontalHeader().setSectionResizeMode(
        #     0, QHeaderView.ResizeMode.ResizeToContents
        # )
        self.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        # self.horizontalHeader().setSectionResizeMode(
        #     2, QHeaderView.ResizeMode.ResizeToContents
        # )
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self._rebuild_spans()

    def contextMenuEvent(self, event: QContextMenuEvent):
        index = self.indexAt(event.pos())
        if index.isValid():
            log.info("showing context menu for: %s", index.data())
            return DetailsTableContextMenu.open(self, index, event.globalPos())

    def _rebuild_spans(self):
        role: CustomItemDataRole.TypeRole = None
        model: DetailsTableModel = self.model()

        self.setUpdatesEnabled(False)
        self.clearSpans()

        for delegate in self.delegates.keys():
            self.setIndexWidget(model.index(delegate, 0), None)
        self.delegates.clear()

        for row in range(model.rowCount()):
            index = model.index(row, 0)
            role = model.data(index, CustomItemDataRole.TypeRole)
            if role == TypeRole.Header:
                self.setSpan(row, 0, 1, model.columnCount())
            elif role == TypeRole.Stretch:
                self.setSpan(row, 0, 1, model.columnCount() - 1)

            delegate = model.data(index, CustomItemDataRole.DelegateRole)
            if delegate:
                self.setIndexWidget(index, delegate)
                self.delegates[row] = True

        self.setUpdatesEnabled(True)
