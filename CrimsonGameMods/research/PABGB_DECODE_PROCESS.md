# How to Decode a New PABGB Table — Step-by-Step Process

Reference document for future sessions. Documents the exact steps used to decode `skill.pabgb` from scratch to 100% roundtrip parser.

---

## Prerequisites

- IDA Pro with MCP server running on the Windows game binary
- The unstripped Mac binary (`CrimsonDesert_Steam-*`) for RTTI field names
- `crimson_rs` for PAZ extraction (`extract_file`)
- The target pabgb + pabgh extracted from the game

---

## Phase 1: PABGH Index Format

Every pabgb has a companion pabgh (index file). Determine the format:

```
u16 count + N × (u32 key, u32 offset)    — 8-byte records (most common)
u16 count + N × (u16 key, u32 offset)    — 6-byte records (rare)
u32 count + N × (u32 key, u32 offset)    — u32 count variant
```

**How to detect:** Read `u16` at offset 0 as count. Check if `2 + count * 8 == file_size` (8-byte records) or `2 + count * 6 == file_size` (6-byte records). If neither, try `u32` count.

**Output:** List of `(key, offset)` pairs sorted by offset. Entry boundaries = offset[i] to offset[i+1].

---

## Phase 2: Entry Header Format

Read a few entries and identify the header:

```
u32 key                    — entry numeric ID
u32 name_len               — string length
bytes[name_len] name       — ASCII entry name (e.g., "Skill_10004")
u8 null_term (optional)    — some tables have it, some don't
```

**Verify:** Check that the name is printable ASCII and the key matches the pabgh index.

---

## Phase 3: RTTI Field Names from Mac Binary

The Mac binary has unstripped symbols with error strings in Korean:

```
"SkillInfo의 _fieldName를 읽어들이는데 실패했다"
= "Failed to read _fieldName of SkillInfo"
```

**Extract all field names in order:**

```python
# Search for consecutive "ClassName... _fieldName" patterns
for m in re.finditer(b'ClassName', mac_binary):
    # Find underscore-prefixed name after padding
    # These appear in the EXACT read order
```

This gives you the field names and their read sequence. For skill.pabgb, this yielded 34 fields.

---

## Phase 4: Find the Reader Function in IDA

Two approaches:

### Approach A: Via error strings
1. Search IDA for the error string (e.g., `"_buffLevelList"`)
2. Find xrefs to that string → leads to the error handler
3. The caller is the readEntryFields function

### Approach B: Via known sub-readers
1. Find a known reader (e.g., BuffLevelList reader via the `"BuffLevelData"` string)
2. Find xrefs TO that function → the caller is readEntryFields

**For skill.pabgb:** Found via xrefs to `sub_1411098F0` (BuffLevelList reader) → caller was `sub_1410F8680` (SkillInfo::readEntryFields).

---

## Phase 5: Map the Read Sequence from IDA

The readEntryFields function is a linear sequence of read calls:

```c
read(stream, &struct.field, size)       → raw read of N bytes
sub_string(stream, &struct.field)       → CString: u32 len + bytes
sub_hash_lookup(stream, &struct.field)  → read u32, lookup → store u16
sub_list_reader(stream, &struct.field)  → u32 count + N × elements
sub_struct_reader(stream, &struct.field)→ fixed-size sub-structure
```

**Identify each sub-reader by decompiling it:**

| Pattern | Type | File format |
|---------|------|-------------|
| `read(a1, dest, 1)` | u8 | 1 byte |
| `read(a1, dest, 4)` | u32/i32 | 4 bytes |
| `read(a1, dest, 8)` | u64/i64 | 8 bytes |
| `sub_1410A96C0` | CString | u32 len + bytes |
| `sub_1410FE920` etc. | hash_lookup | reads u32, stores u16 in memory |
| `sub_1410FF5D0` etc. | list of hash_lookups | u32 count + N × u32 |
| `sub_1410FE7D0` | list of u16 | u32 count + N × u16 |
| `sub_1411017F0` | list of u32 | u32 count + N × u32 |
| `sub_141E2B740` | struct_28B | i64 + i64 + i64 + u32 |

**CRITICAL:** Hash lookups read u32 from file but store u16 in memory. For roundtrip, always read and store the original u32.

---

## Phase 6: Handle Nested Structures

For complex fields like `_buffLevelList`:

1. **Trace the reader chain:**
   - Level 1: `sub_1411098F0` → reads u32 count, calls per-level reader
   - Level 2: `sub_141109A60` → reads u32 count, calls per-buff reader
   - Level 3: `sub_1419D9780` → reads u8 flag, calls factory if flag==0

2. **Decompile the factory** to find all subclass types (120 types, 38 vtables for skill.pabgb)

3. **Map the common base** (shared by all subclasses) — this covers most modding needs

4. **For subclass tails:** Store as raw bytes initially. Decode individual subclasses later by:
   - Decompiling each vtable[10] function
   - Or empirically: compare entries of the same type_id to find fixed patterns

---

## Phase 7: Build the Parser (Python)

Structure:

```python
def parse_all(pabgh_bytes, pabgb_bytes) -> list[dict]:
    """Parse all entries."""
    
def parse_entry(data, offset, end) -> dict:
    """Parse one entry. Uses sequential reader with position tracking."""
    
def serialize_entry(entry_dict) -> bytes:
    """Serialize one entry back to bytes."""
    
def serialize_all(entries) -> (pabgh_bytes, pabgb_bytes):
    """Serialize all entries + rebuild pabgh index."""
    
def roundtrip_test(pabgh, pabgb) -> bool:
    """Parse → serialize → compare = identical."""
```

**Key pattern:** Use a position counter that advances with each read:

```python
pos = 0
field_a = struct.unpack_from('<I', data, pos)[0]; pos += 4
field_b = data[pos]; pos += 1
str_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
str_data = data[pos:pos+str_len]; pos += str_len
```

---

## Phase 8: Roundtrip Validation

1. Parse all entries
2. Serialize each entry back to bytes
3. Compare against original: `serialize_entry(parse_entry(raw)) == raw`
4. Also verify full file: `serialize_all(parse_all(pabgh, pabgb)) == (pabgh, pabgb)`

**If roundtrip fails:**
- Print the first differing byte position
- Hex dump around the failure point
- Compare field-by-field to find which read consumed wrong byte count
- Common causes: hash_lookup reading u32 but you wrote u16, missing padding bytes, wrong list element size

---

## Phase 9: Handle Version Differences

Different game versions may have:
- Different entry counts (new skills added)
- Extra fields (new u8/u32 added between versions)
- Changed field sizes

**Detection:** Try parsing both baselines. If one fails, probe for version-specific differences (e.g., an extra u8 between two known fields).

**For skill.pabgb:** 1.0.0.3 had no `field_58` (u8) in BuffData common base; 1.0.0.4 added it. Auto-detected by probing.

---

## Phase 10: Save Baselines

Save vanilla pabgb + pabgh for each game version in `game_baselines/<version>/`:

```
game_baselines/1.0.0.3/skill.pabgb
game_baselines/1.0.0.3/skill.pabgh
game_baselines/1.0.0.4/skill.pabgb
game_baselines/1.0.0.4/skill.pabgh
```

Add to PyInstaller spec `datas` so they bundle with the exe.

---

## Quick Reference: Reader Function Signatures

| Function pattern | What it reads from file | Memory size |
|-----------------|------------------------|-------------|
| `read(stream, dest, 1)` | 1 byte (u8) | 1B |
| `read(stream, dest, 2)` | 2 bytes (u16) | 2B |
| `read(stream, dest, 4)` | 4 bytes (u32) | 4B |
| `read(stream, dest, 8)` | 8 bytes (u64/i64) | 8B |
| CString reader | u32 len + bytes[len] | varies |
| Hash lookup | u32 (file) → u16 (memory) | **4B file, 2B memory** |
| List of hash lookups | u32 count + N × u32 | N × 2B memory |
| List of u16 | u32 count + N × u16 | N × 2B |
| List of u32 | u32 count + N × u32 | N × 4B |

**The #1 gotcha:** Hash lookups. The game reads 4 bytes from the file, looks up in a hash table, stores 2 bytes. Your parser must read 4 bytes to match the file, not 2.

---

## Tables Successfully Decoded

| Table | Parser | Fields | Roundtrip | Notes |
|-------|--------|--------|-----------|-------|
| iteminfo.pabgb | crimson_rs (Rust) | 105+ | 100% | Potter's parser |
| skill.pabgb | skillinfo_parser.py | 34 + BuffData base | 100% | 1761/1952 fully decoded, 191 raw fallback |
| skilltreeinfo.pabgb | skilltreeinfo_parser.py | key + name + opaque | 100% | Root package swaps only |
| mercenaryinfo.pabgb | mercenaryinfo_parser.py | 14 fields | 100% | Simple flat records |
| dropsetinfo.pabgb | dropset_editor.py | full | 100% | DropSet + ItemDrop dataclasses |
| inventory.pabgb | pabgb_parser_local.py | slot counts | 100% | External parser |

## Tables NOT Yet Decoded (candidates for future work)

| Table | Priority | Difficulty | Notes |
|-------|----------|-----------|-------|
| buffinfo.pabgb | High | Hard | 120 buff types, polymorphic like skill BuffData |
| storeinfo.pabgb | Medium | Medium | Store editor exists but broken post-update |
| gimmickinfo.pabgb | Medium | Hard | Polymorphic like buffs |
| characterinfo.pabgb | Low | Medium | Already editable via byte offsets in field_edit |
| regioninfo.pabgb | Low | Easy | Simple flags, already editable |
