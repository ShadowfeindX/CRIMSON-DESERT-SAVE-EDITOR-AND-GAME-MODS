# Why CrimsonGameMods is pivoting to its own mod-install path

**TL;DR:** If you use CrimsonGameMods' ItemBuffs tab *and* JMM ("JSON Mod
Manager" / CD JSON Mod Manager) on the same game, one of them wipes the
other's work every time you click Apply. This document explains why,
what I tried to do about it cooperatively, and what I'm building as a
result: the **Stacker Tool** tab inside CrimsonGameMods, which does the
install step itself so your mods stop getting clobbered.

---

## What users are actually seeing

You apply your ItemBuffs edits in CrimsonGameMods. The game loads them.
Buffs work. You then open JMM to install a separate UI / texture /
json mod. JMM runs its Apply. You launch the game — your ItemBuffs
edits are gone.

This is not a bug in my tool. This is not a bug in JMM, strictly
speaking. It's how JMM is *designed* to work: on every Apply, it deletes
overlay directories it doesn't recognize as its own. Anything my tool
wrote that JMM didn't write gets nuked.

You can verify this for yourself. Look in your Crimson Desert install
folder for a directory named `0058/` or similar numeric name after
applying ItemBuffs, then run JMM's Apply — that directory is gone.

---

## Why this happens (plain-English version)

Crimson Desert loads its game data from numbered folders
(`0008/`, `0009/`, etc.). "Modding" mostly means adding another numbered
folder (an **overlay**) that the game merges over the vanilla data.

JMM decided a while ago that on every Apply, it would clean up
"stale" overlays — directories it didn't put there. The reasoning is
reasonable in isolation: don't let leftover broken overlays hang around
confusing the game.

The problem: my tool also writes overlays. My tool is not JMM. So from
JMM's perspective, the directory I wrote is "stale" and it deletes it.

---

## What this actually means for you (the Apple analogy)

Think of it the same way iMessage works on iPhones: iMessage is great,
but only for other iPhone users. The moment you add an Android user to
the group, messages stop working properly and iPhone owners blame the
Android owner even though nobody's actually doing anything wrong.

That's the situation here. Whether it was an intentional design
decision or an accidental byproduct doesn't really change the user
experience: the current loader deletes any overlay it didn't create.
If you use my tool *and* the other loader, the other loader treats
mine as trash and cleans it up. You end up with a choice:

- **Install via the other loader only**, and lose access to every
  feature my tool offers that the other loader doesn't support
  (ItemBuffs field-level editing, stat presets, transmog, Universal
  Proficiency, etc).
- **Install via my tool only**, and give up the other loader's UI,
  texture, and ASI mods.
- **Alternate between the two**, accepting that every time you run
  the other loader, you have to re-Apply from my tool right after.

There's no fourth option where the tools cooperate automatically,
because the only way that fourth option exists is if the other
loader changes its cleanup behavior — and that's a closed-source
tool whose code only one person can edit.

That's the "forced ecosystem" effect. Not dramatic, not personal —
just the mechanical consequence of one tool that won't acknowledge
other tools exist.

---

## What I tried before building my own install path

I reached out to the JMM author. I proposed a small change: when JMM
does its cleanup, preserve directories that another tool clearly owns
(e.g. via a marker file, or by looking them up in a shared state file,
or by simply skipping overlays with non-numeric names). It's a change
that would take somebody with his codebase open maybe an hour.

The response I got back amounted to: *"focus on making your mods
work — it's on my side to make the manager understand them."* I also
offered my tool's source for him to pull anything useful — I'm
open-source on GitHub. He's not interested in open-sourcing his, which
is his right, but it means any compatibility improvement can only come
from one direction, from one person, on his schedule.

I don't want to drag someone through the mud. He's been putting in
real hours maintaining his loader, and he's entitled to run his
project however he wants. But a closed-source loader that nukes other
tools' output and won't accept outside patches isn't a system I can
build a reliable user experience on top of. Every ItemBuffs user who
also installs a UI mod becomes a support ticket that traces back to
this exact design.

---

## The pivot: Stacker Tool

Instead of writing my output and hoping JMM leaves it alone, I'm adding
a new tab to CrimsonGameMods called **Stacker Tool**.

What it does:

- You drag your ItemBuffs edits + any JMM-format iteminfo mods + any
  folder-based iteminfo mods into the same window.
- It merges them **at the field level** — "Item X has 5 sockets, Item Y
  has 9999 stacks" — not at the byte level. Two mods touching different
  fields of the same item both land. Two mods touching the *same* field
  of the same item show up as a clear conflict ("mod A wants 5, mod B
  wants 9; pick one") instead of silent corruption.
- You click Apply Stack. It writes **one single overlay** with
  everything merged together. You launch the game. It works.

Stacker Tool also reads JMM-format `.json` mods (so every iteminfo mod
currently on Nexus works as input), and CrimsonGameMods continues to
export JMM-format JSON (so users still running JMM can install your
mods there too). The bridge is built from my side, without requiring
agreement from anyone.

---

## What this means for different kinds of user

**You only use ItemBuffs + JMM for UI/texture/ASI mods:**
You won't notice much immediately. Once Stacker Tool ships, just use
it for the ItemBuffs Apply step. JMM can still handle your UI overlay.
The two will stop fighting because Stacker writes its overlay under a
name JMM's cleanup doesn't recognize as "numbered."

**You stack 10+ iteminfo mods and keep hitting "incompatible" walls:**
This is the case Stacker Tool is built for. Drop them all in, merge,
install. The field-level merge is categorically more resilient than
byte patches when many mods touch the same file.

**You're an author shipping on Nexus:**
No change required. Keep publishing JMM-format JSON. My tool reads it,
my tool emits it. Your audience grows in both directions.

**You're happy with JMM and only run 2-3 simple mods:**
Nothing changes for you. JMM still works for that use case. You don't
have to install CrimsonGameMods if you don't want its other features.

---

## What I'm *not* doing

- **Not building a competing loader.** Stacker Tool is a single tab. It
  doesn't manage profiles, doesn't babysit ASI plugins, doesn't do any
  of the "mod manager" surface area that JMM does well. It does one
  thing: merge many iteminfo mods into one overlay.
- **Not attacking the JMM author.** He's put in real work. This
  document describes an engineering problem and a design choice, both
  of which I can point at in the decompile. I'm not claiming anyone
  acted in bad faith — I'm saying the current architecture doesn't
  accommodate external tools, and since the architecture is closed, I
  had to route around it.
- **Not burning the bridge.** CrimsonGameMods will keep reading and
  emitting JMM format. Any mod that works in one tool works in the
  other (for the mod types each supports). If the JMM author ever
  wants to pick up a cooperative change, I'll be happy to meet halfway.

---

## What you can do

- **Test Stacker Tool** once it ships in CrimsonGameMods and tell me if
  your mod set works. That's the only test that matters.
- **Report the overlay-wipe symptom** (screenshots / game logs) if
  you've hit it — I'll collect them so the problem is documented
  publicly, not just in my head.
- **If you author mods:** keep publishing JMM-format JSON. Everything
  downstream consumes it. No reason to change authoring workflow.
- **If you're technical:** read [MOD_COMPATIBILITY_PROBLEM.md](MOD_COMPATIBILITY_PROBLEM.md)
  for the engineering details, including the specific line references
  in the JMM decompile that describe the overlay-wipe behavior.

---

## One last thing

I spent a long time going back and forth on whether to pivot or keep
trying to find a middle path. I don't like writing documents like
this. But I have 3K people in the community who install my tool and
then run into this wall, and the answer "use my thing or his thing,
not both" is not an answer I'm willing to keep giving. Building
Stacker Tool is how I stop having to give it.

If you want to chat about it, come to the Discord. If you want to
audit the code, it's on GitHub.

— RicePaddyMaster
