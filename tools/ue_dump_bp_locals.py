"""
Dump function-local variable defaults (and member variable defaults) from Blueprints.

Run inside the Unreal Editor Python console (Window > Output Log, switch to Python), or:
    py "C:/path/to/ue_dump_bp_locals.py"

Edit ASSET_PATHS below, or pass a folder to scan. Output goes to the log AND to
<Project>/Saved/stealth_spec/LOCALS.md so it survives the session.

Why this exists: the MCP inspector tools in use cannot read function-local defaults.
Those live on each function graph's K2Node_FunctionEntry node, in its LocalVariables
array (FBPVariableDescription: VarName, VarType, DefaultValue). This script reaches them
through reflection. Three strategies are tried in order; each one reports exactly why it
failed so the next person doesn't repeat it.

UNVERIFIED against a live editor at the time of writing. Read the log; every line that
starts with "!!" is a strategy that failed and says why.
"""

import os
import sys
import traceback

import unreal

# ---- configure -------------------------------------------------------------------------

# Either list assets explicitly...
ASSET_PATHS = [
    "/Game/STEALTH_SYSTEM/BP_DARKNESS_DETECTION",
    "/Game/STEALTH_SYSTEM/BPC_STEALTH_SYSTEM",
    "/Game/STEALTH_SYSTEM/BP_BUSH",
    "/Game/STEALTH_SYSTEM/BP_STEALTH_ACTOR",
    "/Game/STEALTH_SYSTEM/BP_LIGHT_EMITTER",
    "/Game/STEALTH_SYSTEM/BP_AI_STEALTH_DUMMY",
]
# ...or scan a folder (set to None to use the list above).
SCAN_FOLDER = "/Game/STEALTH_SYSTEM"

OUT_DIR = os.path.join(unreal.Paths.project_saved_dir(), "stealth_spec")
OUT_FILE = os.path.join(OUT_DIR, "LOCALS.md")

# ---------------------------------------------------------------------------------------

lines = []


def out(s=""):
    print(s)
    lines.append(s)


def fail(strategy, err):
    out(f"!! {strategy} failed: {type(err).__name__}: {err}")


def find_blueprints():
    if SCAN_FOLDER:
        reg = unreal.AssetRegistryHelpers.get_asset_registry()
        assets = reg.get_assets_by_path(SCAN_FOLDER, recursive=True)
        paths = []
        for a in assets:
            cls = str(a.asset_class_path.asset_name) if hasattr(a, "asset_class_path") else str(a.asset_class)
            if cls in ("Blueprint", "AnimBlueprint", "WidgetBlueprint"):
                paths.append(str(a.package_name))
        if paths:
            return sorted(paths)
        out(f"!! no Blueprints found under {SCAN_FOLDER}; falling back to ASSET_PATHS")
    return ASSET_PATHS


def prop(obj, name):
    """get_editor_property with a clear error instead of a silent None."""
    return obj.get_editor_property(name)


def pin_type_str(vt):
    try:
        cat = str(prop(vt, "pin_category"))
        sub = prop(vt, "pin_sub_category_object")
        cont = str(prop(vt, "container_type"))
        s = cat
        if sub:
            s += f"<{sub.get_name()}>"
        if cont and cont != "PinContainerType.NONE":
            s = f"{cont.split('.')[-1]}[{s}]"
        return s
    except Exception as e:
        return f"?({e})"


def dump_var_desc(vd, indent="    "):
    try:
        name = str(prop(vd, "var_name"))
    except Exception as e:
        out(f"{indent}!! could not read var_name: {e}")
        return
    try:
        vtype = pin_type_str(prop(vd, "var_type"))
    except Exception as e:
        vtype = f"?({e})"
    try:
        default = prop(vd, "default_value")
        default = "" if default is None else str(default)
    except Exception as e:
        default = f"?({e})"
    shown = default if default != "" else "«empty → engine zero/false/None»"
    out(f"{indent}- `{name}` : {vtype} = {shown}")


# ---- strategy 1: Blueprint.FunctionGraphs -> K2Node_FunctionEntry.LocalVariables ---------

def strategy_graphs(bp):
    graphs = []
    for gp in ("function_graphs", "ubergraph_pages", "macro_graphs"):
        try:
            g = prop(bp, gp)
            if g:
                graphs.extend([(gp, x) for x in g])
        except Exception as e:
            fail(f"read Blueprint.{gp}", e)
    if not graphs:
        raise RuntimeError("no graphs reachable via get_editor_property")

    any_locals = False
    for kind, graph in graphs:
        gname = graph.get_name()
        try:
            nodes = prop(graph, "nodes")
        except Exception as e:
            fail(f"read {gname}.Nodes", e)
            continue
        entries = [n for n in nodes if n and n.get_class().get_name() == "K2Node_FunctionEntry"]
        if not entries:
            continue
        for entry in entries:
            try:
                locals_ = prop(entry, "local_variables")
            except Exception as e:
                fail(f"read {gname} FunctionEntry.LocalVariables", e)
                continue
            out(f"  ### {gname}  ({kind})")
            if not locals_:
                out("    (no locals)")
            for vd in locals_:
                any_locals = True
                dump_var_desc(vd)
    return any_locals


# ---- strategy 2: T3D export of the whole Blueprint, grep LocalVariables -----------------

def strategy_t3d(bp, asset_path):
    task = unreal.AssetExportTask()
    task.object = bp
    task.filename = os.path.join(OUT_DIR, bp.get_name() + ".t3d")
    task.automated = True
    task.replace_identical = True
    task.prompt = False
    ok = unreal.Exporter.run_asset_export_task(task)
    if not ok or not os.path.exists(task.filename):
        raise RuntimeError(f"export returned {ok}; file present: {os.path.exists(task.filename)}")
    hits = 0
    with open(task.filename, "r", encoding="utf-8", errors="replace") as f:
        cur_graph = None
        for line in f:
            s = line.strip()
            if s.startswith("Begin Object Class=/Script/BlueprintGraph.K2Node_FunctionEntry"):
                cur_graph = s
            if "LocalVariables(" in s:
                hits += 1
                out(f"    {s}")
    out(f"  (T3D at {task.filename}; {hits} LocalVariables lines)")
    return hits > 0


# ---- strategy 3: member variables via BlueprintEditorLibrary / NewVariables -------------

def member_variables(bp):
    try:
        nv = prop(bp, "new_variables")
    except Exception as e:
        fail("read Blueprint.NewVariables", e)
        return
    out("  ### member variables")
    if not nv:
        out("    (none)")
    for vd in nv:
        dump_var_desc(vd)


# ---- main ------------------------------------------------------------------------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    out("# Blueprint local + member variable defaults")
    out(f"engine {unreal.SystemLibrary.get_engine_version()}  ·  project {unreal.Paths.get_project_file_path()}")
    out()
    for path in find_blueprints():
        out(f"## {path}")
        bp = unreal.load_asset(path)
        if bp is None:
            out("!! load_asset returned None")
            out()
            continue
        member_variables(bp)
        try:
            got = strategy_graphs(bp)
            if not got:
                out("  (strategy 1 found graphs but no locals on any FunctionEntry)")
        except Exception as e:
            fail("strategy 1 (FunctionGraphs reflection)", e)
            try:
                strategy_t3d(bp, path)
            except Exception as e2:
                fail("strategy 2 (T3D export)", e2)
                out("  → UNREADABLE by script. Open the function, click the local, read Default Value.")
        out()

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {OUT_FILE}")


try:
    main()
except Exception:
    traceback.print_exc()
