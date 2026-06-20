import json
import os
import string
from pathlib import Path
from typing import Any
import dmm_parser as dmm

from data.item_editor_database.database_entry import Buff, Skill


MISSING_ENTRY = "(unknown)"


def find_game_path() -> str:
    candidates = []

    for letter in string.ascii_uppercase:
        candidates.append(
            f"{letter}:\\SteamLibrary\\steamapps\\common\\Crimson Desert"
        )

    candidates.extend(
        [
            r"C:\Program Files (x86)\Steam\steamapps\common\Crimson Desert",
            r"C:\Program Files\Steam\steamapps\common\Crimson Desert",
            r"C:\Program Files\Epic Games\CrimsonDesert",
        ]
    )

    for path in candidates:
        papgt = os.path.join(path, "meta", "0.papgt")
        if os.path.isfile(papgt):
            return path

    raise FileExistsError("No Game Path Found!")


def load_stat_data(game_path: str, databse: Path):
    pabgb = dmm.extract_file(
        game_dir=game_path,
        group_name="0008",
        dir_path="gamedata/binary__/client/bin",
        file_name="statusinfo.pabgb",
    )

    pabgh = dmm.extract_file(
        game_dir=game_path,
        group_name="0008",
        dir_path="gamedata/binary__/client/bin",
        file_name="statusinfo.pabgh",
    )

    ACCEPTED = (
        "key",
        "string_key",
        "stat_level_data",
        "stat_type",
        "use_percent",
        # "static_stat_type",
        # "status_index_xxxxx",
        # "status_key_hash_code32",
        # "regenerate_type",
        # "elemental_stat_type"
    )

    def cat(entry):
        if entry["stat_level_data"]:
            return "stat_list_static_level"
        if entry["regenerate_type"]:
            return "regen_stat_list"
        return "stat_list_static"

    table: list[dict[str, Any]] = dmm.parse_table("status_info", pabgb, pabgh)

    data = {
        entry["key"]: {
            k: v if k != "stat_type" else cat(entry)
            for k, v in entry.items()
            if k in ACCEPTED
        }
        for entry in table
    }

    # data: dict[str, Buff] = {
    #     entry["key"]: {
    #         "key": entry["key"],
    #         "string_key": entry.get("string_key", MISSING_ENTRY),
    #     }
    #     for entry in table
    #     if entry.get("key")
    # }

    file_path = database / "stats.json"

    with open(file_path, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    # data: list[Buff] = [
    #     {
    #         "key": entry["key"],
    #         "string_key": entry.get("string_key", MISSING_ENTRY),
    #     }
    #     for entry in table
    #     if entry.get("key")
    # ]

    data = [
        {
            k: v if k != "stat_type" else cat(entry)
            for k, v in entry.items()
            if k in ACCEPTED
        }
        for entry in table
    ]

    file_path = database / "stats_list.json"

    with open(file_path, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_buff_data(game_path: str, databse: Path):
    pabgb = dmm.extract_file(
        game_dir=game_path,
        group_name="0008",
        dir_path="gamedata/binary__/client/bin",
        file_name="buffinfo.pabgb",
    )

    pabgh = dmm.extract_file(
        game_dir=game_path,
        group_name="0008",
        dir_path="gamedata/binary__/client/bin",
        file_name="buffinfo.pabgh",
    )

    table: list[dict[str, Any]] = dmm.parse_table("buff_info", pabgb, pabgh)

    data: dict[str, Buff] = {
        entry["key"]: {
            "key": entry["key"],
            "string_key": entry.get("string_key", MISSING_ENTRY),
        }
        for entry in table
        if entry.get("key")
    }

    file_path = database / "buffs.json"

    with open(file_path, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    data: list[Buff] = [
        {
            "key": entry["key"],
            "string_key": entry.get("string_key", MISSING_ENTRY),
        }
        for entry in table
        if entry.get("key")
    ]

    file_path = database / "buffs_list.json"

    with open(file_path, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_skill_data(game_path: str, databse: Path):
    pabgb = dmm.extract_file(
        game_dir=game_path,
        group_name="0008",
        dir_path="gamedata/binary__/client/bin",
        file_name="skill.pabgb",
    )

    pabgh = dmm.extract_file(
        game_dir=game_path,
        group_name="0008",
        dir_path="gamedata/binary__/client/bin",
        file_name="skill.pabgh",
    )

    table: list[dict[str, Any]] = dmm.parse_table("skill_info", pabgb, pabgh)

    data: dict[int, Skill] = {
        entry["key"]: {
            "key": entry["key"],
            "string_key": entry.get("string_key", MISSING_ENTRY),
            "internal_name": entry.get("dev_skill_name", MISSING_ENTRY),
            "internal_description": entry.get("dev_skill_desc", MISSING_ENTRY),
            "localized_name": None,
        }
        for entry in table
        if entry.get("key")
    }

    file_path = database / "skills.json"

    with open(file_path, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    data: list[Skill] = [
        {
            "key": entry["key"],
            "string_key": entry.get("string_key", MISSING_ENTRY),
            "internal_name": entry.get("dev_skill_name", MISSING_ENTRY),
            "internal_description": entry.get("dev_skill_desc", MISSING_ENTRY),
            "localized_name": None,
        }
        for entry in table
        if entry.get("key")
    ]

    file_path = database / "skills_list.json"

    with open(file_path, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


game_path = find_game_path()

database = (
    Path(__file__).resolve().parent.parent / "data" / "item_editor_database"
)

try:
    load_buff_data(game_path, database)
except BaseException as e:
    print(f"Error loading buff data!\n{e}")

try:
    load_skill_data(game_path, database)
except BaseException as e:
    print(f"Error loading skill data!\n{e}")

try:
    load_stat_data(game_path, database)
except BaseException as e:
    print(f"Error loading stat data!\n{e}")

print("Database Reloaded.")
