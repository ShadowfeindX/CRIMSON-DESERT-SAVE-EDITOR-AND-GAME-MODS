# Stacker × ItemBuffs Integration — What Changed

This document summarizes the code changes that make the Stacker Tool
capture ALL ItemBuffs tab features (not just dict-level edits) when
the user clicks "Pull from ItemBuffs tab."

Companion to `ITEMBUFFS_FEATURE_AUDIT.md` (the problem statement).

---

## What was broken before this change

Pulling from ItemBuffs captured only `self._buff_rust_items` — the
dict-level edits. Everything else ItemBuffs does when *it* clicks
Apply (buffs_v319.py:9770) was silently dropped by Stacker:

- Max Stacks / Infinite Durability toggles (only applied at Apply-time)
- Cooldown byte patches (`_cd_patches`)
- Transmog visual swaps (`_transmog_swaps`)
- VFX changes — size, swaps, anims, attach points
- Staged skill.pabgb / skill.pabgh files for passive-skill bundling
- Staged equipslotinfo.pabgb / equipslotinfo.pabgh for Universal Proficiency

Result: an ItemBuffs user who Pulled into Stacker got the dict edits
but lost the rest. Universal Proficiency v2 landed partially (tribe
edits in dict but equipslotinfo not staged → equip gates still closed
→ feature dead in-game). No-Cooldown-All-Items reverted to vanilla.
Transmog swaps had no visible effect.

---

## What changed

### 1. `ModEntry` dataclass — four buckets now captured

```python
@dataclass
class ModEntry:
    # …existing fields…
    # Bucket B — checkbox toggles
    apply_stacks: Optional[int] = None
    apply_inf_dura: bool = False
    # Bucket C — post-serialize byte patches
    cd_patches: dict = field(default_factory=dict)
    transmog_swaps: list = field(default_factory=list)
    vfx_size_changes: list = field(default_factory=list)
    vfx_swaps: list = field(default_factory=list)
    vfx_anim_swaps: list = field(default_factory=list)
    vfx_attach_changes: list = field(default_factory=list)
    # Bucket D — sibling files bundled alongside iteminfo in the overlay
    staged_skill_files: dict = field(default_factory=dict)
    staged_equip_files: dict = field(default_factory=dict)
```

External mod sources (folder_paz / loose_pabgb / legacy_json) don't
populate any of these — they only carry dict-level edits. ItemBuffs
pulls populate all four buckets.

### 2. `_pull_from_itembuffs` — deep-copies all state

Every Pull click now:

- Deep-copies `_buff_rust_items` → Bucket A
- Reads `_stack_check.isChecked()` + `_stack_spin.value()` → Bucket B (stacks)
- Reads `_inf_dura_check.isChecked()` → Bucket B (inf durability)
- Deep-copies `_cd_patches`, `_transmog_swaps`, `_vfx_*` lists → Bucket C
- Shallow-copies `_staged_skill_files`, `_staged_equip_files` dicts → Bucket D (bytes are immutable so shallow is safe)
- Builds a human-readable summary shown in the Sources table note

The Sources table entry now reads like:

    ItemBuffs tab (current edits)  |  itembuffs_edits  |
    6024 entries; stacks→9999; inf-dura; 12 cooldown patches;
    3 transmog swaps; 47 VFX changes; equipslotinfo bundle (2 files)

### 3. `_run_inner` — applies Bucket B before serialize, Bucket C after

Matches the ordering in `buffs_v319.py:9821-9879`:

```text
for each itembuffs source:
    apply Max Stacks → merged_items[*].max_stack_count
    apply Inf Durability → merged_items[*].max_endurance, is_destroy_when_broken
crimson_rs.serialize_iteminfo(merged_items) → bytes
call _apply_bucket_c(bytes, sources) →
    apply VFX changes (temp-swap ItemBuffs state, call _apply_vfx_changes)
    apply cooldown patches (use ItemBuffs._cd_detect to resolve offsets in merged bytes)
    apply transmog swaps (temp-swap, call _apply_transmog_swaps)
call _collect_bucket_d(sources) → sibling file dict
pack overlay with iteminfo + sibling files
```

### 4. Multi-source coalescing rules

When multiple sources contribute to the same bucket:

| Bucket | Coalesce rule |
|---|---|
| B — Max Stacks | Highest target wins across sources (user probably wants more permissive) |
| B — Inf Durability | OR — if any source enables, merged output enables |
| C — VFX changes | Lists concatenated; `_apply_vfx_changes` naturally last-writer-wins per item via sequential writes |
| C — Cooldown patches | Keyed by item_key; last source wins; conflicts logged per-item |
| C — Transmog swaps | Lists concatenated; `_apply_transmog_swaps` last-writer-wins per item |
| D — Sibling files | Keyed by filename (skill.pabgb, equipslotinfo.pabgb, etc.); last source wins; conflicts logged per-file |

### 5. Pack methods accept sibling files

Both install paths (`_pack_and_install_overlay` for direct game write,
`_pack_as_folder_mod` for Export) now accept `sibling_files: dict`
and add every entry into the same overlay PAZ alongside iteminfo.

Export README.txt and modinfo.json now list bundled files explicitly
so users installing through JMM know what's in the pack.

---

## Verification performed

- Syntax: `ast.parse(stacker.py)` + `ast.parse(main_window.py)` — clean.
- Headless import of `StackerTab`, `ModEntry`, `_classify`, `_merge_all`,
  `_apply_legacy_json`, `OVERLAY_GROUP_DEFAULT` under `QT_QPA_PLATFORM=offscreen`.
- ModEntry field inventory: all 19 fields present including 10 new bucket fields.
- ModEntry instantiation with defaults (external mod) and populated (ItemBuffs snapshot) — field access correct.
- `stk1` group name round-trips through `crimson_rs.parse_papgt_file`
  → `add_papgt_entry` → `write_papgt_file` → re-parse (verified earlier).

---

## What's still not verified

- End-to-end run on a real game: user clicks Pull, sees the summary,
  clicks Export, gets a folder mod with iteminfo + equipslotinfo
  bundled, installs through JMM, game launches with UP v2 working.
  This needs a human-in-the-loop test because it requires a running
  ItemBuffs session with actual UP v2 state.
- The multi-source Bucket C coalesce on real game data (currently only
  verified via dataclass instantiation tests).

If either fails, the symptom will be visible in the Stacker log pane:

- UP v2 not working → check log for `Sibling files for overlay: ...`
  line. If equipslotinfo files aren't listed, Bucket D capture failed.
- Cooldowns not working → check log for `Cooldown patches: N/M applied`.
  If M > 0 but N is 0, `_cd_detect` can't find offsets (probably a
  serialization order issue; offsets shifted from what ItemBuffs saw).
- Transmog not visible → check log for `Transmog: N byte patches for M
  swap(s)`. If M > 0 but N is 0, same offset-shift problem as cooldowns.

---

## How to reason about future features

The pattern to extend coverage to new ItemBuffs features:

1. **Identify the bucket.** Does the feature write to `_buff_rust_items`
   (A), set a checkbox state applied at Apply time (B), apply byte
   patches post-serialize (C), or bundle a sibling file (D)?

2. **Extend Pull.** Add the corresponding snapshot capture in
   `_pull_from_itembuffs`. Deep-copy for mutable state.

3. **Extend apply.** A: automatic via dict merge. B: add to
   `_run_inner`'s pre-serialize loop. C: add to `_apply_bucket_c`.
   D: add filename to the recognized set in `_collect_bucket_d`.

4. **Update status summary.** Add a human-readable token to the
   `summary_bits` list in `_pull_from_itembuffs` so the user sees
   their new feature was captured.

5. **Document in the audit matrix.** Add a row to
   `ITEMBUFFS_FEATURE_AUDIT.md` with method name, line number, and
   which bucket it uses.

---

## Test path (next time you have the machine)

1. Launch CrimsonGameMods.
2. Open ItemBuffs tab → Extract (Rust) → make varied edits:
   - Check Max Stacks = 9999, check Infinite Durability
   - Apply Universal Proficiency v2 (stages equipslotinfo)
   - Add a few passive skills (may stage skill.pabgb/pabgh)
   - Apply No Cooldown to one item (adds to `_cd_patches`)
   - Do a transmog swap if you have meshes
3. Switch to Stacker Tool.
4. Click **Pull from ItemBuffs tab**.
5. Check the Sources table — the ItemBuffs row's status should list:
   entry count, `stacks→9999`, `inf-dura`, cooldown count if any,
   transmog count if any, `equipslotinfo bundle (2 files)` if UP v2
   staged them, `skill bundle (N files)` if passives staged.
6. Optionally drag in external mods (Super MOD, Accessory Sockets JSON, etc.)
7. Click **Preview Merge**. Check the log pane. Should show Bucket B
   actions, merge stats, serialize size, Bucket C actions, Bucket D
   sibling file list.
8. Click **Export as Folder Mod**. Pick output location. Verify the
   exported folder has `modinfo.json` listing bundled files, README.txt
   explaining them, and `0036/0.paz` + `0036/0.pamt`.
9. Install that folder through JMM. Apply. Launch game.
10. Verify in-game: stacks at 9999, items indestructible, UP v2 equip
    slots open, cooldowns zero, transmogs visible.

If anything is off, the log pane captures which bucket didn't capture.

---

## Known non-goals

- This change does NOT support pulling from ItemBuffs while the user
  is mid-edit on something complex like the VFX Lab dialog — the
  snapshot captures whatever state is committed at the moment of
  Pull. If VFX Lab is open and has unsaved changes, Pull won't see
  them.
- Repeatedly clicking Pull replaces the prior snapshot (intentional,
  avoids double-counting). User has to re-pull if they edit after.
- Non-iteminfo external mods (UI CSS, sequencer, DDS textures) are
  still out of scope. Those mods remain usable via JMM or any other
  loader; Stacker just doesn't include them in its overlay.
