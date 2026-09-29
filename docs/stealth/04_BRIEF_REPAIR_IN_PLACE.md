# Brief D — repair the migrated stealth system in place (PUNCH_COMBAT)

**This supersedes Briefs A and B.** `/Game/STEALTH_SYSTEM/` and `/Game/STEALTH_HIDER/` are
already migrated into PUNCH_COMBAT. The Blueprints don't compile only because they reference
folders that don't exist in this project (AAMS, TMS, P0Debug, PhoneSystem). Their graphs
are intact — the 29 Sep recon read them here. The `Character` variable in both components
has already been re-pointed to the ThirdPerson character by hand.

So there is nothing to extract and nothing to rebuild. Fix the dangling references, wire
the two components to the character, drop a test scene in, save. Exact behaviour otherwise
— bugs included; the bug pass in `02_BRIEF_B_REBUILD.md` still applies afterwards.

Paste everything between the rules into the Claude Code + Unreal MCP session with
PUNCH_COMBAT open.

---

PUNCH_COMBAT. Confirm the loaded project before touching anything.
Standing rule check: every MCP call in the log since your last marker is yours.
Blueprint only, no C++. Do not start PIE.
Never edit anything under /Game/AAMS/ or /Game/TMS/ in place.

If any modal dialog opens, STOP and tell me, make no further calls. Do not attempt to
create a Blueprint Function Library, an Enumeration, a Struct or a Behavior Tree.

## What this is

`/Game/STEALTH_SYSTEM/` was migrated here from another project. Its Blueprints hold a
working stealth system but fail to compile because a handful of nodes reference classes
from folders that don't exist in this project. Your job is the smallest set of edits that
makes every asset in that folder compile, gets the two components onto the player, and
gives me a scene to test in. **You are not improving the system.** Every graph stays as it
is except the nodes named below. There is a known bug list; it gets fixed later, one bug per
session, after I've played the faithful version. If you see something that looks wrong and
isn't on the list below, tell me, don't fix it.

## Recon — read and report, change nothing

1. List every asset under `/Game/STEALTH_SYSTEM/` and `/Game/STEALTH_HIDER/`: path, class,
   parent, compiles y/n. For each that fails, **every** compiler error and warning verbatim,
   with the graph and node it points at. I need the complete list, not the first three.
2. Find the player: the GameMode's Default Pawn Class in the default map. Report its name,
   parent class, and its component list. Name the PunchCombat ActorComponent on it (call
   it COMBAT below). Report how crouch is wired on it: does it call `Crouch`/`UnCrouch`,
   from which Input Action, Started/Completed or toggle? If there's no crouch, say NONE.
3. On both `BP_DARKNESS_DETECTION` and `BPC_STEALTH_SYSTEM`: what is the `Character`
   variable typed as right now, and where is it assigned? Is either component already
   attached to any actor in this project?
4. Which socket or bone name is on `ROOF ABOVE`'s start node (the head socket), and does the
   player's skeleton have it? List every socket/bone on that skeleton whose name contains
   `head`.
5. `git status` in the project root. No repo → say so.
6. Read the five function-local defaults and print them:
   TRACE SUN → `loacal_MIN RAY DISTANCE` · ROOF ABOVE → `local GRID SIZE HALF`,
   `local GRID CELL DISTANCE`, `HAS A ROOF` · GET MAX STEALTH FACTOR →
   `local_CURRENT MAX FACTOR`. Use any tool that exposes locals; if none does, say
   UNREADABLE for each — do not guess from raw bytes. (Optional: run
   `tools/ue_dump_bp_locals.py` from the docs repo in the editor Python console; it writes
   `Saved/stealth_spec/LOCALS.md`.)

Print all of it. **Then wait for my go.** If crouch is NONE, or the player has no head
bone, stop there — I decide.

## Step 0 — baseline

No git repo → `git init`, Unreal `.gitignore` (Binaries, DerivedDataCache, Intermediate,
Saved, .vs, *.sln), commit everything as `pre-stealth-baseline`. Repo exists → commit the
current state under that message. Nothing else in this step.

## Step 1 — fix the dangling references, one Blueprint at a time

Work through the recon's error list. For each error the fix is one of these four; if an
error doesn't fit any of them, stop and ask.

- **Cast to an AAMS / TMS / P0 class** (e.g. the MotionMatching character, `BP_P0Character`):
  replace the Cast with a Cast to PLAYER (the character from recon 2). Where the cast result
  fed a pin that only needs an Actor or a Character (GetActorLocation, GetMesh, GetCapsule),
  use the `Character` variable directly instead of a cast.
- **`BP_P0Character` TextRender debug write** in `calculate current stealth factor` step 4:
  replace with a `Print String` of `CURRENT STEALTH FACTOR`, duration 0.5, key `STEALTH`,
  wired into the same exec slot. Nothing else in that Sequence changes.
- **`ANIM INSTANCE`**: the variable stays; any node that sets it from an AAMS anim class is
  removed and its exec pins bridged. Nothing reads it.
- **PhoneSystem perception on `BP_AI_STEALTH_DUMMY`**: do not fix. Move
  `BP_AI_STEALTH_DUMMY` to `/Game/STEALTH_SYSTEM/_TO_DELETE/` and leave it uncompiled. It's
  rebuilt later as the NPC base. Do not delete it.

Compile after each Blueprint. Commit each: `stealth: <AssetName> compiles`.

Rules while you're in there: the ForEach-with-Break in TRACE SUN keeps its unwired Break.
The roof end point keeps its `× t + (0,0,2000)` form. The BeginPlay light scan keeps its
Set. `STOP CROUCH` stays inside the overlap loop. These are the known bugs and they stay
until the bug pass.

## Step 2 — attach to the player

On PLAYER:

1. Add `BP_DARKNESS_DETECTION` and `BPC_STEALTH_SYSTEM` as components. COMBAT untouched.
2. At the character's BeginPlay, set each component's `Character` variable to `Self`. Use
   the existing BeginPlay chain; add a Sequence pin if there is none. Do not reorder what's
   there.
3. Crouch: on the existing crouch Input Action — **Started** → `BPC_STEALTH_SYSTEM.START
   CROUCH`; **Completed** → `STOP CROUCH`. If crouch is a toggle, START on the toggle-on
   branch, STOP on the toggle-off branch.
4. If the head socket on ROOF ABOVE's start node doesn't exist on this skeleton, change
   that one node's socket name to the head bone from recon 4. Nothing else.
5. Compile PLAYER. Output log clean of `Accessed None`, `Cast failed`, `Failed to find
   function` after loading the default map.

Commit: `stealth: attached to PLAYER`.

## Step 3 — test scene

In the default map (or the map PLAYER's GameMode is set on), without touching anything
already placed:

- One `BP_LIGHT_EMITTER` on open floor.
- One `BP_BUSH` about 400 units away. If its material slots are empty because the art
  didn't migrate, leave them — the overlap logic still runs.
- A roofed box about 400 units the other way: three walls and a ceiling of any static mesh,
  tall enough to walk under.
- The map's directional light: add tag `SUN` to the **actor** and tag `SUN` to its
  **DirectionalLightComponent** (both — BeginPlay looks for both). No directional light →
  add one and tag it.

Save the level. Per-instance values live in the level file. Commit: `stealth: test scene`.

## Verify — outcomes, not steps

- Every asset under `/Game/STEALTH_SYSTEM/` compiles except the one in `_TO_DELETE/`.
- Loading the map prints `SUN IS UP`, not `NO SUN`.
- Standing in the open under the sun: `STEALTH` reads `1.0`.
- Crouched in the open: drops to `0.9` or below within a second.
- Crouched in the bush: `0.5` or below.
- Un-crouching in the open: report whether the print returns to `1.0`. I expect it to stick
  (bug 2). Report either way.
- Under the roofed box: report the value. I expect the roof term to be dead (bugs 5, 6).
- Walking into the lamp's sphere: add a temporary Print of `POINTLIGHTS` length in the
  overlap handler, confirm it reads 1, remove the print before the commit.

Save all. Do NOT start PIE — I playtest by hand. Print the five local defaults again at the
end, next to the observed values, so I can see whether bugs 6 and 8 are live.

Report anything you did differently from this brief and why. If any of this is wrong or
unbuildable, say so before building it. I'd rather respec than have you force my shape onto
working code.

Invariants: PunchYawFixMap 90/90/90/95/90/90 + Block 90 · FootIKRestAlpha 0.4 ·
Layered Blend spine_01 / depth 3 / Mesh Space Rotation on · Blend Poses by Bool
0.15/0.15 · DefaultSlot and UpperBody intact · all assets compile clean · log clean of
Accessed None.

---

## After this session

- Playtest. Crouch in the open, in the bush, under the box, next to the lamp. Watch the
  `STEALTH` number.
- Then the bug pass: `02_BRIEF_B_REBUILD.md` → "Bug pass (B2)". Bug 2 first; it's the one
  you'll feel.
- Then `03_NPC_FACTION.md`.
