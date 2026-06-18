from enum import StrEnum
from typing import TypedDict


class Skill(TypedDict):
    key: int
    string_key: str
    internal_name: str
    internal_description: str
    localized_name: str | None


class Buff(TypedDict):
    key: int
    string_key: str
    # internal_name: str
    # internal_description: str
    # localized_name: str | None


class StatType(StrEnum):
    REGEN = "regen_stat_list"
    STATIC = "stat_list_static"
    LEVEL = "stat_list_static_level"


class Stat(TypedDict):
    key: int
    stat_level_data: []
    stat_type: StatType
    string_key: str
    use_percent: bool
