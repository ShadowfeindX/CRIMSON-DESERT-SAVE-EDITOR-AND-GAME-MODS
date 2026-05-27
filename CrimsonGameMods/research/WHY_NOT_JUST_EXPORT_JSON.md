# Why I won't ship an "Export as JSON" button for the ItemBuffs tab

Short version: because it keeps the whole community stuck in the
problem I'm trying to solve. "Just export as JSON" sounds like the
easy answer to the compatibility problem. It's actually the thing that
caused the compatibility problem in the first place.

This document exists because a bunch of you are going to read the pivot
PSA and ask "ok but why don't you just add an Export as JSON button so
your mods work with JMM?" That's a reasonable question. The honest
answer takes more than one sentence. Here's the full one.

---

## What "export as JSON" actually means

The JSON mod format everyone on Nexus ships right now looks like this
(simplified):

```json
{
  "patches": [
    {
      "game_file": "gamedata/iteminfo.pabgb",
      "changes": [
        {
          "type": "replace",
          "offset": 2398124,
          "original": "76f5ddb1",
          "patched": "00000000"
        }
      ]
    }
  ]
}
```

Read that carefully. What the mod is saying is:

> "At byte 2,398,124 of the game file iteminfo.pabgb, replace these
> four specific bytes with these four other specific bytes."

Not "give item X more stacks." Not "unlock abyss gear restrictions."
Just "these bytes at this position become these other bytes."

The loader reads the JSON, walks to position 2,398,124 in the game
file, checks the "original" matches, and if it does, writes the
"patched" bytes over it.

That's the format. Every mod on Nexus that isn't a wholesale file
replacement is shaped like that.

---

## Why this format is fragile

### Problem 1: game updates move bytes

Pearl Abyss ships a game patch. It adds a new field to item data —
say, a "craft tier" property that goes 2 bytes into every item's
record. Every item after the first one now starts 2 bytes later in
the file than it used to.

Your JSON mod said "write these bytes at position 2,398,124." That
position used to be the middle of an item's stack-count field. Now it
points at the middle of the item's *cooltime* field, because
everything shifted.

The patch still applies — the `original` bytes happen to match,
because the game update didn't change the value at that specific byte
position. But the patch now writes to the wrong field. Your stack
mod just silently changed an item's cooldown instead.

No error. No warning. No crash. Just subtle wrongness. The user notices
one of their items has weird behavior, blames "some mod conflict,"
spends an hour uninstalling things, never finds the real cause.

### Problem 2: stacking multiple mods multiplies the fragility

If one mod has a 5% chance of breaking on a game update, that's
annoying but manageable.

Twenty mods at a 5% chance of silent breakage: the math says only 36%
of your 20-mod stacks are fully intact after any given update. Two
out of three users running a respectable-size stack get subtle corruption
they can't diagnose.

### Problem 3: mods can't stack cleanly to begin with

Two mods both changing "nearby bytes" in the same item get flagged as
a conflict, even if they're editing completely different attributes
that happen to live a few bytes apart. The loader can't tell — it
only sees "bytes overlap." Users get told their mods are incompatible
when they're not. Or worse: one mod "wins" silently and the other's
changes disappear with no explanation.

### Problem 4: some mods can't be expressed in this format at all

The ItemBuffs tab lets you do things like Universal Proficiency
(restructures how weapons bind to character tribes), transmog (swaps
visual references without swapping stats), gimmick injection (adds
passive skill activators that didn't previously exist on an item).
These aren't "change N bytes at offset M" — they change the
*structure* of an entry. There's no clean way to express them as byte
patches because the length and layout of the data change.

If I export those as JSON, I have to emit the raw before/after bytes
of the entire entry. That's huge, brittle, and the loader on the
other side can only apply it as an all-or-nothing blob — no stacking
with other mods' edits to the same entry.

---

## What happens if I add an "Export as JSON" button anyway

Let's walk through what the user experience actually looks like.

**Day 1 — you use my ItemBuffs tab.** You set 999 stacks on every
item, turn on infinite durability, add sockets to your accessories,
and flip a handful of items to be dyeable. Click Export as JSON.

**Day 2 — you install it through JMM.** It works. You play. Happy.

**Day 3 — game update ships.** Pearl Abyss adds a new 4-byte field to
the start of the item record. Every byte offset in your JSON is now
off by 4.

**Day 4 — you reapply.** Some patches still apply (the bytes at the
shifted offsets happen to match). Some patches fail with
`BYTES-MISMATCH`. Some patches apply *to the wrong fields* and
silently corrupt your save state. You can't tell which is which.

**Day 5 — you blame my tool, or your favorite mod author, or the
loader author.** None of those are the cause. The cause is that the
byte-level format couldn't represent what you actually wanted.

Now multiply that experience by every user who installed an Export-as-JSON
output and by every game update. That's the ecosystem treadmill.
Everyone's running to stand still. Every game update = every mod
needs fixing. Every author does the fixing. Or users just live with
broken mods.

---

## Why adding the button also hurts the ecosystem

Beyond individual user pain, there's a signal problem.

Every tool that emits format:2 JSON is implicitly telling mod authors:
*"This is the format we agree on. This is how you ship mods."*

If I ship an Export as JSON button, I'm adding my 3,000 users to that
chorus. I'm telling authors: keep authoring in byte-patch format. Keep
building on a foundation that breaks every update. Keep paying the
treadmill cost forever.

I don't want to send that signal. I think the format is the bottleneck,
and I don't want to help entrench it just because "works with the
existing loader today" feels like the path of least resistance.

---

## What the Stacker Tool does differently

The Stacker Tool doesn't operate on bytes. It operates on the *parsed
structure* of iteminfo.pabgb.

Same mod example as before. Instead of "at byte 2,398,124, write these
bytes," the Stacker sees:

> "On the item named `Item_Stat_AbyssGear_ADR_LV1`, set the
> `broken_item_prefix_string` field to 0."

When the game ships an update and moves the field to a different byte
position, the Stacker doesn't care. It looks up
`Item_Stat_AbyssGear_ADR_LV1` by its name (names stay stable across
patches). It finds the `broken_item_prefix_string` field inside that
item (field names stay stable too). It writes the value.

The byte position never enters the picture. Game updates stop being
the end of the world. Mods don't need hand-fixing every time.

Multiple mods editing different fields of the same item both land.
Mods that add entries just extend the list without breaking
everything downstream.

This isn't theoretical. It's what the ItemBuffs tab has been doing
internally for months. You use it every time you click Apply to Game
in ItemBuffs. That's why ItemBuffs mods don't spontaneously break on
game updates the way byte-patch mods do.

---

## What I WILL ship instead of byte-level JSON export

The Stacker Tool will have an **"Export as Semantic JSON"** option
that emits a future-proof format that looks like this:

```json
{
  "modinfo": { "title": "My Mod", "version": "1.0" },
  "format": 3,
  "target": "iteminfo.pabgb",
  "intents": [
    {
      "entry": "Item_Stat_AbyssGear_ADR_LV1",
      "field": "broken_item_prefix_string",
      "op": "set",
      "new": 0
    }
  ]
}
```

This format:

- Survives most game updates because it says what to do in names, not
  byte positions.
- Stacks cleanly with other format:3 mods — the Stacker (or any future
  loader that adopts the format) can merge them field by field.
- Is readable. If you open the JSON in a text editor you can actually
  understand what the mod does.
- Is diff-able on GitHub. Small changes produce small diffs. Byte
  patches produce incomprehensible hex diffs.

No loader on Nexus today consumes this format natively. The Stacker
Tool will. If other loaders adopt it — great, the ecosystem advances.
If they don't — at least my users stop being stuck on byte-patch
roulette.

---

## Short answer, for people who skipped to the bottom

**Q: Why don't you just add an Export as JSON button?**

A: Because the JSON format everyone uses today encodes byte positions
instead of what the mod is actually doing. Byte positions break every
time the game updates. Exporting into that format would mean:

1. My mods break on every game update, same as everyone else's.
2. Some of my tool's features (Universal Proficiency, transmog,
   gimmick injection) can't be represented cleanly in that format at
   all.
3. I'd be telling mod authors "keep shipping in the format that
   breaks," which keeps the ecosystem stuck forever.

The better answer is a format that says "on item X, set field Y to
value Z" instead of "at byte N, write bytes M." That format already
exists in the Stacker Tool. It's what I'll be shipping exports in.

The cost to you: you can't install Stacker Tool's output through
JMM's loader. The benefit: your mods don't silently corrupt things on
the next game update. That's a trade I'm making deliberately, and
I'd rather explain it honestly than paper over it with a compatibility
button that hurts everyone in the long run.

If you install via the Stacker Tool, everything keeps working. If you
install via JMM's loader, it handles everything except the iteminfo
mods made by my tool — and that's actually fine, because there are
lots of other iteminfo mods on Nexus that work with JMM and will
keep working with JMM. My tool is for the case where you want to
stack a lot of them together without fighting with byte collisions.

Both paths are fine. Just use the one that matches what you want.

— RicePaddyMaster
