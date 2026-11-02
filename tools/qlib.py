"""Tiny DSL that writes Quest Icons / FTB-style SNBT quest files."""
import os, json

def fnv(s):
    h = 0xcbf29ce484222325
    for c in s:
        h ^= ord(c)
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h or 1

def hid(key):
    return '%016X' % fnv(key)

# ------------------------------------------------------------------ SNBT writer (same layout as the mod)
ORDER = ["id", "type", "filename", "title", "subtitle", "icon", "group", "order_index", "default_quest_shape", "x", "y", "shape",
         "size", "dependencies", "dependency_requirement", "optional", "hide_until_deps_complete", "hide_dependency_lines",
         "description", "tasks", "rewards", "quests", "images"]

def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

def keyorder(k):
    return (ORDER.index(k), '') if k in ORDER else (len(ORDER), k)

def simple(v):
    return not isinstance(v, (dict, list))

def w(v, d=0):
    t = '\t'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, float):
        return (str(int(v)) + '.0d') if v == int(v) else repr(v) + 'd'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return q(v)
    if isinstance(v, list):
        if not v:
            return '[ ]'
        if all(simple(x) for x in v) and not any(isinstance(x, str) and len(x) > 24 for x in v):
            return '[' + ', '.join(w(x, d + 1) for x in v) + ']'
        return '[\n' + ''.join(t * (d + 1) + w(x, d + 1) + '\n' for x in v) + t * d + ']'
    if isinstance(v, dict):
        if not v:
            return '{ }'
        keys = sorted(v, key=keyorder)
        if d > 0 and len(v) <= 3 and all(simple(v[k]) for k in v):
            return '{ ' + ', '.join(f'{k}: {w(v[k], d + 1)}' for k in keys) + ' }'
        return '{\n' + ''.join(f'{t * (d + 1)}{k}: {w(v[k], d + 1)}\n' for k in keys) + t * d + '}'
    raise TypeError(v)

# ------------------------------------------------------------------ tasks
def item(i, n=1, consume=False):
    t = {'type': 'item', 'item': i}
    if n != 1: t['count'] = n
    if consume: t['consume_items'] = True
    return t

def check(title=None):
    t = {'type': 'checkmark'}
    if title: t['title'] = title
    return t

def kill(e, n=1):
    return {'type': 'kill', 'entity': e, 'value': n}

def adv(a, title=None):
    t = {'type': 'advancement', 'advancement': a}
    if title: t['title'] = title
    return t

def dim(dm, title=None):
    t = {'type': 'dimension', 'dimension': dm}
    if title: t['title'] = title
    return t

def biome(b, title=None):
    t = {'type': 'biome', 'biome': b}
    if title: t['title'] = title
    return t

def struct(s, title=None):
    t = {'type': 'structure', 'structure': s}
    if title: t['title'] = title
    return t

def xp(levels, consume=False):
    t = {'type': 'xp', 'value': levels}
    if consume: t['consume'] = True
    return t

def observe(b, timer=40, entity=False, title=None):
    t = {'type': 'observation', 'observe': b, 'timer': timer}
    if entity: t['entity'] = True
    if title: t['title'] = title
    return t

def stat(s, n, title=None):
    t = {'type': 'stat', 'stat': s, 'value': n}
    if title: t['title'] = title
    return t

# ------------------------------------------------------------------ rewards
def give(i, n=1):
    r = {'type': 'item', 'item': i}
    if n != 1: r['count'] = n
    return r

def rxp(n):
    return {'type': 'xp', 'xp': n}

def levels(n):
    return {'type': 'xp_levels', 'xp_levels': n}

def crate(kind, n=1):
    return give(f'questsicons:{kind}_crate', n)

def choice(*items):
    return {'type': 'choice', 'items': [({'id': i, 'count': n} if n > 1 else i) for i, n in items]}

def loot(table, title=None):
    r = {'type': 'loot', 'loot_table': table}
    if title: r['title'] = title
    return r

# ------------------------------------------------------------------ book
class Book:
    def __init__(self):
        self.chapters = []
        self.groups = []
        self.tables = {}

    def group(self, key, title, icon):
        self.groups.append({'id': hid('group/' + key), 'title': title, 'icon': icon})
        return hid('group/' + key)

    def chapter(self, key, title, icon, subtitle=(), group='', shape=''):
        c = Chapter(self, key, title, icon, list(subtitle), group, shape)
        self.chapters.append(c)
        return c

    def table(self, key, title, icon, entries):
        self.tables[key] = {'title': title, 'icon': icon,
                            'entries': [dict(item=i, count=n, weight=wt) if n != 1 else dict(item=i, weight=wt) for i, n, wt in entries]}

    def write(self, out, data):
        os.makedirs(f'{out}/chapters', exist_ok=True)
        os.makedirs(f'{out}/reward_tables', exist_ok=True)
        open(f'{out}/data.snbt', 'w').write(w(data) + '\n')
        open(f'{out}/chapter_groups.snbt', 'w').write(w({'chapter_groups': self.groups}) + '\n')
        for i, c in enumerate(self.chapters):
            open(f'{out}/chapters/{c.key}.snbt', 'w').write(w(c.data(i)) + '\n')
        for k, t in self.tables.items():
            open(f'{out}/reward_tables/{k}.snbt', 'w').write(w(t) + '\n')

    def all_quests(self):
        for c in self.chapters:
            for qq in c.quests:
                yield c, qq


class Chapter:
    def __init__(self, book, key, title, icon, subtitle, group, shape):
        self.book, self.key, self.title, self.icon, self.subtitle, self.group, self.shape = book, key, title, icon, subtitle, group, shape
        self.quests = []
        self.images = []
        self.ids = {}

    def qid(self, key):
        if ':' in key:
            return hid('q/' + key)
        return hid('q/' + self.key + ':' + key)

    def quest(self, key, title, x, y, desc, tasks, rewards=(), icon=None, deps=(), shape=None, size=None, subtitle=None,
              optional=False, any_dep=False, hide=False):
        qd = {'id': self.qid(key), 'title': title, 'x': float(x), 'y': float(y), 'description': list(desc)}
        if icon: qd['icon'] = icon
        if shape: qd['shape'] = shape
        if size: qd['size'] = float(size)
        if subtitle: qd['subtitle'] = subtitle
        if deps: qd['dependencies'] = [self.qid(d) for d in deps]
        if any_dep: qd['dependency_requirement'] = 'one_completed'
        if optional: qd['optional'] = True
        if hide: qd['hide_until_deps_complete'] = True
        qd['tasks'] = [dict(t, id=hid(f'{qd["id"]}/t{n}')) for n, t in enumerate(tasks)]
        if rewards:
            qd['rewards'] = [dict(r, id=hid(f'{qd["id"]}/r{n}')) for n, r in enumerate(rewards)]
        qd['_key'] = key
        self.quests.append(qd)
        return qd

    def image(self, img, x, y, wdt, hgt, hover='', alpha=255, rotation=0, front=False):
        d = {'image': img, 'x': float(x), 'y': float(y), 'width': float(wdt), 'height': float(hgt)}
        if hover: d['hover'] = hover
        if alpha != 255: d['alpha'] = alpha
        if rotation: d['rotation'] = float(rotation)
        if front: d['front'] = True
        self.images.append(d)

    def data(self, idx):
        d = {'id': hid('chapter/' + self.key), 'filename': self.key, 'title': self.title, 'icon': self.icon, 'order_index': idx,
             'quests': [{k: v for k, v in qq.items() if not k.startswith('_')} for qq in self.quests]}
        if self.subtitle: d['subtitle'] = self.subtitle
        if self.group: d['group'] = self.group
        if self.shape: d['default_quest_shape'] = self.shape
        if self.images: d['images'] = self.images
        return d
