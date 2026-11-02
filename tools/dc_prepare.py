"""dc_prepare.py : copy the client mods (all but Fabric API, which the dev run provides) and the pack overrides into dctest's run dir."""
import json, os, shutil, glob
SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
RUN = '/home/user/dctest/build/run/client'
os.makedirs(f'{RUN}/mods', exist_ok=True)
for f in glob.glob(f'{RUN}/mods/*'): os.remove(f)
db = json.load(open(f'{SP}/packdb.json'))
n = 0
for v in db.values():
    i = v['info']
    if v.get('type') == 'Shaders':
        os.makedirs(f'{RUN}/shaderpacks', exist_ok=True); shutil.copy(v['path'], f"{RUN}/shaderpacks/{v['file']}"); continue
    # neruina: its test mixins throw on purpose in a dev environment (Loom run) - production is not affected
    if not i or i['id'] in ('fabric-api', 'neruina') or i['env'] == 'server': continue
    shutil.copy(v['path'], f"{RUN}/mods/{v['file']}"); n += 1
for extra in glob.glob(f'{SP}/ownjars/*.jar'):
    shutil.copy(extra, f'{RUN}/mods/'); n += 1
if os.path.isdir(f'{SP}/pack/overrides'):
    shutil.copytree(f'{SP}/pack/overrides', RUN, dirs_exist_ok=True)
print('client mods', n)
