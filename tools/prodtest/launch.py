"""Starts Minecraft 26.3 + Fabric Loader 0.20.1 the way a launcher does (production, no Loom), on a given instance dir.
usage: launch.py INSTANCE_DIR [--quickPlaySingleplayer WORLD] -> runs java in the foreground (log: INSTANCE/logs/latest.log)."""
import json, os, sys, subprocess, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = f'{HERE}/libraries'
inst = os.path.abspath(sys.argv[1]); extra = sys.argv[2:]
v = json.load(open('/root/.gradle/caches/fabric-loom/26.3/mojang_minecraft_info.json'))
fab = json.load(open(f'{HERE}/fabric_profile.json'))

def allowed(rules):
    if not rules: return True
    ok = False
    for r in rules:
        osr = r.get('os')
        match = osr is None or (osr.get('name') in (None, 'linux') and osr.get('arch') in (None, 'x86_64', 'amd64'))
        if match: ok = r['action'] == 'allow'
    return ok

def fetch(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(['curl', '-sS', '-L', '-m', '300', '-o', path + '.part', url], check=True)
        os.replace(path + '.part', path)
    return path

cp = []
for l in fab['libraries']:                                   # loader first, like the launcher
    g, a, ver = l['name'].split(':')[:3]
    rel = f"{g.replace('.', '/')}/{a}/{ver}/{a}-{ver}.jar"
    cp.append(fetch(l.get('url', 'https://maven.fabricmc.net/') + rel, f'{LIB}/{rel}'))
for l in v['libraries']:
    if not allowed(l.get('rules')): continue
    art = l.get('downloads', {}).get('artifact')
    if art: cp.append(fetch(art['url'], f"{LIB}/{art['path']}"))
cp.append('/root/.gradle/caches/fabric-loom/26.3/minecraft-client.jar')
# assets: vanilla wants indexes/<id>.json; Loom stores it as 26.3-<id>.json
aid = v['assetIndex']['id']
adir = f'{HERE}/assets'
os.makedirs(f'{adir}/indexes', exist_ok=True)
if not os.path.exists(f'{adir}/objects'):
    os.symlink('/root/.gradle/caches/fabric-loom/assets/objects', f'{adir}/objects')
idx = f'{adir}/indexes/{aid}.json'
if not os.path.exists(idx):
    import shutil; shutil.copy(f'/root/.gradle/caches/fabric-loom/assets/indexes/26.3-{aid}.json', idx)
nat = f'{HERE}/natives'
subst = {'${natives_directory}': nat, '${launcher_name}': 'test-launcher', '${launcher_version}': '1', '${classpath}': os.pathsep.join(cp)}
jvm = []
for a in v['arguments']['jvm']:
    if isinstance(a, dict):
        if not allowed(a.get('rules')): continue
        vals = a['value'] if isinstance(a['value'], list) else [a['value']]
    else:
        vals = [a]
    for x in vals:
        for k, s in subst.items(): x = x.replace(k, s)
        jvm.append(x)
game = ['--username', 'Tester', '--version', 'fabric-loader-0.20.1-26.3', '--gameDir', inst, '--assetsDir', adir, '--assetIndex', aid,
        '--uuid', '00000000000000000000000000000001', '--accessToken', '0', '--clientId', '0', '--xuid', '0', '--versionType', 'release'] + extra
cmd = ['/opt/jdk25/jdk-25.0.5+8/bin/java', '-Xmx6G'] + jvm + [fab['mainClass']] + game
os.makedirs(inst, exist_ok=True)
print('classpath entries', len(cp), flush=True)
sys.exit(subprocess.call(cmd, cwd=inst))
