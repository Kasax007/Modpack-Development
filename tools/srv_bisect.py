"""bisect.py BASE_IDS(comma) [--grep PATTERN] : find which server mod (with deps) triggers PATTERN when added to BASE."""
import json, os, sys, shutil, subprocess, glob
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
db = json.load(open(f'{SP}/packdb.json'))
client_only = set(json.load(open(f'{SP}/client_only.json')))
mods = {v['info']['id']: v for v in db.values() if v['info'] and v['info']['env'] != 'client' and v['info']['id'] not in client_only}
prov = {}
for mid, v in mods.items():
    for p in v['info']['provides']: prov.setdefault(p, mid)
def closure(ids):
    out = set(); stack = list(ids)
    while stack:
        m = stack.pop()
        if m in out or m not in mods: continue
        out.add(m)
        for d in mods[m]['info']['depends']:
            if d in prov: stack.append(prov[d])
    return out
def run(ids, pattern):
    D = f'{SP}/srv2'
    for f in glob.glob(f'{D}/mods/*'): os.remove(f)
    for w in ('world', 'logs'):
        if os.path.isdir(f'{D}/{w}'): shutil.rmtree(f'{D}/{w}')
    for m in closure(ids): shutil.copy(mods[m]['path'], f'{D}/mods/')
    shutil.copy(sorted(glob.glob(f'{SP}/srv/mods/QuestIcons*'))[0], f'{D}/mods/') if 'questsicons' in ids else None
    try:
        out = subprocess.run(['timeout', '400', '/opt/jdk25/jdk-25.0.5+8/bin/java', '-Xmx4G', '-jar', 'fabric-server-launch.jar', 'nogui'],
                             cwd=D, input='stop\n', capture_output=True, text=True, errors='replace').stdout
    except Exception as e:
        out = str(e)
    open(f'{D}/last.out', 'w').write(out)
    hit = pattern in out
    done = 'Done (' in out
    print(f'  {len(closure(ids))} mods -> {"HIT" if hit else "ok"} {"(started)" if done else "(no start)"}', flush=True)
    return hit
base = sys.argv[1].split(',')
pattern = sys.argv[sys.argv.index('--grep') + 1] if '--grep' in sys.argv else 'No key item'
cands = sorted(set(mods) - closure(base))
print('candidates', len(cands))
while len(cands) > 1:
    half = cands[:len(cands) // 2]
    print('testing', len(half), half[:4], '...')
    if run(base + half, pattern): cands = half
    else: cands = cands[len(cands) // 2:]
print('CULPRIT', cands, mods[cands[0]]['title'] if cands else None)
print('verify:', run(base + cands, pattern))
