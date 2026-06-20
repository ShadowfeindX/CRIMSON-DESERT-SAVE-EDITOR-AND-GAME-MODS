from __future__ import annotations

from data.item_editor_database.database_entry import Stat
from .data_row import DataRow
from ...dmm_types import EnchantStatChange, EnchantStatData
from ...helpers import STATE
from ...helpers import *


def _create_new_list(item, selected, value) -> list[EnchantStatData]:
    new = item._baseline_enchant_data(0)["enchant_stat_data"]
    new[selected["stat_type"]][:] = [
        {
            "stat": selected["key"],
            "change_mb": value,
        }
    ]
    item.stats([new])


def _update_stat_list(item: ItemEditorInfoDetails, selected: Stat, value=None):
    dirty = False
    for esd in (stats := copy(item.stats())):
        stat_data: list[EnchantStatChange] = esd.get(selected["stat_type"])
        initial = len(stat_data)
        new = False

        stat_data[:] = [
            change
            for change in stat_data
            if change["stat"] != selected["key"]
            or (new := change["change_mb"] == value) is None
        ]

        if value is None:
            if len(stat_data) != initial:
                dirty = True
            continue

        if not new:
            dirty = True
            stat_data.append({"stat": selected["key"], "change_mb": value})

    if dirty:
        item.stats(stats)


def _add(indexes: list[int], selected: Stat, value: int):
    for idx in indexes:
        if len((item := ItemEditorInfoDetails(idx)).stats()) == 0:
            _create_new_list(item, selected, value)
        else:
            _update_stat_list(item, selected, value)


def _remove(indexes: list[int], selected: Stat):
    for idx in indexes:
        _update_stat_list(ItemEditorInfoDetails(idx), selected)


def new():
    return DataRow(
        label="Stat",
        load_fn=STATE.stat_list,
        add_fn=_add,
        remove_fn=_remove,
        min_value=0,
        max_value=9_999_999,
    )
