"""qcheck.py : validate every id used by the quest book against the pack's real registries."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import dc_quests as D
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
items = json.load(open(f'{SP}/items.json'))
reg = json.load(open(f'{SP}/registries.json'))
tags = json.load(open(f'{SP}/tags.json')) if os.path.exists(f'{SP}/tags.json') else {}
bad = []
def chk_item(i, where):
    if isinstance(i, dict): i = i.get('id', '')
    if i.startswith('#'):
        if i[1:] not in tags.get('item', []): bad.append((where, 'item tag', i))
    elif i not in items: bad.append((where, 'item', i))
for c in D.B.chapters:
    chk_item(c.icon, c.key)
    keys = {qq['id'] for qq in c.quests}
    for qq in c.quests:
        w = f"{c.key}:{qq['_key']}"
        if 'icon' in qq: chk_item(qq['icon'], w)
        for t in qq['tasks']:
            ty = t['type']
            if ty == 'item': chk_item(t['item'], w)
            elif ty == 'kill':
                e = t['entity']
                if e.startswith('#'):
                    if e[1:] not in tags.get('entity_type', []): bad.append((w, 'entity tag', e))
                elif e not in reg['entity']: bad.append((w, 'entity', e))
            elif ty == 'structure':
                s = t['structure']
                if s.startswith('#'):
                    if s[1:] not in tags.get('worldgen/structure', []): bad.append((w, 'structure tag', s))
                elif s not in reg['structure']: bad.append((w, 'structure', s))
            elif ty == 'biome':
                b = t['biome']
                if not b.startswith('#') and b not in reg['biome'] and not b.startswith('minecraft:'): bad.append((w, 'biome', b))
            elif ty == 'observation':
                o = t['observe']
                if t.get('entity') and o not in reg['entity']: bad.append((w, 'entity', o))
        for r in qq.get('rewards', []):
            if r['type'] == 'item': chk_item(r['item'], w)
            if r['type'] == 'choice':
                for i in r['items']: chk_item(i, w)
        for dep in qq.get('dependencies', []):
            if not any(dep == x['id'] for cc in D.B.chapters for x in cc.quests): bad.append((w, 'dependency', dep))
for k, t in D.B.tables.items():
    for e in t['entries']: chk_item(e['item'], 'table ' + k)
for b in bad: print('BAD', *b)
print('checked', sum(len(c.quests) for c in D.B.chapters), 'quests;', len(bad), 'problems')
