# iteminfo.pabgb — Complete Index Dump

**Source:** vanilla `iteminfo.pabgb` from `0008/0.paz`
(4,837,568 bytes / 6,024 items / 105 top-level fields per item)

**Generated:** 2026-04-15 18:20:59

**Generator:** `tools/dump_iteminfo.py` — uses Potter's `crimson_rs.parse_iteminfo_from_bytes`
(byte-perfect lossless roundtrip verified).

## Files

| File | Bytes |
|---|---:|
| `by_category.json` | 72,069 |
| `by_equip_type.json` | 36,895 |
| `by_inventory.json` | 70,564 |
| `by_item_type.json` | 71,499 |
| `by_string_key.json` | 233,713 |
| `by_tier.json` | 37,892 |
| `enum_catalogs.json` | 3,640 |
| `field_summary.json` | 93,311 |
| `has_field.json` | 131,245 |
| `items.jsonl` | 27,857,855 |

## How to query

```python
import json

# Full dump — stream line-by-line (one item per line)
with open("items.jsonl", encoding="utf-8") as fh:
    for line in fh:
        item = json.loads(line)
        if "Bow" in item["string_key"]:
            print(item["key"], item["string_key"])

# Lookup by string_key → integer key
sk_index = json.load(open("by_string_key.json", encoding="utf-8"))
hwando_key = sk_index["Hwando_TwoHandSword"]

# All items in a category
cat = json.load(open("by_category.json", encoding="utf-8"))
all_swords = cat["202"]   # category_info=202 = TwoHandSword

# Which items have a field set
hf = json.load(open("has_field.json", encoding="utf-8"))
items_with_passives = hf["equip_passive_skill_list"]
items_with_dye = hf["is_dyeable"]
```

## Field reference

For per-field types (u8/u32/i64/etc) and the hash table each key references,
read Potter's type stub:

```
C:\Users\Coding\AppData\Roaming\Python\Python314\site-packages\crimson_rs\__init__.pyi
```

39 TypedDicts cover every nested struct with field-level docstrings.

## Pretty samples

`samples/` has six items dumped in indented JSON for human reading:
- `1000080_Hwando_TwoHandSword.json`
- `1000082_Troopers_TwoHandSpear.json`
- `1003265_GreyWolf_OneHandBow.json`
- `391518535_Toad_AccessoryRing.json` (Oath of Darkness — godmode template)
- `1003289_Hernandian_Stirrup.json`
- `1000382_Plate Boots of the Shadows`

## Regenerating

When the game updates iteminfo.pabgb, re-run:

```bash
cd CrimsonGameMods
python tools/dump_iteminfo.py
```

Output overwrites in place.
