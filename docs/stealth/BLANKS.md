# Blanks — things only you can answer

Fill in place. Each row says which brief consumes it. Brief A resolves the ones marked
"A reads it" automatically; you only need to answer those if A fails.

## Local variable defaults (Brief A tries first; check in the editor if A can't read them)

| # | Function → local | Value | Consumed by |
|---|---|---|---|
| L1 | TRACE SUN → `loacal_MIN RAY DISTANCE` | | B step 4, bug 8 |
| L2 | ROOF ABOVE → `local GRID SIZE HALF` | | B step 4 |
| L3 | ROOF ABOVE → `local GRID CELL DISTANCE` | | B step 4 |
| L4 | ROOF ABOVE → `HAS A ROOF` | | B step 4, bug 6 |
| L5 | GET MAX STEALTH FACTOR → `local_CURRENT MAX FACTOR` | | B step 5 |

## PUNCH_COMBAT project facts (Brief B needs these before it starts)

| # | Question | Answer |
|---|---|---|
| P1 | Exact name of the player character Blueprint in PUNCH_COMBAT (the one that carries the PunchCombat AC) | |
| P2 | Exact name of the PunchCombat ActorComponent class | |
| P3 | Engine version of PUNCH_COMBAT (5.8 assumed) | |
| P4 | Skeleton / mesh on that character and the **head socket or bone name** (Manny/Quinn: `head`) | |
| P5 | Is crouch already working on that character (engine `Crouch()` / `IsCrouched`)? Which Input Action toggles it? | |
| P6 | Does PUNCH_COMBAT have a git repo? If not, Brief B step 0 makes one. | |
| P7 | Which test map to drop the lamp and bush into | |

## Garbled lines from the recon paste (Brief A re-reads these from the asset)

| # | Where | What was lost |
|---|---|---|
| G1 | validate grid positions | the exact keep condition after "hits nothing" (mentions a hit actor and "tag 7") |
| G2 | Point-light capsule overlap | the component tag it filters on (probably `LIGHTSOURCE`) |
| G3 | BPI_STEALTH_OBJECT | exact names and parameters of the two overlap functions |
| G4 | BP_LIGHT_EMITTER header | first line of the components list |
| G5 | Bug 9 | the exact node that does the Set instead of Add |

## Design calls for Brief C (answer before C is written in full)

| # | Question | Answer |
|---|---|---|
| C1 | Faction list. Proposed: `Player, Civilian, Companion, Soldier, Animal, Enemy_A, Enemy_B`. Add / rename? | |
| C2 | Do companions share the player's faction, or have their own that is Friendly to Player? (Own faction recommended — lets a companion be turned.) | |
| C3 | Should animals be one faction or split (predator hostile to all, prey neutral/flee)? | |
| C4 | Is there an existing AIController / Behavior Tree in PUNCH_COMBAT the NPC base must build on, or is it greenfield? | |
| C5 | Does `S_FactionRelation` in FREESMOKE_001 have the shape `{FactionA: Name, FactionB: Name, Attitude: enum/int}`? (Brief A reports this.) | |
