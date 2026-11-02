"""pack.py fetch|deps : download the selected 26.3 Fabric jars and check their dependencies."""
import json, os, sys, zipfile, io, urllib.request, urllib.parse, re, time
sys.path.insert(0, os.path.dirname(__file__))
from selection import SEL
SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JARS = os.path.join(SP, 'jars'); os.makedirs(JARS, exist_ok=True)
EXTRA = {}  # project id -> file id override
def widget(pid):
    fn = os.path.join(SP, 'cfw', f'{pid}.json')
    if not os.path.exists(fn):
        req = urllib.request.Request(f'https://api.cfwidget.com/{pid}', headers={'User-Agent': 'curl/8.5.0'})
        d = json.loads(urllib.request.urlopen(req, timeout=60).read()); json.dump(d, open(fn, 'w'))
    return json.load(open(fn))
def pick(d):
    fs = [f for f in d['files'] if '26.3' in f['versions']]
    if d.get('type') not in ('Shaders', 'Resource Packs'):
        fab_only = [f for f in fs if 'Fabric' in f['versions'] and 'NeoForge' not in f['versions'] and 'Forge' not in f['versions']]
        multi = [f for f in fs if 'Fabric' in f['versions']]
        named = [f for f in multi if 'fabric' in f['name'].lower()]
        fs = fab_only or named or multi
    fs.sort(key=lambda f: f['uploaded_at'], reverse=True)
    rel = [f for f in fs if f.get('type') == 'release']
    return (rel or fs)[0] if fs else None
def url(f):
    i = f['id']; return f"https://edge.forgecdn.net/files/{i // 1000}/{i % 1000}/{urllib.parse.quote(f['name'])}"
def modinfo(data):
    """fabric.mod.json of a jar plus nested jars' ids."""
    z = zipfile.ZipFile(io.BytesIO(data))
    try:
        fmj = json.loads(z.read('fabric.mod.json').decode('utf-8', 'replace'), strict=False)
    except KeyError:
        return None
    provides = {fmj['id'], *fmj.get('provides', [])}
    for j in fmj.get('jars', []):
        try:
            sub = modinfo(z.read(j['file']))
            if sub: provides |= sub['provides']
        except Exception: pass
    return {'id': fmj['id'], 'name': fmj.get('name', fmj['id']), 'env': fmj.get('environment', '*'),
            'depends': fmj.get('depends', {}), 'recommends': fmj.get('recommends', {}), 'breaks': fmj.get('breaks', {}),
            'provides': provides, 'version': fmj.get('version')}
def fetch(ids):
    out = {}
    for pid in ids:
        d = widget(pid); f = pick(d)
        if not f: print('NO 26.3 FILE', pid, d['title']); continue
        path = os.path.join(JARS, f"{f['id']}-{f['name']}")
        if not os.path.exists(path):
            for a in range(4):
                try:
                    req = urllib.request.Request(url(f), headers={'User-Agent': 'curl/8.5.0'})
                    data = urllib.request.urlopen(req, timeout=300).read(); open(path, 'wb').write(data); break
                except Exception as e:
                    print('retry', pid, e); time.sleep(3)
        info = modinfo(open(path, 'rb').read()) if path.endswith('.jar') else None
        out[pid] = {'pid': pid, 'title': d['title'], 'slug': d['urls']['curseforge'].rstrip('/').split('/')[-1], 'type': d.get('type'),
                    'fileID': f['id'], 'file': f['name'], 'path': path, 'size': os.path.getsize(path), 'cat': SEL.get(pid, 'dep'),
                    'info': ({k: (sorted(v) if isinstance(v, set) else v) for k, v in info.items()} if info else None)}
    return out
if __name__ == '__main__':
    ids = [int(a) for a in sys.argv[2:]] if len(sys.argv) > 2 else list(SEL)
    db_path = os.path.join(SP, 'packdb.json')
    db = json.load(open(db_path)) if os.path.exists(db_path) else {}
    if sys.argv[1] == 'fetch':
        todo = [i for i in ids if str(i) not in db]
        res = fetch(todo)
        for k, v in res.items(): db[str(k)] = v
        json.dump(db, open(db_path, 'w'), indent=1)
        print('fetched', len(res), 'total', len(db))
    # dependency check over everything in db
    provided = {'minecraft', 'java', 'fabricloader', 'fabric', 'mixinextras'}
    for v in db.values():
        if v['info']: provided |= set(v['info']['provides'])
    missing = {}
    for v in db.values():
        if not v['info']: continue
        for dep in v['info']['depends']:
            if dep not in provided: missing.setdefault(dep, []).append(v['title'])
    print('MISSING DEPS:'); [print('  ', k, '<-', ', '.join(t[:30] for t in vs)) for k, vs in sorted(missing.items())]
    breaks = []
    for v in db.values():
        if not v['info']: continue
        for b in v['info']['breaks']:
            if b in provided: breaks.append((v['title'], b))
    print('BREAKS:', breaks)
