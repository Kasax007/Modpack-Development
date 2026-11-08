"""Images of the Dreamcraft 26.3 V1.5 CurseForge page (docs/curseforge/img/*_v15.*): the header, the trailer card,
the "at a glance" numbers, the map of the quest story, two flow diagrams (the quest book, the Dream Star), the news of
V1.5, the section strips, the shader collages, the highlights of the mod list, the main menu and the setup tiles.
The colours follow the official BisectHosting graphics of Dreamcraft (night sky, lavender clouds, cream text).

  python3 docs/curseforge/make_images_v15.py FOOTAGE_DIR FONTS_DIR JAR_DIRS [what ...]

FOOTAGE_DIR: Archive/footage (shader footage, one MP4 per shot: dc/ = the Dreamcraft trailer shots in 1080x1920,
  bc3v2/ = Beach Craft 3.1, tama2/ = Tamacraft (filmed as Tamagotchi)). The trailer itself is read from
  FOOTAGE_DIR/../dreamcraft/tiktok/dreamcraft_tiktok_clean_music.mp4.
FONTS_DIR: Archive/fonts (Lilita One for titles, Inter Display Bold for the small print).
JAR_DIRS: folders holding the pack's jars, separated by ':' (the CurseForge files of pack/mods.json and the own jars
  QuestIcons-*.jar, raft-*.jar, tamacraft-*.jar). Item and block pictures are read from the jars; vanilla ones from
  the Minecraft client jar ($MC_JAR, default: the Loom cache).
what: header video glance story flow_quests flow_star new strips collages mods menu setup counts (default: all but
  counts). Frames are cut with ffmpeg into $DC14_FRAMES (default: a temporary folder). The menu picture also uses the two
  screenshots in docs/curseforge/src_v14 and the menu backgrounds of the pack (config/fancymenu/assets/dreamcraft).

Every number on the pictures is counted from the repository or the pack's jars in counts()."""
import glob
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import zipfile

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'img')
QUESTS = os.path.join(REPO, 'pack', 'overrides', 'config', 'questsicons', 'quests')
MENU = os.path.join(REPO, 'pack', 'overrides', 'config', 'fancymenu', 'assets', 'dreamcraft')
FOOT, FONTS, JARS = sys.argv[1], sys.argv[2], sys.argv[3].split(':')
TRAILER = os.path.join(FOOT, '..', 'dreamcraft', 'tiktok', 'dreamcraft_tiktok_clean_music.mp4')
CACHE = os.environ.get('DC14_FRAMES') or os.path.join(tempfile.gettempdir(), 'dc14_frames')
MC_JAR = os.environ.get('MC_JAR') or os.path.expanduser('~/.gradle/caches/fabric-loom/26.3/minecraft-client.jar')
W = 1200
MAX_BYTES = 950 * 1024

# the colours of the official Dreamcraft graphics (bh_header.png, bh_1.png ...)
SKY0, SKY1 = (21, 0, 54), (45, 14, 76)          # night sky, top and bottom
DEEP = (31, 0, 74)                              # outlines, dark text
CLOUD1, CLOUD2, CLOUD3, CLOUD4 = (51, 26, 133), (80, 53, 195), (127, 105, 253), (150, 140, 249)
CREAM = (255, 250, 206)
MAGENTA = (214, 5, 209)
WHITE = (255, 255, 255)
GOLD = (255, 205, 90)
INK = (40, 16, 86)                              # small print on cards
PANEL = (255, 252, 236)                         # card fill


def font(size):
    return ImageFont.truetype(os.path.join(FONTS, 'LilitaOne-Regular.ttf'), size)


def small(size):
    return ImageFont.truetype(os.path.join(FONTS, 'InterDisplay-Bold.otf'), size)


# ----------------------------------------------------------------------------------------------- the numbers
def snbt(text):
    """Reads the SNBT of the quest book (objects, lists, strings, numbers, bare words)."""
    i, n = 0, len(text)

    def ws():
        nonlocal i
        while i < n and text[i] in ' \t\r\n,':
            i += 1

    def string():
        nonlocal i
        q, i, out = text[i], i + 1, []
        while text[i] != q:
            if text[i] == '\\':
                i += 1
            out.append(text[i])
            i += 1
        i += 1
        return ''.join(out)

    def value():
        nonlocal i
        ws()
        c = text[i]
        if c == '{':
            i, obj = i + 1, {}
            while True:
                ws()
                if text[i] == '}':
                    i += 1
                    return obj
                if text[i] in '"\'':
                    k = string()
                else:
                    j = i
                    while text[i] not in ' \t\r\n:':
                        i += 1
                    k = text[j:i]
                ws()
                i += 1                                          # ':'
                obj[k] = value()
        if c == '[':
            i, lst = i + 1, []
            while True:
                ws()
                if text[i] == ']':
                    i += 1
                    return lst
                lst.append(value())
        if c in '"\'':
            return string()
        j = i
        while i < n and text[i] not in ' \t\r\n,}]:':
            i += 1
        w = text[j:i]
        if re.match(r'^[-+]?(\d+\.?\d*|\.\d+)[bsldfBSLDF]?$', w):
            v = w.rstrip('bsldfBSLDF')
            return float(v) if '.' in v else int(v)
        return {'true': True, 'false': False}.get(w, w)

    return value()


def chapters():
    """The chapters of the quest book in book order: dicts with key, title, subtitle, icon, group, quests."""
    groups = [g['id'] for g in snbt(open(os.path.join(QUESTS, 'chapter_groups.snbt')).read())['chapter_groups']]
    out = []
    for f in sorted(glob.glob(os.path.join(QUESTS, 'chapters', '*.snbt'))):
        c = snbt(open(f, encoding='utf-8').read())
        out.append(dict(key=c['filename'], title=re.sub(r'&[0-9a-fk-or]', '', c['title']), icon=c['icon'],
                        subtitle=re.sub(r'&[0-9a-fk-or]', '', ' '.join(c.get('subtitle', []))), group=groups.index(c['group']),
                        order=c.get('order_index', 0), quests=c['quests']))
    return sorted(out, key=lambda c: (c['group'], c['order']))


def jar(pattern):
    hits = sorted(h for d in JARS for h in glob.glob(os.path.join(d, pattern)))
    if not hits:
        sys.exit('no jar %s in %s' % (pattern, JARS))
    return hits[-1]


def counts():
    """Every number of the pictures, counted from the repository and the pack's jars."""
    mods = json.load(open(os.path.join(REPO, 'pack', 'mods.json')))
    jars = [m for m in mods if m['file'].endswith('.jar')]
    shaders = [m for m in mods if not m['file'].endswith('.jar')]
    own = 2                                   # Quest Icons and Beach Craft, added to the manifest by tools/mkpack.py
    ch = chapters()
    q = {c['key']: len(c['quests']) for c in ch}
    crates = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(QUESTS, 'reward_tables', '*.snbt')))

    def files(pattern, rx):
        return len([n for n in zipfile.ZipFile(jar(pattern)).namelist() if re.match(rx, n)])

    biomes = dict(terralith=files('*Terralith*.jar', r'data/terralith/worldgen/biome/.+\.json$'),
                  betternether=files('*better-nether*.jar', r'data/betternether/worldgen/biome/.+\.json$'),
                  betterend=files('*better-end*.jar', r'data/betterend/worldgen/biome/.+\.json$'))
    raft = zipfile.ZipFile(jar('raft-*.jar'))
    dim = json.loads(raft.read('data/raft/dimension/raftdim.json'))
    biomes['endless_sea'] = len({b['biome'] for b in dim['generator']['biome_source']['biomes']})
    people = len([n for n in raft.namelist()
                  if re.match(r'assets/raft/textures/entity/npc/[a-z_]+\.png$', n) and not n.endswith('_extra.png')])
    tama = json.loads(zipfile.ZipFile(jar('*tamacraft-*.jar')).read('assets/tamacraft/lang/en_us.json'))
    pets = len([k for k in tama if re.match(r'entity\.tamacraft\.[a-z_]+$', k)])
    qi = zipfile.ZipFile(jar('QuestIcons-*.jar'))
    star = json.loads(qi.read('data/questsicons/recipe/dream_star.json'))
    chests = json.loads(zipfile.ZipFile(jar('*upgraded-iron-chests-*.jar')).read('assets/upgraded-iron-chests/lang/en_us.json'))
    tiers = [v for k, v in chests.items() if k.startswith('block.') and 'safe' not in k]
    menu_bgs = len(glob.glob(os.path.join(MENU, 'bg*.jpg')))
    return dict(mods=len(jars) + own, shaders=len(shaders), quests=sum(q.values()), chapters=len(ch),
                story=len([c for c in ch if c['group'] == 0]), side=len([c for c in ch if c['group'] == 1]),
                per_chapter=q, crates=len(crates), crate_names=crates, biomes=sum(biomes.values()),
                biome_parts=biomes, people=people, pets=pets, treasures=len(star['key']), chest_tiers=len(tiers),
                menu_backgrounds=menu_bgs, qol=q['qol'], island=q.get('island', 0))


# ----------------------------------------------------------------------------------------------- textures
_zips = {}


def _zip(path):
    if path not in _zips:
        _zips[path] = zipfile.ZipFile(path)
    return _zips[path]


NS_JAR = {'minecraft': None, 'questsicons': 'QuestIcons-*.jar', 'raft': 'raft-*.jar', 'tamacraft': '*tamacraft-*.jar',
          'upgraded-iron-chests': '*upgraded-iron-chests-*.jar', 'wizards': '*wizards-fabric*.jar',
          'paladins': '*paladins-fabric*.jar', 'mythicupgrades': '*mythicupgrades*.jar', 'techreborn': '*TechReborn*.jar',
          'farmersdelight': '*FarmersDelight*.jar', 'cookingforblockheads': '*cookingforblockheads*.jar',
          'mutantmonsters': '*mutantmonsters*.jar', 'mcwroofs': '*mcw-roofs*.jar', 'waystones': '*waystones*.jar',
          'storagedrawers': '*StorageDrawers*.jar', 'xaerominimap': '*xaerominimap*.jar', 'betterend': '*better-end*.jar',
          'betternether': '*better-nether*.jar', 'naturalist': '*naturalist*.jar', 'jewelry': '*jewelry-fabric*.jar',
          'archers': '*archers-fabric*.jar', 'rogues': '*rogues-fabric*.jar', 'voicechat': '*voicechat*.jar',
          'travelersbackpack': '*travelersbackpack*.jar', 'iris': '*iris-fabric*.jar', 'lootr': '*lootr*.jar',
          'quarrymod': '*quarry-reborn*.jar', 'dawnoftime': '*Dawn Of Time*.jar'}


def raw(ns_path, kind='textures'):
    """A file of a mod: 'namespace:path' -> bytes of assets/namespace/<kind>/path."""
    ns, rel = ns_path.split(':', 1)
    z = _zip(MC_JAR if ns == 'minecraft' else jar(NS_JAR[ns]))
    return z.read('assets/%s/%s/%s' % (ns, kind, rel))


def tex(ns_path, size=None, square=True):
    """A texture 'namespace:item/name' (first frame of animated ones), scaled with NEAREST to size."""
    im = Image.open(io.BytesIO(raw(ns_path + '.png'))).convert('RGBA')
    if square and im.height > im.width:
        im = im.crop((0, 0, im.width, im.width))
    if size:
        im = im.resize((size, size * im.height // im.width), Image.NEAREST)
    return im


def cube(top, left, right, a=48):
    """Inventory-style block from three faces (each a square texture), 2a x 2a."""
    S = top.width
    out = Image.new('RGBA', (2 * a, 2 * a), (0, 0, 0, 0))
    faces = [
        (top, (S / (2 * a), -S / a, S / 2, S / (2 * a), S / a, -S / 2), [(a, 0), (2 * a, a / 2), (a, a), (0, a / 2)], 1.0),
        (left, (S / a, 0, 0, -S / (2 * a), S / a, -S / 2), [(0, a / 2), (a, a), (a, 2 * a), (0, 1.5 * a)], 0.8),
        (right, (S / a, 0, -S, S / (2 * a), S / a, -1.5 * S), [(a, a), (2 * a, a / 2), (2 * a, 1.5 * a), (a, 2 * a)], 0.62),
    ]
    for t, aff, poly, shade in faces:
        t = t.resize((S, S), Image.NEAREST) if t.size != (S, S) else t
        f = t.transform((2 * a, 2 * a), Image.AFFINE, aff, resample=Image.NEAREST)
        if shade < 1:
            r, g, b, al = f.split()
            r, g, b = (c.point(lambda v, s=shade: int(v * s)) for c in (r, g, b))
            f = Image.merge('RGBA', (r, g, b, al))
        m = Image.new('L', (2 * a, 2 * a), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        out.paste(f, (0, 0), Image.composite(f.split()[3], Image.new('L', m.size, 0), m))
    return out


def tcube(top, side=None, front=None, a=48):
    """Cube from textures 'ns:block/x' (top, side, front)."""
    t = tex(top)
    s = tex(side or top)
    return cube(t, tex(front) if front else s, s, a)


def chest(ns_path, a=48):
    """Chest icon from an entity chest texture (64x64 layout of the vanilla chest: lid 14x5x14, base 14x10x14)."""
    t = tex(ns_path, square=False)
    k = t.width // 64

    def r(x0, y0, x1, y1):
        return t.crop((x0 * k, y0 * k, x1 * k, y1 * k))

    top = r(14, 0, 28, 14).transpose(Image.ROTATE_180)
    front = Image.new('RGBA', (14 * k, 15 * k))
    front.paste(r(42, 14, 56, 19), (0, 0))
    front.paste(r(42, 33, 56, 43), (0, 5 * k))
    side = Image.new('RGBA', (14 * k, 15 * k))
    side.paste(r(28, 14, 42, 19), (0, 0))
    side.paste(r(28, 33, 42, 43), (0, 5 * k))
    lock = r(1, 1, 3, 5)
    front.paste(lock, (6 * k, 3 * k))
    sq = lambda im: im.resize((16 * k, 16 * k), Image.NEAREST)
    return cube(sq(top), sq(front), sq(side), a)


def npc_face(npc, size):
    """Head of a person of the sea (front of the skin's head plus the hat layer)."""
    skin = tex('raft:entity/npc/' + npc, square=False)
    head = skin.crop((8, 8, 16, 16))
    head.alpha_composite(skin.crop((40, 8, 48, 16)))
    return head.resize((size, size), Image.NEAREST)


def egg(ns_path, size):
    """The dragon egg as the inventory shows it: its texture inside an egg shape."""
    t = tex(ns_path, 16)
    mask = Image.new('L', (16, 16), 0)
    rows = [(6, 9), (5, 10), (4, 11), (3, 12), (3, 12), (2, 13), (2, 13), (1, 14), (1, 14), (1, 14), (1, 14), (1, 14),
            (2, 13), (2, 13), (3, 12), (5, 10)]
    d = ImageDraw.Draw(mask)
    for y, (x0, x1) in enumerate(rows):
        d.line([(x0, y), (x1, y)], fill=255)
    out = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    out.paste(t, (0, 0), mask)
    shade = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y, (x0, x1) in enumerate(rows):
        sd.line([(x1 - 2, y), (x1, y)], fill=(0, 0, 0, 90))
        sd.point((x0 + 1, y), fill=(255, 255, 255, 40))
    out = Image.alpha_composite(out, Image.composite(shade, Image.new('RGBA', (16, 16), (0, 0, 0, 0)), mask))
    return out.resize((size, size), Image.NEAREST)


def icon(name, size=96):
    """The item and block pictures of the page, by short name."""
    I = {
        'book': lambda: tex('questsicons:item/quest_book'), 'star': lambda: tex('questsicons:item/dream_star'),
        'crown': lambda: tex('questsicons:item/quest_crown'), 'fabric': lambda: tex('questsicons:item/logo_fabric'),
        'common': lambda: tex('questsicons:item/common_crate'), 'rare': lambda: tex('questsicons:item/rare_crate'),
        'epic': lambda: tex('questsicons:item/epic_crate'), 'legendary': lambda: tex('questsicons:item/legendary_crate'),
        'pedestal': lambda: tcube('questsicons:block/dream_star_pedestal_top', 'questsicons:block/dream_star_pedestal_side'),
        'heart': lambda: tex('tamacraft:item/tamacraft_heart'), 'kibble': lambda: tex('tamacraft:item/pet_kibble'),
        'helm': lambda: tex('raft:item/helm'), 'tide': lambda: tex('raft:block/heart_of_the_tide'),
        'ametrine': lambda: tex('mythicupgrades:item/ametrine_ingot'),
        'staff': lambda: tex('wizards:item/staff_netherite_fire'), 'fire_staff': lambda: tex('wizards:item/staff_fire'),
        'orb': lambda: tex('techreborn:item/battery/lapotronic_orb'),
        'nether_star': lambda: tex('minecraft:item/nether_star'), 'egg': lambda: egg('minecraft:block/dragon_egg', 64),
        'iron': lambda: chest('upgraded-iron-chests:entity/chest/normal'),
        'gold': lambda: chest('upgraded-iron-chests:entity/chest/gold_normal'),
        'diamond': lambda: chest('upgraded-iron-chests:entity/chest/diamond_normal'),
        'netherite': lambda: chest('upgraded-iron-chests:entity/chest/netherite_normal'),
        'safe': lambda: tcube('upgraded-iron-chests:block/safe_chest'),
        'grinder': lambda: tcube('techreborn:block/machines/tier1_machines/machine_top',
                                 'techreborn:block/machines/tier1_machines/machine_side',
                                 'techreborn:block/machines/tier1_machines/grinder_front_on'),
        'pot': lambda: tex('farmersdelight:item/cooking_pot'),
        'roofs': lambda: tex('mcwroofs:item/roofing_hammer'),
        'map': lambda: tex('minecraft:item/filled_map'), 'chemical_x': lambda: tex('mutantmonsters:item/chemical_x'),
        'amethyst': lambda: tex('minecraft:item/amethyst_shard'), 'compass': lambda: tex('minecraft:item/compass_16'),
        'clock': lambda: tex('minecraft:item/clock_00'), 'sword': lambda: tex('minecraft:item/netherite_sword'),
        'xp': lambda: tex('minecraft:item/experience_bottle'), 'spyglass': lambda: tex('minecraft:item/spyglass'),
        'ender_eye': lambda: tex('minecraft:item/ender_eye'), 'chorus': lambda: tex('minecraft:item/popped_chorus_fruit'),
        'blaze': lambda: tex('minecraft:item/blaze_powder'), 'emerald': lambda: tex('minecraft:item/emerald'),
        'goat_horn': lambda: tex('minecraft:item/goat_horn'), 'apple': lambda: tex('minecraft:item/golden_apple'),
        'lantern': lambda: tex('minecraft:item/lantern'), 'bell': lambda: tex('minecraft:item/bell'),
    }
    for k in ('moon', 'house', 'pickaxe', 'gear', 'magic', 'raft', 'trophy', 'food', 'map', 'heart', 'chest', 'compass',
              'star', 'sword', 'tree', 'skull', 'shield', 'potion', 'question', 'exclamation'):
        I.setdefault('icon_' + k, lambda k=k: tex('questsicons:item/icon_' + k))
    for k in ('portal_two', 'dungeon', 'key', 'reward', 'backpack'):
        I.setdefault(k, lambda k=k: tex('questsicons:item/quest_' + k))
    I['end_lock'] = lambda: tex('questsicons:item/end_lock')
    im = I[name]()
    return im.resize((size, size * im.height // im.width), Image.NEAREST)


def item_icon(item_id, size):
    """Icon of a quest-book item id ('ns:name')."""
    ns, name = item_id.split(':', 1)
    special = {'upgraded-iron-chests:diamond_chest': 'diamond', 'tamacraft:tamacraft_heart': 'heart',
               'questsicons:end_lock': 'end_lock', 'questsicons:quest_portal_two': 'portal_two'}
    if item_id in special:
        return icon(special[item_id], size)
    return tex('%s:item/%s' % (ns, name), size)


# ----------------------------------------------------------------------------------------------- drawing helpers
def outlined(d, xy, text, f, fill=CREAM, stroke=6, stroke_fill=DEEP, anchor='la', shadow=True):
    if shadow:
        d.text((xy[0], xy[1] + stroke // 2 + 3), text, font=f, fill=stroke_fill, stroke_width=stroke,
               stroke_fill=stroke_fill, anchor=anchor)
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)


def rounded(im, r):
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    out = im.convert('RGBA')
    out.putalpha(m)
    return out


def gradient(w, h, c0, c1, horizontal=False):
    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    n = w if horizontal else h
    for i in range(n):
        t = i / max(1, n - 1)
        c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3)) + (255,)
        d.line([(i, 0), (i, h)] if horizontal else [(0, i), (w, i)], fill=c)
    return im


def sparkle(d, x, y, r, col=CREAM):
    """A four-pointed star like the ones in the official graphics."""
    k = max(1.0, r * 0.22)
    d.polygon([(x, y - r), (x + k, y - k), (x + r, y), (x + k, y + k), (x, y + r), (x - k, y + k), (x - r, y),
               (x - k, y - k)], fill=col)


def stars(im, box, n, seed, rmax=9, alpha=230):
    """Sparkles and dots scattered in box (x0, y0, x1, y1); the same seed gives the same sky."""
    import random
    rnd = random.Random(seed)
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if rnd.random() < 0.35:
            sparkle(d, x, y, rnd.uniform(4, rmax), CREAM + (alpha,))
        else:
            r = rnd.uniform(1.2, 2.6)
            d.ellipse([x - r, y - r, x + r, y + r], fill=CREAM + (int(alpha * 0.8),))
    im.alpha_composite(lay)


def clouds(im, y, seed, layers=((CLOUD1, CLOUD2), (CLOUD2, CLOUD3), (CLOUD3, CLOUD4)), r=(34, 64), step=0.8, gap=20):
    """Bands of round clouds from y down to the bottom, darkest band at the back, each bump with a lighter rim."""
    import random
    rnd = random.Random(seed)
    d = ImageDraw.Draw(im)
    w, h = im.size
    for k, (fill, rim) in enumerate(layers):
        top = y + k * gap
        x = -rnd.uniform(0, r[1])
        bumps = []
        while x < w + r[1]:
            rr = rnd.uniform(*r)
            bumps.append((x, top + rnd.uniform(-0.25, 0.35) * rr, rr))
            x += rr * step * 2
        for bx, by, rr in bumps:
            d.ellipse([bx - rr, by - rr - 3, bx + rr, by + rr - 3], fill=rim)
        for bx, by, rr in bumps:
            d.ellipse([bx - rr + 2, by - rr + 3, bx + rr - 2, by + rr + 3], fill=fill)
        if top + r[0] * 0.6 < h:
            d.rectangle([0, top + r[0] * 0.6, w, h], fill=fill)


def night(w, h, seed=1, cloud_y=None, n_stars=None):
    """Night-sky background with stars and, if cloud_y is given, cloud bands from there down."""
    im = gradient(w, h, SKY0, SKY1)
    stars(im, (0, 0, w, (cloud_y or h) - 10), n_stars if n_stars is not None else w * h // 9000, seed)
    if cloud_y is not None:
        clouds(im, cloud_y, seed)
    return im


def moon(im, center, r, glow=2.2):
    cx, cy = center
    g = Image.new('RGBA', im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    R = int(r * glow)
    gd.ellipse([cx - R, cy - R, cx + R, cy + R], fill=CREAM + (60,))
    g = g.filter(ImageFilter.GaussianBlur(r * 0.5))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r * 1.35, cy - r * 1.35, cx + r * 1.35, cy + r * 1.35], fill=CREAM + (40,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM)


def card(w, h, r=22, fill=PANEL, outline=CLOUD3, width=4):
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    g = gradient(w, h, fill, tuple(max(0, v - 18) for v in fill))
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    c.paste(g, (0, 0), m)
    if outline:
        ImageDraw.Draw(c).rounded_rectangle([0, 0, w - 1, h - 1], r, outline=outline + (255,), width=width)
    return c


def shadowed(im, layer, xy, blur=10, offset=(0, 6), alpha=120):
    sh = Image.new('RGBA', (layer.width + 4 * blur, layer.height + 4 * blur), (0, 0, 0, 0))
    a = layer.split()[3].point(lambda v: v * alpha // 255)
    sh.paste((8, 0, 24, 255), (2 * blur, 2 * blur), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(sh, (xy[0] - 2 * blur + offset[0], xy[1] - 2 * blur + offset[1]))
    im.alpha_composite(layer, xy)


def wrap(d, s, f, width):
    lines = ['']
    for word in s.split():
        t = (lines[-1] + ' ' + word).strip()
        if d.textlength(t, font=f) <= width or not lines[-1]:
            lines[-1] = t
        else:
            lines.append(word)
    return lines


def para(d, xy, s, f, width, fill=INK, gap=6, anchor='la'):
    """Wrapped text; anchor 'ma' centres every line on x. Returns the y below the last line."""
    x, y = xy
    asc, desc = f.getmetrics()
    for ln in wrap(d, s, f, width):
        d.text((x, y), ln, font=f, fill=fill, anchor=anchor)
        y += asc + desc + gap
    return y


def fitfont(d, s, maker, size, width, minimum=14):
    f = maker(size)
    while d.textlength(s, font=f) > width and size > minimum:
        size -= 1
        f = maker(size)
    return f


def badge(im, center, n, r=22, fill=CLOUD2):
    d = ImageDraw.Draw(im)
    x, y = center
    d.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], fill=CREAM)
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    d.text((x, y + 1), str(n), font=font(int(r * 1.25)), fill=CREAM, anchor='mm')


def arrow(d, pts, color=CREAM, width=14, head=26, outline=DEEP):
    """An outlined arrow along the points (head at the last one)."""
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    ang = math.atan2(yb - ya, xb - xa)
    bx, by = xb - head * math.cos(ang), yb - head * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    line = list(pts[:-1]) + [(bx + 2 * math.cos(ang), by + 2 * math.sin(ang))]
    tri = [(xb, yb), (bx + nx * head * 0.9, by + ny * head * 0.9), (bx - nx * head * 0.9, by - ny * head * 0.9)]
    mx, my = sum(p[0] for p in tri) / 3, sum(p[1] for p in tri) / 3
    big = [(mx + (px - mx) * 1.32, my + (py - my) * 1.32) for px, py in tri]
    for col, extra, t in ((outline, 7, big), (color, 0, tri)):
        r = (width + extra) / 2
        d.ellipse([line[0][0] - r, line[0][1] - r, line[0][0] + r, line[0][1] + r], fill=col)
        d.line(line, fill=col, width=width + extra, joint='curve')
        d.polygon(t, fill=col)


def slot(im, x, y, s=64, item=None, count=None):
    """A slot of the crafting grid (vanilla look) with an item."""
    d = ImageDraw.Draw(im)
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=(139, 139, 139))
    d.line([(x, y), (x + s - 1, y)], fill=(55, 55, 55), width=4)
    d.line([(x, y), (x, y + s - 1)], fill=(55, 55, 55), width=4)
    d.line([(x, y + s - 2), (x + s - 1, y + s - 2)], fill=WHITE, width=4)
    d.line([(x + s - 2, y), (x + s - 2, y + s - 1)], fill=WHITE, width=4)
    if item is not None:
        ic = item.resize((s - 16, (s - 16) * item.height // item.width), Image.NEAREST)
        im.alpha_composite(ic, (x + (s - ic.width) // 2, y + (s - ic.height) // 2))
    if count:
        outlined(d, (x + s - 6, y + s - 4), str(count), font(int(s * 0.42)), fill=WHITE, stroke=3,
                 stroke_fill=(40, 40, 40), anchor='rd', shadow=False)


def keycap(im, x, y, label, w=None, h=50, f=None):
    d = ImageDraw.Draw(im)
    f = f or small(24)
    w = w or max(h, int(d.textlength(label, font=f)) + 28)
    d.rounded_rectangle([x, y + 5, x + w, y + h + 5], 9, fill=(120, 100, 170))
    d.rounded_rectangle([x, y, x + w, y + h], 9, fill=WHITE, outline=(120, 100, 170), width=2)
    d.text((x + w / 2, y + h / 2), label, font=f, fill=INK, anchor='mm')
    return w


def save(im, name):
    """PNG (keeps rounded corners; falls back to 256 colours when too big) or JPEG; every file stays under 950 KB."""
    path = os.path.join(OUT, name)
    if name.endswith('.jpg'):
        q = 90
        while True:
            im.convert('RGB').save(path, quality=q, optimize=True, progressive=True)
            if os.path.getsize(path) <= MAX_BYTES or q <= 70:
                break
            q -= 3
    else:
        im.save(path, optimize=True)
        if os.path.getsize(path) > MAX_BYTES:
            alpha = im.split()[3] if im.mode == 'RGBA' else None
            p = im.convert('RGB').quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
            if alpha is not None:
                p = p.convert('RGBA')
                p.putalpha(alpha)
                p = p.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
            p.save(path, optimize=True)
    size = os.path.getsize(path)
    print('%-26s %4dx%-4d %4d KB' % (name, im.size[0], im.size[1], size // 1024))
    if size > MAX_BYTES:
        sys.exit('%s is too big' % name)


# ----------------------------------------------------------------------------------------------- footage
def frame(spec):
    """'group/clip@t': the picture at t seconds of FOOTAGE_DIR/group/clip.mp4 ('trailer@t': of the trailer)."""
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, spec.replace('/', '_') + '.jpg')
    if not os.path.exists(out):
        clip, t = spec.split('@')
        src = TRAILER if clip == 'trailer' else os.path.join(FOOT, clip + '.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', t, '-i', src, '-frames:v', '1', '-q:v', '2', out], check=True)
    return Image.open(out).convert('RGB')


def shot(spec, enh=None):
    im = frame(spec)
    if enh:
        b, c, s = enh
        im = ImageEnhance.Color(ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(b)).enhance(c)).enhance(s)
    return im


def fit(im, w, h, focus=(0.5, 0.5), zoom=1.0, box=None):
    """Crops im to the aspect of w x h around focus (fractions), zoomed in by zoom, and scales it to w x h."""
    if box:
        im = im.crop(box)
    sw, sh = im.size
    cw = sw / zoom
    ch = cw * h / w
    if ch > sh / zoom:
        ch = sh / zoom
        cw = ch * w / h
    cx = min(max(focus[0] * sw, cw / 2), sw - cw / 2)
    cy = min(max(focus[1] * sh, ch / 2), sh - ch / 2)
    return im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((w, h), Image.LANCZOS)


def tide_icon(size):
    """The Heart of the Tide as a small sprite: the crystal on its frame (raft:block/heart_of_the_tide model)."""
    crystal, frame_ = tex('raft:block/heart_of_the_tide', 16), tex('raft:block/heart_of_the_tide_frame', 16)
    fc = frame_.convert('RGB').resize((1, 1), Image.BOX).getpixel((0, 0))
    out = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    dark = tuple(int(v * 0.6) for v in fc)
    d.line([(4, 13), (2, 6)], fill=fc)
    d.line([(11, 13), (13, 6)], fill=fc)
    gem = [(8, 0), (12, 4), (12, 10), (8, 13), (4, 10), (4, 4)]
    m = Image.new('L', (16, 16), 0)
    ImageDraw.Draw(m).polygon(gem, fill=255)
    out.paste(crystal, (0, 0), m)
    sh = Image.new('L', (16, 16), 0)
    ImageDraw.Draw(sh).polygon([(8, 0), (12, 4), (12, 10), (8, 13)], fill=80)
    out.paste((0, 30, 50, 255), (0, 0), sh)
    d.line([(6, 3), (6, 8)], fill=(230, 255, 255, 200))
    d.rectangle([3, 13, 12, 15], fill=fc)
    d.line([(3, 15), (12, 15)], fill=dark)
    return out.resize((size, size), Image.NEAREST)


def cluster(names, size):
    """Three item pictures overlapping, for a tile that stands for many mods."""
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    s = int(size * 0.62)
    for (n, (fx, fy)) in zip(names, [(0.0, 0.32), (0.38, 0.38), (0.19, 0.0)]):
        ic = icon(n, s)
        out.alpha_composite(ic, (int(fx * size), int(fy * size)))
    return out


# ----------------------------------------------------------------------------------------------- header
def arch_mask(w, h, inset=0):
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    r = (w - 2 * inset) / 2
    d.ellipse([inset, inset, w - 1 - inset, inset + 2 * r], fill=255)
    d.rectangle([inset, inset + r, w - 1 - inset, h - 1], fill=255)
    return m


def window(pic, w, h, border=6):
    """A picture in an arched window with a cream frame."""
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(CREAM + (255,), (0, 0), arch_mask(w, h))
    out.paste(pic.convert('RGBA'), (0, 0), arch_mask(w, h, border))
    return out


def glow(im, mask, xy, radius=18, alpha=110, color=CREAM):
    g = Image.new('RGBA', (mask.width + 6 * radius, mask.height + 6 * radius), (0, 0, 0, 0))
    g.paste(color + (alpha,), (3 * radius, 3 * radius), mask)
    g = g.filter(ImageFilter.GaussianBlur(radius))
    im.alpha_composite(g, (xy[0] - 3 * radius, xy[1] - 3 * radius))


HERO = [('dc/castle@1.0', (0.42, 0.5), 1.2), ('dc/magic@1.25', (0.42, 0.56), 1.3),
        ('bc3v2/r_build_sail@3.2', (0.47, 0.5), 1.0), ('dc/tech@0.75', (0.5, 0.56), 1.25), ('dc/end@1.0', (0.47, 0.6), 1.3)]


def header(name='header_v15.png', size=(1600, 660)):
    """Five dream windows (shader shots of the pack) rising out of the clouds, the slogan above them."""
    w, h = size
    im = night(w, h, seed=11, n_stars=150)
    moon(im, (1508, 86), 38)
    d = ImageDraw.Draw(im)
    slogan = 'WHAT MINECRAFT IN YOUR DREAMS COULD LOOK LIKE'
    outlined(d, (w // 2 - 20, 70), slogan, fitfont(d, slogan, font, 64, 1220), stroke=7, anchor='mm')
    ww, gap = 262, 34
    heights = [420, 470, 500, 470, 420]
    x = (w - 5 * ww - 4 * gap) // 2
    for (spec, focus, zoom), wh in zip(HERO, heights):
        pic = fit(shot(spec, (1.02, 1.05, 1.1)), ww, wh, focus, zoom)
        y = h - wh
        glow(im, arch_mask(ww, wh), (x, y), radius=16, alpha=120)
        im.alpha_composite(window(pic, ww, wh), (x, y))
        x += ww + gap
    clouds(im, 586, seed=5, r=(26, 46), gap=18)
    d = ImageDraw.Draw(im)
    tag = 'Minecraft 26.3  ·  Fabric  ·  V1.5'
    f = font(38)
    tw = d.textlength(tag, font=f)
    d.rounded_rectangle([w / 2 - tw / 2 - 30, 596, w / 2 + tw / 2 + 30, 648], 26, fill=CREAM, outline=CLOUD4, width=4)
    d.text((w / 2, 622), tag, font=f, fill=DEEP, anchor='mm')
    save(rounded(ImageOps.posterize(im.convert('RGB'), 7).convert('RGBA'), 30), name)


# ----------------------------------------------------------------------------------------------- trailer card
def phone(pic, w, h, r=26, bezel=10):
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, w - 1, h - 1], r, fill=(14, 4, 30, 255), outline=CREAM + (255,), width=4)
    scr = fit(pic, w - 2 * bezel, h - 2 * bezel)
    out.alpha_composite(rounded(scr, r - bezel), (bezel, bezel))
    return out


def play_glyph(size, ring=CREAM, tri=CLOUD2):
    s = 4 * size
    g = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    d.ellipse([0, 0, s - 1, s - 1], fill=ring + (245,))
    d.polygon([(s * 0.38, s * 0.27), (s * 0.38, s * 0.73), (s * 0.76, s * 0.5)], fill=tri)
    return g.resize((size, size), Image.LANCZOS)


def video_card(name='video_v15.jpg', length='0:44'):
    """Fallback picture of the trailer (portrait, 44 s): three phones with frames of it, a big play button."""
    w, h = 1200, 660
    im = night(w, h, seed=21, cloud_y=560, n_stars=90)
    d = ImageDraw.Draw(im)
    outlined(d, (w // 2, 62), 'DREAMCRAFT IN 44 SECONDS', font(64), stroke=7, anchor='mm')
    side = [('trailer@21.5', -7, 290), ('trailer@31.5', 7, 910)]
    for spec, ang, cx in side:
        ph = phone(shot(spec), 236, 420).rotate(ang, resample=Image.BICUBIC, expand=True)
        shadowed(im, ph, (cx - ph.width // 2, 150), blur=12, offset=(0, 8), alpha=150)
    ph = phone(shot('trailer@0.6'), 272, 484)
    glow(im, ph.split()[3], ((w - 272) // 2, 116), radius=18, alpha=90)
    shadowed(im, ph, ((w - 272) // 2, 116), blur=14, offset=(0, 10), alpha=170)
    p = play_glyph(124)                  # in the lower third: the player of the castle shot stays visible
    shadowed(im, p, ((w - 124) // 2, 116 + int(484 * 0.74) - 62), blur=12, offset=(0, 8), alpha=150)
    d = ImageDraw.Draw(im)
    f = small(26)
    tw = d.textlength(length, font=f)
    x1, y1 = (w + 272) // 2 - 22, 116 + 484 - 24
    d.rounded_rectangle([x1 - tw - 24, y1 - 40, x1, y1], 8, fill=(0, 0, 0, 210))
    d.text((x1 - 12, y1 - 20), length, font=f, fill=WHITE, anchor='rm')
    outlined(d, (w // 2, 628), 'WATCH THE TRAILER', font(46), stroke=6, anchor='mm')
    save(im.convert('RGB'), name)


# ----------------------------------------------------------------------------------------------- the story map
MC_COLOURS = {'d': (255, 85, 255), 'a': (85, 255, 85), '6': (255, 170, 0), 'e': (255, 255, 85), '5': (170, 0, 170),
              'c': (255, 85, 85), 'b': (85, 255, 255), '2': (0, 170, 0), '3': (0, 170, 170)}


def chapter_colour(key):
    raw_title = snbt(open(os.path.join(QUESTS, 'chapters', key + '.snbt'), encoding='utf-8').read())['title']
    m = re.match(r'&([0-9a-f])', raw_title)
    return MC_COLOURS.get(m.group(1), CREAM) if m else CREAM


def dashed(d, pts, color, width=6, dash=16, gap=12):
    """A dashed polyline through pts."""
    seg = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg.append(((x0, y0), (x1, y1), math.hypot(x1 - x0, y1 - y0)))
    on, left = True, dash
    for (x0, y0), (x1, y1), L in seg:
        t = 0.0
        while t < L:
            step = min(left, L - t)
            if on:
                a, b = t / L, (t + step) / L
                d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)],
                       fill=color, width=width)
            t += step
            left -= step
            if left <= 0:
                on = not on
                left = dash if on else gap


def bezier(p0, p1, p2, p3, n=40):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1])
            for t in (i / n for i in range(n + 1))]


def node(im, center, pic, ring, r=50):
    cx, cy = center
    g = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=ring + (90,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=ring)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SKY0, outline=CREAM, width=3)
    im.alpha_composite(pic, (cx - pic.width // 2, cy - pic.height // 2))


def count_pill(d, center, n, fill=CREAM, ink=DEEP):
    x, y = center
    f = small(19)
    t = '%d quests' % n
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([x - tw / 2 - 12, y - 15, x + tw / 2 + 12, y + 15], 15, fill=fill)
    d.text((x, y), t, font=f, fill=ink, anchor='mm')


def story(name='story_v15.png'):
    """The nine chapters of the dream as a path from the prologue to the Dream Star, the six side paths below."""
    ch = chapters()
    main = [c for c in ch if c['group'] == 0]
    side = [c for c in ch if c['group'] == 1]
    w, h = W, 960
    im = night(w, h, seed=31, n_stars=0)
    for k, box in enumerate(((0, 0, w, 50), (0, 350, w, 400), (0, 680, w, 714))):
        stars(im, box, 26, seed=31 + k, rmax=8)
    xs = [130, 365, 600, 835, 1070]
    rows = [100, 430]
    pos = [(xs[i], rows[0]) for i in range(5)] + [(xs[4 - i], rows[1]) for i in range(4)]
    star_pos = (xs[0], rows[1])
    path = []
    for i in range(4):
        path += [pos[i], pos[i + 1]]
    path += bezier(pos[4], (1222, rows[0] + 30), (1222, rows[1] - 30), pos[5])
    for i in range(5, 8):
        path += [pos[i], pos[i + 1]]
    path += [pos[8], star_pos]
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    dashed(ImageDraw.Draw(lay), path, CREAM + (150,), width=10, dash=1, gap=0)
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(7)))
    dashed(ImageDraw.Draw(im), path, CREAM, width=6)
    d = ImageDraw.Draw(im)
    for c, (x, y) in zip(main, pos):
        node(im, (x, y), item_icon(c['icon'], 60), chapter_colour(c['key']))
        d = ImageDraw.Draw(im)
        label, _, title = c['title'].partition(': ') if ':' in c['title'] else ('', '', c['title'])
        if not label:
            num, _, title = c['title'].partition('. ')
            label = 'CHAPTER ' + num
        count_pill(d, (x, y + 50), len(c['quests']))
        d.text((x, y + 84), label.upper(), font=small(18), fill=CLOUD4, anchor='ma')
        tf = fitfont(d, title, font, 27, 222, 18)
        outlined(d, (x, y + 106), title, tf, stroke=4, anchor='ma', shadow=False)
        para(d, (x, y + 142), c['subtitle'], small(18), 222, fill=(222, 214, 255), gap=2, anchor='ma')
    sx, sy = star_pos
    node(im, star_pos, icon('star', 76), MAGENTA, r=58)
    d = ImageDraw.Draw(im)
    d.text((sx, sy + 76), 'THE TROPHY', font=small(18), fill=CLOUD4, anchor='ma')
    outlined(d, (sx, sy + 98), 'The Dream Star', font(27), fill=GOLD, stroke=4, anchor='ma', shadow=False)
    para(d, (sx, sy + 134), 'Craft it from treasures of the whole pack.', small(18), 222, fill=(222, 214, 255), gap=2,
         anchor='ma')
    # side paths
    top = 712
    band = card(w - 40, h - top - 24, r=26, fill=(66, 40, 160), outline=CLOUD4, width=4)
    shadowed(im, band, (20, top), blur=10, offset=(0, 6), alpha=140)
    d = ImageDraw.Draw(im)
    f = font(32)
    pill = 'SIDE PATHS'
    pw = d.textlength(pill, font=f) + 44
    d.rounded_rectangle([w / 2 - pw / 2, top - 24, w / 2 + pw / 2, top + 24], 24, fill=CREAM, outline=CLOUD4, width=4)
    d.text((w / 2, top + 1), pill, font=f, fill=DEEP, anchor='mm')
    cw = (w - 80) / len(side)
    for k, c in enumerate(side):
        cx = int(40 + cw * k + cw / 2)
        cy = top + 78
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=SKY0, outline=chapter_colour(c['key']), width=5)
        pic = item_icon(c['icon'], 50)
        im.alpha_composite(pic, (cx - pic.width // 2, cy - pic.height // 2))
        d = ImageDraw.Draw(im)
        y = cy + 52
        for ln in wrap(d, c['title'], font(23), cw - 16):
            outlined(d, (cx, y), ln, font(23), stroke=3, anchor='ma', shadow=False)
            y += 27
        count_pill(d, (cx, top + 206), len(c['quests']), fill=CLOUD3, ink=WHITE)
    save(rounded(im, 26), name)


# ----------------------------------------------------------------------------------------------- flow: the quest book
def card_title(c, xy, n, title, size=30):
    x, y = xy
    badge(c, (x + 20, y + 20), n, r=20)
    d = ImageDraw.Draw(c)
    f = fitfont(d, title, font, size, c.width - x - 70, 18)
    d.text((x + 50, y + 22), title, font=f, fill=DEEP, anchor='lm')
    return y + 54


def icon_card(w, h, n, title):
    c = card(w, h)
    card_title(c, (18, 16), n, title)
    return c


def chip(im, x, y, text, f=None, fill=(232, 222, 255), ink=INK):
    d = ImageDraw.Draw(im)
    f = f or small(18)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + tw + 20, y + 32], 9, fill=fill, outline=CLOUD3, width=2)
    d.text((x + 10, y + 16), text, font=f, fill=ink, anchor='lm')
    return tw + 20


def flow_quests(name='flow_quests_v15.png'):
    """Open the book, do the tasks, claim the rewards, play as a team (Quest Icons: key J, /quests team ...)."""
    M, gapx, ch = 24, 40, 380
    n = 4
    cw = (W - 2 * M - (n - 1) * gapx) // n
    h = ch + 2 * M + 16
    im = night(W, h, seed=41, n_stars=40)
    cards = []
    c1 = icon_card(cw, ch, 1, 'OPEN THE BOOK')
    keycap(c1, 34, 92, 'J', 74, 74, font(46))
    bk = icon('book', 84)
    c1.alpha_composite(bk, (cw - 34 - bk.width, 88))
    d1 = ImageDraw.Draw(c1)
    d1.text((cw // 2 + 6, 128), 'or', font=small(20), fill=INK, anchor='mm')
    para(d1, (18, 196), 'Press J, use the Quest Book or the button in your inventory. You get the book when you join.',
         small(19), cw - 32)
    cards.append(c1)
    c2 = icon_card(cw, ch, 2, 'DO THE TASKS')
    d2 = ImageDraw.Draw(c2)
    tasks = [('icon_chest', 'Collect'), ('icon_map', 'Explore'), ('icon_sword', 'Defeat'), ('spyglass', 'Look')]
    tw_ = (cw - 20) / 2
    for k, (ic, lab) in enumerate(tasks):
        cx, cy = 10 + tw_ * (k % 2) + tw_ / 2, 92 + (k // 2) * 84
        pic = icon(ic, 46)
        c2.alpha_composite(pic, (int(cx - pic.width / 2), int(cy - 6)))
        d2.text((cx, cy + 50), lab, font=small(18), fill=INK, anchor='mm')
    para(d2, (18, 268), 'Every quest explains how its mod really works.', small(19), cw - 32)
    cards.append(c2)
    c3 = icon_card(cw, ch, 3, 'CLAIM REWARDS')
    d3 = ImageDraw.Draw(c3)
    crates = ['common', 'rare', 'epic', 'legendary']
    for k, cr in enumerate(crates):
        pic = icon(cr, 52)
        c3.alpha_composite(pic, (int(14 + k * (cw - 28) / 4 + ((cw - 28) / 4 - 52) / 2), 84))
    xp = icon('xp', 44)
    c3.alpha_composite(xp, (cw // 2 - 70, 152))
    d3.text((cw // 2 - 18, 174), 'XP and items', font=small(19), fill=INK, anchor='lm')
    keycap(c3, cw // 2 - 50, 212, 'Claim', 100, 40, small(21))
    para(d3, (18, 274), 'Loot crates: common, rare, epic and legendary.', small(19), cw - 32)
    cards.append(c3)
    c4 = icon_card(cw, ch, 4, 'PLAY TOGETHER')
    d4 = ImageDraw.Draw(c4)
    y = 84
    for t in ('/quests team create <name>', '/quests team invite <player>', '/quests team join <name>'):
        chip(c4, 14, y, t, small(16))
        y += 44
    para(d4, (18, 226), 'Make a team and share your quest progress with your friends.', small(19), cw - 32)
    cards.append(c4)
    x, xs = M, []
    for c in cards:
        shadowed(im, c, (x, M), blur=9, offset=(0, 6), alpha=130)
        xs.append(x)
        x += cw + gapx
    d = ImageDraw.Draw(im)
    for k in range(n - 1):
        x0 = xs[k] + cw
        arrow(d, [(x0 + 4, M + ch // 2), (x0 + gapx - 4, M + ch // 2)], width=12, head=22)
    save(rounded(im, 26), name)


# ----------------------------------------------------------------------------------------------- flow: the Dream Star
TREASURES = [('ametrine', 'Ametrine Ingot  ×2', 'Mythic Upgrades: ametrine comes from the End'),
             ('crown', 'Quest Crown', 'the reward of "Master of Dreams"'),
             ('staff', 'Netherite Staff', 'of a wizard or a priest: Paths of Power'),
             ('nether_star', 'Nether Star', 'defeat the Wither'),
             ('orb', 'Lapotronic Energy Orb', 'the top of Tech Reborn'),
             ('heart', 'Tamacraft Heart', 'it tames the rare pets'),
             ('egg', 'Dragon Egg or Dragon Head', 'the End: the dragon or an End ship'),
             ('tide', 'Heart of the Tide', 'the Leviathan guards it, deep in the sea')]


def flow_star(name='flow_star_v15.png'):
    """Gather the eight treasures, craft the star (questsicons recipe dream_star.json), put it on its pedestal."""
    recipe = json.loads(_zip(jar('QuestIcons-*.jar')).read('data/questsicons/recipe/dream_star.json'))
    keyicon = {'mythicupgrades:ametrine_ingot': 'ametrine', 'questsicons:quest_crown': 'crown',
               'wizards:staff_netherite_arcane': 'staff', 'minecraft:nether_star': 'nether_star',
               'techreborn:lapotronic_orb': 'orb', 'tamacraft:tamacraft_heart': 'heart', '#questsicons:dream_star_hearts': 'heart',
               'minecraft:dragon_egg': 'egg',
               'raft:heart_of_the_tide': 'tide'}
    M, gapx, ch = 24, 44, 500
    widths = [492, 318, 270]
    h = ch + 2 * M + 16
    im = night(W, h, seed=51, n_stars=40)
    c1 = icon_card(widths[0], ch, 1, 'GATHER 8 TREASURES')
    d1 = ImageDraw.Draw(c1)
    y = 82
    for ic, nm, src in TREASURES:
        pic = tide_icon(40) if ic == 'tide' else icon(ic, 40)
        c1.alpha_composite(pic, (22, y + (44 - pic.height) // 2))
        d1.text((74, y), nm, font=small(20), fill=DEEP, anchor='la')
        d1.text((74, y + 25), src, font=fitfont(d1, src, small, 17, widths[0] - 90, 14), fill=(92, 70, 150), anchor='la')
        y += 51
    c2 = icon_card(widths[1], ch, 2, 'CRAFT THE STAR')
    s, g = 76, 6
    gx, gy = (widths[1] - (3 * s + 2 * g)) // 2, 84
    for r, row in enumerate(recipe['pattern']):
        for c, k in enumerate(row):
            v = recipe['key'][k]
            v = v[0] if isinstance(v, list) else v
            n_ = keyicon[v]
            slot(c2, gx + c * (s + g), gy + r * (s + g), s, tide_icon(64) if n_ == 'tide' else icon(n_, 64))
    d2 = ImageDraw.Draw(c2)
    ay = gy + 3 * s + 2 * g + 8
    arrow(d2, [(widths[1] // 2, ay), (widths[1] // 2, ay + 40)], color=CLOUD2, width=10, head=18, outline=WHITE)
    slot(c2, widths[1] // 2 - 44, ay + 48, 88, icon('star', 72))
    c3 = icon_card(widths[2], ch, 3, 'SHOW IT OFF')
    d3 = ImageDraw.Draw(c3)
    cx = widths[2] // 2
    g_ = Image.new('RGBA', c3.size, (0, 0, 0, 0))
    ImageDraw.Draw(g_).ellipse([cx - 70, 80, cx + 70, 220], fill=(255, 120, 255, 110))
    c3.alpha_composite(g_.filter(ImageFilter.GaussianBlur(18)))
    st = icon('star', 96)
    c3.alpha_composite(st, (cx - 48, 100))
    d3 = ImageDraw.Draw(c3)
    for (sx, sy, r) in ((cx - 70, 110, 9), (cx + 66, 140, 7), (cx + 40, 92, 5), (cx - 52, 196, 5)):
        sparkle(d3, sx, sy, r, (214, 120, 255))
    ped = icon('pedestal', 104)
    c3.alpha_composite(ped, (cx - 52, 214))
    para(d3, (18, 340), 'Craft its pedestal and put the star on it: it floats, turns slowly and lights up the room.', small(19), widths[2] - 32)
    xs, x = [], M
    for c in (c1, c2, c3):
        shadowed(im, c, (x, M), blur=9, offset=(0, 6), alpha=130)
        xs.append(x)
        x += c.width + gapx
    d = ImageDraw.Draw(im)
    for k in range(2):
        x0 = xs[k] + widths[k]
        arrow(d, [(x0 + 4, M + ch // 2), (xs[k + 1] - 4, M + ch // 2)], width=12, head=22)
    save(rounded(im, 26), name)


# ----------------------------------------------------------------------------------------------- new in V1.5
def bullet_lines(c, x, y, items, width, f=None, gap=10):
    """Lines with a small icon in front; returns the y below."""
    d = ImageDraw.Draw(c)
    f = f or small(19)
    for pic, text in items:
        if pic is not None:
            c.alpha_composite(pic, (x, y + 1))
        y2 = para(d, (x + 44, y + 4), text, f, width - 44, fill=INK, gap=3)
        y = max(y + 40, y2) + gap
    return y


def news(name='new_v15.png'):
    """Beach Craft 3.3, Tamacraft and Quest Icons 1.3, and the quests of V1.5 (changelog-26.3-V1.5.md)."""
    c = counts()
    M, gapx, ch = 24, 24, 462
    widths = [452, 344, 332]
    h = ch + 2 * M + 16
    im = night(W, h, seed=61, n_stars=40)
    # Beach Craft 3.3: a photo of the cozy beach house from the mod's in-game test (src_v15/)
    c1 = card(widths[0], ch)
    src = Image.open(os.path.join(HERE, 'src_v15', 'cozy_scene_day.jpg')).convert('RGB')
    ph = fit(src, widths[0] - 16, 200, (0.5, 0.5), 1.1)
    c1.alpha_composite(rounded(ph, 16), (8, 8))
    d1 = ImageDraw.Draw(c1)
    d1.text((20, 236), 'BEACH CRAFT 3.3', font=font(30), fill=DEEP, anchor='lm')
    bullet_lines(c1, 20, 266, [(tex('raft:item/sail', 34), 'Sail, mast and anchor for the raft you build.'),
                                (tex('raft:item/cutlass', 34), 'Guarded places, new enemies and a harder Leviathan.'),
                                (tex('raft:item/island_curry', 34), 'Cozy furniture that heals you, a kitchen and new gear.')],
                 widths[0] - 36)
    # Tamacraft and Quest Icons 1.3
    c2 = card(widths[1], ch)
    d2 = ImageDraw.Draw(c2)
    d2.text((20, 34), 'NEW NAME, NEW TOOLS', font=font(28), fill=DEEP, anchor='lm')
    d2.text((20, 64), 'Tamacraft and Quest Icons 1.3', font=small(18), fill=(92, 70, 150), anchor='lm')
    row = [(icon('heart', 64), 'Tamacraft'), (tex('questsicons:item/icons/ui/ui_pencil', 64), 'Editor'),
           (tex('questsicons:item/icons/letters/letter_a', 64), 'Icons'),
           (tex('questsicons:item/icons/ranks/trophy_gold', 64), 'Pictures')]
    tw_ = (widths[1] - 20) / 4
    for k, (pic, lab) in enumerate(row):
        cx = 10 + tw_ * k + tw_ / 2
        c2.alpha_composite(pic, (int(cx - pic.width / 2), 96))
        d2.text((cx, 176), lab, font=small(17), fill=INK, anchor='mm')
    bullet_lines(c2, 20, 214, [(icon('heart', 34), 'Tamagotchi is now Tamacraft: same pets, your world carries over.'),
                                (tex('questsicons:item/icons/ui/ui_pencil', 34), 'Edit the quest book in the game, no SNBT needed.'),
                                (tex('questsicons:item/icons/letters/letter_a', 34), '470 quest icons and 56 pictures for the map.')],
                 widths[1] - 30)
    # quests
    c3 = card(widths[2], ch)
    d3 = ImageDraw.Draw(c3)
    d3.text((20, 34), '%d QUESTS' % c['quests'], font=font(30), fill=DEEP, anchor='lm')
    bk = icon('book', 72)
    c3.alpha_composite(bk, (widths[2] - 92, 20))
    bullet_lines(c3, 20, 110, [(tex('raft:item/boomerang', 34), 'New side path Island Life: %d quests for the new Beach Craft.' % c['island']),
                                (icon('icon_raft', 34), 'The Endless Sea explains the new sailing and the Leviathan.'),
                                (icon('heart', 34), 'Tamacraft in every quest of the pets path.')],
                 widths[2] - 30)
    x = M
    for cc in (c1, c2, c3):
        shadowed(im, cc, (x, M), blur=9, offset=(0, 6), alpha=130)
        x += cc.width + gapx
    save(rounded(im, 26), name)


# ----------------------------------------------------------------------------------------------- collages
def caption(tile, name, sub=None, right=False):
    """Name in the display font, an optional second line in the small print, on a dark band at the bottom
    (right=True: at the bottom right, the band fading out to the left)."""
    d = ImageDraw.Draw(tile)
    f = fitfont(d, name, font, 30, tile.width - 28, 18)
    band = 92 if sub else 64
    shade = Image.new('RGBA', tile.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(band):
        sd.line([(0, tile.height - band + i), (tile.width, tile.height - band + i)],
                fill=(16, 0, 40, int(200 * (i / band) ** 1.2)))
    if right:
        ramp = Image.linear_gradient('L').rotate(90).resize(tile.size).point(lambda v: min(255, max(0, (255 - v) * 2 - 200)))
        shade.putalpha(Image.composite(shade.split()[3], Image.new('L', tile.size, 0), ramp))
    tile.alpha_composite(shade)
    d = ImageDraw.Draw(tile)
    x, a1, a2 = (tile.width - 14, 'rs', 'rs') if right else (14, 'ls', 'ls')
    y = tile.height - (42 if sub else 16)
    outlined(d, (x, y), name, f, stroke=4, anchor=a1, shadow=False)
    if sub:
        fs = fitfont(d, sub, small, 19, tile.width - 28, 14)
        d.text((x + (0 if right else 1), tile.height - 14), sub, font=fs, fill=(222, 214, 255), anchor=a2, stroke_width=2,
               stroke_fill=(16, 0, 40))


def T(spec, cap=None, sub=None, w=1.0, focus=(0.5, 0.5), zoom=1.0, box=None, enh=(1.02, 1.04, 1.08), right=False):
    return dict(spec=spec, cap=cap, sub=sub, w=w, focus=focus, zoom=zoom, box=box, enh=enh, right=right)


def collage(name, rows, pad=16, gap=12):
    """rows: list of (height, [tile, ...]); a tile is a frame of the footage (or a picture) with a caption."""
    inner = W - 2 * pad
    total_h = pad + sum(hh for hh, _ in rows) + gap * (len(rows) - 1) + pad + 18
    im = night(W, total_h, seed=len(name), n_stars=60)
    clouds(im, total_h - 36, seed=len(name) + 3, layers=((CLOUD1, CLOUD2), (CLOUD2, CLOUD3)), r=(18, 32), gap=12)
    y = pad
    for hh, tiles in rows:
        weights = sum(t['w'] for t in tiles)
        avail = inner - gap * (len(tiles) - 1)
        x = pad
        for i, t in enumerate(tiles):
            tw = int(avail * t['w'] / weights) if i < len(tiles) - 1 else pad + inner - x
            src = t['spec'] if isinstance(t['spec'], Image.Image) else shot(t['spec'], t['enh'])
            tile = fit(src, tw, hh, t['focus'], t['zoom'], t['box']).convert('RGBA')
            if t['cap']:
                caption(tile, t['cap'], t['sub'], t['right'])
            fr = Image.new('RGBA', (tw, hh), (0, 0, 0, 0))
            ImageDraw.Draw(fr).rounded_rectangle([0, 0, tw - 1, hh - 1], 16, fill=CREAM + (255,))
            fr.alpha_composite(rounded(tile.crop((3, 3, tw - 3, hh - 3)), 13), (3, 3))
            shadowed(im, fr, (x, y), blur=8, offset=(0, 5), alpha=120)
            x += tw + gap
        y += hh + gap
    save(im.convert('RGB'), name)


def collages(which=None):
    """The section collages, cut from the shader footage of the trailer (dc), Beach Craft 3.1 (bc3v2) and
    Tamagotchi (tama2); the places and mobs of the dc shots are set up in tools/dctest Film.java."""
    sets = {
        'worlds_v15.jpg': lambda: [
            (470, [T('dc/castle@1.0', 'Castles', 'ATi Structures', focus=(0.45, 0.47), zoom=1.15),
                   T('dc/village@1.0', 'Villages', 'here in a cherry grove', focus=(0.42, 0.42), zoom=1.15),
                   T('dc/nether@1.0', 'Nether Jungle', 'BetterNether', focus=(0.45, 0.55), zoom=1.15),
                   T('dc/end@1.0', 'Glowing Grasslands', 'BetterEnd', focus=(0.47, 0.55), zoom=1.15)])],
        'life_v15.jpg': lambda: [
            (470, [T('dc/magic@1.25', 'Fire Wizard', 'Wizards (RPG Series)', focus=(0.42, 0.55), zoom=1.15),
                   T('dc/mutant@1.0', 'Mutant Zombie', 'Mutant Monsters', focus=(0.5, 0.5), zoom=1.15),
                   T('dc/kitchen@0.75', "Farmer's Delight", 'and Cooking for Blockheads', focus=(0.5, 0.5), zoom=1.15),
                   T('dc/tech@0.75', 'Tech Reborn', 'machines, power, a quarry', focus=(0.5, 0.52), zoom=1.15)])],
        'pets_v15.jpg': lambda: [
            (470, [T('tama2/lineup_dolly@4.25', 'Ten Rare Pets', 'in the structures of the world', focus=(0.5, 0.56), zoom=1.15),
                   T('tama2/tame_heart@2.5', 'Tame Them', 'with a Tamacraft Heart', focus=(0.5, 0.45), zoom=1.15),
                   T('tama2/hook_petting@3.15', 'Look After Them', 'with food, toys and a brush', focus=(0.5, 0.45), zoom=1.15),
                   T('tama2/igloo_penguin@2.25', 'Frost Penguin', 'one of the ten', focus=(0.58, 0.6), zoom=1.7)])],
        'sea_v15.jpg': lambda: [
            (330, [T('bc3v2/r_build_sail@3.2', 'Build Your Own Raft', 'with sail, mast and anchor', w=1.35, focus=(0.47, 0.45), zoom=1.15),
                   T('bc3v2/n_nalu_greet@0.5', 'People of the Sea', 'hints, gifts and trades', w=1.0, box=(0, 0, 1440, 1080), focus=(0.4, 0.5))]),
            (250, [T('bc3v2/r_sail_orbit@2.0', 'Bruce the Shark', 'he bites rafts', focus=(0.5, 0.55), zoom=1.6),
                   T('dc/raft@1.25', 'Survive at Sea', 'crops, grill and water purifier', focus=(0.5, 0.45), zoom=1.0),
                   T('bc3v2/s_lev_strike4@4.0', 'The Leviathan', 'the boss of the deep, now harder', focus=(0.5, 0.42), zoom=1.25)])],
    }
    for n, rows in sets.items():
        if which is None or n in which:
            collage(n, rows())


# ----------------------------------------------------------------------------------------------- the main menu
def menu(name='menu_v15.jpg'):
    """The main menu and the loading screen (src_v14/: screenshots of the production test of 2.11.2026, the menu at
    1920x1080 and the loading screen of a 1280x720 window without its progress bar) and the eight menu backgrounds."""
    mainmenu = Image.open(os.path.join(HERE, 'src_v14', 'main_menu_1920x1080.jpg')).convert('RGB')
    loading = Image.open(os.path.join(HERE, 'src_v14', 'loading_screen_1280.jpg')).convert('RGB')
    bgs = [Image.open(os.path.join(MENU, 'bg%d.jpg' % i)).convert('RGB') for i in range(1, 9)]
    c = counts()
    rows = [(330, [T(mainmenu, 'The Main Menu', '%d backgrounds, one picked at random' % c['menu_backgrounds'], w=1.78, enh=None, right=True),
                   T(loading, 'The Loading Screen', 'in the Dreamcraft style', w=1.88, enh=None)]),
            (160, [T(b, enh=None) for b in bgs[:4]]),
            (160, [T(b, enh=None) for b in bgs[4:]])]
    collage(name, rows)


# ----------------------------------------------------------------------------------------------- the highlights
def highlights():
    """The highlights of the mod list by kind (every name is a mod of pack/mods.json or one of the own mods)."""
    mods = json.load(open(os.path.join(REPO, 'pack', 'mods.json')))
    macaws = len([m for m in mods if m['title'].startswith("Macaw's")])
    return [
        ('icon_map', 'WORLDS AND STRUCTURES', "Terralith and Tectonic, Towns and Towers, Repurposed Structures, Dungeons and "
                                         "Taverns, ATi Structures, Structory, Moog's structures, Explorations"),
        ('ender_eye', 'NETHER AND END', "BetterNether and BetterEnd with new biomes, plants and mobs, and Moog's Nether "
                                        "and End structures"),
        ('fire_staff', 'MAGIC AND COMBAT', 'Wizards, Paladins & Priests, Archers, Rogues & Warriors, Jewelry, Relics, '
                                           'Arsenal, Armory, Better Combat, Combat Roll'),
        ('ametrine', 'GEAR BEYOND NETHERITE', 'Mythic Upgrades and Advanced Netherite'),
        ('grinder', 'TECH AND STORAGE', "Tech Reborn, Quarry Reborn, Additional Enchanted Miner, Storage Drawers, Tom's "
                                        "Simple Storage, Upgraded Iron Chests, Traveler's Backpack"),
        ('pot', 'FOOD AND FARMING', "Farmer's Delight with More, Rustic, Ube's and Storage Delight, Cooking for "
                                    'Blockheads, Farming for Blockheads, RightClickHarvest'),
        ('roofs', 'BUILDING', "All %d Macaw's mods, Rechiseled, Dawn of Time, Beautify, Effortless Building, "
                              'Construction Wand, Armor Statues' % macaws),
        ('chemical_x', 'CREATURES', 'Mutant Monsters, Friends & Foes, Naturalist, Ecologics, Variants & Ventures, '
                                    'Woodwalkers, Tamacraft'),
        ('icon_compass', 'HELPERS', "JEI, Jade, Xaero's Minimap and World Map, Waystones, Lootr, Carry On, FallingTree, "
                                    'Simple Voice Chat, AppleSkin'),
        ('amethyst', 'LOOKS AND SPEED', 'Sodium, Lithium, FerriteCore, ImmediatelyFast, Entity Culling, and Iris with BSL '
                                        'and Complementary Reimagined (off by default)'),
    ]


def mods_image(name='mods_v15.png'):
    items = highlights()
    M, gx, gy, cols = 20, 16, 16, 2
    cw, chh = (W - 2 * M - gx) // cols, 176
    rows = (len(items) + cols - 1) // cols
    h = 2 * M + rows * chh + (rows - 1) * gy + 10
    im = night(W, h, seed=71, n_stars=30)
    for k, (ic, title, text) in enumerate(items):
        x, y = M + (k % cols) * (cw + gx), M + (k // cols) * (chh + gy)
        c = card(cw, chh)
        d = ImageDraw.Draw(c)
        d.ellipse([18, chh // 2 - 50, 118, chh // 2 + 50], fill=(232, 222, 255))
        pic = icon(ic, 64)
        c.alpha_composite(pic, (68 - pic.width // 2, chh // 2 - pic.height // 2))
        d = ImageDraw.Draw(c)
        d.text((138, 20), title, font=fitfont(d, title, font, 28, cw - 160, 18), fill=DEEP, anchor='la')
        para(d, (138, 58), text, small(19), cw - 156, fill=INK, gap=4)
        shadowed(im, c, (x, y), blur=8, offset=(0, 5), alpha=130)
    save(rounded(im, 26), name)


# ----------------------------------------------------------------------------------------------- recommendations
def ram_glyph(size):
    s = 4 * size
    g = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    d.rounded_rectangle([s * 0.04, s * 0.3, s * 0.96, s * 0.7], s * 0.04, fill=(46, 140, 80))
    for k in range(4):
        x = s * (0.1 + 0.215 * k)
        d.rectangle([x, s * 0.36, x + s * 0.16, s * 0.56], fill=(28, 28, 36))
    for k in range(14):
        x = s * (0.08 + 0.061 * k)
        d.rectangle([x, s * 0.62, x + s * 0.03, s * 0.7], fill=(232, 196, 90))
    return g.resize((size, size), Image.LANCZOS)


def setup(name='setup_v15.png'):
    """RAM, Java, shaders and servers (the recommendations of the page; start.sh in tools/mkpack.py)."""
    M, gapx, ch = 20, 16, 330
    n = 4
    cw = (W - 2 * M - (n - 1) * gapx) // n
    h = ch + 2 * M + 10
    im = night(W, h, seed=81, n_stars=30)
    cards = []
    c1 = card(cw, ch)
    c1.alpha_composite(ram_glyph(84), (cw // 2 - 42, 8))
    d = ImageDraw.Draw(c1)
    d.text((cw // 2, 104), 'MEMORY', font=font(26), fill=DEEP, anchor='mm')
    outlined(d, (cw // 2, 160), '8–10 GB', font(56), fill=WHITE, stroke=6, stroke_fill=CLOUD2, anchor='mm', shadow=False)
    d.text((cw // 2, 206), 'recommended', font=small(19), fill=INK, anchor='mm')
    para(d, (cw // 2, 236), '6 GB at least, more for shaders or a far view.', small(19), cw - 36, anchor='ma')
    cards.append(c1)
    c2 = card(cw, ch)
    c2.alpha_composite(tex('farmersdelight:item/hot_cocoa', 72), (cw // 2 - 36, 16))
    d = ImageDraw.Draw(c2)
    d.text((cw // 2, 104), 'JAVA', font=font(26), fill=DEEP, anchor='mm')
    outlined(d, (cw // 2, 160), '25', font(64), fill=WHITE, stroke=6, stroke_fill=CLOUD2, anchor='mm', shadow=False)
    para(d, (cw // 2, 214), 'The CurseForge app brings the right Java for you.', small(19), cw - 36, anchor='ma')
    cards.append(c2)
    c3 = card(cw, ch)
    c3.alpha_composite(tex('minecraft:item/amethyst_shard', 72), (cw // 2 - 36, 16))
    d = ImageDraw.Draw(c3)
    d.text((cw // 2, 104), 'SHADERS', font=font(26), fill=DEEP, anchor='mm')
    para(d, (cw // 2, 128), 'BSL and Complementary Reimagined, off by default.', small(19), cw - 36, anchor='ma')
    y = 196
    for t in ('Options', 'Video Settings', 'Shader Packs'):
        f = small(18)
        tw = d.textlength(t, font=f)
        d.rounded_rectangle([cw / 2 - tw / 2 - 12, y, cw / 2 + tw / 2 + 12, y + 32], 9, fill=(232, 222, 255),
                            outline=CLOUD3, width=2)
        d.text((cw / 2, y + 16), t, font=f, fill=INK, anchor='mm')
        y += 42
    cards.append(c3)
    c4 = card(cw, ch)
    d = ImageDraw.Draw(c4)
    btn = Image.open(os.path.join(MENU, 'btn_rent.png')).convert('RGBA')
    btn = btn.resize((cw - 70, (cw - 70) * btn.height // btn.width), Image.LANCZOS)
    d.rounded_rectangle([20, 22, cw - 20, 34 + btn.height], 12, fill=SKY0)
    c4.alpha_composite(btn, (35, 28))
    d = ImageDraw.Draw(c4)
    d.text((cw // 2, 104), 'PLAY TOGETHER', font=font(26), fill=DEEP, anchor='mm')
    para(d, (cw // 2, 128), 'Rent a server at BisectHosting with code KASAX007 for 25% off, use Rent a Server in the '
                            'menu, or run the server pack yourself.', small(19), cw - 30, anchor='ma')
    cards.append(c4)
    x = M
    for c in cards:
        shadowed(im, c, (x, M), blur=8, offset=(0, 5), alpha=130)
        x += cw + gapx
    save(rounded(im, 26), name)


# ----------------------------------------------------------------------------------------------- strips
STRIPS = [('story', 'THE STORY OF THE DREAM', 'icon_moon'), ('star', 'THE DREAM STAR', 'star'),
          ('new', 'NEW IN V1.5', 'helm'), ('worlds', 'NEW WORLDS TO EXPLORE', 'icon_map'),
          ('life', 'MAGIC, MONSTERS AND MACHINES', 'fire_staff'), ('sea', 'THE ENDLESS SEA', 'icon_raft'),
          ('pets', 'TEN RARE PETS', 'heart'), ('mods', 'THE HIGHLIGHTS', 'icon_chest')]


def strip(name, title, ic):
    h = 104
    im = gradient(W, h, SKY0, CLOUD1, horizontal=True)
    stars(im, (420, 6, W - 10, 60), 26, seed=len(title), rmax=8)
    clouds(im, 86, seed=len(name) * 7, layers=((CLOUD1, CLOUD2), (CLOUD2, CLOUD3)), r=(16, 30), gap=12)
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([22, 6, 114, 98], fill=CREAM + (70,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(im)
    d.ellipse([28, 12, 108, 92], fill=SKY0 + (255,), outline=CREAM + (255,), width=3)
    pic = icon(ic, 60) if isinstance(ic, str) else ic
    im.alpha_composite(pic, (68 - pic.width // 2, 52 - pic.height // 2))
    d = ImageDraw.Draw(im)
    f = fitfont(d, title, font, 58, W - 200, 30)
    outlined(d, (136, 50), title, f, stroke=5, anchor='lm')
    save(rounded(im, 22), 'strip_%s_v15.png' % name)


def strips():
    for name, title, ic in STRIPS:
        strip(name, title, ic)


# ----------------------------------------------------------------------------------------------- at a glance
def glance(name='glance_v15.png'):
    c = counts()
    print('counts', {k: v for k, v in c.items() if k != 'per_chapter'})
    tiles = [
        (cluster(['grinder', 'fire_staff', 'pot'], 96), c['mods'], 'MODS', 'and %d shader packs' % c['shaders']),
        (icon('book', 92), c['quests'], 'QUESTS', 'in %d chapters' % c['chapters']),
        (icon('icon_map', 92), c['biomes'], 'NEW BIOMES', 'Overworld, Nether, End, Endless Sea'),
        (icon('heart', 92), c['pets'], 'RARE PETS', 'to find, tame and care for'),
        (icon('legendary', 92), c['crates'], 'LOOT CRATES', 'common, rare, epic, legendary'),
        (icon('star', 92), 1, 'DREAM STAR', 'made from %d treasures' % c['treasures']),
    ]
    news = [(tex('raft:item/boomerang', 64), 'Beach Craft 3.3:\ncozy, kitchen, gear'),
            (tex('raft:item/cutlass', 64), 'Guarded places,\nnew enemies'),
            (icon('heart', 64), 'Tamagotchi is\nnow Tamacraft'),
            (tex('questsicons:item/icons/ui/ui_pencil', 64), 'Quest Icons 1.3:\nedit in the game'),
            (icon('book', 64), 'Island Life\npath, %d quests' % c['island'])]
    cols, tw, th, gx, gy = 3, 368, 216, 16, 16
    top, band_h = 112, 176
    by = top + 2 * th + gy + 46
    h = by + band_h + 64
    im = night(W, h, seed=3, cloud_y=h - 70, n_stars=70)
    moon(im, (96, 58), 26)
    d = ImageDraw.Draw(im)
    outlined(d, (W // 2, 58), 'DREAMCRAFT AT A GLANCE', font(60), stroke=7, anchor='mm')
    x0 = (W - cols * tw - (cols - 1) * gx) // 2
    for k, (pic, num, label, sub) in enumerate(tiles):
        x, y = x0 + (k % cols) * (tw + gx), top + (k // cols) * (th + gy)
        shadowed(im, card(tw, th), (x, y), blur=8, offset=(0, 5), alpha=140)
        d = ImageDraw.Draw(im)
        cx, cy = x + 82, y + 88
        d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=(232, 222, 255))
        im.alpha_composite(pic, (cx - pic.width // 2, cy - pic.height // 2))
        d = ImageDraw.Draw(im)
        nf = font(100) if num < 1000 else font(84)
        outlined(d, (x + 166, y + 104), str(num), nf, fill=WHITE, stroke=7, stroke_fill=CLOUD2, anchor='ls')
        lf = fitfont(d, label, font, 34, tw - 176, 22)
        d.text((x + 168, y + 146), label, font=lf, fill=DEEP, anchor='ls')
        f = fitfont(d, sub, small, 21, tw - 28, 15)
        d.text((x + tw // 2, y + th - 30), sub, font=f, fill=INK, anchor='ms')
    band = Image.new('RGBA', (W - 32, band_h), (0, 0, 0, 0))
    ImageDraw.Draw(band).rounded_rectangle([0, 0, band.width - 1, band_h - 1], 24, fill=CLOUD2 + (255,),
                                           outline=CLOUD4 + (255,), width=4)
    shadowed(im, band, (16, by), blur=8, offset=(0, 5), alpha=120)
    d = ImageDraw.Draw(im)
    f = font(34)
    pill = 'NEW IN V1.5'
    pw = d.textlength(pill, font=f) + 48
    d.rounded_rectangle([W // 2 - pw / 2, by - 25, W // 2 + pw / 2, by + 25], 25, fill=CREAM, outline=CLOUD4, width=4)
    d.text((W // 2, by + 1), pill, font=f, fill=DEEP, anchor='mm')
    n = len(news)
    cw = (W - 64) / n
    for k, (pic, label) in enumerate(news):
        cx = 32 + cw * k + cw / 2
        im.alpha_composite(pic, (int(cx - pic.width / 2), by + 42 + (64 - pic.height) // 2))
        d = ImageDraw.Draw(im)
        for i, ln in enumerate(label.split('\n')):
            d.text((cx, by + 116 + 28 * i), ln, font=small(23), fill=CREAM, anchor='ma')
    save(rounded(im, 26), name)


if __name__ == '__main__':
    what = sys.argv[4:] or ['all']
    jobs = {'header': header, 'video': video_card, 'strips': strips, 'glance': glance, 'story': story,
            'flow_quests': flow_quests, 'flow_star': flow_star, 'new': news, 'collages': collages, 'menu': menu,
            'mods': mods_image, 'setup': setup}
    for k, f in jobs.items():
        if 'all' in what or k in what:
            f()
    if 'counts' in what:
        print(json.dumps(counts(), indent=1))
