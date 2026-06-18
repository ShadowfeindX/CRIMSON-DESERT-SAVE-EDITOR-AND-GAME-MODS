from __future__ import annotations

from collections.abc import Sequence
from typing import Any, List

from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QStyledItemDelegate,
    QWidget,
)

from ..signals import SIGNALS

from .roles import CustomItemDataRole, TypeRole


# from .view import ItemEditorTableView
# from ..signals import SIGNALS, SLOTS

from ..helpers import *
from ..dmm_types import EnchantLevelChange, EnchantStatChange, EnchantStatData

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import DetailsTableModel

    "STUB"

Role = Qt.ItemDataRole
C_Role = CustomItemDataRole


class IntRangeDelegate(QStyledItemDelegate):
    def __init__(self, min_val, max_val, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setRange(self.min_val, self.max_val)
        return editor

    def setEditorData(self, editor, index):
        # Correctly using index.model().data() to fetch from the proxy
        model = index.model()
        value = model.data(index, Qt.ItemDataRole.EditRole)
        editor.setValue(int(value) if value is not None else self.min_val)

    def setModelData(self, editor, model, index):
        # Submits data safely back through the active model/proxy
        editor.interpretText()
        model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)

    def display(
        self, details: ItemEditorInfoDetails = None
    ) -> list[dict[Role | C_Role, tuple]]:

        if details is None:
            return self._display


_details: ItemEditorInfoDetails = None

COLUMNS = 1


def new_row(value):
    return tuple(value for _ in range(COLUMNS))


NOT_IMPLEMENTED = new_row(None)


def is_implemented(value):
    return value is not NOT_IMPLEMENTED


def new_view(data={}):
    return (
        {role.value: NOT_IMPLEMENTED for role in Role}
        | {role.value: NOT_IMPLEMENTED for role in CustomItemDataRole}
        | data
    )


def passives_view():
    view = []

    # --- Passives Header ---
    view.append(
        new_view(
            {
                C_Role.TypeRole: new_row(TypeRole.Header),
                Role.DisplayRole: new_row("--- Passives ---"),
                Role.TextAlignmentRole: new_row(Qt.AlignmentFlag.AlignCenter),
            }
        )
    )

    # --- Passives List ---
    view.extend(
        new_view(
            {
                C_Role.TypeRole: (TypeRole.Passive, i),
                Role.DisplayRole: (
                    passive["skill"],
                    STATE.skill_index()[str(passive["skill"])]["string_key"],
                    passive["level"],
                ),
                Role.EditRole: new_row(passive["level"]),
            }
        )
        for i, passive in enumerate(_details.passives())
    )

    return view


def buffs_view():
    view = []

    # --- Buffs Header ---
    view.append(
        new_view(
            {
                C_Role.TypeRole: new_row(TypeRole.Header),
                Role.DisplayRole: new_row("--- Buffs ---"),
                Role.TextAlignmentRole: new_row(Qt.AlignmentFlag.AlignCenter),
            }
        )
    )

    # --- Buffs List ---
    view.extend(
        new_view(
            {
                C_Role.TypeRole: (TypeRole.Buff, i),
                Role.DisplayRole: (
                    buff["buff"],
                    STATE.buff_index()[str(buff["buff"])]["string_key"],
                    buff["level"],
                ),
                Role.EditRole: new_row(buff["level"]),
            }
        )
        for i, buff in enumerate(_details.buffs())
    )

    return view


_current_level = 0


def render_stat_list():
    "stub"


class LevelDelegate(QWidget):
    _registry: dict[int, int] = {}

    def __init__(
        self, start: int, model: DetailsTableModel, data: list[EnchantStatData]
    ):
        super().__init__()

        self._idx = _details.idx
        self._model = model
        self._start = start
        self._end = -1
        self._level = self._registry.get(self._idx, 0)
        self._max_level = max(len(data), 1) - 1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        left = QPushButton("<")
        left.clicked.connect(self.prev)

        right = QPushButton(">")
        right.clicked.connect(self.next)

        label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        self.left = left
        self.right = right
        self.label = label

        layout.addWidget(left)
        layout.addWidget(label, 1)
        layout.addWidget(right)

        self._refresh_label()  # Only update text, no model notification

    def next(self):
        if self._level >= self._max_level:
            return
        self._level += 1
        self._refresh_label()
        self._notify_model()

    def prev(self):
        if self._level <= 0:
            return
        self._level -= 1
        self._refresh_label()
        self._notify_model()

    def _refresh_label(self):
        """Update the label text and registry only (no model side-effects)."""
        self._registry[self._idx] = self._level
        self.label.setText(
            f"--- Stats (Level {self._level}/{self._max_level}) ---"
        )

    def _notify_model(self):
        """Tell the model to rebuild the stats rows for the new level."""
        index = self._model.index(self._start + 1, 0)
        if not index.isValid() or index.row() == self._end:
            return

        SIGNALS.s_data_changed.emit(self._idx)

STAT_LISTS = ["max", "regen", "static", "level"]
def stats_view(model: DetailsTableModel, start: int):
    view = []
    stat_data = _details.stats()

    delegate = LevelDelegate(start, model, stat_data)
    stat_data_list: Sequence[List[EnchantStatChange | EnchantLevelChange]] = (
        stat_data[delegate._level].values() if stat_data else []
    )

    # --- Stats Header ---
    view.append(
        new_view(
            {
                C_Role.DelegateRole: delegate,
                C_Role.TypeRole: new_row(TypeRole.Header),
                Role.DisplayRole: new_row("--- Stats ---"),
                Role.TextAlignmentRole: new_row(Qt.AlignmentFlag.AlignCenter),
            }
        )
    )

    # --- Stats List ---
    view.extend(
        new_view(
            {
                C_Role.TypeRole: (TypeRole.Stat, i),
                Role.DisplayRole: (
                    stat["key"],
                    stat["string_key"],
                    change["change_mb"],
                ),
                Role.EditRole: print(STAT_LISTS[type]),
                Role.EditRole: new_row(change["change_mb"]),
            }
        )
        for i, (type, change, stat) in enumerate(
            (
                (
                    list_type,
                    stat_change,
                    STATE.stat_index()[str(stat_change["stat"])],
                )
                for list_type, stat_list in enumerate(stat_data_list)
                for stat_change in stat_list
            )
        )
    )

    # view.extend(
    #     new_view(
    #         {
    #             C_Role.TypeRole: (TypeRole.Buff, i),
    #             Role.DisplayRole: (
    #                 stats["buff"],
    #                 STATE.buff_index[str(stats["buff"])]["string_key"],
    #                 stats["level"],
    #             ),
    #             Role.EditRole: new_row(stats["level"]),
    #         }
    #     )
    #     for i, stats in enumerate(_details.stats())
    # )

    delegate._end = start + len(view)

    return view


OTHER_HEADER = False


def other_view(key: str, value: Any):
    global OTHER_HEADER

    view = []
    if not OTHER_HEADER:
        # --- Other Header ---
        view.append(
            new_view(
                {
                    C_Role.TypeRole: new_row(TypeRole.Header),
                    Role.DisplayRole: new_row("--- Other ---"),
                    Role.TextAlignmentRole: new_row(
                        Qt.AlignmentFlag.AlignCenter
                    ),
                }
            )
        )

    match key:
        case "stack_size":
            view.append(
                new_view(
                    {
                        C_Role.TypeRole: new_row(TypeRole.Stretch),
                        Role.DisplayRole: ("Stack Size", None, value),
                        Role.EditRole: new_row(value),
                        Role.TextAlignmentRole: new_row(
                            Qt.AlignmentFlag.AlignCenter
                        ),
                    }
                )
            )
        case _:
            view.append(new_view({Role.DisplayRole: (None, key, value)}))

    return view


# # --- Other Data ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Buff, i),
#             Role.DisplayRole: (
#                 buff["buff"],
#                 STATE.buff_index[str(buff["buff"])]["string_key"],
#                 buff["level"],
#             ),
#             Role.EditRole: new_row(buff["level"]),
#         }
#     )
#     for i, buff in enumerate(_details.buffs())
# )


def build_view(self: DetailsTableModel, start: int, key: str, value: Any):
    match key:
        case "passives":
            return passives_view()
        case "buffs":
            return buffs_view()
        case "stats":
            return stats_view(self, start)
        case _:
            return other_view(key, value)


def display(self: DetailsTableModel, details: ItemEditorInfoDetails):
    global COLUMNS, NOT_IMPLEMENTED
    COLUMNS = self.columnCount()
    NOT_IMPLEMENTED = new_row(None)

    global _details
    _details = details

    views = []
    for key, value in details.editable():
        views.extend(build_view(self, len(views), key, value))

    return views

    # def display(
    #     self, details: ItemEditorInfoDetails = None
    # ) -> list[dict[Role | C_Role, tuple]]:

    #     if details is None:
    #         return self._display

    #     return _build_views(self, details)


# views = []
# for key, value in _details.editable():
#     views.extend(build_views(key, value))
# # map(views.extend, map(build_views, details.editable()))
# print(views)
# views.clear()

# # --- Passives Header ---
# views.append(
#     new_view(
#         {
#             # C_Role.HeaderRole: new_row(True),
#             C_Role.TypeRole: new_row(TypeRole.Header),
#             Role.DisplayRole: new_row("--- Passives ---"),
#         }
#     )
# )

# # --- Passives List ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Passive, i),
#             Role.DisplayRole: (
#                 passive["skill"],
#                 STATE.skill_index[str(passive["skill"])]["string_key"],
#                 passive["level"],
#             ),
#             Role.EditRole: new_row(passive["level"]),
#         }
#     )
#     for i, passive in enumerate(_details.passives())
# )

# # --- Buffs Header ---
# views.append(
#     new_view(
#         {
#             C_Role.TypeRole: new_row(TypeRole.Header),
#             Role.DisplayRole: new_row("--- Buffs ---"),
#         }
#     )
# )

# # --- Buffs List ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Buff, i),
#             Role.DisplayRole: (
#                 buff["buff"],
#                 STATE.buff_index[str(buff["buff"])]["string_key"],
#                 buff["level"],
#             ),
#             Role.EditRole: new_row(buff["level"]),
#         }
#     )
#     for i, buff in enumerate(_details.buffs())
# )

# # --- Other Header ---
# views.append(
#     new_view(
#         {
#             C_Role.TypeRole: new_row(TypeRole.Header),
#             Role.DisplayRole: new_row("--- Other ---"),
#         }
#     )
# )
# # --- Other Data ---
# views.extend(
#     new_view(
#         {
#             C_Role.TypeRole: (TypeRole.Buff, i),
#             Role.DisplayRole: (
#                 buff["buff"],
#                 STATE.buff_index[str(buff["buff"])]["string_key"],
#                 buff["level"],
#             ),
#             Role.EditRole: new_row(buff["level"]),
#         }
#     )
#     for i, buff in enumerate(_details.buffs())
# )

# self._display = views
