"""qjars.py : read the ids a mod jar brings (items, mobs, advancements, structures, biomes, tags) straight from the jar.

qcheck.py uses it for the pack's own jars ($SP/ownjars: Quest Icons, Beach Craft, Tamagotchi), so the quest book is
checked against the jars that really ship, not against an older registry dump.
  python3 tools/qjars.py some.jar [more.jar ...]   prints a short summary per jar
"""
import json, re, sys, zipfile

TAG_KINDS = ('item', 'block', 'entity_type', 'worldgen/structure', 'worldgen/biome')


def scan(path):
    """Ids of one jar: {'items': {id: name}, 'entity': set, 'advancement': set, 'structure': set, 'biome': set,
    'tags': {kind: set}, 'namespaces': set, 'file': jar name}."""
    z = zipfile.ZipFile(path)
    names = z.namelist()
    lang = {}
    for n in names:
        if re.fullmatch(r'assets/[^/]+/lang/en_us\.json', n):
            try:
                lang.update(json.loads(z.read(n).decode('utf-8', 'replace'), strict=False))
            except ValueError:
                pass
    out = {'items': {}, 'entity': set(), 'advancement': set(), 'structure': set(), 'biome': set(),
           'tags': {k: set() for k in TAG_KINDS}, 'namespaces': set(), 'file': path.rsplit('/', 1)[-1]}
    for n in names:
        m = re.fullmatch(r'assets/([^/]+)/items/(.+)\.json', n)
        if m:
            ns, p = m.groups()
            out['items'][f'{ns}:{p}'] = lang.get(f'item.{ns}.{p}') or lang.get(f'block.{ns}.{p}') or p
            out['namespaces'].add(ns)
            continue
        m = re.fullmatch(r'data/([^/]+)/(advancement|worldgen/structure|worldgen/biome)/(.+)\.json', n)
        if m:
            ns, kind, p = m.groups()
            out[{'advancement': 'advancement', 'worldgen/structure': 'structure', 'worldgen/biome': 'biome'}[kind]].add(f'{ns}:{p}')
            out['namespaces'].add(ns)
            continue
        m = re.fullmatch(r'data/([^/]+)/tags/(item|block|entity_type|worldgen/structure|worldgen/biome)/(.+)\.json', n)
        if m:
            ns, kind, p = m.groups()
            out['tags'][kind].add(f'{ns}:{p}')
    for k in lang:
        m = re.fullmatch(r'entity\.([a-z0-9_.-]+?)\.([a-z0-9_/]+)', k)
        if m and m.group(1) in out['namespaces']:
            out['entity'].add(f'{m.group(1)}:{m.group(2)}')
    return out


if __name__ == '__main__':
    for j in sys.argv[1:]:
        s = scan(j)
        print(s['file'], 'namespaces', sorted(s['namespaces']), 'items', len(s['items']), 'mobs', len(s['entity']),
              'advancements', len(s['advancement']), 'structures', len(s['structure']), 'biomes', len(s['biome']),
              'tags', {k: len(v) for k, v in s['tags'].items()})
