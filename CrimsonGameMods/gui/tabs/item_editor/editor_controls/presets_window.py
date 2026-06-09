from __future__ import annotations


import textwrap
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
)

from .presets import Presets
from gui.theme import COLORS


class PresetsWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Presets")

        self.Presets = Presets.get_presets()
        self.Presets._set_current_item(parent.get_current_item())

        self._config = {}

        self._build_ui()

    def _build_ui(self) -> QWidget:
        """Hero Presets Window — grid rows of 3 large colored buttons."""

        # TEMP styles array
        styles = [
            ("#4682B4", "White"),
            ("#FFFFFF", "Black"),
            ("#00FF7F", "Black"),
            ("#00BFFF", "Black"),
            ("#9370DB", "Black"),
            ("#DC143C", "White"),
            ("#778899", "Black"),
            ("#FFD700", "Black"),
            ("#FF69B4", "Black"),
            ("#FF8C00", "Black"),
            ("#00FFFF", "Black"),
            ("#7FFF00", "Black"),
            ("#DDA0DD", "Black"),
            ("#2E8B57", "White"),
        ]

        def gen_styles(font_color: str, bkg_color: str):
            return f"""
            QPushButton, QToolTip {{
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton {{
                color: {font_color};
                background-color: {bkg_color};
                padding: 16px 24px;
            }}
            
            QToolTip {{
                color: black;
                background-color: white;
                border: 1px solid black;
            }}
            """

        pl = QVBoxLayout(self)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(8)
        grid_columns = 3

        grid = QGridLayout()
        grid_buttons: list[QPushButton] = []
        grid_label = QLabel(
            "One-Click Presets. Click an item in the list, "
            "then choose a preset below to apply."
        )
        self._build_standard_grid(grid_buttons)

        dev_grid = QGridLayout()
        dev_grid_buttons: list[QPushButton] = []
        dev_grid_label = QLabel(
            "DEV Ring Presets. Click an item in the list, "
            "then choose a preset below to apply."
        )
        self._build_dev_grid(dev_grid_buttons)

        custom_grid = QGridLayout()
        custom_grid_buttons: list[QPushButton] = []
        custom_grid_label = QLabel(
            "Custom Saved Presets. "
            "Choose a preset below to apply. "
            "Click the plus button to add a new custom preset."
        )
        self._build_custom_grid(custom_grid_buttons)

        # Apply Layout and Styles to all grid buttons
        # i = 0
        grid.setSpacing(8)
        for i, btn in enumerate(grid_buttons):
            bc, fc = styles[i % len(styles)]
            r, c = divmod(i, grid_columns)
            btn.setStyleSheet(gen_styles(fc, bc))
            grid.addWidget(btn, r, c)
            # i += 1

        # i = 0
        dev_grid.setSpacing(8)
        for i, btn in enumerate(dev_grid_buttons):
            bc, fc = styles[~(i % len(styles))]
            r, c = divmod(i, grid_columns)
            btn.setStyleSheet(gen_styles(fc, bc))
            dev_grid.addWidget(btn, r, c)
            # i += 1

        # i = 0
        custom_grid.setSpacing(8)
        for i, btn in enumerate(custom_grid_buttons):
            bc, fc = styles[i % len(styles)]
            r, c = divmod(i, grid_columns)
            btn.setStyleSheet(gen_styles(fc, bc))
            custom_grid.addWidget(btn, r, c)
            # i += 1

        pl.addWidget(grid_label)
        pl.addLayout(grid)
        pl.addWidget(dev_grid_label)
        pl.addLayout(dev_grid)
        pl.addWidget(custom_grid_label)
        pl.addLayout(custom_grid)
        pl.addStretch(1)

    def __build_standard_grid(self, grid_buttons: list[QPushButton]):
        "───────────────────── Standard Presets ──────────────────────────────"

        godmode_desc = textwrap.dedent("""
            - No Cooldown   
            - Max Charges
            - Max Sockets
            - Max Enchant
            - Invincible
            - Great Thief (All Crimes)
            - Max Attack/Defense
            - Max Attack/Move Speed
            - Max Regen
            - Max Crit/Resist
            - 8 Equipment Buffs at level 10
        """).strip()

        def apply_godmode():
            # edl = rust_info.get("enchant_data_list", [])
            # if not edl:
            #     _eq = rust_info.get(
            #         "equip_type", rust_info.get("equipment_type", 0)
            #     )
            #     if isinstance(_eq, dict):
            #         _eq = _eq.get("a", 0)
            #     _it = rust_info.get("item_type", rust_info.get("type", 0))
            #     if isinstance(_it, dict):
            #         _it = _it.get("a", 0)
            #     _is_equippable = bool(_eq) or int(_it or 0) in {
            #         1,
            #         2,
            #         3,
            #         4,
            #         5,
            #         6,
            #         7,
            #         8,
            #         9,
            #         10,
            #         11,
            #         12,
            #         13,
            #         14,
            #         15,
            #         16,
            #         17,
            #         18,
            #         19,
            #         20,
            #     }
            #     if not _is_equippable:
            #         QMessageBox.warning(
            #             self,
            #             "God Mode",
            #             "This item has no enchant data.\n"
            #             "Only equippable items (weapons, armor, accessories) can have buffs.",
            #         )
            #         return
            #     edl = []

            # display_name = self._name_db.get_name(
            #     self._buff_current_item.item_key
            # )
            display_name = "Item"

            reply = QMessageBox.warning(
                self,
                "Potter's God Mode",
                f"Apply God Mode to {display_name}?\n\n"
                f"This will inject into ALL enchant levels:\n"
                f"{godmode_desc}\n\n"
                f"Click 'Export Field JSON v3' after to write.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            self.apply_std_preset("god_mod", True)
            self.apply_std_preset("great_thief_all", True)
            self.apply_std_preset("open_sockets", True)
            self.apply_std_preset("max_charges", True)
            self.apply_std_preset("max_enchant", True)
            self.apply_std_preset("no_cooldown", True)

        def apply_great_thief() -> None:
            # from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

            dlg = QDialog(self)
            dlg.setWindowTitle("Great Thief — Pick Variant")
            dlg.resize(480, 220)
            dl = QVBoxLayout(dlg)

            info = QLabel(
                "Pick which variant of Great Thief to apply.\n\n"
                "Block Theft only: skills 9128 + 76009. Suppresses pickpocket crime detection.\n"
                "Other crimes (vandalism, assault) will still flag you.\n\n"
                "Block ALL crime: also adds 76011 + 76012. Full crime immunity —\n"
                "theft, vandalism, and all other crime types.\n\n"
                "Passives stack with existing; gimmick replaces."
            )
            info.setWordWrap(True)
            info.setStyleSheet(f"color: {COLORS['text_dim']}; padding: 4px;")
            dl.addWidget(info)

            btn_row = QHBoxLayout()
            b1 = QPushButton("Block Theft only")
            b1.clicked.connect(
                lambda: (dlg.accept(), self.apply_std_preset("great_thief"))
            )
            btn_row.addWidget(b1)

            b2 = QPushButton("Block ALL crime")
            b2.setObjectName("accentBtn")
            b2.clicked.connect(
                lambda: (
                    dlg.accept(),
                    self.apply_std_preset("great_thief_all"),
                )
            )
            btn_row.addWidget(b2)

            cancel = QPushButton("Cancel")
            cancel.clicked.connect(dlg.reject)
            btn_row.addWidget(cancel)
            dl.addLayout(btn_row)

            dlg.exec()

        sockets_btn = QPushButton("5 Sockets")
        sockets_btn.setToolTip(
            "Item will drop with 5 open sockets by default."
        )
        sockets_btn.clicked.connect(
            lambda: self.apply_std_preset("open_sockets")
        )
        grid_buttons.append(sockets_btn)

        enchant_btn = QPushButton("Max Refine")
        enchant_btn.setToolTip("Item will drop at lvl 10 by default.")
        enchant_btn.clicked.connect(
            lambda: self.apply_std_preset("max_enchant")
        )
        grid_buttons.append(enchant_btn)

        cooldown_btn = QPushButton("No Cooldown")
        cooldown_btn.setToolTip("Item will have 1s cooldown by default.")
        cooldown_btn.clicked.connect(
            lambda: self.apply_std_preset("no_cooldown")
        )
        grid_buttons.append(cooldown_btn)

        charges_btn = QPushButton("Max Charges")
        charges_btn.setToolTip("Item will have 100 charges by default.")
        charges_btn.clicked.connect(
            lambda: self.apply_std_preset("max_charges")
        )
        grid_buttons.append(charges_btn)
        stacks_btn = QPushButton("Max Stacks")
        stacks_btn.setToolTip("Item will have a max stack size of 999999.")
        stacks_btn.clicked.connect(lambda: self.apply_std_preset("max_stacks"))
        grid_buttons.append(stacks_btn)

        abyss_socket_btn = QPushButton("Abyss + 5 Sockets")
        abyss_socket_btn.setToolTip(
            "Unlock abyss restriction (equipable_hash = 0) AND\n"
            "extend to 5 sockets on the selected item."
        )
        # abyss_socket_btn.clicked.connect(self._eb_abyss_plus_sockets)
        grid_buttons.append(abyss_socket_btn)

        godmode_btn = QPushButton("God Mode")
        godmode_btn.setToolTip(f"Inject full God Mode stats:\n{godmode_desc}")
        godmode_btn.clicked.connect(apply_godmode)
        grid_buttons.append(godmode_btn)

        shadow_boots_btn = QPushButton("Shadow Boots")
        shadow_boots_btn.setToolTip(
            "Apply Potter's Shadow Boots config to selected item:\n"
            "Skills: Shadow Dash (7201) + Breeze Step (7055) + Swimming (7202)\n"
            "Gimmick: 1004431 (boots gimmick — activates the skills)"
        )
        shadow_boots_btn.clicked.connect(
            lambda: self.apply_std_preset("shadow_boots")
        )
        grid_buttons.append(shadow_boots_btn)

        lightning_btn = QPushButton("Lightning Weapon")
        lightning_btn.setToolTip(
            "Apply lightning weapon config (Potter's Hwando recipe):\n"
            "Skills: Lightning (91101) + Fire (91105) + Ice (91104) affinity\n"
            "Gimmick: 1001961 (weapon gimmick)"
        )
        lightning_btn.clicked.connect(
            lambda: self.apply_std_preset("lightning_weapon")
        )
        grid_buttons.append(lightning_btn)

        great_thief_btn = QPushButton("Great Thief")
        great_thief_btn.setToolTip(
            "Apply Great Thief activated skill (works on ANY item).\n"
            "Opens a picker: Block Theft only, or Block ALL crime.\n"
            "Gimmick: 1002041, 1 charge, 30-min cooldown."
        )
        great_thief_btn.clicked.connect(apply_great_thief)
        grid_buttons.append(great_thief_btn)

        no_fall_btn = QPushButton("No Fall Damage")
        no_fall_btn.setToolTip(
            "Adds fall damage reduction buff to the selected item.\n"
            "Sets equip_buffs: BuffLevel_Food_FallDamageReduce (1000185) level 10\n"
            "on all enchant levels, and stages buffinfo changes so the reduction\n"
            "values export correctly via Export Field JSON v3."
        )
        # no_fall_btn.clicked.connect(self._eb_apply_no_fall_damage)
        grid_buttons.append(no_fall_btn)

    def _build_standard_grid(self, grid_buttons: list[QPushButton]):
        "───────────────────── Standard Presets ──────────────────────────────"

        godmode_desc = textwrap.dedent("""
            - No Cooldown   
            - Max Charges
            - Max Sockets
            - Max Enchant
            - Invincible
            - Great Thief (All Crimes)
            - Max Attack/Defense
            - Max Attack/Move Speed
            - Max Regen
            - Max Crit/Resist
            - 8 Equipment Buffs at level 10
        """).strip()

        def apply_godmode():
            # edl = rust_info.get("enchant_data_list", [])
            # if not edl:
            #     _eq = rust_info.get(
            #         "equip_type", rust_info.get("equipment_type", 0)
            #     )
            #     if isinstance(_eq, dict):
            #         _eq = _eq.get("a", 0)
            #     _it = rust_info.get("item_type", rust_info.get("type", 0))
            #     if isinstance(_it, dict):
            #         _it = _it.get("a", 0)
            #     _is_equippable = bool(_eq) or int(_it or 0) in {
            #         1,
            #         2,
            #         3,
            #         4,
            #         5,
            #         6,
            #         7,
            #         8,
            #         9,
            #         10,
            #         11,
            #         12,
            #         13,
            #         14,
            #         15,
            #         16,
            #         17,
            #         18,
            #         19,
            #         20,
            #     }
            #     if not _is_equippable:
            #         QMessageBox.warning(
            #             self,
            #             "God Mode",
            #             "This item has no enchant data.\n"
            #             "Only equippable items (weapons, armor, accessories) can have buffs.",
            #         )
            #         return
            #     edl = []

            # display_name = self._name_db.get_name(
            #     self._buff_current_item.item_key
            # )
            display_name = "Item"

            reply = QMessageBox.warning(
                self,
                "Potter's God Mode",
                f"Apply God Mode to {display_name}?\n\n"
                f"This will inject into ALL enchant levels:\n"
                f"{godmode_desc}\n\n"
                f"Click 'Export Field JSON v3' after to write.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            self.apply_std_preset("god_mod", True)
            self.apply_std_preset("great_thief_all", True)
            self.apply_std_preset("open_sockets", True)
            self.apply_std_preset("max_charges", True)
            self.apply_std_preset("max_enchant", True)
            self.apply_std_preset("no_cooldown", True)

        def apply_great_thief() -> None:
            # from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

            dlg = QDialog(self)
            dlg.setWindowTitle("Great Thief — Pick Variant")
            dlg.resize(480, 220)
            dl = QVBoxLayout(dlg)

            info = QLabel(
                "Pick which variant of Great Thief to apply.\n\n"
                "Block Theft only: skills 9128 + 76009. Suppresses pickpocket crime detection.\n"
                "Other crimes (vandalism, assault) will still flag you.\n\n"
                "Block ALL crime: also adds 76011 + 76012. Full crime immunity —\n"
                "theft, vandalism, and all other crime types.\n\n"
                "Passives stack with existing; gimmick replaces."
            )
            info.setWordWrap(True)
            info.setStyleSheet(f"color: {COLORS['text_dim']}; padding: 4px;")
            dl.addWidget(info)

            btn_row = QHBoxLayout()
            b1 = QPushButton("Block Theft only")
            b1.clicked.connect(
                lambda: (dlg.accept(), self.apply_std_preset("great_thief"))
            )
            btn_row.addWidget(b1)

            b2 = QPushButton("Block ALL crime")
            b2.setObjectName("accentBtn")
            b2.clicked.connect(
                lambda: (
                    dlg.accept(),
                    self.apply_std_preset("great_thief_all"),
                )
            )
            btn_row.addWidget(b2)

            cancel = QPushButton("Cancel")
            cancel.clicked.connect(dlg.reject)
            btn_row.addWidget(cancel)
            dl.addLayout(btn_row)

            dlg.exec()

        def bind_preset(*args, **kwargs):
            "Bind preset function call to signal"

            def binding():
                self.apply_std_preset(*args, **kwargs)

            return binding

        for key, preset in self.Presets.Standard.items():
            btn = QPushButton(preset["name"])
            btn.setToolTip(preset["description"])
            if key == "godmode":
                btn.clicked.connect(bind_preset(key, skip=True))
            else:
                btn.clicked.connect(bind_preset(key))
            grid_buttons.append(btn)

    def _build_dev_grid(self, grid_buttons: list[QPushButton]):
        "───────────────────── DEV Ring Presets ──────────────────────────────"

        immunity_btn = QPushButton("Immunity")
        immunity_btn.setToolTip("Adds DEV Immune Ring buff to item.")
        immunity_btn.clicked.connect(lambda: self.apply_dev_preset("immune"))
        grid_buttons.append(immunity_btn)

        str_hp_btn = QPushButton("STR/HP")
        str_hp_btn.setToolTip(
            "Inject DEV STR/HP Ring stats:\n- Max DDD (Damage)\n- Max HP Regen"
        )
        str_hp_btn.clicked.connect(lambda: self.apply_dev_preset("str_hp"))
        grid_buttons.append(str_hp_btn)

        dev_def_hp_btn = QPushButton("DEF/HP")
        dev_def_hp_btn.setToolTip(
            "Inject DEV DEF/HP Ring stats:\n"
            "- Max DPV (Defense)\n"
            "- Max HP Regen"
        )
        dev_def_hp_btn.clicked.connect(lambda: self.apply_dev_preset("def_hp"))
        grid_buttons.append(dev_def_hp_btn)

        dev_mp_stam_btn = QPushButton("MP/Stamina")
        dev_mp_stam_btn.setToolTip(
            "Inject DEV MP/Stamina Ring stats:\n"
            "- Max Spirit Regen\n"
            "- Max Stamina Regen\n"
            "- Max Stamina Cost Reduction"
        )
        dev_mp_stam_btn.clicked.connect(
            lambda: self.apply_dev_preset("mp_stam")
        )
        grid_buttons.append(dev_mp_stam_btn)

        speed = QPushButton("Speed")
        speed.setToolTip(
            "Inject DEV Speed Ring stats:\n"
            "- Max Attack Speed\n"
            "- Max Move Speed\n"
            "- Max Crit Rate"
        )
        speed.clicked.connect(lambda: self.apply_dev_preset("speed"))
        grid_buttons.append(speed)

        dev_mode_desc = textwrap.dedent("""
            Inject ALL DEV Ring stats:
            - Immunity
            - Max DDD (Damage)
            - Max DPV (Defense)
            - Max Attack Speed
            - Max Move Speed
            - Max Crit Rate
            - Max HP Regen
            - Max Spirit Regen
            - Max Stamina Regen
            - Max Stamina Cost Reduction
        """).strip()
        all = QPushButton("All")
        all.setToolTip(dev_mode_desc)
        all.clicked.connect(lambda: self.apply_dev_preset("all"))
        grid_buttons.append(all)

    def _build_custom_grid(self, grid_buttons: list[QPushButton]):
        "─────────────────────── Custom Presets ──────────────────────────────"

        def add_custom_preset():
            dlg = QDialog(self)
            dlg.setWindowTitle("Create a new preset?")
            layout = QVBoxLayout(dlg)
            buttons = QHBoxLayout()

            layout.addWidget(
                QLabel("Would you like to create a new Custom Preset?")
            )

            yes_btn = QPushButton("Yes")
            no_btn = QPushButton("No")
            no_more_btn = QPushButton("Don't Ask Again")
            no_more_btn.setObjectName("btnDestructive")

            buttons.addWidget(yes_btn)
            buttons.addWidget(no_btn)
            buttons.addWidget(no_more_btn)
            layout.addLayout(buttons)

            def set_no_ask():
                self._config["custom_preset_ask"] = False
                # self.config_save_requested.emit()
                dlg.close()

            def show_mod_details_editor():
                _dlg = QDialog(dlg)
                _dlg.setWindowTitle("Mod Details")

                _layout = QVBoxLayout(_dlg)

                title = QLineEdit()
                title.setPlaceholderText("Merged Stack")
                author = QLineEdit()
                author.setPlaceholderText("CrimsonGameMods Stacker")
                version = QDoubleSpinBox()
                version.setValue(1.0)
                version.setSingleStep(0.01)
                version.setRange(0.01, 100)
                description = QTextEdit()
                description.setPlaceholderText("Mod Description")
                note = QTextEdit()
                note.setPlaceholderText("Author Notes")
                _buttons = QHBoxLayout()
                save_btn = QPushButton("Save")
                discard_btn = QPushButton("Discard Changes")
                _buttons.addWidget(save_btn)
                _buttons.addWidget(discard_btn)

                details = self._config.get("last_mod_details")
                if details:
                    title.setText(details["title"])
                    author.setText(details["author"])
                    title.setText(details["title"])
                    version.setValue(float(details["version"]))
                    description.setText(details["description"])
                    note.setText(details["note"])

                _layout.addWidget(QLabel("Title"))
                _layout.addWidget(title)
                _layout.addWidget(QLabel("Author"))
                _layout.addWidget(author)
                _layout.addWidget(QLabel("Version"))
                _layout.addWidget(version)
                _layout.addWidget(description)
                _layout.addWidget(note)
                _layout.addLayout(_buttons)
                _dlg.setLayout(_layout)

                def save_mod_details():
                    self._config["last_mod_details"] = {
                        "title": title.text(),
                        "version": version.text(),
                        "author": author.text(),
                        "description": description.toPlainText(),
                        "note": note.toPlainText(),
                    }
                    self.config_save_requested.emit()
                    _dlg.close()

                save_btn.clicked.connect(save_mod_details)
                discard_btn.clicked.connect(_dlg.close)
                _dlg.exec()
                dlg.close()

            yes_btn.clicked.connect(show_mod_details_editor)
            no_btn.clicked.connect(dlg.close)
            no_more_btn.clicked.connect(set_no_ask)
            dlg.exec()

        for i, (key, preset) in enumerate(self.Presets.Custom.items()):
            try:
                name = preset["name"]
                desc = preset["description"]
                # warning = preset.pop("warning", None)

                btn = QPushButton(name)
                btn.setToolTip(desc)
                btn.clicked.connect(lambda: self.apply_custom_preset(key))

            except KeyError:
                QMessageBox.warning(
                    self,
                    "Invalid Preset",
                    f"Preset {key} is in an invalid format!",
                )
                continue

        custom_add = QPushButton("+")
        custom_add.setToolTip("Create a new Custom Preset")
        custom_add.clicked.connect(add_custom_preset)
        grid_buttons.append(custom_add)

    def apply_std_preset(
        self, preset_key: str, skip: bool = False, warn: str = ""
    ):
        if self.Presets._current_item is None:
            self._warn("Please select an item first!")
            return

        if skip:
            self.Presets.apply_std_preset(preset_key, skip=skip, warn=warn)
            return

        preset = self.Presets.Standard[preset_key]

        if warn:
            warning = warn
        else:
            warning = preset.get("warning", "")
            if warning:
                warning = f"WARNING: {warning}\n\n"

        skill_str = ", ".join(
            str(p["skill"]) for p in preset.get("passives", [])
        )
        default_desc = (
            f"Skills (stack with existing): {skill_str}\n"
            f"Gimmick: {preset.get('gimmick_info', 'unchanged')}\n"
            f"Replaces existing gimmick."
            if preset.get("passives")
            else ""
        )

        display_name = "Item"

        # cur_charge = rust_info.get('item_charge_type', 0)
        # new_charge = preset.get('item_charge_type', cur_charge)
        # charge_change_warn = ""
        # if cur_charge != new_charge and new_charge == 0:
        #     charge_change_warn = (
        #         f"WARNING: Switching item from passive -> activated.\n"
        #         f"Existing copies in your save have NO charge-tracking data and\n"
        #         f"will show '0 uses' in-game. Get a FRESH copy (store/craft/drop)\n"
        #         f"AFTER applying the mod for the activation to work.\n\n"
        #     )

        # cur_stack_size = rust_info.get('max_stack_count', 1)
        # new_stack_size = preset.get('max_stack_count', cur_stack_size)
        # max_stack_warn = ""
        # if cur_stack_size != new_stack_size and cur_stack_size == 1:
        #     max_stack_warn = (
        #         "WARNING: Changing the stack size for items that do "
        #         "not stack by default can cause ui glitches and lost items.\n"
        #         "Proceed with caution.\n\n"
        #     )

        reply = QMessageBox.question(
            self,
            f"Apply Preset: {preset['name']}",
            f"Apply {preset['name']} preset to {display_name}?\n\n"
            f"{preset.get('description', default_desc)}\n\n"
            f"{warning}"
            # f"{warning}{charge_change_warn}{max_stack_warn}"
            f"",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.Presets.apply_std_preset(preset_key, skip=skip, warn=warn)
        # log.info("Applying Preset: %s", preset)

    def apply_dev_preset(
        self, preset: str, skip: bool = False, warn: str = ""
    ):
        log.info("Applying Dev Preset: %s", preset)

    def apply_custom_preset(
        self, preset: str, skip: bool = False, warn: str = ""
    ):
        log.info("Applying Custom Preset: %s", preset)

    def _warn(self, warning):
        QMessageBox.warning(self, "Warning!", warning)