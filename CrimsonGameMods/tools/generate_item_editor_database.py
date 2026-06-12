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

    data: list[Buff] = [
        {
            entry["key"]: {
                "key": entry["key"],
                "string_key": entry.get("string_key", MISSING_ENTRY),
            }
        }
        for entry in table
        if entry.get("key")
    ]

    file_path = database / "buffs.json"

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

    data: list[Skill] = [
        {
            entry["key"]: {
                "key": entry["key"],
                "string_key": entry.get("string_key", MISSING_ENTRY),
                "internal_name": entry.get("dev_skill_name", MISSING_ENTRY),
                "internal_description": entry.get(
                    "dev_skill_desc", MISSING_ENTRY
                ),
                "localized_name": None,
            }
        }
        for entry in table
        if entry.get("key")
    ]

    file_path = database / "skills.json"

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

print("Database Reloaded.")