"""usage: cf_install.py CLIENT_FILE_ID|CLIENT_ZIP [SERVER_FILE_ID]  (e.g. 9409459 9409463 for V1.2)
Installs Dreamcraft the way a launcher does: the client zip from CurseForge (or a local zip built by mkpack.py, to test
a pack before its upload), every manifest file from CurseForge (by project and file id), the overrides on top.
Writes report.json (file names, sizes, sha1)."""
import json, os, subprocess, zipfile, hashlib, sys
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.abspath(__file__))
INST = f'{BASE}/instance'
def get(pid, fid, dst_dir):
    url = f'https://www.curseforge.com/api/v1/mods/{pid}/files/{fid}/download'
    for attempt in range(4):
        r = subprocess.run(['curl', '-sS', '-L', '-m', '600', '-o', f'{dst_dir}/.part_{fid}', '-w', '%{http_code} %{url_effective}', url],
                           capture_output=True, text=True)
        out = r.stdout.strip().split(' ', 1)
        if r.returncode == 0 and out and out[0] == '200':
            name = out[1].split('?')[0].rsplit('/', 1)[-1]
            name = subprocess.run(['python3', '-c', 'import urllib.parse,sys;print(urllib.parse.unquote(sys.argv[1]))', name],
                                  capture_output=True, text=True).stdout.strip()
            os.replace(f'{dst_dir}/.part_{fid}', f'{dst_dir}/{name}')
            return name
    return None
os.makedirs(f'{INST}/mods', exist_ok=True)
if os.path.isfile(sys.argv[1]):
    pack = os.path.abspath(sys.argv[1])          # a local pack zip, not uploaded yet
else:
    pack = f'{BASE}/' + get(545167, int(sys.argv[1]), BASE)
print('pack', pack, flush=True)
z = zipfile.ZipFile(pack)
man = json.loads(z.read('manifest.json'))
for n in z.namelist():
    if n.startswith('overrides/') and not n.endswith('/'):
        p = os.path.join(INST, n[len('overrides/'):])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(z.read(n))
files = man['files']
def one(f):
    name = get(f['projectID'], f['fileID'], f'{INST}/mods')
    if not name:
        return dict(f, error='download failed')
    data = open(f'{INST}/mods/{name}', 'rb').read()
    return dict(f, file=name, size=len(data), sha1=hashlib.sha1(data).hexdigest())
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, files))
bad = [r for r in res if 'error' in r]
json.dump(dict(manifest=man, files=res), open(f'{BASE}/report.json', 'w'), indent=1)
print('mods', len(res), 'failed', len(bad), bad[:5], flush=True)
srv = get(545167, int(sys.argv[2]), BASE) if len(sys.argv) > 2 else None
print('server pack', srv, flush=True)
