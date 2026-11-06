"""Generates the Dreamcraft FancyMenu v3 layouts (title screen x8 random backgrounds, Drippy loading overlay)."""
import re, uuid, os, sys, hashlib
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
CC = f'{SP}/dl/cc4/overrides/config/fancymenu/customization'
OUT = f'{SP}/pack/overrides/config/fancymenu/customization'
os.makedirs(OUT, exist_ok=True)
A = '[source:local]/config/fancymenu/assets/dreamcraft'
summit = open(f'{CC}/title_screen_challengecraft_summit.txt').read()
drippy = open(f'{CC}/drippy_loading_overlay_layout.txt').read()

def uid(seed):
    h = hashlib.md5(seed.encode()).hexdigest()
    return f'{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}-1793600000000'

def blocks(text, name):
    return re.findall(r'\n' + name + r' \{\n.*?\n\}', text, re.S)

def setkeys(block, **kv):
    for k, v in kv.items():
        if re.search(r'\n  ' + re.escape(k) + r' = .*', block):
            block = re.sub(r'\n  ' + re.escape(k) + r' = .*', lambda m: f'\n  {k} = {v}', block, count=1)
        else:
            block = block[:-2] + f'\n  {k} = {v}\n}}'
    return block

def fresh_ids(block, seed):
    # new identifiers for every uuid-like value so layouts never share instances. The same old id must get the same
    # new id everywhere in the block: a button names its action block twice (button_element_executable_block_identifier
    # and [executable_block:...]); different ids there left the Mods and Rent a Server buttons without any action.
    def rep(m):
        return uid(f'{seed}/{m.group(0)}')
    return re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-\d{13}', rep, block)

IMG = [b for b in blocks(summit, 'element') if 'element_type = image' in b][0]
VB = [b for b in blocks(summit, 'vanilla_button') if 'mc_titlescreen_singleplayer_button' in b][0]
HEAD_END = summit.index('\nelement {')
head = summit[:HEAD_END]
# keep all menu_background/decoration blocks, but switch the image background to ours
def title_layout(i):
    h = head
    h = re.sub(r'identifier = title_screen\n', 'identifier = title_screen\n', h)
    # Custom elements behind vanilla: the sidebar band is a custom image. Drawn above the vanilla widgets it tinted
    # Singleplayer, Multiplayer, Options and Quit Game (vanilla buttons) purple, while Mods and Rent a Server (custom
    # buttons after the band) stayed bright (fixed in V1.4.1).
    h = setkeys_meta(h, randommode='true', randomonlyfirsttime='true', is_enabled='true', layout_index=str(i),
                     render_custom_elements_behind_vanilla='true')
    # The layout is drawn at GUI scale 2 on a 1920x1080 window (960x540 GUI units). Auto-scaling turns that scale
    # into scale 2 * min(window / 1920x1080), so smaller windows (the default 854x480, 1366x768) show the whole menu
    # instead of cutting off the lower buttons.
    h = h.replace('customization {\n  action = setscale\n  scale = 2.0\n}',
                  'customization {\n  action = setscale\n  scale = 2.0\n}\n\ncustomization {\n  action = autoscale\n'
                  '  basewidth = 1920\n  baseheight = 1080\n}', 1)
    assert 'action = autoscale' in h
    h = h.replace('[source:local]/config/fancymenu/assets/cc_menu_bg.png', f'{A}/bg{i}.jpg')
    h = re.sub(r'(background_type = image\n  show_background = )\w+', r'\1true', h)
    h = re.sub(r'parallax_intensity_x = 0.015\n  parallax_intensity_y = 0.015', 'parallax_intensity_x = 0.01\n  parallax_intensity_y = 0.01', h)
    h = fresh_ids(h, f'title{i}/head')
    els = []
    # sidebar band with the DreamCraft logo
    els.append(image(f't{i}/sidebar', f'{A}/sidebar.png', 'top-left', 36, 0, 176, 542, stretch_y=True))
    # buttons (vanilla ones restyled, so they keep their real function)
    bx, bw, bh = 49, 150, 29
    y0, step = 232, 34
    order = [('mc_titlescreen_singleplayer_button', 'single'), ('mc_titlescreen_multiplayer_button', 'multi'),
             ('mc_titlescreen_options_button', 'options')]
    for n, (vid, tex) in enumerate(order):
        els.append(vbutton(f't{i}/{vid}', vid, bx, y0 + n * step, bw, bh, tex))
    els.append(cbutton(f't{i}/mods', 'mods', bx, y0 + 3 * step, bw, bh, 'opengui', 'com.terraformersmc.modmenu.gui.ModsScreen'))
    els.append(cbutton(f't{i}/rent', 'rent', bx, y0 + 4 * step, bw, bh, 'openlink', 'https://bisecthosting.com/kasax007'))
    els.append(vbutton(f't{i}/quit', 'mc_titlescreen_quit_button', bx, y0 + 5 * step, bw, bh, 'quit'))
    # hide everything else vanilla draws on the title screen
    for vid in ['mc_titlescreen_realms_button', 'mc_titlescreen_accessibility_button', 'mc_titlescreen_language_button',
                'minecraft_logo_widget', 'minecraft_splash_widget', 'minecraft_realms_notification_icons_widget', 'minecraft_branding_widget', 'modmenu_titlescreen_mods_button',
                '454370', '478370', '502370', '526370', '612319', '700416', '788416', '490370', '612441', '466370', '612274', '514370', '612416']:
        els.append(hidden(f't{i}/{vid}', vid))
    els.append(image(f't{i}/version', f'{A}/version_tag.png', 'bottom-left', 4, -22, 166, 18))
    return h + '\n' + '\n'.join(els) + '\n'

def setkeys_meta(h, **kv):
    meta = re.search(r'layout-meta \{.*?\n\}', h, re.S).group(0)
    new = meta
    for k, v in kv.items():
        new = re.sub(r'\n  ' + k + r' = .*', f'\n  {k} = {v}', new)
    return h.replace(meta, new)

def image(seed, src, anchor, x, y, w, h, stretch_y=False):
    b = fresh_ids(IMG, seed)
    b = setkeys(b, instance_identifier=uid(seed + '/image'), anchor_point=anchor, x=x, y=y, width=w, height=h, source=src, enable_parallax='false',
                stretch_y='true' if stretch_y else 'false', auto_sizing='false')
    return b.lstrip('\n')

def vbutton(seed, vid, x, y, w, h, tex):
    b = fresh_ids(VB, seed)
    b = setkeys(b, instance_identifier=vid, anchor_point='top-left', x=x, y=y, width=w, height=h, is_hidden='false',
                label='', backgroundnormal=f'{A}/btn_{tex}.png', backgroundhovered=f'{A}/btn_{tex}_hover.png',
                background_texture_inactive=f'{A}/btn_{tex}.png', transparent_background='false', label_shadow='false')
    return b.lstrip('\n')

def hidden(seed, vid):
    b = fresh_ids(VB, seed)
    b = setkeys(b, instance_identifier=vid, is_hidden='true', anchor_point='top-left', x=-5000, y=-5000, stay_on_screen='false')
    return b.lstrip('\n')

def cbutton(seed, tex, x, y, w, h, action, value):
    b = fresh_ids(VB, seed)
    block_id = re.search(r'button_element_executable_block_identifier = (\S+)', b).group(1)
    act_id = uid(seed + '/action')
    b = re.sub(r'\[executable_block:' + re.escape(block_id) + r'\]\[type:generic\] = \[executables:\]',
               f'[executable_block:{block_id}][type:generic] = [executables:{act_id};]\n'
               f'  [executable_action_instance:{act_id}][action_type:{action}] = {value}', b)
    b = setkeys(b, element_type='custom_button', instance_identifier=uid(seed + '/el'), anchor_point='top-left', x=x, y=y,
                width=w, height=h, is_hidden='false', label='', backgroundnormal=f'{A}/btn_{tex}.png',
                backgroundhovered=f'{A}/btn_{tex}_hover.png', background_texture_inactive=f'{A}/btn_{tex}.png',
                transparent_background='false', label_shadow='false')
    b = b.replace('\nvanilla_button {', '\nelement {', 1)
    return b.lstrip('\n')

for i in range(1, 9):
    open(f'{OUT}/title_screen_dreamcraft_{i}.txt', 'w').write(title_layout(i))

# Drippy loading overlay: star background, DREAMCRAFT FABRIC logo, purple progress bar
d = drippy
d = d.replace('[source:local]/config/fancymenu/assets/cc_loading_bg.png', f'{A}/loading_bg.jpg')
d = fresh_ids(d, 'drippy')
d = re.sub(r'(source = )\[source:local\]/config/fancymenu/assets/final.png', r'\g<1>' + A + '/loading_logo.png', d)
logo = [b for b in blocks(d, 'element') if 'loading_logo' in b][0]
d = d.replace(logo, setkeys(logo, anchor_point='mid-centered', x=-200, y=-190, width=400, height=300))
bar = [b for b in blocks(d, 'vanilla_button') if 'instance_identifier = progress_bar' in b][0]
# the vanilla bar widget cannot be coloured (it ignores any colour key): hide it and draw Drippy's own bar in purple
d = d.replace(bar, setkeys(bar, anchor_point='mid-centered', x=-200, y=110, width=400, height=10, is_hidden='true'))
pbar = fresh_ids(IMG, 'drippy/purple_bar')
pbar = re.sub(r'\n  source = .*', '', pbar)
pbar = setkeys(pbar, element_type='drippy_vanilla_bar', instance_identifier=uid('drippy/purple_bar/el'), anchor_point='mid-centered', x=-200, y=110, width=400, height=10,
               color='#7E0CC9FF', stretch_y='false', auto_sizing='false')
d = d.rstrip('\n') + '\n\n' + pbar.lstrip('\n') + '\n'
open(f'{OUT}/drippy_loading_overlay_layout.txt', 'w').write(d)

open(f'{SP}/pack/overrides/config/fancymenu/customizablemenus.txt', 'w').write(
    'type = customizablemenus\n\nde.keksuccino.drippyloadingscreen.customization.DrippyOverlayScreen {\n}\n\n'
    'net.minecraft.client.gui.screens.TitleScreen {\n}\n')
print('ok', sorted(os.listdir(OUT)))
