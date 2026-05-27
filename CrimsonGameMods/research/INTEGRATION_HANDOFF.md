# Integration Handoff — `rebase_helper` + PAPGT Cooperation Notes

An open letter to the JMM maintainer. If you want to pick up any of
this — partially, fully, or not at all — the code and notes below are
yours to use. No attribution required beyond a credit line if you
feel like it. No lock-in, no licensing conversation needed — it's
already in your hands.

I'm going to keep building my own parallel tool (Stacker Tool inside
CrimsonGameMods) because I need a path that doesn't depend on anyone
else's schedule. But if you want to close the gap on your side too, so
users stop being forced to pick a camp, this document tells you
exactly where to plug things in.

---



Location: the folder I handed over —
`PerfectLoaderCS/rebase_helper/` — two files, ~1,840 lines of working
Python.

### `rebase_helper.py` (~890 lines)

Entry points you'd actually call:

| Function | Line | What it does |
|---|---|---|
| `build_entry_map(pabgb, pabgh)` | 188 | Same shape as your `PabgbParser.BuildEntryMap`. Returns `{entry_name: (entry_offset, blob_start)}`. |
| `apply_replaces(pabgb, replaces)` | 124 | Your existing byte-replace loop, but wrapped as a clean function. Returns applied count + skip reasons. |
| `apply_inserts_with_pabgh_fixup(...)` | 140 | Handles inserts that grow the pabgb — walks the pabgh and rewrites entry offsets for everything past the insertion. This is the piece byte-patch loaders silently miss. |
| `build_entry_map(pabgb, pabgh)` | 188 | Drop-in replacement for your current entry map if you want to harden it against schema drift. |
| `diff_items(vanilla, modded)` | 271 | Given two parsed dict lists, emits the set of field-level intents. Used to compile a byte mod into semantic form automatically. |
| `merge_intents(mods)` | 311 | N mods → single merged intent list + conflict report. This is the core of the stacking fix. |
| `apply_intents(items, intents)` | 350 | Apply a merged intent list to a fresh parsed vanilla. Mutates in place. |
| `cmd_merge` (CLI) | 379 | Reference wiring: how all of the above compose into a full mod-merge pipeline. |

### `iteminfo_schema.py` (~950 lines)

The field catalog for `ItemInfo`, machine-readable, plus a binary
walker:

| Piece | Line | What it does |
|---|---|---|
| `ITEM_INFO` top-level spec | 259 | Every field in ItemInfo with its type and nesting. Used by the walker. |
| `Walker` class | 372 | Stateful binary reader that produces `[{path, type, rel_offset, value}, …]` for a given entry blob. |
| `walk_entry(buf, entry_start, spec)` | 515 | Convenience wrapper — one entry in, field list out. |
| `offset_to_field(fields, rel_offset)` | 527 | Given a byte patch's `rel_offset`, tell me which named field it targets. Inverse of patch resolution. |
| `compile_intent(...)` | 569 | Take a byte patch (your `format:2` JSON entry), walk the entry, identify which field it targets, emit a semantic intent. One-shot upgrader. |
| `apply_intents_to_items(items, intents)` | 789 | Apply intents to parsed dicts. |
| `_split_cross_field_patch(...)` | 817 | Handles byte patches that span multiple adjacent fields. |

Both files are self-contained Python — no runtime deps beyond stdlib
and `crimson_rs` for the parse/serialize boundary (which you already
use).

---

## How you'd integrate it, if you want to

Three integration levels, each smaller than the last. Pick what fits.

### Level 1: Drop-in replacement for your stacking path

Inside your `CmdApply`, where you currently walk patches and call
byte-replace: instead, for mods touching `iteminfo.pabgb`:

```text
for each JSON mod M targeting iteminfo.pabgb:
    compile M's byte patches → semantic intents via iteminfo_schema.compile_intent
merge all intents via rebase_helper.merge_intents  → (merged, conflicts)
apply merged intents to fresh parsed vanilla via rebase_helper.apply_intents
serialize → write overlay
```

That's it. You keep your overlay-write path, your PAPGT surgery, your
file-index scan. You swap the *iteminfo patching inner loop* for the
semantic one. The rest of your loader doesn't need to change.

Expected effect on the stacking test set (my `faillogs.txt` vs the
good `loader.txt` I shared):

- The 142 `BYTES-MISMATCH` skips on Super MOD + JSON stack → drop to
  the 3 real conflicts (Super MOD and Double_Abyss_Gear_Effect
  overwriting the same bytes, which is a genuine same-field conflict).
- Mods that add entries stop shifting other mods' rel_offsets by
  hundreds of bytes — because nothing looks at absolute offsets after
  compile.
- `Accessory & Cloak Sockets` stops silently failing on its insert
  patches, because `apply_inserts_with_pabgh_fixup` already rewrites
  the pabgh entry index after insertion (which the current byte
  pipeline does manually and sometimes wrong).

### Level 2: Just the intent merge

If touching your byte-patch path feels invasive, just run the semantic
merge on the mod set *before* your byte pipeline runs. Produce an
"effective iteminfo.pabgb" with the merge baked in, then let your
existing byte pipeline apply any remaining intents. This is additive
— it won't break anything you have that works.

```text
for each mod M:
    produce M's effective iteminfo (parse mod or apply its byte patches)
merge all effective iteminfos via rebase_helper.merge_intents
produce one rebased pabgb from the merge
feed that to your existing overlay write path
```

### Level 3: Just borrow the schema

If you don't want to run Python in your pipeline at all: the
`ITEM_INFO` spec in `iteminfo_schema.py` (line 259) is a pure data
description. Translate it to C# once. From there you can write the
same walker/compiler/merger in C# with about the same line count as
the Python. The 950 lines of schema + walker is the actual reverse
engineering work I already did — that's the part that took time. The
C# rewrite from there is mechanical.

---

## On extending PAPGT cleanup to coexist with external tools

Separate question from the semantic merge. Independent of whether you
adopt `rebase_helper`. This is just about the overlay-deletion
behavior in `CleanupStaleOverlayGroups` at
`ModManager.cs:2485` (v10 build).

Three options, simplest first, so you can pick based on how much you
feel like doing:

### Option A — one-line predicate tighten

Current predicate deletes any numeric overlay directory ≥ 36 that's
not in your `.bak`. Non-numeric names already escape the check. If
you just *document* that as the extension point, any external tool
(including my Stacker Tool which uses `stk1`) can rely on it
indefinitely. Zero code change. One line of docs.

### Option B — marker-file opt-out

Before deleting an overlay group, check if the group dir contains a
file named `.managed_by_external` (or any convention you pick). If
yes, skip. That's maybe five lines inside the existing foreach:

```csharp
if (File.Exists(Path.Combine(path, ".managed_by_external")))
{
    Console.WriteLine("  Kept externally-managed overlay: " + item + "/");
    continue;
}
```

External tools drop the marker when they write their overlay; you
respect it. No handshake required, no shared state file, no registry.

### Option C — shared registry file

A JSON file at `<game>/_mod_overlays.json` where each tool lists its
owned groups. Something like:

```json
{
  "managed_groups": {
    "stk1":  {"owner": "CrimsonGameMods.Stacker"},
    "cgm2":  {"owner": "CrimsonGameMods.ItemBuffs"}
  }
}
```

Your cleanup consults this file too; anything listed is skipped.
Tools write their entries when they create an overlay, clean them up
when they remove it. More structured than the marker, lets you show
users "here's who owns what" in your UI if you ever want to.

Any of the three unblocks the ecosystem. If Option A sits fine with
you (literally zero change), that's enough for me and I'll keep
Stacker pinned to non-numeric names.

---

## How a PAPGT change lets my Apply-to-Game work with your loader

Right now:

```
User clicks ItemBuffs "Apply to Game"  →  writes 0058/0.paz + papgt entry
User clicks your JMM Apply             →  CleanupStaleOverlayGroups wipes 0058/
User launches game                     →  ItemBuffs edits missing
```

With Option A (and my current non-numeric-name fix on my side):

```
User clicks ItemBuffs "Apply to Game"  →  writes stk1/0.paz + papgt entry
User clicks your JMM Apply             →  "stk1" fails numeric check, skipped
User launches game                     →  both sets of mods live
```

With Option B (marker file):

```
ItemBuffs writes 0058/0.paz + 0058/.managed_by_external
JMM Apply sees the marker, skips deletion
Game loads both
```

Either way, the user's "do I use CrimsonGameMods OR JMM" forced
choice goes away. Users who use one only see no change. Users who use
both stop getting overlays wiped.

---

## What I'm building on my side regardless

Stacker Tool in CrimsonGameMods. Inside
`gui/tabs/stacker.py`, ~580 lines, one tab.

What it does:
- Drag N iteminfo mods in (compiled folder mods, loose pabgb, legacy
  JMM format:2 JSONs, ItemBuffs in-memory edits — all four).
- Dict-merge them against vanilla via `crimson_rs.parse_iteminfo_from_bytes`
  + field-level resolution.
- Serialize via `crimson_rs.serialize_iteminfo` (rebuilds correct
  sizes regardless of inserts/deletes).
- Update your modify `meta/0.papgt` with our entry.

What it deliberately isn't:
- Not a mod manager. No profile UI, no ASI support, no UI-file
  file-replacement handling. Your manager keeps doing that stuff; I'm
  not trying to compete on the features you already handle well.
- Not a fork of your loader. Doesn't decompile, doesn't redistribute,
  doesn't share binary code. Just reads the `format:2` JSON spec
  (public, shipped on Nexus by every mod author) and emits overlays
  in the PAZ format that's the game's public contract.

---

None of this is a demand. None of it is conditional. The Stacker
Tool ships either way. 

