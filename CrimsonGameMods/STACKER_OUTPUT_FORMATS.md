# Stacker Tool — Two Output Paths

The Stacker Tool gives you two ways to use the merged result. Pick
whichever fits your workflow. The merge logic is identical for both;
only the destination differs.

---

## 1. Apply Stack to Game

Writes the merged overlay directly into your Crimson Desert install at
`<game>/stk1/0.paz` + updates `meta/0.papgt`. Launch the game, mods
are live.

**Use this when:** you only want one tool involved in your mod
pipeline. You don't run another loader. Fastest path from "drag mods"
to "play game."

---

## 2. Export as Folder Mod (recommended for users who also use JMM or CDUMM)

Writes a standard compiled folder mod to a location you pick. Output
layout:

```
MyMergedMod/
  modinfo.json
  README.txt
  0036/
    0.paz     (contains the merged iteminfo.pabgb)
    0.pamt
```

**Use this when:** you want the merged result as a portable mod you
can install with any loader — or share, upload to Nexus, or drop into
the game manually.

### How to install what you exported

Once you have the exported folder, pick your installer:

- **JMM (CD JSON Mod Manager):** drag the folder into JMM's
  `mods/_enabled/`, click Apply. JMM treats it as any other compiled
  folder mod — no special handling, no wipe.
- **CDUMM:** import the folder, enable it, Apply.
- **Manual drop:** copy `0036/` directly into your Crimson Desert
  install directory. If nothing else claims 0036, it just works.
  Otherwise use a loader to handle the slot.

### Why this is the preferred path

Exporting as a folder mod means:

- **No fight with anyone's cleanup.** Your merged mod looks identical
  to every other Nexus folder mod. Whatever loader you run treats it
  as one of its own.
- **Shareable.** Zip the folder and send it to a friend. Upload it
  to Nexus as "My 20-mod pack." One mod install = all your merges.
- **Portable across loaders.** If you try JMM today and CDUMM
  tomorrow, the same exported folder works in both.
- **No game folder changes until you install.** The Stacker run
  doesn't touch your game at all. You can build, inspect, and share
  without risk.

---

## Both paths produce identical iteminfo.pabgb

The merge happens dict-level before either path branches. The bytes
written to `stk1/0.paz` (direct install) and the bytes written to
`MyMergedMod/0036/0.paz` (export) are the same. Only the surrounding
files differ (direct install writes a PAPGT entry; export writes
modinfo.json + README instead).

So you can use Export mode even if you don't use another loader —
treat it as your "save point." Apply Stack to Game whenever you want
to actually play. If something breaks, remove the stk1 overlay, pick
a different export, or re-build from source.

---

## What Stacker Tool does NOT do

- **Not a full mod manager.** It doesn't install ASI plugins. It
  doesn't handle UI CSS/XML overlays for non-iteminfo files. It
  doesn't manage mod load order profiles. Use JMM or similar for
  those features.
- **Not a byte-patch emitter.** It doesn't produce `format:2` JSON
  files. See `WHY_NOT_JUST_EXPORT_JSON.md` for the reason.

Stacker does one thing: merge N iteminfo.pabgb mods into one clean
iteminfo.pabgb. The two output paths are just different ways of
delivering that one result to your game.
