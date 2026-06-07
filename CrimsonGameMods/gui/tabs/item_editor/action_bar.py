from __future__ import annotations


from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMenu,
    QPushButton,
    QWidget,
)

from .signals import SIGNALS

# from gui.theme import COLORS, CATEGORY_COLORS


class ActionBar(QWidget):
    s_extract = Signal(str)
    s_import = Signal(str)
    s_export = Signal(str)
    s_reset = Signal()
    s_undo = Signal()
    s_apply_to_game = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        SIGNALS.ActionBar.s_extract = self.s_extract
        SIGNALS.ActionBar.s_import = self.s_import
        SIGNALS.ActionBar.s_export = self.s_export
        SIGNALS.ActionBar.s_reset = self.s_reset
        SIGNALS.ActionBar.s_undo = self.s_undo
        SIGNALS.ActionBar.s_apply_to_game = self.s_apply_to_game

        self._build_ui(parent)

    def _build_ui(self, parent: QWidget):
        layout = QHBoxLayout(self)

        extract_btn = QPushButton("Extract")
        extract_menu = QMenu(extract_btn)
        extract_btn.setMenu(extract_menu)
        extract_menu.addAction("Extract from Overlay").triggered.connect(
            lambda: self.s_extract.emit("overlay")
        )
        extract_menu.addAction("Extract Vanilla").triggered.connect(
            lambda: self.s_extract.emit("vanilla")
        )

        import_btn = QPushButton("Import")
        import_menu = QMenu(import_btn)
        import_btn.setMenu(import_menu)
        import_menu.addAction("Import Config").triggered.connect(
            lambda: self.s_import.emit("config")
        )
        import_menu.addAction("Import v3 Mod").triggered.connect(
            lambda: self.s_import.emit("v3")
        )
        import_menu.addAction("Import Mod Folder").triggered.connect(
            lambda: self.s_import.emit("mod_folder")
        )

        export_btn = QPushButton("Export")
        export_menu = QMenu(export_btn)
        export_btn.setMenu(export_menu)
        export_menu.addAction("Export Config").triggered.connect(
            lambda: self.s_export.emit("config")
        )
        export_menu.addAction("Export v3 Mod").triggered.connect(
            lambda: self.s_export.emit("v3")
        )
        export_menu.addAction("Export Mod Folder").triggered.connect(
            lambda: self.s_export.emit("mod_folder")
        )

        apply_btn = QPushButton("Apply to Game")
        apply_btn.clicked.connect(
            lambda: self.s_apply_to_game.emit()
        )
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(
            lambda: self.s_reset.emit()
        )
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(
            lambda: self.s_undo.emit()
        )

        layout.addWidget(extract_btn)
        layout.addWidget(import_btn)
        layout.addWidget(export_btn)
        layout.addWidget(apply_btn)
        layout.addWidget(reset_btn)
        layout.addWidget(undo_btn)
        layout.addStretch(1)
