"""Download third-party files listed in sources.toml, or write the bibliography.
  uv run python tools/fetch.py fetch [key ...]    download every entry with a `fetch` URL (skips files that already exist)
  uv run python tools/fetch.py bib <out.bib>      write a BibTeX file for pandoc --citeproc
"""
import sys, os, tomllib, urllib.request, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = tomllib.load(open(os.path.join(ROOT, "sources.toml"), "rb"))["source"]

def download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (project build script)"})
    with urllib.request.urlopen(req, timeout=60) as r, open(path + ".part", "wb") as f: f.write(r.read())
    os.replace(path + ".part", path)

def fetch(keys):
    bad = 0
    for s in SOURCES:
        if "fetch" not in s or (keys and s["key"] not in keys): continue
        urls = s["fetch"] if isinstance(s["fetch"], list) else [s["fetch"]]
        for u in urls:
            dest = os.path.join(ROOT, s["dest"])
            path = dest if len(urls) == 1 else os.path.join(dest, urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(u).path)))
            if os.path.exists(path): print("have ", os.path.relpath(path, ROOT)); continue
            try: download(u, path); print("got  ", os.path.relpath(path, ROOT))
            except Exception as e: print("FAIL ", u, e); bad += 1
    return bad

def bib(out):
    esc = lambda x: str(x).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        for s in SOURCES:
            f.write(f"@misc{{{s['key']},\n  title = {{{esc(s['title'])}}},\n  author = {{{{{esc(s.get('author', ''))}}}}},\n")
            if "year" in s: f.write(f"  year = {{{s['year']}}},\n")
            f.write(f"  url = {{{s['url']}}},\n")
            if s.get("note"): f.write(f"  note = {{{esc(s['note'])}}},\n")
            f.write("}\n\n")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if cmd == "fetch": sys.exit(1 if fetch(sys.argv[2:]) else 0)
    elif cmd == "bib": bib(sys.argv[2])
    else: sys.exit(__doc__)
