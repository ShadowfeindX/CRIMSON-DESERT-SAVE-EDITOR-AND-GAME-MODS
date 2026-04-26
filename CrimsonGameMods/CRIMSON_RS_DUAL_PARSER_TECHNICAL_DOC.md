# crimson_rs Dual Parser Setup — Technical Documentation for Potter

## TL;DR

CrimsonGameMods ships **two versions of crimson_rs.pyd** side by side.
The current (updated) parser handles the April 2026 game update. The
legacy parser handles pre-update files. Both are needed simultaneously
because community JSON mods were authored against the old format and
we need to translate them to field-name-based semantic edits.

**You don't need to create a new release yet.** What we need is the
housing item fix (see bottom). Once that lands, a tagged release
with the game version it targets would be ideal.

---

## Why two parsers

### The problem

The April 2026 game update added ~10 new fields to `ItemInfo`. Every
community mod on Nexus was built as JSON v2 byte patches against the
**old** `iteminfo.pabgb` (4,837,568 bytes, 6024 items, 105 fields).
These mods are now broken — byte offsets shifted by the new fields.

We built a **legacy JSON translator** that recovers the semantic intent
from these dead byte patches:

1. Parse old vanilla `iteminfo.pabgb` with the **legacy** parser
2. Apply the JSON v2 byte patches to the old raw bytes
3. Re-parse the patched bytes with the **legacy** parser
4. Diff the two parsed results → field-level changes with field names
5. Apply those field-name changes to the **new** `iteminfo.pabgb` using the **current** parser

Step 1-3 require the old parser because the old file has the old field
layout (105 fields). The current parser (115 fields) can't parse the
old file — it expects the new fields and fails with a UTF-8 error
when the byte positions don't line up.

Step 5 requires the current parser because the new file has the new
field layout.

### Compatibility matrix

```
                     Old pabgb (pre-Apr 2026)    New pabgb (post-Apr 2026)
                     4,837,568 bytes              5,357,774 bytes
                     6024 items                   6339 items
                     105 fields                   115 fields
                     ─────────────────────────    ─────────────────────────
Legacy parser        ✓ 6024/6024 (100%)           ✗ FAILS (missing fields)
  (commit dd3c1d3)   

Current parser       ✗ FAILS (extra fields)       ✓ 6331/6339 (99.87%)
  (commit b038c2d)                                 8 housing items fail
```

Neither parser handles both files. That's why we need both.

---

## File layout in CrimsonGameMods

```
CrimsonGameMods/
├── crimson_rs/
│   ├── __init__.py          # Package wrapper (exports enums + re-exports .pyd)
│   ├── crimson_rs.pyd       # CURRENT parser (commit b038c2d + tracked reader)
│   └── _legacy/
│       └── crimson_rs.pyd   # LEGACY parser (commit dd3c1d3)
```

### How they're loaded

The two `.pyd` files cannot coexist in the same Python process via
normal `import` because they share the module name `crimson_rs`. We
load them in separate contexts:

```python
# Current parser — normal import (used everywhere)
import crimson_rs
items = crimson_rs.parse_iteminfo_from_bytes(new_data)

# Legacy parser — isolated import for translator only
import sys, importlib
sys.path.insert(0, 'crimson_rs/_legacy')
legacy_rs = importlib.import_module('crimson_rs')
sys.path.pop(0)
old_items = legacy_rs.parse_iteminfo_from_bytes(old_data)
```

In practice, the legacy parser is only invoked in the Stacker Tool's
JSON translator pipeline. It never touches the game's current files.

---

## What changed between the two parsers

### New fields added to `ItemInfo` (item.rs)

```rust
// After extract_multi_change_info:
pub extract_additional_drop_set_info: u32,    // NEW
pub minimum_extract_enchant_level: u16,       // NEW

// After is_destroy_when_broken:
pub is_housing_only: u8,                      // NEW

// After cooltime:
pub unk_post_cooltime_a: i64,                 // NEW (mirrors cooltime)
pub unk_post_cooltime_b: i64,                 // NEW (mirrors cooltime)

// After item_charge_type:
pub usable_alert_type: u8,                    // NEW (replaces removed usable_alert)

// After max_charged_useable_count:
pub unk_post_max_charged_a: u32,              // NEW (mirrors max_charged)
pub unk_post_max_charged_b: u32,              // NEW (mirrors max_charged)

// After convert_item_info_by_drop_npc:
pub pattern_description_data_list: CArray<PatternDescriptionData<'a>>,  // NEW

// After is_preorder_item:
pub is_has_item_use_data_inventory_buff: u8,  // NEW
pub is_preserved_on_extract: u8,              // NEW
```

### Removed field
- `usable_alert: u8` → replaced by `usable_alert_type: u8` (different position)

### Renamed field
- `unk_texture_path` → `default_texture_path` (same type, same position relative to neighbors)

### New sub-structs (structs.rs)

```rust
// DockingChildData gained:
pub inherit_summoner: u8,
pub summon_tag_name_hash: [u32; 4],   // was [u32; 1] → [u32; 4]

// New struct:
pub struct PatternDescriptionData<'a> {
    pub pattern_description_info: u32,
    pub param_string_list: CArray<CString<'a>>,
}
```

### Field name compatibility

103 of 105 old field names have a **direct 1:1 match** in the new parser.
This means any semantic intent recovered from old JSON mods using old
field names can be applied to new items by field-name lookup. The two
exceptions:

| Old name         | New name              | Action needed     |
|------------------|-----------------------|-------------------|
| `unk_texture_path` | `default_texture_path` | Rename in translator |
| `usable_alert`   | *(removed)*           | Skip — field gone  |

---

## The 8 housing items — what we need from you

Keys: `1003774, 1003823, 1003824, 1003825, 1003976, 1003977, 1003978, 1003979`

These items have **4 u32 fields** after `sharpness_data` instead of 3.
The py_binary_struct macro generates a fixed struct that reads exactly 3:

```rust
pub max_charged_useable_count: u32,
pub unk_post_max_charged_a: u32,
pub unk_post_max_charged_b: u32,
// ← housing items have an extra u32 HERE
pub hackable_character_group_info_list: CArray<CharacterGroupKey>,
```

The extra 4 bytes shift everything after it, and the parser hits a
string field that reads garbage → `parse error at offset 0x00094852:
invalid utf-8 sequence`.

**Hypothesis:** ALL items might actually have 4 u32s here, with
non-housing items having the 4th as `0`. If you add one field:

```rust
pub unk_post_max_charged_c: u32,  // add this
pub hackable_character_group_info_list: CArray<CharacterGroupKey>,
```

...and all 6339 items parse, that confirms the hypothesis and the fix
is one line.

**If the 4th u32 is conditional** (only present when `is_housing_only
== 1`), the macro would need conditional parsing support — bigger change.

### Current workaround

CrimsonGameMods uses PABGH-bounded per-entry parsing. Each item is
parsed individually using the PABGH index to determine entry boundaries.
Housing items that fail are stored as raw bytes and round-tripped
verbatim. They can't be edited but they're never lost.

Parse rate: **6331/6339** (99.87%).

---

## Game version tracking — recommendation

Right now we identify parsers by git commit hash, which is fragile.
A versioning scheme tied to the game version would help:

```
crimson-rs v0.5.0   → game version 1.0.0 / 1.0.1 (pre-Apr 2026)
crimson-rs v0.6.0   → game version 1.0.2+ (post-Apr 2026, new fields)
```

What would help us:

1. **Tag/release the pre-update parser** as e.g. `v0.5.0` so we can
   pin the legacy `.pyd` to a known version.
2. **Tag/release the updated parser** (once housing items are fixed)
   as `v0.6.0`.
3. **Add a `crimson_rs.game_version()` or `crimson_rs.parser_version()`**
   function that returns which game version the parser targets. This lets
   CrimsonGameMods auto-detect which parser to use for a given pabgb file
   instead of hard-coding paths.

The ideal end state: one parser that handles both old and new formats
(maybe via a version flag or auto-detection of field count). But having
tagged releases for each game version is the practical minimum.

---

## Summary for Potter

| Question | Answer |
|----------|--------|
| Do we need two parsers? | Yes, until one parser handles both formats |
| Should you create a new release? | Yes — once housing items are fixed. Tag it with game version |
| What blocks the release? | The 8 housing items (try adding a 4th u32 after unk_post_max_charged_b) |
| What's the PR? | https://github.com/potter420/crimson-rs/pull/1 |
| What game version does the PR target? | Post-April 2026 update (1.0.2+, 6339 items, 115 fields) |

— RicePaddySoftware, 2026-04-23
