from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QVBoxLayout,
)

from .view import DetailsTableView

from .proxy import DetailsTableProxy

from .model import DetailsTableModel

from ..helpers import ItemEditorInfoDetails


def _safe_iv(v, default=0):
    """Safely extract int from plain int, float, or dmm_parser nested dict.
    dmm_parser returns numeric structs as {'a': int, 'b': int, 'c': int}.
    """
    if v is None:
        return default
    if isinstance(v, (int, float, bool)):
        return int(v)
    if isinstance(v, dict):
        for k in ("a", "value", "_v", "v", "val", "n", "data"):
            if k in v:
                sub = v[k]
                if isinstance(sub, (int, float, bool)):
                    return int(sub)
                if sub is None:
                    return default
        return default
    try:
        return int(v)
    except Exception:
        return default


try:
    from gui.utils import make_help_btn
except Exception:

    def make_help_btn(topic, fn=None):
        btn = QPushButton("?")
        btn.setFixedSize(22, 22)
        if fn:
            btn.clicked.connect(lambda: fn(topic))
        return btn


log = logging.getLogger(__name__)


class ItemDetailsTable(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self._build_ui(parent)

    def _build_ui(self, parent):
        layout = QVBoxLayout(self)
        self.model = DetailsTableModel(self)
        self.proxy = DetailsTableProxy(self, self.model)
        self.table = DetailsTableView(parent, self.proxy)

        layout.addWidget(self.table)
        self.table.refresh_view()

    def load(self, details: ItemEditorInfoDetails):
        self.model.load(details)
        self.table.refresh_view()
