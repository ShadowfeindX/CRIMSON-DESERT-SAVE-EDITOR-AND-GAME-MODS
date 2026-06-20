from __future__ import annotations

from data.item_editor_database.database_entry import Skill
from .data_row import DataRow

from ...helpers import STATE

from ...helpers import *


def _update_skill_list(indexes: list[int], selected: Skill, value: int = None):
    for idx in indexes:
        item = ItemEditorInfoDetails(idx)
        new = False

        passives = [
            skill
            for skill in item.passives()
            if skill["skill"] != selected["key"]
            or (new := skill["level"] == value) is None
        ]

        if value is None:
            if len(item.passives()) != len(passives):
                item.passives(passives)
            continue

        if not new:
            passives.append({"skill": selected["key"], "level": value})
            item.passives(passives)


def new():
    return DataRow(
        label="Passives",
        load_fn=STATE.skill_list,
        add_fn=_update_skill_list,
        remove_fn=_update_skill_list,
        min_value=1,
        max_value=10,
    )
