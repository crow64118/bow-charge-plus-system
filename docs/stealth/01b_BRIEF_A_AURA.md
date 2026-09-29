# Brief A, Aura edition — same extraction, for the in-editor agent

Use this instead of `01_BRIEF_A_EXTRACT.md` if you'd rather run the extraction in Aura
(it already read these assets once on 29 Sep and its `unreal_inspector` server is read
only, which suits this job). Paste as one message. Put Aura in **Agent** mode with the
`unreal_inspector` server only; `unreal_editor` is not needed and should stay off.

---

Read only. Do not modify, save or compile any asset. Write text files under
`Saved/stealth_spec/` and nothing else. If a tool would change an asset, don't call it.

You read `/Game/STEALTH_SYSTEM/` on 29 Sep and produced `Saved/stealth_recon/`. That was a
report for a human. This time produce a **build spec for another agent** in a different
project that cannot see this one: every node, every pin default, every link, every class
default, per Blueprint, in `Saved/stealth_spec/<AssetName>.md`. Standard: reproducible
node for node by someone with only your files. Where you can't read something, write the
word UNREADABLE next to it. Never fill a gap with a plausible value.

Scope: every asset under `/Game/STEALTH_SYSTEM/` and `/Game/STEALTH_HIDER/`, plus
`S_FactionRelation` and `BPI_CombatRelay` wherever they live. Start with an inventory
(`00_INVENTORY.md`: path, class, parent, compiles y/n, first three errors if not).

Per Blueprint file, in order: class settings · components with every non-default property
(collision per channel, tags, transforms, light values, materials) · variables with type,
category, default, flags · dispatchers · functions and macros with inputs, outputs, pure
flag, **local variables with defaults** · every graph as a numbered node list with all pin
defaults and links as `N1.pin -> N2.pin`, exec links included, comment boxes included.
Expand collapsed graphs and macros into their own sections.

The known gap is function-local defaults. First run the script at
`tools/ue_dump_bp_locals.py` from this repo through the editor's Python console (the
human will paste it if it isn't on disk); it writes `Saved/stealth_spec/LOCALS.md` and
says per strategy what failed. Then, for these five, confirm by opening the function and
reading the local's Default Value in the Details panel if any tool lets you; else
UNREADABLE:

- TRACE SUN → `loacal_MIN RAY DISTANCE`
- ROOF ABOVE → `local GRID SIZE HALF`, `local GRID CELL DISTANCE`, `HAS A ROOF`
- GET MAX STEALTH FACTOR → `local_CURRENT MAX FACTOR`

Answer these five from the asset, at the top of the relevant file under `## Confirmed
facts`:

- G1 `validate grid positions`: the exact condition under which a point is KEPT, node by node.
- G2 the component tag the point-light capsule overlap filters on, and the node that filters.
- G3 `BPI_STEALTH_OBJECT`: exact names and parameters of the two overlap functions.
- G4 `BP_LIGHT_EMITTER`: full component list.
- G5 BeginPlay light scan: is the `POINTLIGHTS` write for already-overlapping lights a Set
  or an Add? Quote the node.

Also report, changing nothing: which character Blueprint carries the two components today,
what `Character` is typed as, how it's assigned, what calls START/STOP CROUCH, and the
head-socket name on ROOF ABOVE's start node.

Finish with `99_SUMMARY.md`: files written · every UNREADABLE by location · every place
you disagree with your own 29 Sep report (its bug list is 1–9; confirm or refute each with
the node that proves it) · anything that surprised you.

Do not open PIE. Do not save. If any of this is wrong or can't be done, say so before
doing it.
