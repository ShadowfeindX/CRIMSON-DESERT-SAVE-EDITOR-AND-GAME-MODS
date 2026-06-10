from __future__ import annotations

import html
import json
import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
)

from ..signals import SIGNALS
from ..helpers import HistoryEntry, ItemEditorInfoDetails

log = logging.getLogger(__name__)


class HistoryWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__()

        self.setWindowTitle("History Registry")

        self._ready_signals()
        self._build_ui(parent)
        self._connect_signals()
        self._load_history()

    def closeEvent(self, event: QCloseEvent):
        return super().closeEvent(event)

    def _ready_signals(self):
        pass

    def _connect_signals(self):
        SIGNALS.s_history_entry_added.connect(self._append_entry)
        self.table.currentCellChanged.connect(self._on_row_selected)
        self.btn_clear.clicked.connect(self._clear_history)

    def _build_ui(self, parent: QWidget):
        main_layout = QVBoxLayout(self)

        # ── Top bar ───────────────────────────────────────────────────────
        top_bar = QHBoxLayout()

        self.count_label = QLabel("Entries: 0")

        self.btn_clear = QPushButton("Clear History")
        self.btn_clear.setStyleSheet(
            "QPushButton { background: #a33; color: white; }"
            "QPushButton:hover { background: #c44; }"
        )

        top_bar.addWidget(self.count_label)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_clear)
        main_layout.addLayout(top_bar)

        # ── Splitter: table (top) + detail pane (bottom) ──────────────────
        splitter = QSplitter(Qt.Vertical)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Type", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Interactive
        )
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        splitter.addWidget(self.table)

        # Detail pane
        self.detail_pane = QTextEdit()
        self.detail_pane.setReadOnly(True)
        self.detail_pane.setPlaceholderText(
            "Select a history entry above to view its payload data."
        )
        splitter.addWidget(self.detail_pane)

        main_layout.addWidget(splitter)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _load_history(self):
        """Populate the table with all existing history entries on window open."""
        for entry in ItemEditorInfoDetails._history:
            self._add_row(entry)
        self._refresh_ui()

    def _add_row(self, entry: HistoryEntry):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(entry.type.value.upper()))
        self.table.setItem(row, 1, QTableWidgetItem(entry.description))

    def _refresh_ui(self):
        count = len(ItemEditorInfoDetails._history)
        self.count_label.setText(f"Entries: {count}")

    def _clear_history(self):
        ItemEditorInfoDetails._history.clear()
        self.table.setRowCount(0)
        self.detail_pane.clear()
        self._refresh_ui()

    def _append_entry(self, entry: HistoryEntry):
        self._add_row(entry)
        self._refresh_ui()

    def _on_row_selected(self, row: int, *_):
        history = ItemEditorInfoDetails._history
        if 0 <= row < len(history):
            try:
                data = _to_dict(history[row].entry_data)
                text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
                body = html.escape(text).replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")
                self.detail_pane.setHtml(
                    f'<pre style="font-family: monospace; white-space: pre;">{body}</pre>'
                )
            except Exception:
                self.detail_pane.setPlainText(repr(history[row].entry_data))
        else:
            self.detail_pane.clear()


def _to_dict(obj):
    """Recursively unpack POJOs (and similar plain-class objects) into
    JSON-native structures before serialization, preventing the double-encoding
    that occurs when json.dumps receives a str(pojo) as its default handler.
    """
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if hasattr(obj, "__dict__"):
        return {k: _to_dict(v) for k, v in vars(obj).items()}
    return obj
