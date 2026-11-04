"""qsource.py [--json OUT] : can every item the quest book asks for be obtained in survival?

Reads the data of every jar of the pack (pack db paths, $SP/ownjars, the vanilla 26.3 jar): recipes, loot tables,
villager trades, block transformers (axe/hoe/shovel), item tags, worldgen JSON and structure templates. Then it
computes which items a survival player can reach:

  base     = items from non-block loot tables (chests, mobs, fishing, archaeology, gameplay ...), blocks that appear
             in worldgen or in structure templates, a few hand-listed mechanics (buckets, shearing, brewing ...)
  closure  = repeat until nothing changes: a recipe / trade / transformer whose every ingredient slot has one
             obtainable alternative adds its outputs; a block that is obtainable (as item or because it generates)
             adds its block drops; a block without an item form counts as placeable when one of its drops is
             obtainable (crops, cakes, ...); quest rewards and Quest Icons crate tables add their items.

Limits (the report lists what it could not prove, for a manual check): loot or trades that mods add in code,
features that mods register in code (BCLib: BetterEnd, BetterNether), drops of mobs that never spawn, recipes
with unusual JSON. Items without a source are not necessarily impossible - they need a look.
"""
import json, os, re, sys, glob, gzip, zipfile, collections
sys.path.insert(0, os.path.dirname(__file__))
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
VANILLA = '/root/.gradle/caches/fabric-loom/26.3/minecraft-client.jar'
ID = re.compile(r'^#?[a-z0-9_.-]+:[a-z0-9_./-]+$')

jars = [v['path'] for v in json.load(open(f'{SP}/packdb.json')).values()]
jars += sorted(glob.glob(f'{SP}/ownjars/*.jar')) + [VANILLA]
mod_ids = {'minecraft', 'java', 'fabricloader'}
for v in json.load(open(f'{SP}/packdb.json')).values():
    try:
        mod_ids.add(eval(v['info'])['id'])
    except Exception:
        pass
import io
def _ids(z, depth=0):
    """Mod ids of a jar and of the jars nested in it (a recipe condition may name a bundled library)."""
    try:
        mod_ids.add(json.loads(z.read('fabric.mod.json').decode('utf-8-sig'), strict=False)['id'])
    except Exception:
        pass
    for n in z.namelist():
        if depth < 2 and n.startswith('META-INF/jars/') and n.endswith('.jar'):
            try:
                _ids(zipfile.ZipFile(io.BytesIO(z.read(n))), depth + 1)
            except Exception:
                pass
for j in [v['path'] for v in json.load(open(f'{SP}/packdb.json')).values()] + glob.glob(f'{SP}/ownjars/*.jar'):
    try:
        _ids(zipfile.ZipFile(j))
    except Exception:
        pass

dump = json.load(open(f'{SP}/v13/regdump3.json'))
ITEMS = set(dump['items'])


def ids_in(x, out):
    """All ids (and #tags) inside a JSON value."""
    if isinstance(x, str):
        if ID.match(x): out.add(x)
    elif isinstance(x, list):
        for e in x: ids_in(e, out)
    elif isinstance(x, dict):
        if 'tag' in x and isinstance(x['tag'], str): out.add('#' + x['tag'].lstrip('#'))
        for k, v in x.items():
            if k in ('type', 'fabric:type', 'neoforge:conditions', 'fabric:load_conditions', 'conditions', 'count',
                     'components', 'nbt', 'predicate'):
                continue
            ids_in(v, out)
    return out


def conditions_ok(j):
    """fabric:load_conditions: the simple mod checks."""
    def ok(c):
        t = c.get('condition') or c.get('type', '')
        if t == 'fabric:all_mods_loaded': return all(m in mod_ids for m in c.get('values', []))
        if t == 'fabric:any_mods_loaded': return any(m in mod_ids for m in c.get('values', []))
        if t == 'fabric:not': return not ok(c.get('value', {}))
        if t == 'fabric:and': return all(ok(x) for x in c.get('values', []))
        if t == 'fabric:or': return any(ok(x) for x in c.get('values', []))
        return True
    cs = j.get('fabric:load_conditions')
    if isinstance(cs, dict): cs = [cs]
    return all(ok(c) for c in cs or [])


tags = collections.defaultdict(set)       # 'item' / 'block' -> tag -> members
tag_replace = set()
recipes = []                              # (where, [slots(set of ids)], outputs(set))
loot = {}                                 # table id -> (kind, block or None, items set, table refs set)
natural = set()                           # block ids seen in worldgen / templates
legacy = collections.Counter()            # data in pre-1.21 folder names (not loaded in 26.3)
NAME_RE = re.compile(rb'\x08\x00\x04Name(..)', re.S)

import io
def open_all(path):
    """The jar and every jar nested in it (META-INF/jars, Fabric jar-in-jar)."""
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        print('cannot open', path, e); return
    yield path, z
    for n in z.namelist():
        if n.startswith('META-INF/jars/') and n.endswith('.jar'):
            try:
                yield f'{path}!{n}', zipfile.ZipFile(io.BytesIO(z.read(n)))
            except Exception:
                pass

def all_zips():
    seen = set()
    for jar in jars:
        for name, z in open_all(jar):
            key = os.path.basename(name.split('!')[-1])
            if key in seen: continue
            seen.add(key)
            yield name, z
            # one more level (fabric-api modules bundle nothing deeper, a few libraries do)
            if '!' in name:
                for n in z.namelist():
                    if n.startswith('META-INF/jars/') and n.endswith('.jar'):
                        k2 = os.path.basename(n)
                        if k2 in seen: continue
                        seen.add(k2)
                        try:
                            yield f'{name}!{n}', zipfile.ZipFile(io.BytesIO(z.read(n)))
                        except Exception:
                            pass

nzips = 0
for jar, z in all_zips():
    nzips += 1
    for n in z.namelist():
        if not n.startswith('data/') or n.endswith('/'): continue
        p = n.split('/')
        if len(p) < 4: continue
        ns, kind = p[1], p[2]
        rest = '/'.join(p[3:])
        if kind in ('recipes', 'loot_tables', 'structures'):
            legacy[(os.path.basename(jar), kind)] += 1
            continue
        try:
            if kind == 'structure' and n.endswith('.nbt'):
                raw = gzip.decompress(z.read(n))
                for m in NAME_RE.finditer(raw):
                    ln = int.from_bytes(m.group(1), 'big')
                    s = raw[m.end():m.end() + ln].decode('utf-8', 'replace')
                    if ID.match(s): natural.add(s)
                continue
            if not n.endswith('.json'): continue
            if kind not in ('recipe', 'loot_table', 'tags', 'villager_trade', 'block_transformer', 'worldgen'): continue
            j = json.loads(z.read(n).decode('utf-8-sig'))
        except Exception:
            continue
        path = rest[:-5]
        if kind == 'tags':
            sub = path.split('/', 1)
            if len(sub) < 2 or sub[0] not in ('item', 'block'): continue
            t = f'{ns}:{sub[1]}'
            if isinstance(j, dict):
                if j.get('replace'): tag_replace.add((sub[0], t))
                for v in j.get('values', []):
                    if isinstance(v, dict): v = v.get('id', '')
                    tags[(sub[0], t)].add(v)
        elif kind == 'worldgen':
            ids_in(j, natural)
        elif kind == 'recipe':
            if not isinstance(j, dict) or not conditions_ok(j): continue
            ty = j.get('type', '')
            outs, slots = set(), []
            for k, v in j.items():
                if re.search(r'result|output|product', k, re.I): ids_in(v, outs)
            if 'key' in j and 'pattern' in j and isinstance(j['key'], dict):
                slots = [ids_in(v, set()) for v in j['key'].values()]
            elif isinstance(j.get('ingredients'), list):
                slots = [ids_in(v, set()) for v in j['ingredients']]
            else:
                for k, v in j.items():
                    if k in ('type', 'group', 'category', 'pattern', 'fabric:load_conditions', 'conditions',
                             'neoforge:conditions', 'show_notification') or re.search(r'result|output|product', k, re.I):
                        continue
                    if isinstance(v, list) and all(isinstance(e, (str, dict, list)) for e in v):
                        slots += [ids_in(e, set()) for e in v]
                    else:
                        slots.append(ids_in(v, set()))
            slots = [s for s in slots if s]
            recipes.append((f'{ns}:{path} ({ty})', slots, outs))
        elif kind == 'villager_trade':
            if not isinstance(j, dict): continue
            outs = ids_in(j.get('gives', {}), set())
            slots = [ids_in(j[k], set()) for k in ('wants', 'additional_wants') if k in j]
            recipes.append((f'trade {ns}:{path}', [s for s in slots if s], outs))
        elif kind == 'block_transformer':
            rules = j if isinstance(j, list) else [j]
            for r in rules:
                for rule in (r.get('block_state_provider', {}) or {}).get('rules', []) if isinstance(r, dict) else []:
                    src = ids_in(rule.get('if_true', {}), set())
                    out = ids_in(rule.get('then', {}), set())
                    if src and out: recipes.append((f'{ns}:{path} (block transformer)', [src], out))
        elif kind == 'loot_table':
            if not isinstance(j, dict): continue
            items, refs = set(), set()
            def walk(e):
                if isinstance(e, dict):
                    t = e.get('type', '').replace('minecraft:', '')
                    if t == 'item' and isinstance(e.get('name'), str): items.add(e['name'] if ':' in e['name'] else 'minecraft:' + e['name'])
                    elif t == 'tag' and isinstance(e.get('name'), str): items.add('#' + e['name'])
                    elif t == 'loot_table' and isinstance(e.get('value', e.get('name')), str): refs.add(e.get('value', e.get('name')))
                    for k in ('pools', 'entries', 'children'):
                        for c in e.get(k, []) or []: walk(c)
                    if t == 'loot_table' and isinstance(e.get('value'), dict): walk(e['value'])
            walk(j)
            block = f'{ns}:{path[7:]}' if path.startswith('blocks/') else None
            lk = path.split('/')[0]
            loot[f'{ns}:{path}'] = (lk, block, items, refs)

# tags: resolve nested tags
def tag_members(kind, t, seen=None):
    seen = seen or set()
    if t in seen: return set()
    seen.add(t)
    out = set()
    for v in tags.get((kind, t), ()):
        if isinstance(v, str) and v.startswith('#'): out |= tag_members(kind, v[1:], seen)
        elif isinstance(v, str): out.add(v.rstrip('?'))
    return out

# loot table references: a table that pulls another table gets its items
changed = True
while changed:
    changed = False
    for k, (lk, b, items, refs) in loot.items():
        for r in list(refs):
            if r in loot and not loot[r][2] <= items:
                items |= loot[r][2]; changed = True

def expand(x):
    return tag_members('item', x[1:]) if x.startswith('#') else {x}

HAND = {  # mechanics without data files
    'minecraft:water_bucket', 'minecraft:lava_bucket', 'minecraft:milk_bucket', 'minecraft:powder_snow_bucket',
    'minecraft:honey_bottle', 'minecraft:honeycomb', 'minecraft:carved_pumpkin', 'minecraft:dragon_breath',
    'minecraft:potion', 'minecraft:splash_potion', 'minecraft:lingering_potion', 'minecraft:filled_map',
    'minecraft:written_book', 'minecraft:firework_rocket', 'minecraft:firework_star', 'minecraft:tipped_arrow',
    'minecraft:suspicious_stew', 'minecraft:dragon_egg', 'minecraft:elytra', 'minecraft:nether_star',
    'minecraft:cod_bucket', 'minecraft:salmon_bucket', 'minecraft:tropical_fish_bucket', 'minecraft:pufferfish_bucket',
    'minecraft:axolotl_bucket', 'minecraft:tadpole_bucket', 'minecraft:enchanted_book', 'minecraft:ominous_bottle',
    'minecraft:ominous_trial_key', 'minecraft:trial_key', 'minecraft:experience_bottle', 'minecraft:mud',
}
obt = set(HAND)
why = {i: 'mechanic (hand list)' for i in HAND}
for k, (lk, b, items, refs) in loot.items():
    if b is None:
        for i in items:
            for x in expand(i):
                if x not in obt: obt.add(x); why[x] = f'loot {k}'
for b in natural:
    if b in ITEMS and b not in obt: obt.add(b); why[b] = 'generates in the world'

# quest rewards and crate tables (--no-rewards: leave them out, to see which items only quests give)
import dc_quests as D
for c in ([] if '--no-rewards' in sys.argv else D.B.chapters):
    for q in c.quests:
        for r in q.get('rewards', []):
            if r['type'] == 'item':
                i = r['item']['id'] if isinstance(r['item'], dict) else r['item']
                for x in expand(i):
                    obt.add(x); why.setdefault(x, f"quest reward {c.key}:{q['_key']}")
            if r['type'] == 'choice':
                for i in r['items']:
                    i = i['id'] if isinstance(i, dict) else i
                    obt.add(i); why.setdefault(i, f"quest choice reward {c.key}:{q['_key']}")
for k, t in ({} if '--no-rewards' in sys.argv else D.B.tables).items():
    for e in t['entries']:
        i = e['item']['id'] if isinstance(e['item'], dict) else e['item']
        obt.add(i); why.setdefault(i, f'Quest Icons crate table {k}')

block_tables = [(k, b, items) for k, (lk, b, items, refs) in loot.items() if b]
changed = True
rounds = 0
while changed:
    changed = False; rounds += 1
    for where, slots, outs in recipes:
        if all(any(x in obt for a in s for x in expand(a)) or not any(x in ITEMS for a in s for x in expand(a)) for s in slots):
            for o in outs:
                for x in expand(o):
                    if x not in obt: obt.add(x); why[x] = 'recipe ' + where; changed = True
    for k, b, items in block_tables:
        drops = {x for i in items for x in expand(i)}
        placeable = b in obt or b in natural or (b not in ITEMS and any(d in obt for d in drops))
        if placeable:
            for x in drops:
                if x not in obt: obt.add(x); why[x] = f'block drop {k}'; changed = True

# report on quest items
rows, missing = [], []
for c in D.B.chapters:
    for q in c.quests:
        for t in q['tasks']:
            if t['type'] != 'item': continue
            i = t['item']['id'] if isinstance(t['item'], dict) else t['item']
            members = expand(i)
            ok = [m for m in members if m in obt]
            w = f"{c.key}:{q['_key']}"
            if ok:
                rows.append((w, i, why.get(ok[0], '?')))
            else:
                missing.append((w, i, q['title']))
print(f'{len(jars)} jars ({nzips} with nested ones), {len(recipes)} recipes/trades/transformers, {len(loot)} loot tables, {len(natural)} worldgen ids, '
      f'{rounds} rounds, {len(obt)} obtainable ids')
if legacy:
    print('data in old folder names (not loaded in 26.3):', dict(legacy))
print(f'quest item tasks: {len(rows) + len(missing)}, with a source: {len(rows)}, without: {len(missing)}')
for m in missing: print('NO SOURCE', *m)
if '--json' in sys.argv:
    json.dump({'ok': rows, 'missing': missing, 'why': why}, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
