"""mkpack.py VERSION QUESTICONS_FILE_ID [BEACHCRAFT_FILE_ID [TAMAGOTCHI_FILE_ID]] : build the Dreamcraft client modpack
and the server pack.

Client pack: manifest.json (all CurseForge mods), modlist.html, overrides/ (configs, menu, quests, own jars).
Server pack: a ready folder with the server-capable mods, configs, the Fabric server launcher and start scripts.

Own mods: Quest Icons and Beach Craft come from CurseForge when their file id is given ('-' = ship the jar from
$SP/ownjars inside the client pack instead); the server pack always takes their jars from $SP/ownjars.
Tamacraft (formerly Tamagotchi, same CurseForge project) is a normal CurseForge mod of the pack: its file id is in
pack/mods.json (TAMAGOTCHI_PROJECT); a fourth argument overrides it. The server pack gets exactly that CurseForge file
(cached in $SP/jars, downloaded if missing); a tamacraft (or tamagotchi) jar in $SP/ownjars is only for the test client
(tools/dc_prepare.py).
"""
import json, os, sys, zipfile, shutil, glob, html, time, urllib.request, urllib.parse
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC, LOADER = '26.3', '0.20.1'
TAMAGOTCHI_PROJECT = 1758309
version = sys.argv[1]                      # e.g. "V1"
qi_file = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != '-' else None
raft_file = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != '-' else None   # Raft = CurseForge 'Beach Craft' (1010922)
tama = next(m for m in json.load(open(f'{REPO}/pack/mods.json')) if m['projectID'] == TAMAGOTCHI_PROJECT)
tama_file = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != '-' else tama['fileID']
db = json.load(open(f'{SP}/packdb.json'))


def cf_jar(pid, fid):
    """The jar of one CurseForge file, from the cache $SP/jars/<file id>-<name> or downloaded (name from cfwidget)."""
    hit = glob.glob(f'{SP}/jars/{fid}-*.jar')
    if hit:
        return hit[0]
    req = urllib.request.Request(f'https://api.cfwidget.com/{pid}', headers={'User-Agent': 'curl/8.5.0'})
    files = json.loads(urllib.request.urlopen(req, timeout=60).read())['files']
    f = next((f for f in files if f['id'] == fid), None)
    if f is None:
        sys.exit(f'CurseForge file {fid} of project {pid} is unknown to cfwidget (not approved yet?). '
                 f'Put the jar at {SP}/jars/{fid}-<file name>.jar and run again.')
    url = f"https://edge.forgecdn.net/files/{fid // 1000}/{fid % 1000}/{urllib.parse.quote(f['name'])}"
    path = f"{SP}/jars/{fid}-{f['name']}"
    data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'curl/8.5.0'}), timeout=300).read()
    open(path, 'wb').write(data)
    return path
client_only = set(json.load(open(f'{SP}/client_only.json')))
OUT = f'{SP}/out'
os.makedirs(OUT, exist_ok=True)
name = f'Dreamcraft {MC} {version}'

files = []
rows = []
for v in sorted(db.values(), key=lambda v: v['title'].lower()):
    files.append({'projectID': int(v['pid']), 'fileID': v['fileID'], 'required': True, 'isLocked': False})
    rows.append((v['title'], v['slug']))
if qi_file:
    files.append({'projectID': 690531, 'fileID': qi_file, 'required': True, 'isLocked': False})
    rows.append(('Quest Icons', 'quest-icons'))
if raft_file:
    files.append({'projectID': 1010922, 'fileID': raft_file, 'required': True, 'isLocked': False})
    rows.append(('Beach Craft (Raft)', 'beach-craft'))
files.append({'projectID': TAMAGOTCHI_PROJECT, 'fileID': tama_file, 'required': True, 'isLocked': False})
rows.append((tama['title'], tama['slug']))
tama_jar = cf_jar(TAMAGOTCHI_PROJECT, tama_file)
print('Tamacraft (formerly Tamagotchi): CurseForge file', tama_file, '->', os.path.basename(tama_jar))
rows.sort(key=lambda r: r[0].lower())
manifest = {'minecraft': {'version': MC, 'modLoaders': [{'id': f'fabric-{LOADER}', 'primary': True}]},
            'manifestType': 'minecraftModpack', 'manifestVersion': 1, 'name': f'Dreamcraft {MC}', 'version': version,
            'author': 'Kasax007', 'files': files, 'overrides': 'overrides'}
modlist = '<ul>\n' + ''.join(f'<li><a href="https://www.curseforge.com/minecraft/mc-mods/{s}">{html.escape(t)}</a></li>\n' for t, s in rows) + '</ul>\n'

def add_tree(z, src, arc):
    for root, dirs, fs in os.walk(src):
        for f in sorted(fs):
            p = os.path.join(root, f)
            z.write(p, os.path.join(arc, os.path.relpath(p, src)))

client_zip = f'{OUT}/{name}.zip'
with zipfile.ZipFile(client_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('manifest.json', json.dumps(manifest, indent=2))
    z.writestr('modlist.html', modlist)
    add_tree(z, f'{SP}/pack/overrides', 'overrides')
    for j in sorted(glob.glob(f'{SP}/ownjars/*.jar')):
        if 'QuestIcons' in j and qi_file: continue          # comes from CurseForge
        if os.path.basename(j).startswith('raft-') and raft_file: continue
        if os.path.basename(j).startswith(('tamagotchi-', 'tamacraft-')): continue   # always from CurseForge (manifest)
        z.write(j, 'overrides/mods/' + os.path.basename(j))
print('client pack', client_zip, os.path.getsize(client_zip) // 1024, 'KB,', len(files), 'CurseForge mods')

# ---------------------------------------------------------------- server pack
root = f'Dreamcraft {MC} {version} Server'
server_zip = f'{OUT}/{name} Server Pack.zip'
start_sh = """#!/bin/sh
# Dreamcraft 26.3 server. Needs Java 25 (https://adoptium.net). First start downloads Minecraft itself.
cd "$(dirname "$0")"
if ! grep -q "eula=true" eula.txt 2>/dev/null; then
  echo "Please read https://aka.ms/MinecraftEULA and set eula=true in eula.txt, then start again."
  echo "eula=false" > eula.txt
  exit 1
fi
exec java -Xms4G -Xmx${DREAMCRAFT_RAM:-8G} -jar fabric-server-launch.jar nogui
"""
start_bat = """@echo off
rem Dreamcraft 26.3 server. Needs Java 25 (https://adoptium.net). First start downloads Minecraft itself.
cd /d "%~dp0"
findstr /c:"eula=true" eula.txt >nul 2>&1
if errorlevel 1 (
  echo Please read https://aka.ms/MinecraftEULA and set eula=true in eula.txt, then start again.
  echo eula=false> eula.txt
  pause
  exit /b 1
)
java -Xms4G -Xmx8G -jar fabric-server-launch.jar nogui
pause
"""
readme = f"""Dreamcraft {MC} {version} - Server Pack
==========================================

1. Install Java 25 (https://adoptium.net).
2. Unzip this folder on your server.
3. Start it once with start.sh (Linux/macOS) or start.bat (Windows).
   It creates eula.txt - read the Minecraft EULA and set eula=true.
4. Start again. The Fabric launcher downloads Minecraft {MC} and starts the server
   with Fabric Loader {LOADER} and all {{n}} mods.

RAM: 6-8 GB recommended (edit start.bat / set DREAMCRAFT_RAM=10G for start.sh).
Players: a new Minecraft {MC} server starts with a whitelist. Add your friends in the console with
   whitelist add <name>   - or set white-list=false in server.properties.
Quests: config/questsicons/quests (same files as the client pack).
Need a server? BisectHosting - code KASAX007 for 25% off: https://bisecthosting.com/kasax007
"""
props = """motd=\\u00a7dDreamcraft \\u00a77{mc} \\u00a78- \\u00a7fa dream of a modpack
difficulty=normal
view-distance=10
simulation-distance=8
spawn-protection=0
allow-flight=true
max-tick-time=120000
sync-chunk-writes=false
""".format(mc=MC)
with zipfile.ZipFile(server_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    n = 0
    for v in sorted(db.values(), key=lambda v: v['file']):
        i = v['info']
        if not i or i['env'] == 'client' or i['id'] in client_only: continue
        z.write(v['path'], f"{root}/mods/{v['file']}"); n += 1
    for j in sorted(glob.glob(f'{SP}/ownjars/*.jar')):
        if os.path.basename(j).startswith(('tamagotchi-', 'tamacraft-')): continue   # the server gets the CurseForge file below
        z.write(j, f'{root}/mods/' + os.path.basename(j)); n += 1
    z.write(tama_jar, f'{root}/mods/' + os.path.basename(tama_jar).split('-', 1)[1]); n += 1
    for sub in ('config',):
        src = f'{SP}/pack/overrides/{sub}'
        if os.path.isdir(src):
            for r, ds, fs in os.walk(src):
                rel = os.path.relpath(r, src)
                if rel.startswith('fancymenu') or rel.startswith('drippyloadingscreen'): continue
                for f in fs: z.write(os.path.join(r, f), f'{root}/{sub}/' + os.path.normpath(os.path.join(rel, f)))
    z.write(f'{SP}/srv/fabric-server-launch.jar', f'{root}/fabric-server-launch.jar')
    for fname, content, mode in (('start.sh', start_sh, 0o755), ('start.bat', start_bat, 0o644), ('README.txt', readme.replace('{n}', str(n)), 0o644),
                                 ('server.properties', props, 0o644)):
        info = zipfile.ZipInfo(f'{root}/{fname}', date_time=time.localtime()[:6]); info.external_attr = mode << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, content)
    if os.path.exists(f'{SP}/pack/server-icon.png'):
        z.write(f'{SP}/pack/server-icon.png', f'{root}/server-icon.png')
print('server pack', server_zip, os.path.getsize(server_zip) // (1024 * 1024), 'MB,', n, 'mods')
