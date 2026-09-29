# Recon V1 — `/Game/STEALTH_SYSTEM/` as read in FREESMOKE_001

Read by Aura on 29 Sep 2026. Nothing in the project was changed; text dumps were written
to `Saved/stealth_recon/`, one file per Blueprint. This page is that report, cleaned up.
Lines the paste cut off are marked **[GARBLED]** and appear in [BLANKS.md](BLANKS.md);
Brief A re-reads them from the asset so nothing here has to be trusted from memory.

## 1. Readability

All graphs, node values and wiring read despite the compile failures (the Blueprints
reference AAMS / TMS / P0Debug / PhoneSystem folders that were not migrated). Class defaults
read. **Local variable defaults did not read** — no tool exposes them, and the raw asset
bytes show no default-value text, which is consistent with 0 / false but unverified. Five
locals matter:

| Function | Local | Type | Why it matters |
|---|---|---|---|
| TRACE SUN | `loacal_MIN RAY DISTANCE` | float | Bug 8: if 0, the character always reads as in sun |
| ROOF ABOVE | `local GRID SIZE HALF` | int | grid extent |
| ROOF ABOVE | `local GRID CELL DISTANCE` | float | grid spacing |
| ROOF ABOVE | `HAS A ROOF` | bool | Bug 6: if false, roof can never be true |
| GET MAX STEALTH FACTOR | `local_CURRENT MAX FACTOR` | float | start of the Max fold |

## 2. The logic

### BP_DARKNESS_DETECTION — ActorComponent on the character, `SCAN` on a looping 0.5 s timer

- **Sun discovery (BeginPlay):** first actor tagged `SUN`, then its DirectionalLightComponent
  also tagged `SUN`. Prints `"NO SUN"` or `"SUN IS UP"`.
- **GRID_SCAN:** `CellsCountHalf = 5` → an 11 × 11 grid of points at the character's actor
  location height, spaced by `GRID_SCAN spacing = 25` → 250 × 250 units.
- **validate grid positions:** a Visibility line trace from each point to the character's
  location. A point is kept only if the trace hits nothing **[GARBLED: "…and the hit actor …
  (tag 7)" — the exact keep condition]**.
- **TRACE SUN:**
  - For each kept point, a Visibility line trace toward the sun: `point + (−SunForward × 5000)`.
  - If not blocked, `local = Min(local, Distance(point, character))`.
  - Output `Closest Ray Distance` = distance to the nearest sunlit spot; 0 = standing in sun.
  - ForEach-with-Break loop; the Break is not wired.
- **Point lights:**
  - Capsule overlap with any component tagged **[GARBLED: tag name, probably `LIGHTSOURCE`]**
    adds that actor's PointLightComponents to `POINTLIGHTS`; end-overlap removes them.
  - Each scan traces character → light. Unblocked = lit; distance appended to
    `MIN RAY DISTANCES`.
  - `MIN RAY DISTANCE` = smallest of those, or −1 if no lights or none visible.
- **ROOF ABOVE:**
  - Start = head socket + (0, 0, 30). Grid of (2·half+1)² cells spaced by
    `local GRID CELL DISTANCE`.
  - Traces each cell and folds the result into `HAS A ROOF`.
  - Result written to `UNDER a ROOF?`.
- **Member defaults:** `GRID_SCAN spacing` 25 · `Closest Ray Distance` 0 ·
  `MIN RAY DISTANCE` −1 · `UNDER a ROOF?` false.

### BPC_STEALTH_SYSTEM — `calculate current stealth factor` on a looping 0.5 s timer

Scale: **1.0 fully visible, 0.1 most hidden.** A Sequence of four steps:

1. Not crouching → 1.0. Crouching → `Clamp(0.9 − GetMaxStealthFactor, 0.1, 1.0)`.
2. `factor −= 0.5 × Min(L, S)` where
   - `L = 10000 if MIN RAY DISTANCE == −1 else Clamp(MIN RAY DISTANCE / 900, 0, 1)`
   - `S = Clamp(ClosestRayDistance / 250, 0, 1)`
3. `factor = Clamp(factor + (UNDER a ROOF? ? 0.0 : 0.2), 0.1, 1.0)`
4. Debug only: writes the value to a TextRender on `BP_P0Character`.

- **GET MAX STEALTH FACTOR:** capsule's overlapping actors of class `BP_STEALTH_ACTOR`, calls
  `getSTEALTHFACTOR` on each through the interface, returns `Max` folded into the local.
- Other defaults: `CURRENT STEALTH FACTOR` 1.0 · `IS CROUCHING` false.
- `CAN CROUCH?` = MovementMode is Walking AND the mesh isn't simulating physics.
- `START/STOP CROUCH` are called from the AAMS character's crouch input.
- `ANIM INSTANCE` is set but never read.

### BP_LIGHT_EMITTER — empty graphs, everything is components

- **PointLight:** Intensity 5000 (unitless), attenuation 1000, colour (0, 1, 0.435) green,
  casts shadows, at z = 55.
- **LIGHT DETECT:** Sphere, radius 32, scale (85.6, 30, 30), tagged `LIGHTSOURCE`, query
  only, overlaps Pawn only. Sphere collision uses the smallest axis scale → effective radius
  ≈ 960, which matches the ÷900 in the formula.
- **Bulb and pole:** both ignore Visibility, so the lamp doesn't block its own light trace.

### BP_STEALTH_ACTOR (parent) and BP_BUSH

- `BP_STEALTH_ACTOR`: scene root only; `getSTEALTHFACTOR` returns 0.0.
- `BP_BUSH`: stealth factor **0.4**; `bush-01` at 1.5× scale, query only, overlaps Pawn.
  On begin overlap switches material to `SampleLeaves_CAMERA_FADE`; on end overlap back to
  `SampleLeaves_1`. A crouched character in the bush gets 0.9 − 0.4 = 0.5 before darkness and
  roof terms.

### BP_AI_STEALTH_DUMMY

Its perception component (from PhoneSystem) did not migrate. `VALIDATE PERCEIVED ACTORS`
lived there, so that code is not in FREESMOKE_001. It gets rewritten in Brief C.

## 3. Lift vs. replace

| Blueprint | Lift as-is | Tied to AAMS / P0 — replace |
|---|---|---|
| BP_DARKNESS_DETECTION | grid, validation, sun trace, point-light bookkeeping, roof grid | `Character` variable typed as the AAMS MotionMatching character; only needs actor location + mesh head socket |
| BPC_STEALTH_SYSTEM | formula, GET MAX, CAN CROUCH?, overlap messaging | START/STOP CROUCH from AAMS input → read engine crouch state; BP_P0Character TextRender debug → drop; ANIM INSTANCE → drop |

You have already re-pointed `Character` in both components to ThirdPerson in FREESMOKE_001.

## 4. Interfaces

- `BPI_STEALTH_OBJECT`: `OnBeginOverlap(Character)`, `OnEndOverlap(Character)`,
  `getSTEALTHFACTOR → VALUE (float)`. **[GARBLED: exact signature of the overlap functions]**
- `BPI_STEALTHFACTOR_PROVIDER`: `GET STEALTH FACTOR → STEALTH FACTOR (float)`. Nothing calls it.
- A third interface, `…LISTENER`, has one placeholder function `NewFunction`.

All compile with no outside dependencies.

## 5. Bush art

13 assets under `STEALTH_HIDER/`: 1 mesh, 4 material instances, 1 base material, 7 textures.
Every dependency chain resolves inside the folder. Not checked: how they render.

## Bugs

From the earlier audit, checked against this copy:

1. **VALIDATE PERCEIVED ACTORS** builds a filtered list into a local and never copies it back
   — can't verify, the code didn't migrate. Moot: rewritten in Brief C.
2. **IS CROUCHING sticks true** — confirmed. STOP CROUCH only runs inside the overlap loop, so
   with nothing overlapping it never resets; also gated by CAN CROUCH?, so un-crouching
   mid-air doesn't reset it.
3. **Roof multiplied instead of added** — not true of this copy. It's added (+0.2 open, +0
   under roof). Not a bug.
4. **GET MAX's 0.0 start = maximally hidden** — inverted. 0.9 − 0 = 0.9 = nearly visible.
   0.0 is the correct start. Not a bug.

New, found by the recon:

5. **ROOF ABOVE end point:** computes `point × t + (0, 0, 2000)` so every roof trace ends on
   the world Z axis above the origin, not straight up.
6. **ROOF ABOVE accumulator:** `HAS A ROOF = hit AND HAS A ROOF`. If it starts false the roof
   is always false; if true, every cell must hit.
7. **validate grid positions** treats a trace that hits the character as blocked and discards
   the point. Every trace ends inside the character, so this can discard every point.
8. **TRACE SUN accumulator:** `Min(local, distance)` with local starting at 0 → result always
   0 → character always reads as standing in sun.
9. **BeginPlay light scan:** for already-overlapping lights it **sets** `POINTLIGHTS` per
   component instead of adding, so only the last one survives.

Bugs 6 and 8 hinge on the local defaults. Bug 2 is the one that will show first in a
playtest: crouch once and the factor never returns to 1.0.

## Also noted

`BPI_CombatRelay` and `S_FactionRelation` exist in FREESMOKE_001. Brief C reuses
`S_FactionRelation`'s shape if it fits, since the MCP tooling cannot create structs.
