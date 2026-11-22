"""Build one PCB end to end: placement -> Freerouting -> ground plane -> silkscreen -> DRC -> BOM/CPL -> gerber zip -> renders.
  uv run python pcb/pipeline.py dangle L | dangle R | carrier
Needs: KiCad 10 (kicad-cli on PATH, KICAD_PY = KiCad's bundled python), java, tools/freerouting-1.9.0.jar (make fetch).
Everything it writes is generated and gitignored (pcb/out, pcb/carrier/out, pcb/fab, pcb/renders) EXCEPT the routing locks in pcb/routes/:
KiCad's DSN export is not reproducible (random item IDs reorder it) and the router's result depends on that order, so the accepted Freerouting
result is committed as pcb/routes/<board>.ses together with a fingerprint of the placement it belongs to. The pipeline re-uses the lock while the
fingerprint matches and re-routes (and rewrites the lock) when it does not, or when REROUTE=1 (make reroute).
Small fixes to a routed board (move a via, delete or add a track) go in pcb/routes/<board>.edits.json (see route_edits.py): they are applied after the
import and survive until the placement changes, so a tweak never means a new router run."""
import os, sys, shutil, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
KICAD_PY = os.environ.get("KICAD_PY", "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3")
JAR = os.path.join(ROOT, "tools", "freerouting-1.9.0.jar")
LAYERS = "F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts"
ROUTES = os.path.join(HERE, "routes")
REROUTE = os.environ.get("REROUTE") == "1"

def run(cmd, cwd=HERE, env=None, quiet=True, check=True):
    e = dict(os.environ, **(env or {}))
    r = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True)
    if check and r.returncode != 0: sys.exit(f"FAILED: {' '.join(cmd)}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    return r

def unconnected(drc_path):
    return len(re.findall(r"^\[unconnected_items\]", open(drc_path).read(), re.M))

def build(kind, variant):
    if kind == "dangle":
        name = f"dangle_{variant}"; out = os.path.join(HERE, "out"); size = ("13", "28")
        steps = dict(place=[KICAD_PY, "build_dangle.py", variant, "place"], importer=[KICAD_PY, "import_ses.py", variant],
                     finish=[KICAD_PY, "finish.py", variant], bom=[KICAD_PY, "bom.py", variant], cwd=HERE)
        prefix, var = "dangle", variant; board_final = f"{name}_final.kicad_pcb"; dsn, ses = f"{name}.dsn", f"{name}.ses"
        ground_in = f"{name}_ses.kicad_pcb"; cwd = HERE
    else:
        name = "carrier_C"; out = os.path.join(HERE, "carrier", "out"); size = ("56", "40")
        cwd = os.path.join(HERE, "carrier"); prefix, var = "carrier", "C"; board_final = "carrier_C_final.kicad_pcb"; dsn, ses = "carrier_C.dsn", "carrier_C.ses"
        steps = dict(place=[KICAD_PY, "build_carrier.py", "place"], importer=[KICAD_PY, os.path.join(HERE, "import_ses_generic.py"), "out", "carrier_C"],
                     finish=[KICAD_PY, "finish_carrier.py"], bom=[KICAD_PY, "bom_carrier.py"])
        ground_in = "carrier_C_ses.kicad_pcb"
    os.makedirs(out, exist_ok=True)
    print(f"== {name}: place"); run(steps["place"], cwd=cwd)
    drc = os.path.join(out, f"{name}_drc.txt"); ok = False
    os.makedirs(ROUTES, exist_ok=True); lock = os.path.join(ROUTES, f"{name}.ses"); lockfp = os.path.join(ROUTES, f"{name}.placement.sha256")
    fp = run([KICAD_PY, os.path.join(HERE, "fingerprint.py"), os.path.join(out, f"{name}_placed.kicad_pcb")], cwd=cwd).stdout.strip().splitlines()[-1]

    def finish_and_check(use_edits=True):
        run(steps["importer"], cwd=cwd)
        ed = os.path.join(ROUTES, f"{name}.edits.json")                     # hand edits on top of the router's result (route_edits.py)
        def edits(board, stage):
            if os.path.exists(ed):
                o = run([sys.executable, os.path.join(HERE, "route_edits.py"), os.path.join(out, board), ed, fp, stage], cwd=cwd).stdout.rstrip()
                if o: print(o)
        if use_edits: edits(ground_in, "ses")
        run([KICAD_PY, os.path.join(HERE, "ground_plane.py"), var], cwd=cwd, env=dict(OUTDIR=out, PREFIX=prefix, INPUT=ground_in, BW=size[0], BH=size[1]))
        if use_edits: edits(f"{name}_routed.kicad_pcb", "ground")
        run(steps["finish"], cwd=cwd)
        shutil.copy(os.path.join(out, f"{name}_routed.kicad_pro"), os.path.join(out, f"{name}_final.kicad_pro"))
        run(["kicad-cli", "pcb", "drc", "--format", "report", "-o", drc, os.path.join(out, board_final)], cwd=cwd, check=False)
        return unconnected(drc)

    if not REROUTE and os.path.exists(lock) and os.path.exists(lockfp) and open(lockfp).read().strip() == fp:
        print(f"== {name}: using the committed routing lock pcb/routes/{name}.ses (placement fingerprint matches)")
        shutil.copy(lock, os.path.join(out, ses)); n = finish_and_check(); print(f"   unconnected items: {n}")
        ok = n == 0
        if not ok and os.path.exists(os.path.join(ROUTES, f"{name}.edits.json")):
            sys.exit(f"{name}: the committed lock plus pcb/routes/{name}.edits.json does not route cleanly; not re-routing (that would discard the edits). Fix the edits, see {drc}")
        if not ok: print("   the lock no longer routes cleanly: re-routing")
    elif os.path.exists(lock) and not REROUTE: print(f"== {name}: placement changed since the routing lock was made: re-routing")
    if not ok:
        for mp in (400, 800, 1500, 3000):
            print(f"== {name}: Freerouting (max passes {mp})")
            # -dct 0 = dialog confirmation timeout 0: skip the "Start (20s)" countdown dialog and start routing immediately
            run(["java", "-jar", JAR, "-de", os.path.join(out, dsn), "-do", os.path.join(out, ses), "-mp", str(mp), "-dct", "0"], cwd=ROOT)
            n = finish_and_check(use_edits=False); print(f"   unconnected items: {n}")
            if n == 0: ok = True; break
        if ok:
            txt = open(os.path.join(out, ses)).read().split("\n"); txt[0] = f"(session {name}"; txt[1] = f"  (base_design {name})"       # the filename is in the header: normalise it
            open(lock, "w").write("\n".join(txt)); open(lockfp, "w").write(fp + "\n")
            print(f"   NEW routing lock written: commit pcb/routes/{name}.ses and {name}.placement.sha256")
            ed = os.path.join(ROUTES, f"{name}.edits.json")
            if os.path.exists(ed): os.replace(ed, ed + ".stale"); print(f"   the old hand edits belonged to the previous routing: moved to {name}.edits.json.stale (re-make them for the new routing)")
    if not ok: sys.exit(f"{name}: still unconnected nets after all routing attempts, see {drc}")
    run(steps["bom"], cwd=cwd)
    fabname = "carrier" if kind == "carrier" else name
    fab = os.path.join(HERE, "fab"); gd = os.path.join(fab, fabname); shutil.rmtree(gd, ignore_errors=True); os.makedirs(gd)
    brd = os.path.join(out, board_final)
    run(["kicad-cli", "pcb", "export", "gerbers", "--layers", LAYERS, "-o", gd + "/", brd], cwd=cwd)
    run(["kicad-cli", "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "-o", gd + "/", brd], cwd=cwd)
    zp = os.path.join(fab, f"{fabname}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(gd)): z.write(os.path.join(gd, f), f"{fabname}/{f}")
    for suf in ("BOM", "CPL"): shutil.copy(os.path.join(out, f"{fabname}_{suf}.csv"), os.path.join(fab, f"{fabname}_{suf}.csv"))
    rd = os.path.join(HERE, "renders"); os.makedirs(rd, exist_ok=True)
    w, h = (800, 1700) if kind == "dangle" else (1700, 1200)
    for side in ("top", "bottom"):
        run(["kicad-cli", "pcb", "render", "--side", side, "--width", str(w), "--height", str(h), "-o", os.path.join(rd, f"{fabname}_{side}.png"), brd], cwd=cwd, check=False)
    print(f"== {name}: done -> pcb/fab/{fabname}.zip")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["dangle"] and len(a) == 2 and a[1] in ("L", "R"): build("dangle", a[1])
    elif a == ["carrier"]: build("carrier", "C")
    else: sys.exit(__doc__)
