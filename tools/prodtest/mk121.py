"""mk121.py : instance121 = instance12 (V1.3) turned back into Dreamcraft V1.2.1, as hard links (no copy of 250 jars).
Every file that differs is unlinked first, so instance12 itself is never changed."""
import os, shutil, zipfile, json, subprocess, urllib.request
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
A, B = f'{SP}/cfinst/instance12', f'{SP}/cfinst/instance121'
if os.path.exists(B): shutil.rmtree(B)
subprocess.run(['cp', '-al', A, B], check=True)
for d in ('saves', 'logs', 'crash-reports', 'screenshots'):
    shutil.rmtree(f'{B}/{d}', ignore_errors=True)
for f in os.listdir(f'{B}/mods'):
    if f.startswith(('QuestIcons-', 'raft-', 'tamagotchi-')):
        os.remove(f'{B}/mods/{f}'); print('removed', f)
def get(pid, fid):
    url = f'https://www.curseforge.com/api/v1/mods/{pid}/files/{fid}/download'
    r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'}), timeout=300)
    name = os.path.basename(urllib.parse.unquote(r.geturl().split('?')[0]))
    open(f'{B}/mods/{name}', 'wb').write(r.read()); print('downloaded', name)
import urllib.parse
get(690531, 9415031); get(1010922, 9408472)
z = zipfile.ZipFile(f'{SP}/out/Dreamcraft 26.3 V1.2.1.zip'); z3 = zipfile.ZipFile(f'{SP}/out/Dreamcraft 26.3 V1.3.zip')
n = 0
for name in z.namelist():
    if not name.startswith('overrides/') or name.endswith('/'): continue
    rel = name[len('overrides/'):]
    if rel.startswith('mods/'): continue
    dst = f'{B}/{rel}'
    data = z.read(name)
    if os.path.exists(dst) and open(dst, 'rb').read() == data: continue
    if os.path.exists(dst): os.remove(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(data); n += 1
only13 = [x[len('overrides/'):] for x in set(z3.namelist()) - set(z.namelist()) if x.startswith('overrides/') and not x.endswith('/')]
for rel in only13:
    if os.path.exists(f'{B}/{rel}'): os.remove(f'{B}/{rel}'); print('removed V1.3-only', rel)
print('overrides written', n)
