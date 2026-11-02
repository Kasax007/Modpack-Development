"""Images of the Dreamcraft 26.3 CurseForge description (docs/curseforge/img): header, section strips, framed screenshots.
  python3 docs/curseforge/make_images.py STILLS_DIR ASSETS_DIR FONT.ttf
STILLS_DIR: landscape screenshots of the film run (vista, questbook, castle, magic, tech, kitchen, raft, nether, end, menu).
ASSETS_DIR: the pack's menu assets (config/fancymenu/assets/dreamcraft: loading_logo.png, bg1.jpg)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
STILLS, ASSETS, FONT = sys.argv[1], sys.argv[2], sys.argv[3]
DEEP, VIOLET, GOLD, WHITE = (36, 12, 70), (150, 70, 235), (255, 205, 80), (255, 255, 255)
W = 1200
os.makedirs(OUT, exist_ok=True)


def font(size):
    return ImageFont.truetype(FONT, size)


def outlined(d, xy, text, f, fill=WHITE, stroke=6, stroke_fill=DEEP, anchor='la'):
    d.text((xy[0], xy[1] + stroke // 2 + 3), text, font=f, fill=stroke_fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)


def rounded(im, r):
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    out = im.convert('RGBA')
    out.putalpha(m)
    return out


def sparkle(d, x, y, r, col):
    d.rectangle([x - r, y - 2, x + r, y + 2], fill=col)
    d.rectangle([x - 2, y - r, x + 2, y + r], fill=col)


def header():
    src = os.path.join(STILLS, 'vista.png')
    bg = Image.open(src if os.path.exists(src) else os.path.join(ASSETS, 'bg1.jpg')).convert('RGB')
    h = 460
    s = W / bg.width
    bg = bg.resize((W, int(bg.height * s)), Image.LANCZOS)
    y = max(0, (bg.height - h) // 2)
    im = bg.crop((0, y, W, y + h)).convert('RGBA')
    shade = Image.new('RGBA', (W, h))
    d = ImageDraw.Draw(shade)
    for yy in range(h):
        t = yy / h
        d.line([(0, yy), (W, yy)], fill=(DEEP[0], DEEP[1], DEEP[2], int(60 + 150 * t)))
    im = Image.alpha_composite(im, shade)
    logo = Image.open(os.path.join(ASSETS, 'loading_logo.png')).convert('RGBA')
    logo = logo.crop(logo.getbbox())
    ls = 860 / logo.width
    logo = logo.resize((860, int(logo.height * ls)), Image.LANCZOS)
    im.alpha_composite(logo, ((W - logo.width) // 2, 70))
    d = ImageDraw.Draw(im)
    outlined(d, (W // 2, 70 + logo.height + 46), 'A new dream for Minecraft 26.3', font(46), fill=GOLD, stroke=5, anchor='mm')
    for (x, yy, r) in [(120, 90, 10), (1080, 120, 12), (980, 380, 8), (200, 360, 9), (640, 40, 7)]:
        sparkle(d, x, yy, r, (255, 230, 150, 230))
    rounded(im, 26).save(os.path.join(OUT, 'header.png'))


def strip(name, title, sub):
    h = 104
    im = Image.new('RGBA', (W, h))
    d = ImageDraw.Draw(im)
    for x in range(W):
        t = x / W
        d.line([(x, 0), (x, h)], fill=(int(DEEP[0] + (VIOLET[0] - DEEP[0]) * t), int(DEEP[1] + (VIOLET[1] - DEEP[1]) * t),
                                       int(DEEP[2] + (VIOLET[2] - DEEP[2]) * t), 255))
    for (x, y, r) in [(900, 24, 6), (1010, 70, 8), (1120, 30, 5), (760, 78, 5), (1160, 84, 4)]:
        sparkle(d, x, y, r, (255, 230, 150, 200))
    d.ellipse([28, 16, 100, 88], fill=GOLD + (255,))
    d.ellipse([36, 24, 92, 80], fill=DEEP + (255,))
    outlined(d, (64, 52), sub, font(34), fill=GOLD, stroke=0, anchor='mm')
    outlined(d, (130, 52), title, font(54), stroke=5, anchor='lm')
    rounded(im, 22).save(os.path.join(OUT, f'strip_{name}.png'))


def framed(name, w=W):
    p = os.path.join(STILLS, name + '.png')
    if not os.path.exists(p):
        print('missing still', name)
        return
    im = Image.open(p).convert('RGB')
    s = (w - 24) / im.width
    im = im.resize((w - 24, int(im.height * s)), Image.LANCZOS)
    fr = Image.new('RGBA', (w, im.height + 24), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle([0, 0, fr.width - 1, fr.height - 1], 28, fill=(226, 206, 255, 255))
    fr.alpha_composite(rounded(im, 18), (12, 12))
    fr.save(os.path.join(OUT, name + '.png'))


if __name__ == '__main__':
    header()
    for i, (name, title) in enumerate([('story', 'THE STORY & QUESTS'), ('worlds', 'NEW WORLDS TO EXPLORE'), ('magic', 'MAGIC & COMBAT'),
                                       ('tech', 'TECH & STORAGE'), ('food', 'FOOD & FARMING'), ('build', 'BUILD YOUR DREAM BASE'),
                                       ('sea', 'THE ENDLESS SEA'), ('dims', 'A NEW NETHER AND END'), ('qol', 'QUALITY OF LIFE'),
                                       ('looks', 'PERFORMANCE & LOOKS'), ('server', 'SERVER & REQUIREMENTS')], 1):
        strip(name, title, str(i))
    for name in ('questbook', 'castle', 'magic', 'tech', 'kitchen', 'raft', 'nether', 'end', 'village', 'menu'):
        framed(name)
    print('images ->', OUT)
