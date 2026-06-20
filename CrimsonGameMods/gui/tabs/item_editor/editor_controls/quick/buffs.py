from __future__ import annotations

from data.item_editor_database.database_entry import Stat
from .data_row import DataRow

from ...helpers import STATE

from ...helpers import *


def _update_buff_list(indexes: list[int], selected: Stat, value: int = None):
    for idx in indexes:
        item = ItemEditorInfoDetails(idx)
        new = False

        buffs = [
            buff
            for buff in item.buffs()
            if buff["buff"] != selected["key"]
            or (new := buff["level"] == value) is None
        ]

        if value is None:
            if len(item.buffs()) != len(buffs):
                item.buffs(buffs)
            continue

        if not new:
            buffs.append({"buff": selected["key"], "level": value})
            item.buffs(buffs)


def new():
    return DataRow(
        label="Buff",
        load_fn=STATE.buff_list,
        add_fn=_update_buff_list,
        remove_fn=_update_buff_list,
        max_value=50,
    )
