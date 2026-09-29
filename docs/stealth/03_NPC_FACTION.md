# Brief C — NPC base with a faction channel (design + brief skeleton)

Runs only after Brief B compiles and you've played it. Answer C1–C5 in BLANKS.md first; the
brief at the bottom has `«…»` slots for them.

## What we're building

One `BP_NPC_Base` character that civilians, companions, soldiers, animals and enemies all
derive from, plus a faction relation table, plus perception that reads the player's stealth
factor. Factions can be hostile to each other, so two enemy factions fight when they meet.

## The one engine fact that shapes the design

Unreal's AI Perception filters "detect enemies / neutrals / friendlies" through
`IGenericTeamAgentInterface`. In Blueprint you can set an AIController's team id
(`Set Generic Team Id`), but the **attitude solver is C++ only**, and its default is: same
team → Friendly, any other team → Hostile. There is no Blueprint way to make team 3 neutral
to team 5 but hostile to team 7.

So we don't use the built-in attitude at all. Every NPC's perception detects **all
affiliations**, and a Blueprint function `GET_ATTITUDE(MyFaction, TheirFaction)` looks the
pair up in a relation table. That's the faction channel. It costs one table lookup per
perceived actor per update, which is nothing.

This is a documented workaround, not a hack — it's how most Blueprint-only projects with
more than two sides do it.

## Data

The MCP tooling cannot create structs or enums. So:

- **Faction id is a `Name`** (`Player`, `Civilian`, `Companion`, `Soldier`, `Animal`,
  `Enemy_A`, `Enemy_B` — final list is C1). A Name compares fast, reads in the details
  panel, and needs no enum asset.
- **Attitude is an `Integer`**: `0 Hostile · 1 Neutral · 2 Friendly`. Same reason.
- **Relation table**: if `S_FactionRelation` from FREESMOKE_001 has the shape
  `{FactionA: Name, FactionB: Name, Attitude: int}` (C5), migrate it and build a DataTable
  `DT_FactionRelations` on it. If it doesn't, you create the struct by hand in the editor
  before the session (30 seconds) — the agent can't.
- Lookup rule: try `(A, B)`, then `(B, A)`, else **Neutral**. Unlisted pairs are neutral by
  default so a new faction is safe until you say otherwise. Same faction is always Friendly
  without a lookup.

Proposed starting table (edit freely):

| A | B | Attitude |
|---|---|---|
| Player | Companion | Friendly |
| Player | Civilian | Neutral |
| Player | Soldier | Neutral |
| Player | Enemy_A | Hostile |
| Player | Enemy_B | Hostile |
| Companion | Enemy_A | Hostile |
| Companion | Enemy_B | Hostile |
| Soldier | Enemy_A | Hostile |
| Soldier | Enemy_B | Hostile |
| Enemy_A | Enemy_B | Hostile |
| Animal | Enemy_A | Hostile |
| Animal | Enemy_B | Hostile |
| Civilian | Enemy_A | Hostile (they flee, but it's the same attitude) |

## Class layout

```
Character
└── BP_NPC_Base                     Faction (Name) · Archetype (Name) · BPC_Faction
    ├── BP_NPC_Civilian             flees hostiles, never attacks
    ├── BP_NPC_Companion            follows Player, attacks Player's hostiles
    ├── BP_NPC_Soldier              patrols, attacks hostiles
    ├── BP_NPC_Animal               wanders; predator/prey split is C3
    └── BP_NPC_Enemy                attacks hostiles — Enemy_A and Enemy_B are the SAME class
                                    with a different Faction value on the instance
```

Behaviour differences live in the AIController + BT tasks, selected by `Archetype`. The
character classes are thin: mesh, faction default, archetype default. Enemy_A vs Enemy_B is a
details-panel value, never a class.

- **`BPC_Faction`** (ActorComponent, goes on `BP_NPC_Base` AND on the player character):
  `Faction (Name)`, `GET_ATTITUDE(Other: Actor) → int` (reads the other actor's BPC_Faction
  through an interface; missing component → Neutral), `IS_HOSTILE(Other)`, `IS_FRIENDLY(Other)`.
  Also on the player so NPCs can ask about the player through the same path.
- **`BPI_Faction`**: `GetFaction → Name`. Implemented by `BP_NPC_Base` and the player character,
  forwarding to the component. Cross-actor calls go through the interface, never a cast to
  a component class the tooling can't see.
- **`AIC_NPC_Base`** (AIController): AIPerception with Sight (detect all affiliations),
  Hearing, Damage. `On Target Perception Updated` → `VALIDATE_PERCEIVED(Actor, Stimulus)`.
- **Behavior Tree `BT_NPC_Base`**: the tooling cannot create the tree asset — you make an
  empty tree + blackboard by hand before the session. The agent authors the Blackboard keys,
  the BTTask/BTService Blueprints and the controller. Thin tree, fat tasks. EQS is off the
  table.

## Where stealth plugs in — `VALIDATE_PERCEIVED`

This is the function the old `BP_AI_STEALTH_DUMMY` had and lost (bug 1 was that it built
its filtered list into a local and never copied it back). Rewritten, in the controller:

```
VALIDATE_PERCEIVED(Actor, Stimulus)
├─ Attitude = BPC_Faction.GET_ATTITUDE(Actor)
├─ Attitude != Hostile → clear any blackboard target that equals Actor → return
├─ Stimulus is Sight:
│    ├─ Actor implements BPI_STEALTHFACTOR_PROVIDER?
│    │    └─ yes: SF = GET STEALTH FACTOR           // 1.0 visible … 0.1 hidden
│    │       no:  SF = 1.0
│    ├─ Dist = Distance(Pawn, Actor)
│    ├─ EffectiveRange = SightRadius × SF            // hidden = seen only up close
│    └─ Stimulus.SuccessfullySensed AND Dist <= EffectiveRange
│         → Blackboard.TargetActor = Actor, LastKnownLocation = Actor.Location
│         else → if TargetActor == Actor: TargetActor = None, keep LastKnownLocation
├─ Stimulus is Hearing or Damage → Blackboard.LastKnownLocation = Stimulus.Location
│    (Damage also sets TargetActor regardless of stealth — getting hit reveals you)
└─ writes go straight to the Blackboard, never to a local that's forgotten
```

Two things this needs from Brief B: `BPC_STEALTH_SYSTEM` must implement
`BPI_STEALTHFACTOR_PROVIDER` on the player (the interface exists and nothing calls it — this
is what it was for), and the player character forwards `GET STEALTH FACTOR` to the component.
That's a two-node addition and is the first step of Brief C, not part of B.

**Range, not chance.** Stealth scales *how far* you can be seen, not a dice roll. It's
deterministic, so you can learn it: crouched in a bush at 0.5, a guard with 1500 sight sees
you at 750. That's tunable per archetype later with a `StealthSensitivity` multiplier on the
controller (animals high, civilians low).

## NPC-vs-NPC combat

Same path. A Soldier's perception sees an Enemy_A; `GET_ATTITUDE` says Hostile; the NPC has
no `BPI_STEALTHFACTOR_PROVIDER` so SF = 1.0; it becomes the target. The BT's attack task
calls into whatever PunchCombat exposes for an NPC attacker — **that's the join with the
combat AC and it's a blank until B is done and we've read PunchCombat's surface** (C4). Until
then the attack task is a Print String and a move-to, which is enough to watch two factions
close on each other.

Target selection when several hostiles are perceived: nearest hostile wins, re-evaluated by
a BTService every 0.5 s. No threat scoring in the first pass.

## Brief C skeleton (finish after C1–C5 are answered)

```
PUNCH_COMBAT. Confirm the loaded project before touching anything.
Standing rule check: every MCP call in the log since your last marker is yours.
Blueprint only, no C++. Do not start PIE.
Never edit anything under /Game/AAMS/ or /Game/TMS/ in place.
If any modal dialog opens, STOP and tell me, make no further calls. Do not attempt to
create a Function Library, Enum, Struct or Behavior Tree.

Recon, change nothing: confirm BPC_STEALTH_SYSTEM and BP_DARKNESS_DETECTION are on «P1»
and compile; confirm DT_FactionRelations, BT_NPC_Base and BB_NPC_Base exist (I made them
by hand); report «P1»'s existing AIController if any, and PunchCombat's public functions
and dispatchers by name and signature. Report, then wait.

1. BPC_STEALTH_SYSTEM implements BPI_STEALTHFACTOR_PROVIDER: GET STEALTH FACTOR returns
   CURRENT STEALTH FACTOR. «P1» implements it too and forwards to the component. Commit.
2. BPI_Faction (GetFaction → Name). BPC_Faction per the design; Faction default
   «Player» on the player. Attach to «P1». Commit.
3. Blackboard keys on BB_NPC_Base: TargetActor (Object:Actor), LastKnownLocation (Vector),
   HomeLocation (Vector), Archetype (Name). Commit.
4. AIC_NPC_Base: perception (Sight «radius» / «lose radius» / «FOV», detect all
   affiliations; Hearing «range»; Damage), VALIDATE_PERCEIVED exactly as the design,
   runs BT_NPC_Base on possess. Commit.
5. BP_NPC_Base: Character, BPC_Faction, AIC_NPC_Base as controller, auto-possess placed
   and spawned, Faction/Archetype instance-editable. Mesh «mannequin per C4». Commit.
6. Children: Civilian, Companion, Soldier, Animal, Enemy — thin, defaults only. Commit.
7. BT tasks as Blueprints: BTT_MoveToTarget, BTT_MoveToLastKnown, BTT_Flee (away from
   TargetActor, «distance»), BTT_FollowPlayer («Companion»), BTT_Attack (Print String +
   stop; the PunchCombat call comes later), BTS_SelectNearestHostile (0.5 s).
   I wire the tree by hand from your task list. Commit.
8. Test scene in «P7»: one Soldier, one Enemy_A, one Enemy_B placed 800 units apart in a
   triangle, one Civilian, one Companion near player start. Save the level. Commit.

Verify: log clean of Accessed None on load · a Soldier and an Enemy_A print each other as
targets within 2 s of spawn · the two Enemies target each other · the Civilian's
TargetActor stays None with the player standing in front of it · the player crouched in
the bush at 700 units from an Enemy is NOT targeted; standing at the same spot IS.

Save all. Do NOT start PIE. Report anything done differently and why. If any of this is
wrong or unbuildable, say so before building it.

Invariants: PunchYawFixMap 90/90/90/95/90/90 + Block 90 · FootIKRestAlpha 0.4 ·
Layered Blend spine_01 / depth 3 / Mesh Space Rotation on · Blend Poses by Bool
0.15/0.15 · DefaultSlot and UpperBody intact · all assets compile clean · log clean of
Accessed None.
```
