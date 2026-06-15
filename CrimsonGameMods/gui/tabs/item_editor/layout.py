from __future__ import annotations


from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)



from .item_details_table.table import ItemDetailsTable

from .items_table.table import ItemTable

from .search_bar import SearchBar

from .action_bar import ActionBar

from .editor_controls import EditorControls


class ItemEditorLayout(QVBoxLayout):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._build_ui(parent)

        self.search_bar.s_search.connect(self.items_table.search)

    def _build_ui(self, parent: QWidget):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.action_bar = ActionBar(parent)
        self.search_bar = SearchBar(parent)
        self.items_table = ItemTable(parent)
        self.item_details_table = ItemDetailsTable(parent)
        self.editor_controls = EditorControls(parent)

        layout = QHBoxLayout()
        layout.addWidget(self.items_table)
        layout.addWidget(self.item_details_table)
        layout.addWidget(self.editor_controls)

        self.addWidget(self.action_bar)
        self.addWidget(self.search_bar)
        self.addLayout(layout, 1)

    def closeEvent(self, event):
        self.editor_controls.closeEvent(event)
