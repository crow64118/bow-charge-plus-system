# Phase A — close out stealth (PUNCH_COMBAT)

Option 4 passed its playtest on 1 Oct: walls block line of sight, guards do not see through
them, perception works. Three loose ends remain and then stealth is **closed**. This brief
does exactly those three, in order, with a hard stop at the end. Phase B (combat) is not in
it; the agent is told it exists only so it does not design A into a corner.

The three:

| # | Loose end | What changes |
|---|---|---|
| A1 | Bushes block AI sight | A dedicated `AISight` trace channel, both sight paths on it, a sight-blocker collision setup for foliage |
| A2 | The R2c deletions | Duplicate lighting actors removed, gated on a sun-trace reading only DJ can take |
| A3 | Perception hysteresis | The custom component's distance filter gets the engine's 20% margin |

`CLAUDE_STATE.md` lives in the PUNCH_COMBAT project root, not in this repo. The agent reads
it first; it was updated with the phase board, the animation assets, the PunchYawFixMap
warning and the katana decision. Everything below is written on the facts in this repo plus
the engine facts in "Notes" at the bottom.

Paste everything between the rules into the Claude Code + Unreal MCP session with
PUNCH_COMBAT open.

---

PUNCH_COMBAT. Confirm the loaded project before touching anything.
Standing rule check: every MCP call in the log since your last marker is yours.
Blueprint only, no C++. Do not start PIE.
Never edit anything under /Game/AAMS/ or /Game/TMS/ in place.

If any modal dialog opens, STOP and tell me, make no further calls. Do not attempt to
create a Blueprint Function Library, an Enumeration, a Struct or a Behavior Tree.

Read `CLAUDE_STATE.md` in the project root before anything else. It has the phase board,
the animation assets, the PunchYawFixMap warning and the katana decision. Phase B in that
file is context only. **You are closing Phase A. You do not start B.**

## What this is

Option 4 passed. Walls block sight. Stealth has three loose ends — bushes, the R2c
deletions, hysteresis — and then it is closed. Do them in this order, commit each, stop at
the end and report. Nothing else: no combat, no animation import, no attack reach, no new
props. If you see something wrong that isn't one of the three, tell me, don't fix it.

Two of the three have gates only I can pass, because they need a reading taken in PIE and
I playtest by hand. Where the brief says **WAIT**, stop, print what it asks for, and make
no further calls until I answer.

## A1 — bushes block AI sight

This is a collision-channel problem, not a perception one. The bush must stop a sight trace
and nothing else.

### A1a. Recon — read and report, change nothing

1. Every bush or foliage thing in TESTMAP: `BP_BUSH` instances (placed in Brief D step 3),
   any other actor whose mesh is a bush/plant, and any painted foliage
   (`InstancedFoliageActor` present? which Foliage Types?). Name each.
2. For each: the mesh component (or Foliage Type), Collision Enabled, Object Type, Collision
   Preset name or `Custom`, and the response to **every** channel. Also the static mesh's
   collision geometry: does it have simple collision at all, and what is its Collision
   Complexity? A mesh with no collision primitives and complexity not set to use complex
   cannot be hit by a trace whatever its responses say.
3. Project Settings → Engine → AI System → Default Sight Collision Channel: current value.
4. Project Settings → Engine → Collision: list every existing custom Object and Trace
   channel with its default response. Is there already one named `AISight` or anything
   sight-like?
5. Option 4's line trace in the custom perception component: the exact node, its Trace
   Channel (built as Visibility), whether Trace Complex is ticked, what is in Actors to
   Ignore, and how a hit is interpreted — is "blocked" `hit AND hit actor != target`, or
   just `hit`?
6. The `Pawn` and `CharacterMesh` presets: their response to Visibility and Camera. (They
   ship as Ignore for both; confirm.)
7. Can your tooling edit Project Settings → Collision and → AI System at all? Yes / no.

Print all of it. **WAIT.** If 7 is no, I add the channel and the two settings by hand (see
"By hand" below) and tell you when they're in; you then continue from A1d.

### A1b. The channel

New **Trace** channel `AISight`, **Default Response = Block.** Not Ignore. Not Overlap.
Default Block is mandatory: every wall, floor and prop in the game inherits that default and
keeps blocking sight with no per-mesh work. If it defaults to Ignore, nothing blocks sight
and every guard gets x-ray vision across the whole map in one step.

Confirm by reading `Config/DefaultEngine.ini`: under `[/Script/Engine.CollisionProfile]`
there must be a `+DefaultChannelResponses=(Channel=ECC_GameTraceChannel<N>,
DefaultResponse=ECR_Block,bTraceType=True,...,Name="AISight")` line. `ECR_Block` or stop.
Do **not** edit that ini by hand while the editor is open — if the tooling cannot add the
channel through settings, that's the WAIT above.

### A1c. Both sight paths on it

- Project Settings → Engine → AI System → Default Sight Collision Channel = `AISight`.
- Option 4's line trace → Trace Channel `AISight`.

Both. If they disagree you get a guard whose two sight paths contradict each other, which
is near-impossible to debug from symptoms. While you're on that node, make them agree on
the other two things too:

- **Trace Complex ticked.** The engine's sight trace is a complex trace; a simple trace
  against a leaf-card bush with no simple collision hits nothing.
- **A hit whose actor is the target counts as SEEN**, not blocked, and the owning pawn is in
  Actors to Ignore. The engine does both. Option 4 was built on Visibility, which pawns
  ignore, so it may have been relying on "no hit = seen" — on a Block-default channel the
  player's own capsule would block the trace and he would never be seen. Fix the
  interpretation, don't work around it.

### A1d. Sight-blocker collision for foliage (design call — don't reinterpret)

On the bush mesh components:

| | |
|---|---|
| Collision Enabled | Query Only (No Physics Collision) |
| Pawn | **Ignore** on plain foliage. **Overlap** on `BP_BUSH` — see below |
| Camera | Ignore — or the spring arm jumps every time he brushes one |
| Visibility | Ignore — keeps bushes out of unrelated gameplay traces |
| AISight | **Block** |
| everything else | leave as found |

`BP_BUSH` keeps **Pawn = Overlap**, not Ignore. Its begin/end overlap drives the material
swap and the `BPI_STEALTH_OBJECT` messaging; Ignore silently kills both, and Overlap already
lets the player walk through. The hiding-prop feature is parked, but it is not to be broken.

Painted foliage (if the recon found any): collision is authored on the **Foliage Type**
(its Body Instance / collision section), not per instance and not on the mesh. Report the
Foliage Type's current collision before changing it, change it there, then confirm the
placed instances picked it up — instances painted before a collision change can keep the
old values and need the type re-applied.

Make it reusable: if the tooling can create a collision **preset**, add one named
`SightBlocker` with the plain-foliage values above and apply that to the foliage meshes
(`BP_BUSH` stays Custom because of its Pawn = Overlap). Smoke, curtains, tall grass and
frosted glass all become sight blockers without becoming walls by picking the preset. If
presets can't be created, set the responses per component and say so.

### A1e. Pawns and the "touches everything" check (design call — don't reinterpret)

Changing the sight channel touches **every** sighting in the game. Two consequences:

- `Pawn` and `CharacterMesh` presets: set their response to `AISight` to **Ignore**, matching
  what they do for Visibility today. Otherwise one guard standing in front of another hides
  the player from the second, which option 4 never did. I want today's behaviour preserved;
  pawn-occludes-pawn is a separate decision for later.
- Then verify, without PIE, from the editor: a guard's line trace (Option 4's node, or a
  temporary one-shot trace on the same channel) from a guard position to the player start
  **is blocked by a solid wall** and **is not blocked across open ground**. If walls stop
  blocking, the channel's default response is Ignore — go back to A1b and fix the channel.
  Do **not** start adding Block responses to geometry one mesh at a time.

Compile everything touched. Log clean of `Accessed None` after loading TESTMAP. Remove any
temporary trace before committing.

Commits: `stealth: AISight trace channel` · `stealth: both sight paths on AISight` ·
`stealth: foliage sight-blocker collision`.

## A2 — the R2c deletions

In this order, no shortcuts. The original gate was unsatisfiable: the map is frozen at 22:00
and the night gate (`bIsNight`) skips the sun trace, so the reading cannot be taken at
night. Step 1 exists only to make it takeable.

1. On the DaySequence actor, set the time of day to **12.0 (midday)** using the same
   property you froze it with in R2c. Run Day Cycle stays false. Save the level (the value
   lives in the level). Make sure a readout of the sun-trace result exists: if nothing
   prints it today, add a temporary `Print String` of `Closest Ray Distance` and of
   `bIsNight`, key `SUNTRACE`, duration 0.5, in the same place the `STEALTH` print lives.
   Commit: `stealth: midday for R2c reading (temporary)`. **WAIT.**
2. I read the sun-trace value standing in the open vs under cover. **They must differ**,
   and `bIsNight` must print false. I'll give you both numbers. If they do not differ, the
   SUN re-point failed and **nothing gets deleted** — report and stop A2 there; go on to A3.
3. Re-freeze at **22:00**, Run Day Cycle false. Read both back and print them. Remove the
   temporary print. Save the level. Commit: `stealth: re-frozen 22:00`.
4. Quarantine first, delete second:
   - Commit the current state as `stealth: pre-R2c-deletion` so one revert restores the
     level.
   - For `DirectionalLight_0`, `SkyLight_0`, `SkyLight_1`, `SkyAtmosphere_0`,
     `VolumetricCloud_0`, `VolumetricCloud_1`: move them into a World Outliner folder
     `_TO_DELETE`, set Affects World off on the lights and Hidden on the rest. Nothing
     deleted yet.
   - `ExponentialHeightFog_0`: compare its fog values (density, height falloff, inscattering
     colour, start distance, volumetric fog on/off, and anything else non-default) against
     the fog component the DaySequence actor owns, if it owns one. **Identical → quarantine
     with the others. Different or no such component → leave it alone** and print the
     values side by side.
   - Confirm exactly **one** actor tagged `SUN` carrying a DirectionalLightComponent tagged
     `SUN` remains, and it is the DaySequence one. Save. **WAIT.**
5. I check the night readings: lamp ~1.0, dark gap ~0.5, crouched ~0.4, crouched under roof
   ~0.2. Unchanged → I say go → you delete the quarantined actors, save the level, commit
   `stealth: R2c deletions`. Changed → you move them back out of the folder, restore
   Affects World / visibility, and report which reading moved.

## A3 — perception hysteresis

The custom component's distance filter has none, so `bSeen` can flicker at the stealth-
scaled boundary. Mirror the engine's own 20% margin (SightRadius vs LoseSightRadius):

- **validate** when `distance <= factor × 1000`
- **invalidate** when `distance > factor × 1200`
- once seen, stay seen out to the wider radius.

Build it as one `Select` on the existing seen state: threshold multiplier = `bSeen ? 1200 :
1000`, then the one comparison. No second variable, no timer. **Do not change** BASE SIGHT
RADIUS, LoseSightRadius, MemoryWindow or the stealth formula. If the filter is per target
actor rather than a single `bSeen`, the seen state used for the Select is that target's.

Compile. Log clean. Commit: `stealth: perception hysteresis 1000/1200`.

## By hand (only if A1a item 7 is no)

Three things in Project Settings, under a minute, and you tell the agent when they're in:

1. Engine → Collision → Trace Channels → **New Trace Channel**: Name `AISight`, Default
   Response **Block**.
2. Engine → AI System → **Default Sight Collision Channel** → `AISight`.
3. Engine → Collision → Preset → `Pawn` and `CharacterMesh`: `AISight` → **Ignore**.

## Verify — outcomes, not steps

What the agent checks from the editor, no PIE:

- `DefaultEngine.ini` carries `AISight` with `DefaultResponse=ECR_Block` and `bTraceType=True`.
- AI System's Default Sight Collision Channel and option 4's trace node both read `AISight`;
  the node has Trace Complex ticked and treats a target-owned hit as seen.
- Every bush mesh in TESTMAP: AISight Block, Camera Ignore, Visibility Ignore, Query Only;
  `BP_BUSH` Pawn Overlap, others Pawn Ignore.
- `Pawn` and `CharacterMesh` presets ignore AISight.
- A one-shot editor trace on AISight is blocked by a wall and clear across open ground.
- Exactly one `SUN`-tagged directional light (A2 reached step 4 or not — report which).
- Hysteresis: the Select reads 1200 when seen, 1000 when not; nothing else in the filter
  moved.
- Every touched asset compiles; TESTMAP loads with a log clean of `Accessed None`.

What I check in PIE — stealth is closed when all eight pass:

1. Behind a bush in a guard's line of sight: NOT seen.
2. Walk THROUGH the bush: I pass through, the camera does not jump.
3. Behind a solid wall: still not seen.
4. In the open at medium range: SEEN. Sight still works at all.
5. Walk slowly to the edge of detection: it latches cleanly, no flicker in and out.
6. Guard chases me up the stairs: smooth, no stop-and-go.
7. Night readings after the deletions: lamp ~1.0, dark gap ~0.5, crouched ~0.4, crouched
   under roof ~0.2.
8. Log clean of `Accessed None`.

Save all. Do NOT start PIE. Update `CLAUDE_STATE.md`: phase board A1–A3 done or where each
stopped, the `AISight` channel and the `SightBlocker` profile as standing facts, the Pawn /
CharacterMesh ruling, what A2 deleted or didn't and why.

**STOP HERE. Report. Do not start Phase B.** Not S6c, not attack reach, not the animation
audit, not the defensive kit, not the katana. Phase B begins when I say stealth is closed.

Report anything you did differently from this brief and why. If any of this is wrong or
unbuildable, say so before building it. I'd rather respec than have you force my shape onto
working code.

Invariants: PunchYawFixMap 90/90/90/95/90/90 + Block 90 · FootIKRestAlpha 0.4 ·
Layered Blend spine_01 / depth 3 / Mesh Space Rotation on · Blend Poses by Bool
0.15/0.15 · DefaultSlot and UpperBody intact · all assets compile clean · log clean of
Accessed None.

---

## After this session

- The eight-point playtest above. All eight pass → say "stealth is closed" and Phase A is
  done. Any fail → back to the matching section, one fix, one commit.
- Then, and only then, Phase B. Order as in `CLAUDE_STATE.md`: B1 S6c (punch graph onto the
  component's `Attack()` — before any animation import, so there is one place selecting
  montages) → B2 attack reach (a `bDrawAttackTrace` flag first; measure before touching
  TraceRadius 15 / CombatRange 150 or the AI acceptance radius) → B3 the Combat Master
  "Dynamic hand to hand V1 & V2" audit, in-place vs root-motion, root motion OR the yaw fix
  per clip, never both, no bulk import → B4 parry / counter / perfect dodge. Phase C is the
  katana, end to end, after B closes.
- Parked and staying parked: phone, factions, arena, grab/throw, attack tokens, aerial
  takedown, GASP, haystacks, the bush as a hiding **prop** (enter/exit states on
  `BPI_STEALTH_OBJECT`). A1 is line of sight only.

## Notes — the engine facts this brief leans on

Checked against engine documentation and the AI module's sight sense on 1 Oct 2026; the
agent re-confirms anything it can read from the project.

- **AI Perception sight** traces on one global channel, `Default Sight Collision Channel`,
  Project Settings → Engine → AI System, default Visibility. There is no per-sense-config
  channel; the only finer control is C++ (`IAISightTargetInterface`), which is out.
- The engine's sight trace is a **complex** line trace, ignores the **listener** and the
  **target**, and treats a hit on something owned by the target as seen. Option 4's trace
  must match on all three or the two sight paths disagree (A1c).
- A new trace channel's **Default Response** is what every preset and every Custom component
  answers with unless it stores an override; components store only non-default responses.
  So Default Block makes all existing geometry block the new channel at once, and Default
  Ignore makes nothing block it (A1b). The channel lands in `DefaultEngine.ini` under
  `[/Script/Engine.CollisionProfile]` as `+DefaultChannelResponses=(... Name="AISight")`.
- `Pawn` and `CharacterMesh` presets ignore Visibility and Camera by default, which is why
  guards see through other pawns today. A Block-default channel reverses that unless the
  presets get an explicit Ignore (A1e). Related: a trace on a Block-default channel hits the
  target's own capsule, so "no hit = seen" logic breaks.
- Traces only hit **collision geometry**. A static mesh with no simple collision and
  complexity left at "Project Default" is hit only by a complex trace; one set to "Use
  Simple Collision As Complex" with no primitives is never hit (A1a item 2, A1c).
- **Painted foliage** collision is set on the Foliage Type's Body Instance, applies to every
  instance of that type, and cannot be set per instance; instances painted before a change
  can keep stale collision until the type is re-applied (A1d).
- **Day Sequence** (UE 5.5+ plugin): the actor owns the sun, sky light, atmosphere, clouds
  and (in the shipped template) a height fog; `bRunDayCycle` gates playback, time of day is
  in hours (`SetTimeOfDay`), and per-instance values live in the level (A2).
- Engine sight hysteresis is `SightRadius` / `LoseSightRadius`; A3 copies the ratio
  (1000 → 1200) into the custom filter and leaves the engine values alone.
