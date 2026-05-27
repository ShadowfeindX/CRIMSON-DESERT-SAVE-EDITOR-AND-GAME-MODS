# iteminfo.pabgb Mod Compatibility — Technical Problem Statement

Audience: modders, tool authors, anyone who wants to audit the claims
made in `WHY_WE_PIVOTED.md` against the actual code.

All line references in this document resolve against:
- JMM / JSON Mod Manager decompile at
  `_ilspy_dump_mod_manager/source_v10/CDModManager/` (ILSpy output of a
  public release binary, used for reverse-engineering only).
- CrimsonGameMods: https://github.com/NattKh/CRIMSON-DESERT-SAVE-EDITOR-AND-GAME-MODS/tree/main/CrimsonGameMods (MIT).
- Potter's `crimson_rs` PAZ toolkit (Rust bindings).

---

## 1. The engineering problem

Crimson Desert's primary game data files (`iteminfo.pabgb`,
`skillinfo.pabgb`, `storeinfo.pabgb`, etc.) are tightly packed binary
records — a run of variable-length entries each representing one item /
skill / store definition. There is **no record index inside the data
file itself**. The companion `iteminfo.pabgh` provides an index keyed
by entry name, pointing into the data file.

### 1.1 What "mod" means today

Almost every iteminfo mod on Nexus ships as either:

- a **format:2 JSON** with byte-patch directives:
  ```json
  { "type": "replace", "entry": "Item_X",
    "rel_offset": 266, "original": "00", "patched": "01" }
  ```
- a **compiled folder mod** with its own pre-patched
  `NNNN/0.paz` + `0.pamt` that wholesale replaces vanilla
  `iteminfo.pabgb`.

The JMM loader applies the first kind by walking vanilla bytes and
writing the `patched` bytes at `entry_start + rel_offset` (where
`entry_start` comes from the pabgh index). It applies the second kind
by mounting the mod's PAZ as an overlay.

### 1.2 Where byte-patch mods break

| Failure mode | When it happens | Visible symptom |
|---|---|---|
| **Offset drift across game updates** | Dev team adds a field to `ItemInfo`; every `rel_offset` in every existing mod now points at the wrong field | Silent corruption: patch lands at unintended bytes, game may not crash, behavior subtly wrong |
| **Mods that add entries** | Mod adds a new item, which shifts every following entry's position in the file | Every mod targeting entries after the insertion fails `BYTES-MISMATCH` because `original` doesn't match |
| **Same-region conflicts** | Two mods both patch bytes near each other in the same entry (e.g. both editing the enchant list) | Conflict flagged as "bytes overlap at 0x1AA43D" — no field-level context, user can't tell if the mods are actually semantically incompatible |
| **Compiled mod + JSON patch** | e.g. Super MOD ships a wholesale `iteminfo.pabgb`, user also installs 5 JSON patches that targeted vanilla offsets | JSON patches' `original` bytes don't match Super MOD's replaced bytes; patches skip with `BYTES-MISMATCH`; user loses 100+ edits with no path to recover them |
| **Entry renamed upstream** | Pearl Abyss renames an entry key | Patch fails `NOENTRY` (at least visible); not corruption, but the mod is dead until the author updates it |

These aren't hypotheticals — each has a reproducible case in
`releases/PerfectLoader-v0.2.12/skip.txt` and JMM's own
`releases/.../loader.txt` on the same 25-mod set.

### 1.3 Why this architecture was picked originally

The byte-patch format was a reasonable early-game-life choice: faster
to apply than re-parsing the entire file, smaller JSON diffs for
authors, simpler loader. JMM's author (phorge / Lathiel, credit for
format v1 → v2 → overlay system) has been upfront that v2 format is
"about 95% resilient" to game updates. That's true in the short term.
The 5% failures are exactly the cases that bite users running stacks.

---

## 2. The architectural fix: parse → merge → serialize

Instead of operating on raw bytes, operate on the **parsed structure**.

Primitive: `crimson_rs.parse_iteminfo_from_bytes(bytes) -> list[dict]`
returns one dict per item with every field exposed by name
(`max_stack_count`, `cooltime`, `drop_default_data.use_socket`,
`enchant_data_list[N].level`, etc. — ~100 fields).

Round-trip: `crimson_rs.serialize_iteminfo(list[dict]) -> bytes`
rebuilds a valid `iteminfo.pabgb` from the dict list, sizing each entry
correctly regardless of what fields changed.

Given this primitive, every failure mode above dissolves:

- **Offset drift** — we don't consult offsets at all; we look up fields
  by name. A field moving inside an entry has no effect on our write.
- **Mods adding entries** — merged dict list is just longer; serializer
  writes the correct total size.
- **Same-region conflicts** — replaced with field-level conflicts.
  Two mods setting the same field to different values is an actual
  conflict. Two mods setting different fields is two independent edits
  and both land.
- **Compiled mod + JSON patch** — both get parsed into dict form, both
  get dict-merged; the serialized output carries both contributions.
- **Entry renamed** — still fails cleanly, but with a clear "entry
  not found" message the user can act on.

Cost: parsing and serializing take ~1-3 seconds for full iteminfo
(~5 MB, 6000 entries). JMM authors have cited this cost as a reason
not to adopt the approach. That cost is paid at **install time**, once
per Apply, not at game runtime. The game still loads one overlay PAZ;
nothing changes at boot.

---

## 3. The overlay-ownership problem

Even with the semantic merge in place, there's a second, separate
problem: **JMM deletes overlays it doesn't recognize.**

### 3.1 Evidence from the decompile

`_ilspy_dump_mod_manager/source_v10/CDModManager/ModManager.cs:2485`:

```csharp
private void CleanupStaleOverlayGroups(string papgtBakPath)
{
    HashSet<string> hashSet = File.Exists(papgtBakPath)
        ? ListPapgtGroupNames(papgtBakPath).ToHashSet()
        : new HashSet<string>();
    foreach (string item in Directory.GetDirectories(GameDir)
                             .Select(Path.GetFileName).OrderBy(d => d))
    {
        if (item.All(char.IsDigit) && item.Length != 0 && int.Parse(item) >= 36)
        {
            string path = Path.Combine(GameDir, item);
            if (Directory.Exists(path) && !hashSet.Contains(item))
            {
                Directory.Delete(path, recursive: true);
                Console.WriteLine("  Removed stale overlay: " + item + "/");
            }
        }
    }
}
```

This method runs on every JMM `CmdApply` (see line 3386 in the same
file). It walks every subdirectory of the game dir, and if a directory
has:

- a purely numeric name
- numeric value ≥ 36
- not present in JMM's own `0.papgt.bak` snapshot

…it deletes that directory recursively.

CrimsonGameMods' existing `_buff_export_cdumm_mod` and `_buff_apply_to_game`
paths write overlays in exactly this form (e.g. `0058/`). They are
deleted on the next JMM Apply.

### 3.2 The bidirectional compatibility this breaks

| User state | Outcome |
|---|---|
| Run ItemBuffs Apply only | Works |
| Run JMM Apply only | Works |
| Run ItemBuffs Apply, then JMM Apply | JMM silently deletes ItemBuffs overlay. User thinks ItemBuffs is broken. |
| Run JMM Apply, then ItemBuffs Apply | Both overlays present. ItemBuffs works until the next JMM Apply, then deleted again. |

The net effect: a user can install CrimsonGameMods' mods or JMM's mods,
not both, unless they accept that every JMM Apply re-wipes their
CrimsonGameMods work and re-installing via my tool after every JMM
Apply.

### 3.3 Fixes available to JMM that would close this

The fix on JMM's side would take under an hour for someone with the
repo open. Any of:

1. Add a marker-file check: skip any overlay group that contains a
   file named e.g. `.ownership_<tool_id>` that isn't JMM's marker.
2. Accept a shared state file (`_mod_overlays.json` at the game root)
   where each tool lists its own overlays; cleanup skips any listed.
3. Skip non-numeric group names (they're already outside JMM's own
   naming convention).
4. Simply not delete unknown overlays — warn about them instead.

Any of the four is a drop-in patch. None have been adopted. The author
has stated he does not intend to open-source JMM, which means this
patch can only land if he personally writes it.

### 3.4 The unilateral route

Since CrimsonGameMods is open-source, the fix has to come from my side.
The specific lever JMM's cleanup logic leaves open:

> `item.All(char.IsDigit)` — non-numeric names are ignored.

Stacker Tool (the new CrimsonGameMods tab) writes its overlay under a
non-numeric group name (e.g. `stk1`). The game's PAPGT loader does not
require numeric group names; that's JMM's convention alone. Stacker's
overlay survives JMM's cleanup because JMM's cleanup loop doesn't see
it as a numeric folder.

This doesn't fix the design problem — it works around it. The design
problem is that one tool in the ecosystem unilaterally owns "what's a
legitimate overlay" without a way for other tools to register. The
workaround is stable as long as JMM's cleanup predicate stays
numeric-only. If a future JMM version tightens the predicate (e.g.
"delete anything not in my backup regardless of name"), we'd need a
different approach — but at that point the intent becomes unambiguous
and the community story writes itself.

---

## 4. The Stacker Tool implementation

Source: `CrimsonGameMods/gui/tabs/stacker.py` (~450 lines).

### 4.1 Sources it consumes

| Input type | Detection | Extraction |
|---|---|---|
| Loose `iteminfo.pabgb` | file extension | read bytes |
| Compiled folder mod (`NNNN/0.paz` + `0.pamt`) | directory probe | `crimson_rs.extract_file(mod_dir, group, "gamedata/binary__/client/bin", "iteminfo.pabgb")` |
| Legacy JMM format:2 JSON | JSON contains `patches[].game_file = "gamedata/iteminfo.pabgb"` | apply byte patches to a copy of vanilla bytes, then parse result |
| ItemBuffs tab edits (in-memory) | pull via button | use the dict list directly from `ItemBuffsTab._buff_rust_items` |

All four paths produce a `list[dict]` of parsed items.

### 4.2 Merge

`_merge_all(vanilla_items, [(name, mod_items), …])`:

- Index every mod and vanilla by item's `key` field (the item's dev name).
- For every key present in any mod: compare field-by-field against
  vanilla. Record differences. If multiple mods differ on the same
  field with different values, emit a `FieldConflict` and let the
  last mod in list order win (install-order priority).
- Entries only in mods (new items) get included; entries only in
  vanilla (unchanged) pass through untouched.

Conflict log format: `<entry_key>.<field_path>: <winner_mod>=<value>, <loser_mod>=<value>`.

### 4.3 Output

`crimson_rs.serialize_iteminfo(merged_dicts) → bytes` → pack via
`crimson_rs.PackGroupBuilder(stk1_dir, NONE, NONE).add_file(…).finish()`
→ update `meta/0.papgt` via `crimson_rs.add_papgt_entry`.

Overlay group name: `stk1` (non-numeric, JMM-cleanup-safe).

### 4.4 What it deliberately doesn't do

- **No ASI loader.** Out of scope. ASI mods keep using JMM or manual
  `bin64/` drop.
- **No support for non-iteminfo files.** A future version could absorb
  sequencer / CSS / DDS files from folder mods into the same overlay,
  but that's additive; not required for the core compatibility fix.
- **No attempt to modify JMM's cleanup behavior.** Users can keep
  running JMM for whatever they want; we simply avoid the filename
  pattern JMM cleans up.

---

## 5. What reconciliation would look like

None of this is necessary if the JMM side adopts any of these:

1. Stop deleting non-JMM overlays (or filter by marker/ownership file).
2. Open source the loader so cleanup behavior can be audited and
   patched community-side.
3. Adopt a shared overlay-registry convention: each tool writes to a
   common state file listing its overlays; JMM respects entries it
   didn't write.

Any of the three eliminates the need for the non-numeric-name trick.
The semantic merge work in Stacker Tool stands on its own merits
regardless.

For now: unilateral fix via naming, dict-level merge for compatibility,
format-compat emitters / parsers so mod authors' existing workflows
continue to work in both directions.

---

## 6. Open questions

If you're a modder reading this and want to push on the semantic-merge
approach further:

- **Schema coverage beyond iteminfo.** The parse/serialize round-trip
  currently exists in `crimson_rs` for iteminfo only. skillinfo,
  buffinfo, storeinfo, characterinfo have similar PABGB layouts but
  need their own Rust structs. This is mechanical work; each one
  unlocks another class of stacking mods.
- **Semantic JSON authoring format.** `MODDER_HOWTO.md` sketches a
  `format:3` JSON that describes intents field-by-field
  (`{"entry":"X", "field":"max_stack_count", "op":"set", "new":9999}`).
  Stacker Tool could consume this natively; authors gain version
  resilience for free. No one is authoring in this yet because no
  loader consumes it — chicken and egg, which Stacker breaks.
- **Conflict UI.** Currently install-order-wins with a log. A UI that
  lets users flip individual field conflicts would be straightforward
  (the data's already in the `FieldConflict` struct).

---

## 7. TL;DR

The current ecosystem's mod format is a byte-patch format against
unstable offsets, enforced by a closed-source loader that deletes
external tools' output. This works adequately for 1-3 simple mods,
degrades visibly at 10+ mods, and forces users to pick which tool owns
their game install.

The engineering fix is simple: parse, merge in dict form, serialize.
The ecosystem fix requires either loader-side cooperation or a name
that sidesteps the cleanup. Stacker Tool does the first unilaterally
and chooses a name that sidesteps the second.

This document exists because I want the reasoning for that pivot to be
inspectable in public, not described secondhand in Discord.
