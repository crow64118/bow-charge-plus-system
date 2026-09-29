# Stealth system — port from FREESMOKE_001 into PUNCH_COMBAT

Source of truth for the stealth rebuild. Chat is where decisions get made; this folder is
where they live.

## The plan in one paragraph

`/Game/STEALTH_SYSTEM/` works in **FREESMOKE_001** (UE 5.8, Blueprint only). It does not
exist in **PUNCH_COMBAT**. We extract an exact node-level spec from FREESMOKE_001 (read
only), rebuild it 1:1 in PUNCH_COMBAT as a **sibling ActorComponent next to the PunchCombat
AC** on the same character, get it to a playtestable state, then fix the known bugs in a
second pass. After that, an NPC base (civilian / companion / soldier / animal / enemy) with a
faction channel so factions fight each other, using the stealth factor as the perception
input.

## Order of operations

| # | File | Where it runs | What it produces |
|---|------|---------------|------------------|
| 0 | [00_RECON_V1.md](00_RECON_V1.md) | already done (Aura, 29 Sep) | What the old system does. Read this first. |
| A | [01_BRIEF_A_EXTRACT.md](01_BRIEF_A_EXTRACT.md) (Claude Code + MCP) or [01b_BRIEF_A_AURA.md](01b_BRIEF_A_AURA.md) (Aura) | FREESMOKE_001, read only | `SPEC/` — one file per Blueprint, every node, pin and link, plus the local defaults via `tools/ue_dump_bp_locals.py` |
| B | [02_BRIEF_B_REBUILD.md](02_BRIEF_B_REBUILD.md) | PUNCH_COMBAT | The stealth AC and its actors, exact copy, compiling, on the character |
| — | you playtest | PUNCH_COMBAT | Confirms the port before anything is changed |
| B2 | [02_BRIEF_B_REBUILD.md](02_BRIEF_B_REBUILD.md) §Bug pass | PUNCH_COMBAT | Bugs 2, 5–9 fixed, one commit each |
| C | [03_NPC_FACTION.md](03_NPC_FACTION.md) | PUNCH_COMBAT | `BP_NPC_Base`, faction table, perception that reads the stealth factor |

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
