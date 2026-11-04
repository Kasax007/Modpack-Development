"""qcheck.py [--game DUMP.json | --offline] : validate every id used by the quest book, plus the book's own structure.

Ids are checked against
  - the registry dump of the running pack: --game FILE, or by default $SP/regdump.json (written by the dctest harness
    with -Pdump=FILE; make a new one whenever a mod changes), or else / with --offline
  - the older offline dumps in $SP (items.json, registries.json, tags.json) with the pack's own mods read straight from
    their jars in $SP/ownjars (Quest Icons, Beach Craft, Tamagotchi): their namespaces are replaced by what the jars hold.
Also checked: dependencies (known, no cycles), duplicate ids, quests that sit on top of each other, crate tables.
"""
import json, sys, os, glob, math
sys.path.insert(0, os.path.dirname(__file__))
import dc_quests as D
import qjars
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'

game = sys.argv[sys.argv.index('--game') + 1] if '--game' in sys.argv else None
if not game and '--offline' not in sys.argv and os.path.exists(f'{SP}/regdump.json'):
    game = f'{SP}/regdump.json'
if game:
    g = json.load(open(game))
    items = g['items']
    reg = {k: set(g[k]) for k in ('entity', 'advancement', 'structure', 'biome', 'dimension')}
    tags = {k: set(v) for k, v in g['tags'].items()}
    source = f'registry dump {game}'
else:
    items = json.load(open(f'{SP}/items.json'))
    reg = {k: set(v) for k, v in json.load(open(f'{SP}/registries.json')).items()}
    tags = {k: set(v) for k, v in json.load(open(f'{SP}/tags.json')).items()} if os.path.exists(f'{SP}/tags.json') else {}
    own = sorted(glob.glob(f'{SP}/ownjars/*.jar'))
    for j in own:
        s = qjars.scan(j)
        for ns in s['namespaces']:
            items = {k: v for k, v in items.items() if not k.startswith(ns + ':')}
            for k in ('entity', 'advancement', 'structure', 'biome'):
                reg[k] = {x for x in reg.get(k, set()) if not x.startswith(ns + ':')}
        items.update({k: [v, s['file']] for k, v in s['items'].items()})
        for k in ('entity', 'advancement', 'structure', 'biome'):
            reg.setdefault(k, set()).update(s[k])
        for k, v in s['tags'].items():
            tags.setdefault(k, set()).update(v)
    source = 'offline dumps + ' + ', '.join(os.path.basename(j) for j in own)
    if 'raft:raftdim' not in reg.get('dimension', set()):
        reg.setdefault('dimension', set()).add('raft:raftdim')

bad = []
def chk_item(i, where):
    if isinstance(i, dict): i = i.get('id', '')
    if i.startswith('#'):
        if i[1:] not in tags.get('item', ()): bad.append((where, 'item tag', i))
    elif i not in items: bad.append((where, 'item', i))

all_ids = {}
for c in D.B.chapters:
    for qq in c.quests:
        if qq['id'] in all_ids: bad.append((f"{c.key}:{qq['_key']}", 'duplicate quest id', all_ids[qq['id']]))
        all_ids[qq['id']] = f"{c.key}:{qq['_key']}"
deps_of = {qq['id']: qq.get('dependencies', []) for c in D.B.chapters for qq in c.quests}

for c in D.B.chapters:
    chk_item(c.icon, c.key)
    for qq in c.quests:
        w = f"{c.key}:{qq['_key']}"
        if 'icon' in qq: chk_item(qq['icon'], w)
        for t in qq['tasks']:
            ty = t['type']
            if 'icon' in t: chk_item(t['icon'], w)
            if ty == 'item': chk_item(t['item'], w)
            elif ty == 'kill':
                e = t['entity']
                if e.startswith('#'):
                    if e[1:] not in tags.get('entity_type', ()): bad.append((w, 'entity tag', e))
                elif e not in reg['entity']: bad.append((w, 'entity', e))
            elif ty == 'structure':
                s = t['structure']
                if s.startswith('#'):
                    if s[1:] not in tags.get('worldgen/structure', ()): bad.append((w, 'structure tag', s))
                elif s not in reg['structure']: bad.append((w, 'structure', s))
            elif ty == 'biome':
                b = t['biome']
                if b.startswith('#'):
                    if b[1:] not in tags.get('worldgen/biome', ()): bad.append((w, 'biome tag', b))
                elif b not in reg['biome']: bad.append((w, 'biome', b))
            elif ty == 'observation':
                o = t['observe']
                if t.get('entity'):
                    if o not in reg['entity']: bad.append((w, 'entity', o))
                elif o not in items: bad.append((w, 'block', o))
            elif ty == 'advancement':
                if t['advancement'] not in reg['advancement']: bad.append((w, 'advancement', t['advancement']))
            elif ty == 'dimension':
                if t['dimension'] not in reg.get('dimension', ()): bad.append((w, 'dimension', t['dimension']))
            elif ty not in ('checkmark', 'xp', 'stat'): bad.append((w, 'unknown task type', ty))
        for r in qq.get('rewards', []):
            if r['type'] == 'item': chk_item(r['item'], w)
            if r['type'] == 'choice':
                for i in r['items']: chk_item(i, w)
        for dep in qq.get('dependencies', []):
            if dep not in all_ids: bad.append((w, 'dependency', dep))
        if qq.get('dependency_requirement') == 'one_completed' and len(qq.get('dependencies', [])) < 2:
            bad.append((w, 'any-of with fewer than two dependencies', ''))
    # quests on top of each other (the map draws a quest about 0.9 cells wide at size 1)
    qs = c.quests
    for i in range(len(qs)):
        for j in range(i + 1, len(qs)):
            a, b = qs[i], qs[j]
            need = 0.55 * (a.get('size', 1.0) + b.get('size', 1.0))
            if math.hypot(a['x'] - b['x'], a['y'] - b['y']) < need:
                bad.append((f"{c.key}:{a['_key']}", 'overlaps', b['_key']))

# a literal '&' inside a word (Friends&Foes) is read as a colour code and eats a letter: write '&&'
import re
for c in D.B.chapters:
    for qq in c.quests:
        for text in [qq['title']] + qq['description'] + [t.get('title', '') for t in qq['tasks']]:
            for m in re.finditer(r'(?<=[A-Za-z])&([0-9a-fk-orA-FK-OR])(?=[a-z])', text.replace('&&', '')):
                bad.append((f"{c.key}:{qq['_key']}", 'ampersand eats a letter', text[max(0, m.start() - 12):m.end() + 6]))

# dependency cycles
state = {}
def visit(q, path):
    if state.get(q) == 1: bad.append((all_ids[q], 'dependency cycle', ' > '.join(all_ids[p] for p in path))); return
    if state.get(q) == 2: return
    state[q] = 1
    for d in deps_of.get(q, []):
        if d in deps_of: visit(d, path + [d])
    state[q] = 2
for q in deps_of: visit(q, [q])

for k, t in D.B.tables.items():
    for e in t['entries']: chk_item(e['item'], 'table ' + k)
for b in bad: print('BAD', *b)
print('checked', sum(len(c.quests) for c in D.B.chapters), 'quests in', len(D.B.chapters), 'chapters against', source + ';', len(bad), 'problems')
sys.exit(1 if bad else 0)
