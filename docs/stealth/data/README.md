# Faction relation table

`DT_FactionRelations.csv` imports straight into Unreal as a DataTable. Attitude: `0 Hostile
· 1 Neutral · 2 Friendly`. Same faction is always Friendly and is not listed. Unlisted pairs
are Neutral. Each pair appears once; the lookup tries `(A,B)` then `(B,A)`.

## Import (one-time, by hand — the MCP tooling can't create structs)

1. In PUNCH_COMBAT, Content Browser → `/Game/STEALTH_SYSTEM/Data/` → right-click →
   Blueprints → **Structure** → name it `S_FactionRelation`. Fields, exactly:
   - `FactionA` — Name
   - `FactionB` — Name
   - `Attitude` — Integer (default 1)

   If Brief A reports FREESMOKE_001's `S_FactionRelation` already has this shape, migrate
   that instead and skip this step.
2. Right-click the CSV in Explorer → drag into the same folder → in the import dialog pick
   **DataTable**, row type `S_FactionRelation`. Name the asset `DT_FactionRelations`.
3. Open it and check 21 rows landed with the right numbers.

Edit the CSV and re-import to change relations; don't edit the DataTable by hand or the
next import overwrites you.

## Starting factions

`Player · Companion · Civilian · Soldier · Animal · Enemy_A · Enemy_B`. Rename or add in the
CSV; a faction is just a Name that appears in a row. Civilians are Friendly to Soldiers so
soldiers defend them; Animals are Neutral to everyone but the Enemy factions (predator/prey
split is open — see BLANKS C3).
