from __future__ import annotations

import enum
import json
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
)
from PySide6.QtWidgets import QWidget
from benedict import benedict

from ..signals import SIGNALS

from .display import display, is_implemented

from .roles import CustomItemDataRole, TypeRole

# from .display import DetailsTableModelDisplay

from ..helpers import *

Role = Qt.ItemDataRole
C_Role = CustomItemDataRole


class DetailsTableModel(QAbstractTableModel):
    def __init__(self, parent, index: int = -1) -> None:
        super().__init__(parent)
        self.idx = index
        self.load(index)
        SIGNALS.s_data_changed.connect(
            lambda idx: (
                self.load(idx)
                if idx == self.idx
                else None
            )
        )

    def load(self, index: int) -> None:
        if index == -1:
            return

        self.beginResetModel()

        self.idx = index
        details = ItemEditorInfoDetails(index)
        self.display(details)

        self.endResetModel()

    def data(
        self, index: QModelIndex, role: int
    ) -> ItemEditorInfoDetails | str | QWidget | tuple:
        if not index.isValid():
            return None

        if role == Role.UserRole:
            return ItemEditorInfoDetails(self.idx)

        if role == C_Role.DisplayRole:
            return self.display()[index.row()]

        if role == C_Role.DelegateRole:
            return (
                delegate
                if is_implemented(
                    (
                        delegate := self.display()[index.row()].get(
                            C_Role.DelegateRole
                        )
                    )
                )
                else None
            )

        try:
            cell = None
            cell = self.display()[index.row()][role][index.column()]
        except Exception:
            log.info(
                "Item Details Table: Invalid Index %s or Unsupported Role %s",
                (index.row(), index.column()),
                role,
            )
        else:
            if cell is not None:
                return cell

    def setData(self, index: QModelIndex, value, role: Role | C_Role):
        if not index.isValid():
            return False

        if role != Role.EditRole:
            log.info(
                "Item Details Table: Invalid Index %s or Unsupported Role %s",
                (index.row(), index.column()),
                role,
            )
            return False

        role, data = self._display[index.row()][C_Role.TypeRole]
        details: ItemEditorInfoDetails = self.data(index, Role.UserRole)

        if not role:
            return super().setData(index, value, role)

        match role:
            case TypeRole.Passive:
                if (new := min(max(value, 1), 10)) == (
                    passives := details.passives()
                )[data]["level"]:
                    return False

                passives = copy(passives)
                passives[data]["level"] = new
                details.passives(passives, refresh=False)
                self.display(details)
            case TypeRole.Buff:
                if (new := min(max(value, 1), 50)) == (
                    buffs := details.buffs()
                )[data]["level"]:
                    return False

                buffs = copy(buffs)
                buffs[data]["level"] = new
                details.buffs(buffs, refresh=False)
                self.display(details)
            case TypeRole.Stat:
                self.display(details)

        return True

    def flags(self, index: QModelIndex):
        default = super().flags(index)
        return (
            default | Qt.ItemFlag.ItemIsEditable
            if index.column() == 2
            else default
        )

    def display(
        self, details: ItemEditorInfoDetails = None
    ) -> list[dict[Role | C_Role, tuple]]:

        if details is None:
            return self._display

        self._display = display(self, details)

    #     return _build_views(self, details)

    #     def new_row(value):
    #         return tuple(value for _ in range(self.columnCount()))

    #     NOT_IMPLEMENTED = new_row(None)

    #     def new_view(data={}):
    #         return (
    #             {role.value: NOT_IMPLEMENTED for role in Role}
    #             | {role.value: NOT_IMPLEMENTED for role in CustomItemDataRole}
    #             | data
    #         )

    #     def build_views(key: str, value: Any):
    #         view = []
    #         match key:
    #             case "passives":
    #                 view.append(
    #                     new_view(
    #                         {
    #                             C_Role.TypeRole: new_row(TypeRole.Header),
    #                             Role.DisplayRole: new_row("--- Passives ---"),
    #                         }
    #                     )
    #                 )
    #                 view.extend(
    #                     new_view(
    #                         {
    #                             C_Role.TypeRole: (TypeRole.Passive, i),
    #                             Role.DisplayRole: (
    #                                 passive["skill"],
    #                                 STATE.skill_index[str(passive["skill"])][
    #                                     "string_key"
    #                                 ],
    #                                 passive["level"],
    #                             ),
    #                             Role.EditRole: new_row(passive["level"]),
    #                         }
    #                     )
    #                     for i, passive in enumerate(details.passives())
    #                 )

    #         return [key, value]

    #     views = []
    #     for key, value in details.editable():
    #         views.extend(build_views(key, value))
    #     # map(views.extend, map(build_views, details.editable()))
    #     print(views)
    #     views.clear()

    #     # --- Passives Header ---
    #     views.append(
    #         new_view(
    #             {
    #                 # C_Role.HeaderRole: new_row(True),
    #                 C_Role.TypeRole: new_row(TypeRole.Header),
    #                 Role.DisplayRole: new_row("--- Passives ---"),
    #             }
    #         )
    #     )

    #     # --- Passives List ---
    #     views.extend(
    #         new_view(
    #             {
    #                 C_Role.TypeRole: (TypeRole.Passive, i),
    #                 Role.DisplayRole: (
    #                     passive["skill"],
    #                     STATE.skill_index[str(passive["skill"])]["string_key"],
    #                     passive["level"],
    #                 ),
    #                 Role.EditRole: new_row(passive["level"]),
    #             }
    #         )
    #         for i, passive in enumerate(details.passives())
    #     )

    #     # --- Buffs Header ---
    #     views.append(
    #         new_view(
    #             {
    #                 C_Role.TypeRole: new_row(TypeRole.Header),
    #                 Role.DisplayRole: new_row("--- Buffs ---"),
    #             }
    #         )
    #     )

    #     # --- Buffs List ---
    #     views.extend(
    #         new_view(
    #             {
    #                 C_Role.TypeRole: (TypeRole.Buff, i),
    #                 Role.DisplayRole: (
    #                     buff["buff"],
    #                     STATE.buff_index[str(buff["buff"])]["string_key"],
    #                     buff["level"],
    #                 ),
    #                 Role.EditRole: new_row(buff["level"]),
    #             }
    #         )
    #         for i, buff in enumerate(details.buffs())
    #     )

    #     # --- Other Header ---
    #     views.append(
    #         new_view(
    #             {
    #                 C_Role.TypeRole: new_row(TypeRole.Header),
    #                 Role.DisplayRole: new_row("--- Other ---"),
    #             }
    #         )
    #     )
    #     # --- Other Data ---
    #     views.extend(
    #         new_view(
    #             {
    #                 C_Role.TypeRole: (TypeRole.Buff, i),
    #                 Role.DisplayRole: (
    #                     buff["buff"],
    #                     STATE.buff_index[str(buff["buff"])]["string_key"],
    #                     buff["level"],
    #                 ),
    #                 Role.EditRole: new_row(buff["level"]),
    #             }
    #         )
    #         for i, buff in enumerate(details.buffs())
    #     )

    #     self._display = views

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
                case 2:
                    return "Value"

        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._display) if hasattr(self, "_display") else 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 3
