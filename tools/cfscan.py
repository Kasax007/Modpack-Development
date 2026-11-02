"""cfscan.py MANIFEST OUTJSON : for each CF project, find newest file for 26.3 + Fabric via cfwidget."""
import json, sys, time, urllib.request, os
SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache = os.path.join(SP, 'cfw')
def get(pid):
    fn = os.path.join(cache, f'{pid}.json')
    if os.path.exists(fn):
        return json.load(open(fn))
    for attempt in range(6):
        try:
            req = urllib.request.Request(f'https://api.cfwidget.com/{pid}', headers={'User-Agent': 'curl/8.5.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                code = r.status; data = r.read()
            if code == 200:
                d = json.loads(data)
                if 'files' in d:
                    json.dump(d, open(fn, 'w')); return d
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print('ERR', pid, e, file=sys.stderr); time.sleep(5 * (attempt + 1))
    return None
def best(d, ver='26.3'):
    fs = [f for f in d['files'] if ver in f['versions'] and ('Fabric' in f['versions'] or not any(l in f['versions'] for l in ('Forge','NeoForge','Quilt')))]
    fs.sort(key=lambda f: f['uploaded_at'], reverse=True)
    return fs
if __name__ == '__main__':
    pids = [int(a) for a in sys.argv[2:]] if sys.argv[1] == '-' else [f['projectID'] for f in json.load(open(sys.argv[1]))['files']]
    out = {}
    for pid in pids:
        d = get(pid)
        if d is None: out[pid] = {'error': True}; continue
        fs = best(d)
        allv = sorted({v for f in d['files'] for v in f['versions'] if v[:1].isdigit()}, key=lambda s: [int(x) if x.isdigit() else 0 for x in s.replace('-', '.').split('.')])
        out[pid] = {'title': d['title'], 'url': d['urls']['curseforge'], 'f263': [{'id': f['id'], 'name': f['name'], 'versions': f['versions'], 'date': f['uploaded_at']} for f in fs[:2]], 'newest_versions': allv[-4:]}
        print(pid, d['title'][:40], 'YES' if fs else 'no', allv[-3:], flush=True)
        time.sleep(0.4)
    json.dump(out, open(sys.argv[2], "w"), indent=1) if sys.argv[1] != "-" else None
