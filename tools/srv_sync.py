"""srv_sync.py : rebuild srv/mods from packdb (server-capable mods) + ownjars."""
import json, os, shutil, glob
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
CLIENT_ONLY = set(json.load(open(f'{SP}/client_only.json')))
db = json.load(open(f'{SP}/packdb.json'))
for f in glob.glob(f'{SP}/srv/mods/*'): os.remove(f)
n = 0
for v in db.values():
    i = v['info']
    if not i or i['env'] == 'client' or i['id'] in CLIENT_ONLY: continue
    shutil.copy(v['path'], f"{SP}/srv/mods/{v['file']}"); n += 1
for j in glob.glob(f'{SP}/ownjars/*.jar'): shutil.copy(j, f'{SP}/srv/mods/'); n += 1
for d in ('world', 'logs', 'crash-reports'):
    if os.path.isdir(f'{SP}/srv/{d}'): shutil.rmtree(f'{SP}/srv/{d}')
print('server mods', n)
