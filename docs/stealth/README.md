# Stealth system — port from FREESMOKE_001 into PUNCH_COMBAT

Source of truth for the stealth rebuild. Chat is where decisions get made; this folder is
where they live.

## The plan in one paragraph

`/Game/STEALTH_SYSTEM/` is **already migrated into PUNCH_COMBAT** (UE 5.8, Blueprint only).
It doesn't compile only because a few nodes reference AAMS/TMS/P0/PhoneSystem classes that
aren't in this project; the graphs are intact and were read there on 29 Sep. **Brief D
repairs it in place** — fix the dangling references, attach the two components as
**siblings next to the PunchCombat AC**, drop in a test scene — then the known bugs get
fixed in a second pass. Briefs A and B (extract from FREESMOKE_001 and rebuild) are kept
only as the fallback if the migrated copy turns out to be unrepairable. After that, an NPC base (civilian / companion / soldier / animal / enemy) with a
faction channel so factions fight each other, using the stealth factor as the perception
input.

## Order of operations

| # | File | Where it runs | What it produces |
|---|------|---------------|------------------|
| 0 | [00_RECON_V1.md](00_RECON_V1.md) | already done (Aura, 29 Sep) | What the system does. Read this first. |
| **D** | [04_BRIEF_REPAIR_IN_PLACE.md](04_BRIEF_REPAIR_IN_PLACE.md) | **PUNCH_COMBAT — start here** | Everything compiles, components on the player, test scene, five local defaults printed |
| — | you playtest | PUNCH_COMBAT | Confirms the faithful version before anything is changed |
| fallback | [01_BRIEF_A_EXTRACT.md](01_BRIEF_A_EXTRACT.md) / [01b](01b_BRIEF_A_AURA.md) then [02_BRIEF_B_REBUILD.md](02_BRIEF_B_REBUILD.md) | FREESMOKE_001 → PUNCH_COMBAT | Only if D finds the migrated copy unrepairable |
| B2 | [02_BRIEF_B_REBUILD.md](02_BRIEF_B_REBUILD.md) §Bug pass | PUNCH_COMBAT | Bugs 2, 5–9 fixed, one commit each |
| C | [03_NPC_FACTION.md](03_NPC_FACTION.md) | PUNCH_COMBAT | `BP_NPC_Base`, faction table, perception that reads the stealth factor |
| **A** | [05_PHASE_A_CLOSE_OUT.md](05_PHASE_A_CLOSE_OUT.md) | **PUNCH_COMBAT — current** | Bushes block AI sight (`AISight` channel), R2c lighting deletions, perception hysteresis. Then stealth is CLOSED and Phase B (combat) may start |

[BLANKS.md](BLANKS.md) is the short list of things only you can answer; `data/` holds the faction table ready to import; [LOG.md](LOG.md) is the session log. Fill it as you go; every
brief marks where a blank is consumed.

## Rules that hold for every brief here

- Blueprint only. **No C++, ever** — no Source folder, no build step. The one Python file in `tools/` is an optional editor-console read script, not project code. No PIE started by the agent.
- Nothing under `/Game/AAMS/`, `/Game/TMS/` or `/Game/STEALTH_SYSTEM/` in FREESMOKE_001 is
  edited in place. Brief A is read only; it writes text files under `Saved/` and nothing else.
- Exact copy first. The rebuild reproduces the old graphs including their bugs. Bugs are
  fixed only in the bug pass, one per commit, after the copy compiles and you have played it.
- One brief per session. Read back, playtest, log, stop.
- Every session ends by writing what it did into `docs/stealth/LOG.md` (created by the first
  session that has something to log).
