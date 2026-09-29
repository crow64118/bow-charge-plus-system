# Brief A — extract the stealth spec from FREESMOKE_001 (read only)

Paste everything between the rules into the Claude Code + Unreal MCP session with
FREESMOKE_001 open. It reads; it does not build. Output is a folder of text files you copy
into this repo as `docs/stealth/SPEC/`.

---

FREESMOKE_001. Confirm the loaded project before touching anything.
Standing rule check: every MCP call in the log since your last marker is yours.
Blueprint only, no C++. Do not start PIE.
Never edit anything under /Game/AAMS/ or /Game/TMS/ in place.

THIS BRIEF IS READ ONLY. You change nothing in /Game/. The only writes you make are text
files under `<Project>/Saved/stealth_spec/`. If any tool you reach for would modify an asset,
don't call it. If any modal dialog opens, STOP and tell me, make no further calls.

## Why

`/Game/STEALTH_SYSTEM/` works here. It is going to be rebuilt 1:1 in another project
(PUNCH_COMBAT) by a session that cannot see this one. Your output is the only thing that
session will have. So the standard is: someone with your files and no access to this
project can reproduce every node, pin default, link and class default exactly. Where you
can't read something, say so by name. Never fill a gap with a plausible value.

A previous recon (Aura, 29 Sep) already read these graphs. Its report is context, not
truth: re-read everything from the assets. Where you disagree with it, say so.

## Scope

Every asset under `/Game/STEALTH_SYSTEM/` and `/Game/STEALTH_HIDER/`. Expected, at least:

- `BP_DARKNESS_DETECTION` (ActorComponent)
- `BPC_STEALTH_SYSTEM` (ActorComponent)
- `BP_LIGHT_EMITTER`, `BP_STEALTH_ACTOR`, `BP_BUSH`, `BP_AI_STEALTH_DUMMY`
- `BPI_STEALTH_OBJECT`, `BPI_STEALTHFACTOR_PROVIDER`, a third `…LISTENER` interface
- `S_FactionRelation`, `BPI_CombatRelay` (wherever they live — report the path)
- 13 art assets under `STEALTH_HIDER/`

List the folder first and report anything not on this list before reading further.

## Step 1 — inventory

Write `Saved/stealth_spec/00_INVENTORY.md`: every asset path, class, parent class, and
whether it compiles right now. For each Blueprint that fails to compile, the first three
error messages verbatim.

## Step 2 — one file per Blueprint

For each Blueprint write `Saved/stealth_spec/<AssetName>.md` containing, in this order:

1. **Class settings**: parent class, interfaces implemented, replication flags.
2. **Components** (actors only): every component, its class, parent attachment, relative
   transform, and every non-default property — collision preset, object type, per-channel
   responses, generate-overlap, tags, light intensity/units/attenuation/colour/shadows,
   static mesh, materials, scale. "Non-default" means different from the component class's
   own default; when unsure, include it.
3. **Variables**: name, type (full — `Array<PointLightComponent>` not "array"), category,
   default value, instance-editable, expose-on-spawn, replication.
4. **Event dispatchers**: name and signature.
5. **Functions and macros**: for each — name, inputs, outputs, pure/impure,
   **local variables with their default values** (see step 3), then the graph.
6. **Event graph** and every function graph as a node list: for each node its class, title,
   every pin with its default value, and every link as `NodeA.pin -> NodeB.pin`. Number the
   nodes so links are unambiguous. Exec links included. Comment boxes included with their
   text — they often hold the designer's intent.

Read graphs node by node through the inspector tools. **Do not use the DSL reader as your
source** — it silently drops input events, macros, collapsed graphs and exec links off latent
nodes. If you use it at all, use it only to cross-check, and say where the two disagree.

Collapsed graphs and macros: expand and dump their contents the same way, named
`<Function>/<CollapsedName>`.

## Step 3 — local variable defaults (the known gap)

The previous recon could not read the default values of function-local variables. Five
matter; get all of them for every function. Try in this order and report which one worked:

1. Any inspector tool that lists function locals with defaults.
2. Editor Python: load the Blueprint, find each function graph's `K2Node_FunctionEntry`
   node, read its `LocalVariables` array; each entry has `VarName`, `VarType`,
   `DefaultValue`. Print them. Property access may be blocked; if so say exactly what
   errored.
3. Editor Python: `unreal.BlueprintEditorLibrary` — check whether any exposed function
   reaches function locals. Report yes/no.
4. If none work: for each of the five locals below, report **"UNREADABLE — DJ to check in the
   editor"** and stop trying. Do not infer a value from the raw bytes and present it as read.

The five that matter:

- TRACE SUN → `loacal_MIN RAY DISTANCE` (float)
- ROOF ABOVE → `local GRID SIZE HALF` (int)
- ROOF ABOVE → `local GRID CELL DISTANCE` (float)
- ROOF ABOVE → `HAS A ROOF` (bool)
- GET MAX STEALTH FACTOR → `local_CURRENT MAX FACTOR` (float)

## Step 4 — the five garbled facts

The previous report reached me with these lines cut off. Read each from the asset and put
the answer at the top of the relevant file under a heading `## Confirmed facts`:

- G1 `validate grid positions`: the exact condition under which a grid point is KEPT. Quote
  the Branch's input chain node by node.
- G2 Point-light capsule overlap: the exact component tag string it filters on, and which
  node does the filtering.
- G3 `BPI_STEALTH_OBJECT`: exact function names and parameter names/types of the two overlap
  functions.
- G4 `BP_LIGHT_EMITTER`: the complete component list (the report's first line was lost).
- G5 BeginPlay light scan in `BP_DARKNESS_DETECTION`: the node that writes `POINTLIGHTS` for
  already-overlapping lights — is it a Set (overwrite) or an Add? Quote it.

## Step 5 — interfaces, struct, art

- Each interface: every function, inputs, outputs, in `Saved/stealth_spec/<Name>.md`.
- `S_FactionRelation`: every field, type, default. `BPI_CombatRelay`: every function and
  signature. Also: which assets reference each of them (use the reference viewer).
- Art under `STEALTH_HIDER/`: `Saved/stealth_spec/ART.md` — every asset, its class, and for
  each material instance its parent and every overridden parameter. For each texture: size,
  compression, sRGB. Confirm the dependency chain resolves with nothing outside the folder.

## Step 6 — the character hookup as it stands today

Report, without changing it: where `BP_DARKNESS_DETECTION` and `BPC_STEALTH_SYSTEM` are
attached (which character Blueprint), what the `Character` variable is typed as now
(DJ re-pointed it to ThirdPerson), how it gets assigned (Cast on GetOwner at BeginPlay?),
what calls `START CROUCH` / `STOP CROUCH`, and what the head-socket name on the ROOF ABOVE
start node is.

## Step 7 — summary

`Saved/stealth_spec/99_SUMMARY.md`:

- The list of files you wrote.
- Every place you could not read something, by asset/function/node.
- Every place your reading disagrees with the previous recon (its bug list is 1–9; say
  which you confirm, which you refute, with the node that proves it).
- Anything in the graphs that surprised you.

## Verify

Before you report done:

- `00_INVENTORY.md` lists every asset under both folders and every one has a spec file.
- Every function in every Blueprint appears in its file with a graph dump.
- Every one of the five locals has either a value and the method that read it, or the word
  UNREADABLE.
- All five G-items have an answer or a named reason they don't.
- `git status` in the project shows no modified `.uasset` / `.umap`. If it does, tell me
  which and do not revert them yourself.

Then stop. Do not open PUNCH_COMBAT. Do not start PIE. Do not save any asset.

If any of this is wrong or unbuildable, say so before doing it. I'd rather respec than have
you force my shape onto working code.

---

## After the session

1. Copy `Saved/stealth_spec/` into this repo as `docs/stealth/SPEC/` and commit.
2. Copy the five local values and the G-answers into [BLANKS.md](BLANKS.md).
3. Answer P1–P7 in BLANKS.md (facts about PUNCH_COMBAT).
4. Then run Brief B.
