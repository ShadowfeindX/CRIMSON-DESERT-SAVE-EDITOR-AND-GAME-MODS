from __future__ import annotations

from PySide6.QtCore import (
    QSortFilterProxyModel,
)


class DetailsTableProxy(QSortFilterProxyModel):
    def __init__(self, parent, model):
        super().__init__(parent)

        if model:
            self.setSourceModel(model)
