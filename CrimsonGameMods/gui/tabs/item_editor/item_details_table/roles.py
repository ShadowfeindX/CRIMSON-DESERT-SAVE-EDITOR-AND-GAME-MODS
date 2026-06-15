from __future__ import annotations

from enum import IntEnum, auto

from PySide6.QtCore import Qt


class CustomItemDataRole(IntEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 1 + Qt.ItemDataRole.UserRole + count
        # return super()._generate_next_value_(name, start, count, last_values)

    DisplayRole = auto()
    TypeRole = auto()
    # BuffRole = auto()


class TypeRole(IntEnum):
    Header = auto()
    Stretch = auto()
    Passive = auto()
    Buff = auto()
    Stat = auto()
    #  = auto()
