# Cross-Character Equipment & Mount Riding — Progress Tracker

## Last Updated: 2026-04-17

---

## Milestone 1: PAB Skeleton Format RE — COMPLETE ✓

### What we learned
- PAB files use `PAR ` magic, bone_count is **u16** at offset 0x14 (not u8)
- Per-bone record: `hash(4) + name_len(1) + name(N) + parent_i32(4) + 4×matrix(256) + scale(12) + rot(16) + pos(12)` = **305 + name_len bytes**
- Tail data after bone list = constraints/IK metadata (preserved during injection)

### What we fixed
- `CrimsonGameMods/Model/pab_skeleton_parser.py` — rewrote with correct format
- Added `serialize_pab()` for writing back to binary
- Added `inject_bone()` for cross-skeleton bone transplant with parent remapping

### Files
- Parser: `CrimsonGameMods/Model/pab_skeleton_parser.py`
- Research: `ResearchFolder/SKELETON_RIDING_BONE_RESEARCH.md`

---

## Milestone 2: Blackstar vs Golden Star Analysis — COMPLETE ✓

### Key Finding
Blackstar and Golden Star use **DIFFERENT** skeleton files (not the same as initially assumed):
- **Blackstar**: `cd_m0004_00_dragon.pab` — 274 bones, 89KB, has `B_Rider_01`
- **Golden Star**: `cd_m0004_00_golemdragon.pab` — 428 bones, 139KB, **NO rider bones**

### What makes Blackstar rideable
1. `B_Rider_01` bone in skeleton (index 19, parented to `Bip01 Spine1`)
2. Runtime lookup at `0x140660140` finds bone by name string `"B_Rider_01"`
3. PostureAdaptation initializer at `0x140E7B7B0` sets up rider seat mapping

### Identity Map
| Entity | CharKey | Internal Name | Skeleton |
|--------|---------|--------------|----------|
| Blackstar | 1000799 | Riding_Dragon_1 | cd_m0004_00_dragon.pab |
| Golden Star | 1002241 | Boss_Dragon_TriStar_Armor_Stage | cd_m0004_00_golemdragon.pab |

### Golden Star unique bones (vs Blackstar)
- Wings: `L_Wing`, `R_Wing`, `L_Wing02-04`, `R_Wing02-04`, 10× WingFinger per side
- ~80× `B_Bone0XX` structural/armor bones
- `NeckFat`, `B_Jaw_SubControll`, extra chin/lip bones
- Scale 4× (vs Blackstar's 2×)

---

## Milestone 3: B_Rider_01 Injection — COMPLETE ✓

### What we built
Injected Blackstar's `B_Rider_01` bone into Golden Star's skeleton:
- Extracted 315-byte bone record from Blackstar
- Remapped parent: Blackstar index 11 → Golden Star index 13 (both = `Bip01 Spine1`)
- Appended as bone 428 in Golden Star's skeleton
- Updated bone count 428 → 429

### Output
- `_dragon_research/goldstar_WITH_RIDER.pab` (139,230 bytes)

### Deployment
Replace via PAZ overlay: `character/model/2_mon/cd_m0004_00_dragon/cd_m0004_00_golemdragon/cd_m0004_00_golemdragon.pab`

---

## Milestone 4: In-Game Testing — RIDING CONFIRMED ✓

### Results (2026-04-17)
- **Horse mesh-swap to Golden Star: RIDEABLE** — full controls and movement working
- **No PostureAdaptation XML needed** — game finds B_Rider_01 by name at runtime
- **Rider position needs Y calibration** — original Y≈0 puts rider in stomach
- Camera zoom not auto-adjusted (minor, configurable)
- Dragon-swap version: can't mount from ground (interact height issue, not a bone issue)

### Critical Lessons Learned

**1. PAZ overlay MUST use a new group number (not vanilla 0009)**
- v1 deployed to group 0009 → overwrote PAPGT checksum → game won't start
- Fix: use unused group (0062) like Field Edits uses 0039

**2. Bone volume flag MUST be appended to tail section**
- v1 omitted the flag byte → "bone volume 로드를 실패" crash on world load
- Fix: append `0x00` (no volume) to the per-bone flag array in the tail

**3. Rider Y position needs per-mount calibration**
- Y=0 (Blackstar original): in stomach
- Y=3.0: almost but still inside
- Y=4.0: still inside
- Y=8.0: under testing
- Position is in skeleton-local space, CharacterScale multiplies it

### Deploy Process (verified working)
```
1. Build .pab with inject_bone() + flag byte
2. pack_mod() to NEW group (0062)
3. Copy 0062/ + meta/0.papgt to game dir
4. Restart game
```

---

## Milestone 5: Rider Position Calibration — IN PROGRESS

### Y Position Test Data (Golden Star, CharacterScale=4)
| Version | Y | Result |
|---------|---|--------|
| v2 | 0.0 | Deep in stomach |
| v3 | 3.0 | Almost, still slightly inside |
| v4 | 4.0 | Still inside |
| v5 | 8.0 | Testing... |

### Goal: derive formula
```
rider_Y = base_offset * (target_scale / reference_scale)
```
Once Golden Star's correct Y is found, `base_offset = correct_Y / (4.0/2.0)` gives us the universal multiplier for any mount.

---

## Milestone 6: Generalize to Other Mounts — NOT STARTED

### Goal
Make any non-rideable animal rideable by injecting `B_Rider_01`:
- Dogs/wolves (`cd_m0011_00_dog.pab`)
- Wyverns (`cd_m0004_00_wyvern.pab`)
- Bears (`cd_m0001_00_bear.pab`)
- Any community-requested mount

### Pipeline — BUILT: `rider_bone_injector.py`
```python
from rider_bone_injector import make_rideable, restore_overlay

# One-call to make any skeleton rideable
result = make_rideable(
    game_path="<game>",
    target_skeleton_paz_path="character/model/2_mon/.../skeleton.pab",
    rider_y=8.0,            # tune per mount
    overlay_group="0062",
)

# Undo
restore_overlay(game_path, "0062")
```

Internals:
1. Extracts target `.pab` from PAZ via `crimson_rs.extract_file()`
2. Parses bones, finds `Bip01 Spine1` parent index
3. Copies `B_Rider_01` from Blackstar reference, patches parent + Y position
4. Appends volume flag=0 to tail section
5. `pack_mod()` to new overlay group → deploys to game

Known skeleton mappings in `KNOWN_SKELETONS` dict:
- Golden Star, Wyvern, Wolf/Dog, Bear, T-Rex Dragon, Carmabirdsaurus
- Each with suggested rider_y (estimates, need testing)

### Dev Community Idea
Scan identical dog skeletons in memory to understand bone transform format from the game engine's perspective. All dogs share the same `.pab` → bone data should match exactly in memory, confirming our parse is correct.

---

## Related Work

### Cross-Character Equip (Oongka Axes)
See `TODO_CROSS_CHARACTER_EQUIP.md`:
- Universal Proficiency covers ~95% of weapons
- Oongka axes still blocked by skeleton/rig compatibility
- Same class of problem: mesh weighted for wrong skeleton

### Dye-Slot Asset Gate
See `TODO_CROSS_CHARACTER_EQUIP.md`:
- `Make All Dyeable` sets iteminfo flags but game checks `.pab` mesh material slots
- Needs `.pab` appearance format RE (same PAZ group 0009)

### Alpine Ibex Mod Reference
- `True Legendary Alpine Ibex` mod swaps appearance XML only
- Alpine Ibex already in `4_riding/` category with rider bones
- Confirms: riding gate = skeleton bones, not save/characterinfo data
