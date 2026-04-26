# ItemBuffs → Stacker Tool Feature Audit

Exhaustive list of every ItemBuffs tab feature that modifies iteminfo.pabgb
(or bundles sibling files into the same overlay), how each is stored in
memory, and whether Stacker's current Pull captures it.

Sources audited:
- `gui/tabs/buffs_v319.py` (10,703 lines)
- `_buff_apply_to_game` at line 9770 (the canonical apply path — anything
  it consumes is in-scope for Stacker)
- `_buff_export_cdumm_mod` at line 7428 (secondary path — same state surface)

---

## The 4 buckets of state

Every modification funnels into one of four storage buckets. Stacker's
current `Pull from ItemBuffs` only captures Bucket A. The other three
are silently dropped.

### Bucket A — Dict-level edits in `self._buff_rust_items`

Modifications that edit the parsed dict tree in memory. When
`crimson_rs.serialize_iteminfo(items)` runs, these become part of the
output bytes.

**Stacker captures this:** ✅ (via `_buff_rust_items` snapshot on Pull)

### Bucket B — Checkbox toggles applied at Apply-time

`_stack_check` + `_stack_spin`, and `_inf_dura_check`. These only mutate
`_buff_rust_items` *at the moment the user clicks Apply to Game* — before
that, the dict still has vanilla values.

**Stacker captures this:** ⚠️ PARTIAL — only if user clicked Apply in ItemBuffs before pulling

### Bucket C — Post-serialize byte patches

Patches applied to the serialized bytes AFTER `serialize_iteminfo`. They
don't exist in the dict form at all.

**Stacker captures this:** ❌ MISSING

### Bucket D — Sibling files bundled into the overlay

Non-iteminfo files (skill.pabgb, equipslotinfo.pabgb) that ItemBuffs
packs into the same overlay PAZ as iteminfo.

**Stacker captures this:** ❌ MISSING

---

## Complete feature × bucket matrix

### Bucket A — Dict-level (captured)

| Feature | Method | Line | What it writes to dict |
|---|---|---|---|
| Apply passive (single item) | `_eb_apply` | 2858 | `equip_passive_skill_list` on selected items |
| Remove passive | `_eb_remove_passive` | 4663 | removes from `equip_passive_skill_list` |
| God Mode (bulk passive injection) | `_eb_god_mode` | 4693 | adds passives to all equipment |
| Copy effect to another item | `_eb_copy_effect` | 4887 | copies enchants/passives/gimmicks |
| Add enchant stat | `_eb_add_stat` | 2918 | `enchant_data_list[N].enchant_stat_data.max_stat_list` |
| Remove enchant stat | `_eb_remove_stat` | 2969 | removes from enchant stat list |
| Add enchant buff | `_eb_add_buff` | 6766 | `enchant_data_list[N].equip_buffs` |
| Remove enchant buff | `_eb_remove_buff` | 6818 | removes buff from enchant list |
| Apply preset (dev ring) | `_eb_apply_preset` | 5154 | bulk enchants/stats from preset JSON |
| Apply dev preset | `_eb_apply_dev_preset` | 6996 | dev ring buffs |
| Extend sockets (single item) | `_eb_extend_sockets` | 5306 | `drop_default_data.use_socket` + `socket_valid_count` |
| Extend all sockets to 5 | `_eb_extend_all_sockets_to_5` | 5357 | bulk socket extension |
| Add imbue to selected | `_eb_add_imbue_to_selected` | 5416 | enchant list additions |
| Bulk buffs on weapons | `_eb_bulk_apply_buffs_to_weapons` | 5593 | bulk weapon enchant buffs |
| Bulk imbue all weapons | `_eb_bulk_imbue_all_weapons` | 5718 | bulk weapon imbue |
| Bulk make dyeable | `_eb_bulk_make_dyeable` | 6291 | `is_dyeable=1` + `is_editable_grime=1` |
| Universal Proficiency v1 | `_eb_universal_proficiency` | 5978 | tribe_gender edits in dict (plus Bucket D) |
| Universal Proficiency v2 | `_eb_universal_proficiency_v2` | 6119 | tribe_gender edits in dict (plus Bucket D) |
| Apply VFX gimmick | `_eb_apply_vfx_gimmick` | 5246 | `gimmick_info` injection |
| Enable all QoL | `_eb_enable_all_qol` | 8070 | bulk QoL flags |
| Enable everything (one-click) | `_eb_enable_everything_oneclick` | 8311 | bulk preset |
| Apply to Selected (context menu) | `_buff_apply_to_selected` | 8609 | applies current stats to selection |
| Add to Item (context menu) | `_buff_add_to_item` | 8678 | merges edits into item |
| Remove all buffs | `_buff_remove_all` | 8858 | clears enchant lists |
| Max stacks (button/context) | `_buff_max_stacks` | 8999 | sets `max_stack_count` |

### Bucket B — Checkbox toggles (partial capture)

| Feature | Widget | Line | What it does at Apply-time |
|---|---|---|---|
| Max Stacks toggle | `_stack_check` + `_stack_spin` | 1549 / 1557 | Sets `max_stack_count = stack_spin.value()` on all items where `max_stack_count > 1`, only at Apply/Export time |
| Infinite Durability toggle | `_inf_dura_check` | 1569 | Sets `max_endurance = 65535` + `is_destroy_when_broken = 0` on all items with `max_endurance > 0`, only at Apply/Export time |

**Problem:** these are only transferred into `_buff_rust_items` when user clicks Apply or Export inside ItemBuffs. If they just click Pull in Stacker, the toggles are ignored.

### Bucket C — Post-serialize byte patches (NOT captured)

| Feature | Storage attribute | Line defined | Applied at |
|---|---|---|---|
| Cooldown patches | `_cd_patches: dict` | 375 | 9851 (`_buff_apply_to_game`) |
| Transmog (visual swap) | `_transmog_swaps: list` | 624 | 3176 (`_apply_transmog_swaps`) |
| VFX size scale | `_vfx_size_changes: list` | 626 | 3203 (`_apply_vfx_changes`) |
| VFX / trail swaps | `_vfx_swaps: list` | 627 | 3203 |
| Animation swaps | `_vfx_anim_swaps: list` | 628 | 3203 |
| Attach-point changes | `_vfx_attach_changes: list` | 629 | 3203 |

**These apply AFTER `serialize_iteminfo` in `_buff_apply_to_game`:**

```python
final_data = bytearray(crimson_rs.serialize_iteminfo(self._buff_rust_items))  # bucket A
self._apply_vfx_changes(final_data)                                             # bucket C (vfx)
# cooldown byte patches                                                          # bucket C (cd)
for item_key, (_, _, new_val) in cd_patches.items():
    cd_off, _ = self._cd_detect(item_key, bytes(final_data))
    if cd_off is not None:
        final_data[cd_off:cd_off + 4] = struct.pack('<I', new_val)
self._apply_transmog_swaps(final_data)                                          # bucket C (transmog)
```

Stacker's merge path runs `serialize_iteminfo` and packs. It never runs
the equivalent post-serialize byte patches, so Bucket C edits vanish.

### Bucket D — Sibling files (NOT captured)

| File | Storage attribute | Line defined | Generated by |
|---|---|---|---|
| `skill.pabgb` | `_staged_skill_files["skill.pabgb"]` | 2017 | Passive-skill-dependent features (god mode chains, skill injection) |
| `skill.pabgh` | `_staged_skill_files["skill.pabgh"]` | 2017 | Companion to skill.pabgb |
| `equipslotinfo.pabgb` | `_staged_equip_files["equipslotinfo.pabgb"]` | 1999 | Universal Proficiency v1/v2 (to open equip-slot gates) |
| `equipslotinfo.pabgh` | `_staged_equip_files["equipslotinfo.pabgh"]` | 1999 | Companion to equipslotinfo.pabgb |

**These are bundled into the overlay PAZ in `_buff_apply_to_game`:**

```python
builder.add_file(INTERNAL_DIR, "iteminfo.pabgb", final_data)

staged_skill = getattr(self, "_staged_skill_files", None) or {}
for fname in ("skill.pabgb", "skill.pabgh"):
    if fname in staged_skill:
        builder.add_file(INTERNAL_DIR, fname, staged_skill[fname])

staged_equip = getattr(self, "_staged_equip_files", None) or {}
for fname in ("equipslotinfo.pabgb", "equipslotinfo.pabgh"):
    if fname in staged_equip:
        builder.add_file(INTERNAL_DIR, fname, staged_equip[fname])
```

Stacker's `_pack_and_install_overlay` and `_pack_as_folder_mod` only
add iteminfo.pabgb. A Universal Proficiency v2 user who pulls from
ItemBuffs today gets iteminfo merged but NO equipslotinfo override,
which means UP v2's tribe_gender equipment gates aren't opened and
the whole feature fails in-game.

---

## Effect on real user scenarios

### Scenario: "I enable Max Stacks + Infinite Durability in ItemBuffs, then Pull into Stacker"

Without fix: Stacker sees the dict as vanilla. Final overlay has no
stack changes, no durability changes. User thinks Stacker is broken.

### Scenario: "I apply Universal Proficiency v2 + 20 passive skills, then Pull"

Without fix: Stacker captures the passive-skill dict edits (Bucket A).
Stacker does NOT capture the staged equipslotinfo.pabgb. Output: UP v2
is partially applied — dict says Kliff can equip dagger, but
equipslotinfo still gates him out. Game ignores the feature.

### Scenario: "I apply transmog swaps + merge 5 Nexus mods"

Without fix: Stacker captures Nexus mods' dict edits + ItemBuffs' dict
edits. Transmog byte patches (Bucket C) are silently dropped. User's
weapons look vanilla in-game despite the UI showing transmog applied.

### Scenario: "No Cooldown on all items via ItemBuffs + merge"

Without fix: Stacker has no knowledge of `_cd_patches`. Cooldowns
revert to vanilla.

---

## Required Stacker changes

### 1. Extend `ModEntry` to carry all 4 buckets

```python
@dataclass
class ModEntry:
    name: str
    path: str
    kind: str                # adds "itembuffs_edits"
    group: str = ""
    ok: bool = True
    note: str = ""
    effective_pabgb: Optional[bytes] = None
    parsed_items: Optional[list] = None
    # Bucket B
    apply_stacks: Optional[int] = None       # target value or None
    apply_inf_dura: bool = False
    # Bucket C
    cd_patches: dict = field(default_factory=dict)
    transmog_swaps: list = field(default_factory=list)
    vfx_size_changes: list = field(default_factory=list)
    vfx_swaps: list = field(default_factory=list)
    vfx_anim_swaps: list = field(default_factory=list)
    vfx_attach_changes: list = field(default_factory=list)
    # Bucket D
    staged_skill_files: dict = field(default_factory=dict)
    staged_equip_files: dict = field(default_factory=dict)
    apply_stats: str = ""
```

### 2. Extend `_pull_from_itembuffs` to snapshot all of it

Add snapshots of every attribute above. Deep-copy lists/dicts so later
ItemBuffs edits don't mutate the captured state.

### 3. At merge+serialize time, apply Bucket B & C in correct order

After the dict merge + serialize, replicate ItemBuffs's post-serialize
logic:
1. Apply stack/dura toggles to the merged dict BEFORE serialize (not after)
2. Serialize
3. Apply VFX changes to bytes
4. Apply cooldown byte patches to bytes
5. Apply transmog byte patches to bytes

### 4. At pack-overlay time, include Bucket D sibling files

Add `staged_skill_files` + `staged_equip_files` contents to the
PackGroupBuilder alongside iteminfo.pabgb.

### 5. Inform the user what was pulled

The Sources table should show a summary like:
> ItemBuffs tab (current edits) — 6024 entries, +47 dict edits,
> stacks→9999, inf-dura on, 12 cooldown patches, 3 transmog swaps,
> UP v2 equipslotinfo staged

So the user can verify the pull captured what they expect.

---

## Merging multiple ItemBuffs-like contributions

If the user pulls ItemBuffs once, then drops in another compiled folder
mod (e.g. SoraSkySun's buff mod) that also has dict-level edits AND
its own staged equipslotinfo, the merge needs to handle:

1. Dict-level: field merge works, last-writer wins per field.
2. Bucket B: stacks+dura are commutative — if either source enables
   them, merged output has them enabled.
3. Bucket C (byte patches): these are per-item. Merge by `item_key` —
   if two sources patch the cooldown of the same item, last-writer
   wins with a conflict log entry. VFX/transmog: if both sources swap
   the same item's visuals, last-writer wins.
4. Bucket D (sibling files): last-writer wins (these are wholesale
   file replacements).

The field-level merge for dict edits is unchanged. The new work is
coalescing Bucket B/C/D across multiple sources.

---

## Smoke-test plan (diff vanilla vs modded, per feature)

For each Bucket A feature: apply in isolation, compare
`serialize_iteminfo(vanilla)` vs `serialize_iteminfo(modded_dict)`.
Bytes should differ only at the expected fields. These are already
implicitly tested by ItemBuffs's existing Apply flow.

For each Bucket B/C/D: apply in isolation through ItemBuffs's Apply
path, dump the resulting overlay bytes, then apply the same operation
through Stacker's extended Pull + merge + pack, dump its overlay bytes,
compare.

If the two overlays are byte-equal (or differ only in incidental
padding), the Stacker capture is faithful.

The concrete smoke-test script would:
1. Launch CrimsonGameMods headless (or in test mode).
2. Programmatically construct ItemBuffs state for one feature.
3. Run `_buff_apply_to_game` internals to get expected bytes.
4. Run Stacker `_pull_from_itembuffs` + merge + pack to get actual bytes.
5. Diff. Report mismatches.

This test requires fixtures (a fresh ItemBuffs instance with game path
set) but doesn't require the UI. Wiring it up is a follow-up task
once the code changes in §1-4 are in place.

---

## Summary of what to fix, in order

1. Extend `ModEntry` to carry Bucket B/C/D (one-time schema change).
2. Extend `_pull_from_itembuffs` to snapshot them.
3. Extend `_run_inner` to apply Bucket B before serialize, Bucket C
   after serialize.
4. Extend `_pack_and_install_overlay` + `_pack_as_folder_mod` to add
   Bucket D sibling files to the PackGroupBuilder.
5. Extend the Sources-table status text to show captured summary.
6. Add merge semantics for Bucket B/C/D coalescing across multiple
   sources (for the case where user pulls ItemBuffs AND drops a
   compiled mod that has its own byte-level quirks).

Steps 1-4 make ItemBuffs-pull round-trip faithfully. Step 5 gives
visible verification. Step 6 is only needed once a second source also
contributes non-dict state, which doesn't happen in the 95% case
(Nexus mods are dict-level only).
