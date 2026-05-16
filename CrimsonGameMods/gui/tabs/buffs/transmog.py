
from __future__ import annotations


import logging
import json
import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QMessageBox, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QListWidget, QListWidgetItem, QFileDialog,
    QSplitter, QWidget,
)

from gui.utils import FlowLayout
from gui.theme import COLORS

from armor_catalog import ArmorItem

log = logging.getLogger(__name__)


class TransmogDialog(QDialog):
    QUICK_FILTERS = [
        ("⛑️ Helm", "Helm"),
        ("🛡️ Chest", "Chest"),
        ("🧤 Gloves", "Gloves"),
        ("👢 Boots", "Boots"),
        ("🧥 Cloak", "Cloak"),
        ("🗡️ 1H Sword", "OneHand Sword"),
        ("⚔️ 2H Sword", "TwoHand Sword"),
        ("🗡️🗡️ Dual Sword", "Dual Sword"),
        ("🔪 Dual Daggers", "Dual Daggers"),
        ("🪓 2H Axe", "TwoHand Axe"),
        ("🪓🪓 Dual Axe", "Dual Axe"),
        ("🔨 Hammer", "Hammer"),
        ("🔱 Spear", "Spear"),
        ("🏹 Bow", "Bow"),
        ("🛡 Shield", "Shield"),
        ("🏮 Lantern", "Lantern"),
        ("🔥 Torch", "Torch"),
        ("📿 Necklace", "Necklace"),
        ("✨ Earring", "Earring"),
        ("💍 Ring", "Ring"),
        ("🔁 All", "All"),
    ]
            
    def __init__(self, parent=None, catalog: list[ArmorItem]=[]):
        super().__init__(parent)
        self._transmog_swaps: list = []
        self._armor_catalog = catalog

        self.setWindowTitle("Transmog / Visual Swap")
        self.resize(1000, 700)
        self.setSizeGripEnabled(True)
        _dl_outer = QVBoxLayout(self)
        _dl_outer.setContentsMargins(0, 0, 0, 0)
        _scroll = QScrollArea(self)
        _scroll.setWidgetResizable(True)
        _scroll.setFrameShape(QScrollArea.NoFrame)
        _scroll_widget = QWidget()
        _dl_outer.addWidget(_scroll)
        _scroll.setWidget(_scroll_widget)
        dl = QVBoxLayout(_scroll_widget)

        header = QLabel(
            "Make YOUR armor look like another armor.\n"
            "Pick a piece you own on the LEFT, then pick the look you want from the RIGHT.\n"
            "Your stats/buffs/enchants are kept — only the visual model and textures change."
        )
        header.setWordWrap(True)
        header.setStyleSheet(f"color: {COLORS['text_dim']}; padding: 4px;")
        dl.addWidget(header)

        filt_row = QHBoxLayout()
        filt_row.addWidget(QLabel("Category (both lists):"))
        cat_combo = QComboBox()
        cat_combo.addItems([
            "All",
            "Chest", "Gloves", "Boots", "Helm", "Cloak", "Shoulder",
            "OneHand Sword", "TwoHand Sword", "Dual Sword",
            "Dual Daggers", "TwoHand Axe", "Dual Axe",
            "Hammer", "Spear", "Bow",
            "Shield", "Bracer", "Lantern", "Torch",
            "Necklace", "Earring", "Ring", "Belt", "Trinket",
            "Other",
        ])
        filt_row.addWidget(cat_combo)
        only_owned_cb = QCheckBox("Only show items I own (left list)")
        only_owned_cb.setChecked(True)
        only_owned_cb.setToolTip(
            "Left list: filter to equipment you currently own.\n"
            "The right list always shows all items — you can use any look you want.")
        filt_row.addWidget(only_owned_cb)
        filt_row.addStretch(1)
        dl.addLayout(filt_row)

        # ── Quick category filter buttons (matches Mesh Swap pattern) ──
        quick_w = QWidget()
        quick_row = FlowLayout(quick_w, margin=0, h_spacing=4, v_spacing=4)
        ql = QLabel("Quick filter:")
        ql.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold;")
        quick_row.addWidget(ql)


        for label, cat_name in self.QUICK_FILTERS:
            b = QPushButton(label)
            b.setToolTip(f"Filter both lists to: {cat_name}")
            b.setStyleSheet("padding: 4px 8px;")
            def _make_setter(c):
                return lambda: cat_combo.setCurrentText(c) if cat_combo.findText(c) >= 0 else None
            b.clicked.connect(_make_setter(cat_name))
            quick_row.addWidget(b)
        dl.addWidget(quick_w)

        splitter = QSplitter(Qt.Horizontal)

        tgt_panel = QWidget()
        tgt_l = QVBoxLayout(tgt_panel)
        tgt_l.setContentsMargins(2, 2, 2, 2)
        tgt_l.addWidget(QLabel("YOUR EQUIPMENT — pick the piece to re-skin:"))
        tgt_search = QLineEdit()
        tgt_search.setPlaceholderText("Search your items...")
        tgt_l.addWidget(tgt_search)
        tgt_list = QListWidget()
        tgt_list.setIconSize(QSize(32, 32))
        tgt_l.addWidget(tgt_list, 1)
        splitter.addWidget(tgt_panel)

        src_panel = QWidget()
        src_l = QVBoxLayout(src_panel)
        src_l.setContentsMargins(2, 2, 2, 2)
        src_l.addWidget(QLabel("NEW LOOK — pick the item whose look you want:"))
        src_search = QLineEdit()
        src_search.setPlaceholderText("Search all items...")
        src_l.addWidget(src_search)
        src_list = QListWidget()
        src_list.setIconSize(QSize(32, 32))
        src_l.addWidget(src_list, 1)
        splitter.addWidget(src_panel)

        splitter.setSizes([500, 500])
        dl.addWidget(splitter, 1)

        action_row = QHBoxLayout()
        add_btn = QPushButton("Add Swap")
        add_btn.setObjectName("accentBtn")
        add_btn.setToolTip("Add the selected Target+Source pair to the swap queue")
        action_row.addWidget(add_btn)
        remove_btn = QPushButton("Remove Selected")
        action_row.addWidget(remove_btn)
        clear_btn = QPushButton("Clear All")
        action_row.addWidget(clear_btn)
        action_row.addStretch(1)
        import_btn = QPushButton("Import Config")
        import_btn.setToolTip("Load queued swaps from a JSON file")
        action_row.addWidget(import_btn)
        export_btn = QPushButton("Export Config")
        export_btn.setToolTip("Save queued swaps to a JSON file for sharing")
        action_row.addWidget(export_btn)
        export_field_btn = QPushButton("Export Field JSON v3")
        export_field_btn.setStyleSheet("background-color: #0277BD; color: white; font-weight: bold;")
        export_field_btn.setToolTip(
            "Export queued transmog swaps as a Format 3 field JSON mod.\n"
            "Copies prefab visual fields from source to target item.\n"
            "Compatible with Stacker Tool and DMM mod loader.")
        export_field_btn.setStyleSheet(
            "QPushButton { background-color: #1565C0; color: white; font-weight: bold; }")
        action_row.addWidget(export_field_btn)
        dl.addLayout(action_row)

        dl.addWidget(QLabel("Queued swaps (applied on Export as Mod / Apply to Game):"))
        queue_list = QListWidget()
        queue_list.setMaximumHeight(140)
        dl.addWidget(queue_list)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("Save & Close")
        ok_btn.setObjectName("accentBtn")
        btn_row.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(cancel_btn)
        dl.addLayout(btn_row)

        local_swaps = list(self._transmog_swaps)

        owned_keys: set = set()
        try:
            for it in getattr(self, '_items', []) or []:
                if hasattr(it, 'item_key'):
                    owned_keys.add(it.item_key)
        except Exception:
            pass
        owned_count_label = QLabel(f"({len(owned_keys)} owned items detected)")
        owned_count_label.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 10px;")
        filt_row.addWidget(owned_count_label)

        def refresh_queue():
            queue_list.clear()
            for sw in local_swaps:
                src = sw['src']
                tgt = sw['tgt']
                queue_list.addItem(f"{tgt.display_name} ({tgt.category})  →  now looks like  →  "
                                    f"{src.display_name} ({src.category})")

        def matches(a, cat, q):
            if cat != "All" and a.category != cat:
                return False
            if q:
                ql = q.lower()
                if ql not in a.display_name.lower() and ql not in a.internal_name.lower():
                    return False
            return True

        def _add_row(lst, a):
            label = f"[{(a.category or '')[:8]}] {a.display_name}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, a.item_id)
            # Skip icon loading during bulk populate — too slow per-item
            lst.addItem(item)

        def populate_target():
            prev_key = tgt_list.currentItem().data(Qt.UserRole) if tgt_list.currentItem() else None
            cat = cat_combo.currentText()
            q = tgt_search.text().strip()
            only_owned = only_owned_cb.isChecked()
            tgt_list.setUpdatesEnabled(False)
            tgt_list.clear()
            restored_row = -1
            items_to_add = []
            for a in self._armor_catalog:
                if not matches(a, cat, q):
                    continue
                if only_owned and owned_keys and a.item_id not in owned_keys:
                    continue
                label = f"[{(a.category or '')[:8]}] {a.display_name}"
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, a.item_id)
                items_to_add.append((item, a.item_id))
            for item, item_id in items_to_add:
                tgt_list.addItem(item)
                if item_id == prev_key:
                    restored_row = tgt_list.count() - 1
            tgt_list.setUpdatesEnabled(True)
            if restored_row >= 0:
                tgt_list.setCurrentRow(restored_row)

        INVISIBLE_SENTINEL_KEY = -9999
        from armor_catalog import ArmorItem as _ArmorItem
        invisible_template = _ArmorItem(
            item_id=INVISIBLE_SENTINEL_KEY,
            internal_name='__INVISIBLE_ZERO__',
            display_name='Invisible Model',
            category='Invisible',
            hashes=[],
        )

        invisible_named_items = [
            a for a in self._armor_catalog if a.item_id == 1000491
        ]

        def populate_source():
            prev_key = src_list.currentItem().data(Qt.UserRole) if src_list.currentItem() else None
            q = src_search.text().strip()
            cat = cat_combo.currentText()
            src_list.setUpdatesEnabled(False)
            src_list.clear()
            restored_row = -1

            show_invis = (not q or 'invis' in q.lower() or 'empty' in q.lower() or 'none' in q.lower() or 'ghost' in q.lower())
            if show_invis:
                for inv in invisible_named_items:
                    lbl = "★ Invisible (Ghost_TwohandSword) — universal invisible"
                    it = QListWidgetItem(lbl)
                    it.setData(Qt.UserRole, inv.item_id)
                    it.setForeground(QBrush(QColor("#FFD700")))
                    src_list.addItem(it)
                    if prev_key == inv.item_id:
                        restored_row = src_list.count() - 1

            pinned_ids = {inv.item_id for inv in invisible_named_items} if show_invis else set()
            items_to_add = []
            for a in self._armor_catalog:
                if a.item_id in pinned_ids:
                    continue
                if not matches(a, cat, q):
                    continue
                label = f"[{(a.category or '')[:8]}] {a.display_name}"
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, a.item_id)
                items_to_add.append((item, a.item_id))
            for item, item_id in items_to_add:
                src_list.addItem(item)
                if item_id == prev_key:
                    restored_row = src_list.count() - 1
            src_list.setUpdatesEnabled(True)
            if restored_row >= 0:
                src_list.setCurrentRow(restored_row)

        def populate_both():
            populate_target()
            populate_source()

        cat_combo.currentTextChanged.connect(lambda _: populate_both())
        tgt_search.textChanged.connect(lambda _: populate_target())
        src_search.textChanged.connect(lambda _: populate_source())
        only_owned_cb.stateChanged.connect(lambda _: populate_target())
        populate_both()
        refresh_queue()

        def on_add():
            ti = tgt_list.currentItem()
            si = src_list.currentItem()
            if not ti or not si:
                QMessageBox.information(self, "Transmog",
                    "Pick ONE item in each list:\n"
                    "  Left  = your armor (the piece you want to re-skin)\n"
                    "  Right = the look you want it to have")
                return
            tgt_key = ti.data(Qt.UserRole)
            src_key = si.data(Qt.UserRole)
            if tgt_key == src_key:
                QMessageBox.information(self, "Transmog",
                    "Your armor and the new look must be different items.")
                return
            tgt = next((a for a in self._armor_catalog if a.item_id == tgt_key), None)
            if src_key == INVISIBLE_SENTINEL_KEY:
                src = invisible_template
                if src is None:
                    QMessageBox.warning(self, "Transmog",
                        "No Invisible Model template available in this iteminfo.")
                    return
                if not tgt:
                    return
                local_swaps[:] = [s for s in local_swaps if s['tgt'].item_id != tgt_key]
                import copy
                fake_src = copy.copy(src)
                fake_src.display_name = "Invisible Model"
                fake_src.category = "Invisible"
                local_swaps.append({'src': fake_src, 'tgt': tgt})
                refresh_queue()
                return
            src = next((a for a in self._armor_catalog if a.item_id == src_key), None)
            if not tgt or not src:
                return
            local_swaps[:] = [s for s in local_swaps if s['tgt'].item_id != tgt_key]
            local_swaps.append({'src': src, 'tgt': tgt})
            refresh_queue()

        def on_remove():
            row = queue_list.currentRow()
            if 0 <= row < len(local_swaps):
                del local_swaps[row]
                refresh_queue()

        def on_clear():
            local_swaps.clear()
            refresh_queue()

        def on_export():
            if not local_swaps:
                QMessageBox.information(self, "Export", "No swaps queued.")
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Transmog Config", "transmog_config.json", "JSON (*.json)")
            if not path:
                return
            out = {
                'version': 1,
                'swaps': [
                    {
                        'target_key': s['tgt'].item_id,
                        'target_name': s['tgt'].internal_name,
                        'source_key': s['src'].item_id,
                        'source_name': s['src'].internal_name,
                    }
                    for s in local_swaps
                ],
            }
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(out, f, indent=2)
                QMessageBox.information(self, "Export", f"Wrote {len(local_swaps)} swap(s) to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

        def on_import():
            path, _ = QFileDialog.getOpenFileName(
                self, "Import Transmog Config", "", "JSON (*.json)")
            if not path:
                return
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                by_key = {a.item_id: a for a in self._armor_catalog}
                by_name = {a.internal_name: a for a in self._armor_catalog}
                added = 0
                missed = 0

                if isinstance(cfg.get('swaps'), list):
                    for s in cfg['swaps']:
                        tgt = by_key.get(s.get('target_key'))
                        src = by_key.get(s.get('source_key'))
                        if (not tgt or not src) and s.get('target_name') and s.get('source_name'):
                            tgt = tgt or by_name.get(s['target_name'])
                            src = src or by_name.get(s['source_name'])
                        if not tgt or not src:
                            missed += 1
                            log.warning("Transmog import: could not resolve target_key=%s source_key=%s",
                                        s.get('target_key'), s.get('source_key'))
                            continue
                        log.info("Transmog import: queued tgt=%s (key %s) <- src=%s (key %s)",
                                    tgt.internal_name, tgt.item_id, src.internal_name, src.item_id)
                        local_swaps[:] = [x for x in local_swaps if x['tgt'].item_id != tgt.item_id]
                        local_swaps.append({'src': src, 'tgt': tgt})
                        added += 1

                elif isinstance(cfg.get('patches'), list):
                    seen_pairs = set()
                    for patch in cfg['patches']:
                        for change in patch.get('changes', []):
                            label = change.get('label', '')
                            if ' -> ' not in label:
                                continue
                            tgt_name, src_name = label.split(' -> ', 1)
                            tgt_name, src_name = tgt_name.strip(), src_name.strip()
                            pair_key = (tgt_name, src_name)
                            if pair_key in seen_pairs:
                                continue
                            seen_pairs.add(pair_key)
                            src = by_name.get(src_name)
                            tgt = by_name.get(tgt_name)
                            if not src or not tgt:
                                missed += 1
                                continue
                            local_swaps[:] = [x for x in local_swaps if x['tgt'].item_id != tgt.item_id]
                            local_swaps.append({'src': src, 'tgt': tgt})
                            added += 1
                else:
                    QMessageBox.warning(self, "Import",
                        "Unrecognized JSON format. Expected either our 'swaps' format "
                        "or HexeMarie's 'patches' format.")
                    return

                refresh_queue()
                QMessageBox.information(self, "Import",
                    f"Imported {added} swap(s). {missed} skipped (items not found).")
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", str(e))

        add_btn.clicked.connect(on_add)
        remove_btn.clicked.connect(on_remove)
        clear_btn.clicked.connect(on_clear)
        def on_export_field_json():
            if not local_swaps:
                QMessageBox.information(self, "Export Field JSON v3", "No swaps queued.")
                return
            # Use _buff_rust_lookup (int-keyed, same source as _apply_transmog_swaps)
            # rather than building a new lookup from _buff_rust_items, which can
            # have key-type mismatches and misses _apply_transmog_swaps mutations.
            rust_lookup = getattr(parent, '_buff_rust_lookup', None) or {}
            if not rust_lookup:
                QMessageBox.warning(self, "Export Field JSON v3",
                    "Item data not extracted.\n"
                    "Click Extract first, then try again.")
                return
            intents = []
            skipped = []
            same_visual = []
            PREFAB_FIELDS = ('prefab_data_list', 'gimmick_visual_prefab_data_list')
            for sw in local_swaps:
                tgt = sw['tgt']
                src = sw['src']
                src_key = src.item_id if hasattr(src, 'item_id') else 0
                tgt_key = tgt.item_id if hasattr(tgt, 'item_id') else 0
                tgt_item = rust_lookup.get(int(tgt_key))
                src_item = rust_lookup.get(int(src_key))
                if not tgt_item or not src_item:
                    skipped.append(tgt.internal_name)
                    continue
                # Invisible swap: clear visual fields
                is_invisible = (src_key == 0 or
                                getattr(src, 'internal_name', '') == '__INVISIBLE_ZERO__')
                swap_had_diff = False
                for field in PREFAB_FIELDS:
                    if is_invisible:
                        src_val = []
                    else:
                        src_val = src_item.get(field)
                        if src_val is None:
                            continue
                    tgt_val = tgt_item.get(field)
                    # Use JSON round-trip for reliable deep equality check on
                    # nested structures that may not support Python == correctly.
                    try:
                        src_json = json.dumps(src_val, sort_keys=True, default=str)
                        tgt_json = json.dumps(tgt_val, sort_keys=True, default=str)
                        if src_json == tgt_json:
                            continue
                    except Exception:
                        if src_val == tgt_val:
                            continue
                    intents.append({
                        'entry': tgt.internal_name,
                        'key': tgt_key,
                        'field': field,
                        'op': 'set',
                        'new': src_val,
                        '_comment': f'transmog: visual from {src.internal_name}',
                    })
                    swap_had_diff = True
                if not swap_had_diff and not is_invisible:
                    same_visual.append(f"{tgt.display_name} → {src.display_name}")
            if not intents:
                msg = "No field-level differences found."
                if same_visual:
                    msg += ("\n\nThese item pairs share the same visual appearance "
                            "(identical prefab data):\n" + "\n".join(same_visual))
                    msg += ("\n\nTransmog only works between visually distinct items. "
                            "Try selecting items with different meshes or skins.")
                if skipped:
                    msg += f"\n\nItems not found in extracted data: {', '.join(skipped)}"
                QMessageBox.warning(self, "Export Field JSON v3", msg)
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Field JSON v3", "transmog.field.json",
                "Field JSON (*.field.json *.json);;All Files (*)")
            if not path:
                return
            doc = {
                'modinfo': {
                    'title': 'Transmog Mod',
                    'version': '1.0',
                    'author': 'CrimsonGameMods Transmog',
                    'description': f'{len(local_swaps)} swap(s), {len(intents)} intent(s)',
                    'note': 'Format 3 — copies prefab visual fields by name.',
                },
                'format': 3,
                'format_minor': 1,
                'targets': [{'file': 'iteminfo.pabgb', 'intents': intents}],
            }
            try:
                with open(path, 'w', encoding='utf-8') as _fh:
                    json.dump(doc, _fh, indent=2, ensure_ascii=False, default=str)
                msg2 = f"Exported {len(intents)} intent(s) for {len(local_swaps)} swap(s)."
                if skipped:
                    msg2 += f"\n\nSkipped: {', '.join(skipped)}"
                QMessageBox.information(self, "Export Field JSON v3",
                    f"{msg2}\n\nFile: {os.path.basename(path)}")
            except Exception as _ej:
                QMessageBox.critical(self, "Export Failed", str(_ej))

        export_btn.clicked.connect(on_export)
        export_field_btn.clicked.connect(on_export_field_json)
        import_btn.clicked.connect(on_import)

        def on_ok():
            self._transmog_swaps = list(local_swaps)
            self._buff_modified = self._buff_modified or bool(local_swaps)
            count = len(local_swaps)
            self._buff_status_label.setText(
                f"Transmog queue: {count} swap(s). Applied on Apply to Game / Export.")
            self.accept()

        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(self.reject)
