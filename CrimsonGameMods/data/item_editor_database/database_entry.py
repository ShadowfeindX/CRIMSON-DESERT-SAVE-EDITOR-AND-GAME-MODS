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