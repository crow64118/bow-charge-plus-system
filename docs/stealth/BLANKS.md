# Blanks — the short list

Everything else has been made self-serve: Brief A reads the graphs, `tools/ue_dump_bp_locals.py`
tries to read the local defaults, Brief B discovers the PUNCH_COMBAT facts in its own recon
step and prints them for your go.

## Must have before Brief B (only if the script and Brief A both fail to read them)

| # | Function → local | Value |
|---|---|---|
| L1 | TRACE SUN → `loacal_MIN RAY DISTANCE` (float) | |
| L2 | ROOF ABOVE → `local GRID SIZE HALF` (int) | |
| L3 | ROOF ABOVE → `local GRID CELL DISTANCE` (float) | |
| L4 | ROOF ABOVE → `HAS A ROOF` (bool) | |
| L5 | GET MAX STEALTH FACTOR → `local_CURRENT MAX FACTOR` (float) | |

How to read one by hand: open the Blueprint → My Blueprint panel → double-click the
function → in My Blueprint, under **Local Variables**, click the variable → Details panel →
**Default Value**.

## Decisions for Brief C (defaults in brackets are what gets built if you say nothing)

| # | Question | Answer |
|---|---|---|
| C1 | Faction list [`Player, Companion, Civilian, Soldier, Animal, Enemy_A, Enemy_B`] | |
| C2 | Companions get their own faction, Friendly to Player [yes] | |
| C3 | Animals: one neutral faction, or split predator/prey [one faction, neutral to all but Enemies] | |
| C4 | Existing AIController / Behavior Tree in PUNCH_COMBAT to build on [greenfield; Brief C's recon reports if it finds one] | |

## Things you do by hand because the tooling can't

- Migrate the 13 `STEALTH_HIDER` art assets from FREESMOKE_001 to PUNCH_COMBAT (Content
  Browser → right-click folder → Migrate). Before or after Brief B, either works.
- Create `S_FactionRelation` and import `data/DT_FactionRelations.csv` (see `data/README.md`).
- Create an empty `BT_NPC_Base` Behavior Tree and `BB_NPC_Base` Blackboard before Brief C.
