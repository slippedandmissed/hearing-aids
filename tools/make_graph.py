"""Draw the Makefile's dependency graph (Graphviz) and refresh the Mermaid copy inside README.md.
  uv run python tools/make_graph.py      -> docs/build/figures/build_graph.png + .dot, and the block between the BUILD-GRAPH markers in README.md"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "build", "figures"); os.makedirs(OUT, exist_ok=True)

def parse():
    txt = subprocess.run(["make", "-pnrq", "-C", ROOT, "all"], capture_output=True, text=True).stdout
    phony = set(re.findall(r"^\.PHONY:\s*(.*)$", txt, re.M)[0].split()) if re.search(r"^\.PHONY:", txt, re.M) else set()
    rules = {}
    for m in re.finditer(r"^([^\s#:=%.\\][^:=%\n]*?)\s*:(?!=)\s*([^\n#]*)$", txt, re.M):
        tg, pre = m.group(1).strip(), m.group(2).strip()
        if tg.startswith(("Makefile", "$", "/")) or "%" in tg or tg in ("MAKEFILE_LIST", ".DEFAULT_GOAL"): continue
        for t in tg.split():
            if t not in rules or pre: rules[t] = [p for p in pre.split() if not p.startswith("|")]
    return rules, phony

def group(name):
    if re.match(r"cad/[^/]+\.py$", name): return "cad/*.py"
    if re.match(r"pcb/(carrier/)?[^/]+\.py$", name) or "/lib/" in name and name.startswith("pcb"): return "pcb scripts + footprint libs"
    if re.match(r"docs/manual/", name) or name.startswith("docs/manual"): return "docs/manual/*.md"
    if re.match(r"firmware/passthrough/src/", name): return "firmware src/*.rs"
    return name

def colour(n):
    if n.startswith(("cad", "assets")) or n in ("previews", "print-files"): return "#cfe3ff"
    if n.startswith(("pcb", "tools/freerouting")) or n in ("dangle-L", "dangle-R", "carrier", "pcb", "pcb-renders"): return "#d3f2e0"
    if n.startswith("firmware") or n == "firmware": return "#ffe2c2"
    if n.startswith("docs") or n in ("docs", "figures", "graph"): return "#e6dcff"
    return "#eeeeee"

def main():
    rules, phony = parse()
    edges, nodes = set(), set()
    skip = {"help", "setup", "fetch", "clean", "distclean", "check", "graph", "all", "docs/build/references.bib"}
    for tg, pres in rules.items():
        if tg in skip and tg != "all": continue
        for p in pres:
            a, b = group(p), group(tg)
            if a in skip or b in skip or a == b: continue
            edges.add((a, b)); nodes |= {a, b}
    for tg in list(rules):
        if tg not in skip and group(tg) in nodes: pass
    # drop the stamp noise: show figure groups as 'figures: <name>'
    def pretty(n): return n.replace("docs/build/figures/", "figures/").replace("docs/build/tables/", "tables/")
    lines = ["digraph build {", '  rankdir=LR; bgcolor="white"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10]; edge [color="#6b7785", arrowsize=0.7];']
    for n in sorted(nodes):
        shape = "ellipse" if n in phony else "box"; lines.append(f'  "{pretty(n)}" [shape={shape}, fillcolor="{colour(n)}"];')
    for a, b in sorted(edges): lines.append(f'  "{pretty(a)}" -> "{pretty(b)}";')
    lines.append("}")
    dot = "\n".join(lines); open(os.path.join(OUT, "build_graph.dot"), "w").write(dot)
    r = subprocess.run(["dot", "-Tpng", "-Gdpi=150", "-o", os.path.join(OUT, "build_graph.png")], input=dot, text=True, capture_output=True)
    if r.returncode: sys.exit("graphviz `dot` failed: " + r.stderr + "\n(brew install graphviz)")
    print("wrote docs/build/figures/build_graph.png", len(nodes), "nodes", len(edges), "edges")
    # ----- mermaid copy in the README
    ids = {n: f"n{i}" for i, n in enumerate(sorted(nodes))}
    mm = ["```mermaid", "flowchart LR"]
    for n, i in ids.items(): mm.append(f'  {i}(["{pretty(n)}"])' if n in phony else f'  {i}["{pretty(n)}"]')
    for a, b in sorted(edges): mm.append(f"  {ids[a]} --> {ids[b]}")
    mm.append("```")
    rd = os.path.join(ROOT, "README.md")
    if os.path.exists(rd):
        t = open(rd).read(); m = re.search(r"(<!-- BUILD-GRAPH:START -->\n).*?(<!-- BUILD-GRAPH:END -->)", t, re.S)
        if m: open(rd, "w").write(t[:m.start()] + m.group(1) + "\n".join(mm) + "\n" + m.group(2) + t[m.end():]); print("updated README.md")

if __name__ == "__main__": main()
