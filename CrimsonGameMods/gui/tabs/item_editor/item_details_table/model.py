from __future__ import annotations

import json

from PySide6.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
)

from ..helpers import ItemEditorInfoDetails, log


class DetailsTableModel(QAbstractTableModel):
    def __init__(
        self, parent, data: ItemEditorInfoDetails = ItemEditorInfoDetails()
    ) -> None:
        super().__init__(parent)

        self.load(data)

    def load(self, details: ItemEditorInfoDetails) -> None:
        if details is None:
            return
        
        self.beginResetModel()

        # data = [(key, detail) for key, detail in details._data.items()]
        display_data: list[tuple[str, str]] = [
            (
                key,
                json.dumps(detail),
            )
            for key, detail in details.editable()
        ]

        self._data: ItemEditorInfoDetails = details
        self._display: list[tuple[str, str]] = display_data

        self.endResetModel()

    def data(
        self, index: QModelIndex, role: int
    ) -> None | ItemEditorInfoDetails | str:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.UserRole:
            return self._data

        match role:
            case Qt.ItemDataRole.DisplayRole:
                key, detail = self._display[index.row()]
                match index.column():
                    case 0:
                        return key
                    case 1:
                        return detail
                    case _:
                        log.info(
                            "Item Details Table: Invalid index column %s",
                            index.column(),
                        )
                # return self._data[index.row()]

    def display(self, key: str) -> None:
        "stub"

    def headerData(self, idx, orientation, role) -> None | str:
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            match idx:
                case 0:
                    return "Key"
                case 1:
                    return "Details"

        return None

    def rowCount(self, _) -> int:
        return len(self._display)

    def columnCount(self, _) -> int:
        return 2
