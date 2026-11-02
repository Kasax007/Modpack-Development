"""cfslug.py OUT.json slug... : resolve CF slugs via cfwidget, report newest 26.3 Fabric file."""
import json, sys, time, os, urllib.request
SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache = os.path.join(SP, 'cfw'); os.makedirs(cache, exist_ok=True)
def fetch(path):
    for a in range(5):
        try:
            req = urllib.request.Request('https://api.cfwidget.com/' + path, headers={'User-Agent': 'curl/8.5.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            if 'files' in d: return d
            time.sleep(4 * (a + 1))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(4 * (a + 1))
        except Exception:
            time.sleep(4 * (a + 1))
    return None
out = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
for slug in sys.argv[2:]:
    if slug in out: continue
    d = fetch('minecraft/mc-mods/' + slug)
    if not d:
        out[slug] = None; print(slug, 'NOTFOUND', flush=True); continue
    json.dump(d, open(os.path.join(cache, f"{d['id']}.json"), 'w'))
    fs = [f for f in d['files'] if '26.3' in f['versions'] and ('Fabric' in f['versions'] or not any(l in f['versions'] for l in ('Forge', 'NeoForge', 'Quilt')))]
    fs.sort(key=lambda f: f['uploaded_at'], reverse=True)
    allv = sorted({v for f in d['files'] for v in f['versions'] if v[:1].isdigit()})
    out[slug] = {'id': d['id'], 'title': d['title'], 'file': fs[0] if fs else None, 'newest': allv[-3:]}
    print(slug, d['id'], d['title'][:30], ('YES ' + fs[0]['name']) if fs else 'no', allv[-2:], flush=True)
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
    time.sleep(0.3)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
