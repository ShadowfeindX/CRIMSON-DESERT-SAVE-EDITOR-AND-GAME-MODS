# Using CrimsonGameMods Stacker with JMM

A quick how-to for anyone who already uses **JMM (CD JSON Mod Manager)** and wants to also use CrimsonGameMods Stacker for iteminfo stacking (UP v2, sockets, custom items, Lantern-style mods, etc.).

Stacker and JMM both modify your game's overlay registry (`meta/0.papgt`). They can coexist, but **order matters**. Follow this and your mods from both tools will load every time.

---

## The one rule

> **Run JMM first. Run Stacker last.**

That's it. If you do that, everything works.

**Why:** JMM's mount process wipes numeric overlay folders it doesn't know about. Stacker writes its overlays to folders `0062/` and `0063/`, which JMM doesn't recognize and will delete if JMM runs after Stacker. The fix is to just run Stacker after JMM has finished.

**Why can't we swap the names?** We tried. Non-numeric names like `stk1` survive JMM's cleanup, but the game's PAZ loader silently refuses to load them. Only all-digit names load. There's no single name that satisfies both.

---

## Your workflow, step-by-step

### First time

1. **Install and mount your JMM mods.**
   - Open JMM, enable the mods you want, click Apply. Wait for it to finish.
   - Verify JMM's done — no progress bars, no "still processing" messages.

2. **Download and run CrimsonGameMods.exe** (v1.0.4 or later).
   - Run it as **Administrator** (required because it writes to Program Files).

3. **Prepare your iteminfo edits in the ItemBuffs tab.**
   - Click **Extract (Rust)**.
   - Click **Enable All** (or pick individual features — Make Dyeable, All 5 Sockets, Universal Proficiency v2, etc.).
   - Any custom items via Create Item, any transmog swaps, any cooldown edits — do them all here.

4. **Open the Stacker tab.**
   - Click **Pull Buffs** to import everything from step 3 as a source.
   - Drag any external iteminfo JSON mods you want to add (Lantern, Axiom Necklace, etc.) onto the Sources panel.
   - For any mod row showing a ⚠ warning about `insert` patches, `__count__`, or `__len__`: click its mode button until it shows **RPD** (Reparse-Diff).

5. **Click ✔ APPLY STACK.**
   - Stacker preserves every PAPGT entry JMM wrote.
   - Stacker adds `0062/` (iteminfo + index) and `0063/` (equipslotinfo) on top.
   - Your JMM mods + your Stacker mods are now both registered.

6. **Launch Crimson Desert.**

### Every subsequent time you change JMM mods

1. Re-run JMM (Apply).
2. Re-run Stacker Apply Stack.

Yes, both. JMM's Apply wipes our `0062/0063` because they're not in JMM's manifest. Re-running Stacker re-registers them. Takes 30 seconds.

### Every subsequent time you change Stacker mods

Just re-run Stacker. No need to touch JMM.

---

## Verify it worked

After Apply Stack + game restart, check any of these in-game:

- Open inventory on Kliff, check a ring — should show 5 socket slots (if you force-enabled sockets via Enable All).
- Try to equip a Marni_Musket on Kliff — should work (if you ran UP v2).
- Look for items your other mods added — they should appear normally (JMM's mods are intact).
- Check the game didn't load vanilla — obvious once you see your custom stats / appearances.

If anything's missing, check the "Something went wrong" section below.

---

## Something went wrong

### "After JMM's Apply, my Stacker mods disappeared"

Expected — JMM wiped `0062/0063`. Re-run Stacker Apply Stack. That's the intended workflow.

### "After Stacker's Apply Stack, my JMM mods disappeared"

Shouldn't happen — Stacker preserves all foreign PAPGT entries. If it does, open the Stacker Tool log panel and screenshot the Apply output, then report it as a bug. Include:
- Which JMM mods were installed
- What groups exist in `<game>/` (all folder names starting with digits)
- The contents of `<game>/meta/0.papgt` (can read with Stacker's Preview)

### "Ultimate Lantern Reborn crashes my game"

Open its source row in Stacker → click the mode button until it says **RPD** → Preview Merge → should show ~33 clean edits, zero parse breaks → Apply Stack. If you byte-apply (STR mode) on a Lantern mod, it will crash because Lantern uses absolute file offsets that go stale whenever any other mod grows iteminfo.

### "The game says a file is corrupted / won't start"

1. Close the game.
2. Stacker → **✖ REMOVE STACK** (removes our `0062/0063/` only, leaves JMM alone).
3. If the game still won't start, JMM has a Mount/Unmount cycle too — run JMM's unmount/reapply cycle.
4. As a last resort: Steam → Verify Integrity. This restores `meta/0.papgt` to vanilla. Then re-run JMM and Stacker in order.

### "I want to remove everything and go back to vanilla"

1. Stacker → **✖ REMOVE STACK**.
2. JMM → its Unmount button.
3. If that's not enough: Steam → Verify Integrity.

### "Can I use Stacker without JMM?"

Absolutely. Stacker stands alone. Apply Stack writes `0062/0063/` and registers them in PAPGT. Nothing else is required.

---

## Quick reference: what goes where

| Overlay | Owner | Contents |
|---|---|---|
| `0008/` | game (vanilla) | all original game data |
| `0036+` numeric ranges | JMM / community mod loaders | texture swaps, audio, skills, whatever JMM installs |
| `0058/` | CrimsonGameMods ItemBuffs tab direct Apply | iteminfo + pabgh |
| `0059/` | CrimsonGameMods ItemBuffs tab direct Apply | equipslotinfo |
| `0062/` | CrimsonGameMods **Stacker Apply Stack** | merged iteminfo + pabgh (+ skill if staged) |
| `0063/` | CrimsonGameMods **Stacker Apply Stack** | merged equipslotinfo |

If you see any of `0058`, `0059`, `0062`, `0063` show up in `<game>/` — that's CrimsonGameMods. Everything else with digit-only names is either vanilla or another tool.

---

## Short version

1. JMM first, Stacker last.
2. If JMM re-runs, re-run Stacker too.
3. For weird mods (`insert` / absolute offsets): flip the source row to **RPD** mode before applying.
4. Problems → Stacker's REMOVE STACK button, then re-mount from scratch.

Most people's issues come from running the tools in the wrong order. Follow the rule and it works.
