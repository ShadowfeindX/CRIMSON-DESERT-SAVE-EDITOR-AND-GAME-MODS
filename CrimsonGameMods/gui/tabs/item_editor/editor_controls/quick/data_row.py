from __future__ import annotations


from PySide6.QtCore import (
    Qt,
)
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QWidget,
)


from ...signals import SLOTS

from ...helpers import *


class DataRow(QWidget):
    def __init__(
        self,
        label="",
        load_fn=None,
        add_fn=None,
        remove_fn=None,
        display_fn=None,
        min_value=1,
        max_value=10,
    ):
        super().__init__()
        row = QHBoxLayout(self)

        self._list = QComboBox()
        self._list.setEditable(True)
        self._list.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._list.lineEdit().setPlaceholderText("Type to search...")
        self._list.completer().setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        self._list.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        self._value = QSpinBox(minimum=min_value, maximum=max_value)

        def showPopup():
            if load_fn is None:
                return

            self._data = load_fn()
            if self._list.count() != len(self._data):
                self._list.addItems(
                    [display_fn(entry) for entry in self._data]
                    if display_fn
                    else [
                        f"{entry['key']} - {entry['string_key']}"
                        for entry in self._data
                    ]
                )
            self._list._showPopup()

        self._data = None
        self._load_fn = load_fn
        self._add_fn = add_fn
        self._remove_fn = remove_fn

        self._add_btn = QPushButton(f"Add {label}")
        self._add_btn.clicked.connect(self.add)

        self._remove_btn = QPushButton(f"Remove {label}")
        self._remove_btn.clicked.connect(self.remove)

        self._list._showPopup = self._list.showPopup
        self._list.showPopup = showPopup

        row.addWidget(self._value)
        row.addWidget(self._list, 1)
        row.addWidget(self._add_btn)
        row.addWidget(self._remove_btn)

    def add(self):
        if self._data is None or self._add_fn is None:
            return

        return self._add_fn(
            SLOTS.current_selection(),
            self._data[self._list.currentIndex()],
            self._value.value(),
        )

    def remove(self):
        if self._data is None or self._remove_fn is None:
            return

        return self._remove_fn(
            SLOTS.current_selection(),
            self._data[self._list.currentIndex()],
        )
