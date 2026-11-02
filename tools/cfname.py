"""cfname.py OUT.json "Name|alt"... : search CF ids via FTB API, details via cfwidget, newest 26.3 Fabric file."""
import json, sys, time, os, re, urllib.request, urllib.parse
SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache = os.path.join(SP, 'cfw'); os.makedirs(cache, exist_ok=True)
UA = {'User-Agent': 'curl/8.5.0'}
def jget(url):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(3 * (a + 1))
        except Exception:
            time.sleep(3 * (a + 1))
    return None
def widget(pid):
    fn = os.path.join(cache, f'{pid}.json')
    if os.path.exists(fn): return json.load(open(fn))
    for a in range(4):
        d = jget(f'https://api.cfwidget.com/{pid}')
        if d and 'files' in d:
            json.dump(d, open(fn, 'w')); return d
        time.sleep(4)
    return None
def norm(s): return re.sub(r'[^a-z0-9]', '', re.sub(r'\[.*?\]|\(.*?\)', '', s.lower()))
def f263(d):
    fs = [f for f in d['files'] if '26.3' in f['versions'] and ('Fabric' in f['versions'] or not any(l in f['versions'] for l in ('Forge', 'NeoForge', 'Quilt')))]
    fs.sort(key=lambda f: f['uploaded_at'], reverse=True)
    return fs
out = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
args = []
for a in sys.argv[2:]:
    args += [l.strip() for l in open(a[1:]) if l.strip()] if a.startswith('@') else [a]
for arg in args:
    key = arg.split('|')[0]
    if key in out: continue
    names = arg.split('|')
    ids = []
    for n in names:
        if n.isdigit(): ids.append(int(n)); continue
        r = jget('https://api.modpacks.ch/public/mod/search/8?term=' + urllib.parse.quote(n))
        if r: ids += [m for m in r.get('mods', []) if isinstance(m, int)]
    best = None
    for pid in list(dict.fromkeys(ids))[:5]:
        d = widget(pid)
        if not d: continue
        if d.get('type') and 'Mods' not in d['type'] and 'Shader' not in d['type'] and 'Resource' not in d['type']: continue
        score = (norm(d['title']) == norm(names[0])) * 4 + (norm(names[0]) in norm(d['title'])) * 2 + (1 if f263(d) else 0) * 3
        if best is None or score > best[0]: best = (score, d)
        if score >= 9: break
    if not best:
        out[key] = None; print(key, 'NOTFOUND', flush=True); continue
    d = best[1]; fs = f263(d)
    allv = sorted({v for f in d['files'] for v in f['versions'] if v[:1].isdigit()})
    out[key] = {'id': d['id'], 'title': d['title'], 'type': d.get('type'), 'file': fs[0] if fs else None, 'newest': allv[-3:], 'score': best[0]}
    print(key, '->', d['id'], d['title'][:34], ('YES ' + fs[0]['name']) if fs else 'no', allv[-2:], 's=%d' % best[0], flush=True)
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
