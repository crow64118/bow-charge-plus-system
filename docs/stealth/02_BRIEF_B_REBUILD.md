# Brief B — rebuild the stealth AC in PUNCH_COMBAT, exact copy

Prerequisites, all in this repo before you paste:

- `docs/stealth/SPEC/` exists (output of Brief A).
- BLANKS.md rows L1–L5 and P1–P7 are filled. Where an L-value is UNREADABLE, decide it
  yourself in the editor first — the rebuild cannot start with an unknown default.

Fill the `«…»` slots from BLANKS.md, then paste everything between the rules.

---

PUNCH_COMBAT. Confirm the loaded project before touching anything.
Standing rule check: every MCP call in the log since your last marker is yours.
Blueprint only, no C++. Do not start PIE.
Never edit anything under /Game/AAMS/ or /Game/TMS/ in place.

If any modal dialog opens, STOP and tell me, make no further calls. Do not attempt to
create a Blueprint Function Library, an Enumeration, a Struct or a Behavior Tree — the
tooling can't, and the Function Library attempt blocks the game thread.

## What this is

A 1:1 port of `/Game/STEALTH_SYSTEM/` from FREESMOKE_001, from the spec files I'm giving you
(`docs/stealth/SPEC/*.md` — I'll paste each file when you ask for it, or point you at the
folder if it's on this machine). **Exact copy, bugs included.** The spec's graphs are the
design; do not improve them, do not simplify them, do not fix what looks wrong. There is a
known bug list and it gets fixed in a later pass, after I've played the faithful copy. The
only permitted departures from the spec are the five in "Design calls" below.

The stealth system is a **sibling ActorComponent** on the player character, next to the
existing PunchCombat AC. It does not go inside PunchCombat. PunchCombat is not modified in
this brief.

## Recon before build

Read and report, change nothing:

1. Confirm `«P1: player character Blueprint»` exists, its parent class, its component list,
   and that `«P2: PunchCombat AC»` is on it.
2. Confirm the mesh's skeleton and that socket/bone `«P4: head socket»` exists on it.
3. Confirm crouch: does the character call `Crouch` / `UnCrouch` on the movement component,
   from which Input Action? Is `Can Crouch` ticked on the CharacterMovement nav-agent props?
4. Does `/Game/STEALTH_SYSTEM/` or any asset named like the spec already exist here? If yes,
   STOP and report — do not overwrite.
5. `git status` of the project. If there is no repo, say so; step 0 makes one.

Report, then wait for my go.

## Step 0 — baseline

If no git repo: `git init`, add a `.gitignore` for Unreal (Binaries, DerivedDataCache,
Intermediate, Saved, .vs, *.sln), commit everything as `pre-stealth-baseline`. If a repo
exists, commit the current state under that message. Nothing else in this step.

## Step 1 — folders and art

- Create `/Game/STEALTH_SYSTEM/` and `/Game/STEALTH_HIDER/`.
- Art: the 13 `STEALTH_HIDER` assets are imported by hand by me (migrate from FREESMOKE_001,
  Content Browser → Migrate). If they are already present, verify against `SPEC/ART.md`:
  every material instance's parent and overridden parameters match. If absent, tell me and
  continue with the Blueprints; `BP_BUSH`'s material slots stay empty until I migrate.

## Step 2 — interfaces

From their spec files, create `BPI_STEALTH_OBJECT`, `BPI_STEALTHFACTOR_PROVIDER` and the
listener interface, with exactly the function names, parameter names and types in the spec.
Compile. Commit: `stealth: interfaces`.

## Step 3 — BP_STEALTH_ACTOR, BP_BUSH, BP_LIGHT_EMITTER

One at a time, each compiled and committed before the next.

- `BP_STEALTH_ACTOR`: parent Actor, scene root, implements `BPI_STEALTH_OBJECT`,
  `getSTEALTHFACTOR` returns 0.0. Exactly as spec.
- `BP_BUSH`: child of `BP_STEALTH_ACTOR`. Every component and property per spec: `bush-01`
  scale 1.5, query only, overlaps Pawn; stealth factor 0.4; material swap on begin/end
  overlap. Rebuild the graphs node-for-node from the spec dump.
- `BP_LIGHT_EMITTER`: empty graphs, components per spec: PointLight 5000 unitless /
  attenuation 1000 / colour (0, 1, 0.435) / shadows on / z 55; `LIGHT DETECT` sphere radius
  32, scale (85.6, 30, 30), tag `«G2: tag»`, query only, overlaps Pawn only; bulb and pole
  ignore Visibility. Every collision response per channel exactly as spec — the sphere's
  odd scale and the Visibility-ignore are load-bearing, don't normalise them.

Commit each: `stealth: BP_STEALTH_ACTOR`, `stealth: BP_BUSH`, `stealth: BP_LIGHT_EMITTER`.

## Step 4 — BP_DARKNESS_DETECTION

ActorComponent. Build in this order, compiling after each:

1. Variables with defaults per spec. `Character` is typed **`«P1»`** (design call 1).
2. Functions, empty shells first with inputs/outputs/locals, so cross-references resolve.
   Local defaults: `loacal_MIN RAY DISTANCE = «L1»`, `local GRID SIZE HALF = «L2»`,
   `local GRID CELL DISTANCE = «L3»`, `HAS A ROOF = «L4»`.
3. Function bodies from the spec dumps: `GRID_SCAN`, `validate grid positions`, `TRACE SUN`,
   `ROOF ABOVE`, the point-light functions, `SCAN`. Node for node. The ForEach-with-Break in
   TRACE SUN keeps its unwired Break. The roof end point keeps its `× t + (0,0,2000)` form.
   The BeginPlay light scan keeps its Set-vs-Add exactly as the spec shows.
4. Event graph: BeginPlay sun discovery (tag `SUN`, print strings included), the 0.5 s
   looping timer calling `SCAN`, the capsule overlap begin/end handlers.
5. The head-socket name on the ROOF ABOVE start node is `«P4»` (design call 2).

Array writes land one element per call through this tooling — verify every array default
element by element after writing. Impure functions with no exec input get pruned — check
each impure call has its exec wired before compiling.

Commit: `stealth: BP_DARKNESS_DETECTION`.

## Step 5 — BPC_STEALTH_SYSTEM

ActorComponent. Same order:

1. Variables per spec: `CURRENT STEALTH FACTOR` 1.0, `IS CROUCHING` false, the rest per
   spec. `Character` typed `«P1»`. `ANIM INSTANCE` is created but left unassigned and unread
   (design call 3) — keep the variable so the graphs match.
2. `GET MAX STEALTH FACTOR` with `local_CURRENT MAX FACTOR = «L5»`; `CAN CROUCH?`;
   `START CROUCH`; `STOP CROUCH`; `calculate current stealth factor` — all node for node,
   including the Sequence of four steps and the exact FMin/FMax/FClamp arrangement.
3. Step 4 of the Sequence (the `BP_P0Character` TextRender debug write) is **replaced** by a
   `Print String` of the factor, 0.5 s duration, key `STEALTH` (design call 4). Nothing else
   in the Sequence changes.
4. Event graph: the 0.5 s looping timer, the overlap messaging to `BPI_STEALTH_OBJECT`.

Commit: `stealth: BPC_STEALTH_SYSTEM`.

## Step 6 — attach to the character

On `«P1»`:

1. Add `BP_DARKNESS_DETECTION` and `BPC_STEALTH_SYSTEM` as components. Leave PunchCombat
   untouched.
2. Assign each component's `Character` variable at the character's BeginPlay: `Self` →
   set on both components. Use the character's existing BeginPlay chain; add a Sequence pin
   if it has none — do not reorder anything already there.
3. Crouch hook (design call 5): in the character, on the existing crouch Input Action —
   **Started** → `BPC_STEALTH_SYSTEM.START CROUCH`; **Completed** → `STOP CROUCH`. If crouch
   is a toggle, wire START on the toggle-on branch and STOP on the toggle-off branch. If the
   character has no crouch at all, STOP and tell me — I'll decide, don't add one.
4. Compile the character. Log must show no Accessed None on load.

Commit: `stealth: attached to «P1»`.

## Step 7 — test scene

In `«P7: test map»`, without saving over anything I have open:

- A `BP_LIGHT_EMITTER` at a spot on the floor with clear sky.
- A `BP_BUSH` about 400 units away.
- A roofed box (three walls and a ceiling of any static mesh) about 400 units the other way,
  tall enough to walk under.
- One actor tagged `SUN` carrying a DirectionalLightComponent also tagged `SUN`. If the
  map already has a directional light, tag it and its component instead of adding one.

Save the level. Per-instance values live in the level; an unsaved level loses them.
Commit: `stealth: test scene`.

## Design calls — don't reinterpret

1. `Character` is typed as `«P1»`, assigned from the character's BeginPlay. No cast to any
   AAMS class anywhere.
2. The roof start uses socket/bone `«P4»`.
3. `ANIM INSTANCE` stays as a dead variable. Do not wire it.
4. The TextRender debug is a Print String. No new widget, no new actor.
5. Crouch is driven by the character's input events calling START/STOP CROUCH. The engine
   crouch (`Crouch()`/`IsCrouched`) is **not** consulted by the stealth AC in this pass, even
   though that would be cleaner. Exact copy first.

Everything else is the spec, verbatim.

## Verify

Observable outcomes, not steps:

- All new assets compile clean; the output log after loading `«P7»` is free of
  `Accessed None`, `Failed to find function` and `Cast failed`.
- With the character standing in the open under the sun: `STEALTH` print reads `1.0`.
- Crouched in the open: the print drops to `0.9` or below within one second.
- Crouched in the bush: prints `0.5` or below.
- Bush material swaps on entering and back on leaving.
- Walking into the light emitter's sphere prints nothing new but `POINTLIGHTS` length goes
  to 1 (add a temporary Print of the length in the overlap handler, remove it before commit).
- Un-crouching in the open: whether the print returns to `1.0` — **report either way**,
  this is bug 2 and I expect it to stick.
- Under the roofed box: report the printed value. I expect the roof term to be dead (bugs 5
  and 6); say what you see.

I playtest by hand after this. Save all. Do NOT start PIE.

Report anything you did differently from this brief and why. If any of this is wrong or
unbuildable, say so before building it. I'd rather respec than have you force my shape onto
working code.

Invariants: PunchYawFixMap 90/90/90/95/90/90 + Block 90 · FootIKRestAlpha 0.4 ·
Layered Blend spine_01 / depth 3 / Mesh Space Rotation on · Blend Poses by Bool
0.15/0.15 · DefaultSlot and UpperBody intact · all assets compile clean · log clean of
Accessed None.

---

# Bug pass (B2) — only after you've played the faithful copy

One bug per session, one commit per bug, playtest between. Same header block as above.
Order chosen so each fix is observable on its own:

| Order | Bug | Fix | Observable |
|---|---|---|---|
| 1 | 2 — IS CROUCHING sticks | Move `STOP CROUCH` out of the overlap loop; call it from the Completed / toggle-off input regardless of CAN CROUCH? | Un-crouch in the open → print returns to 1.0 |
| 2 | 7 — grid points discarded | In `validate grid positions`, a hit whose actor is `Character` counts as **clear**, not blocked | Grid keeps ~all points on flat ground (temporary print of kept count) |
| 3 | 8 — sun accumulator | `loacal_MIN RAY DISTANCE` starts at a large value (100000); if no point is lit it stays there; output reports that as "no sun reached" | Standing in shadow of a wall → Closest Ray Distance > 0 |
| 4 | 5 — roof end point | End = `start + (0,0,2000)` per cell, not `× t + (0,0,2000)` | Roof traces draw straight up (debug draw one session only) |
| 5 | 6 — roof accumulator | `HAS A ROOF = hit OR HAS A ROOF`, start false | Under the box → factor no longer gets the +0.2 |
| 6 | 9 — BeginPlay light Set | Add instead of Set | Two lamps overlapping at spawn → `POINTLIGHTS` length 2 |

After the pass, design call 5 gets revisited: read `IsCrouched` from the movement component
instead of START/STOP events. That's a separate session too.
