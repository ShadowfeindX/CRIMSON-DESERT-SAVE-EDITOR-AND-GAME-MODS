from __future__ import annotations

from collections.abc import ItemsView
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from .window import PassiveWindow


class TargetPassivesTable(QWidget):
    def __init__(self, parent: PassiveWindow):
        super().__init__(parent)

        self.get_skill_name = parent.get_skill_name

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            [
                "Key",
                "Name",
                "Level",
            ]
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        v_header = table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(24)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        """
        Get all currently selected rows
        Extract passive key and levels (use 1 as default level)
        Add all passives to selected passives dictionary
            Overrite key if level is higher
        Refresh target passives list

        Optional Optimizations:
            Mark list as stale when adding/removing passives. Only rebuild if stale
            Store change flag when selecion changes. Ignore add/remove signal if selection is unchanged
        """

        self.table = table

        layout.addWidget(QLabel("Passives to Apply:"))
        layout.addWidget(table)

    def load_passives(self, passives: ItemsView[str, str]):
        self.table.setRowCount(len(passives))
        for row, (key, level) in enumerate(passives):
            name = self.get_skill_name(key)

            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(level))
