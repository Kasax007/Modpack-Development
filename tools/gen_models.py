import json, os
from PIL import Image

R='/home/user/Kasax_Raft_Mod/src/main/resources/assets/raft'
def w(path, data):
    p=os.path.join(R,path)
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,'w') as f:
        json.dump(data,f,indent=2)
        f.write('\n')

def face(tex, uv, cull=None, rot=None):
    d={'uv':uv,'texture':tex}
    if cull: d['cullface']=cull
    if rot: d['rotation']=rot
    return d

def box(frm,to,faces,**kw):
    d={'from':frm,'to':to,'faces':faces}
    d.update(kw)
    return d

def all_faces(tex, uvs):
    # uvs: dict dir->uv, or single uv
    out={}
    for dname in ['north','south','east','west','up','down']:
        uv=uvs[dname] if isinstance(uvs,dict) else uvs
        out[dname]=face(tex,uv)
    return out

def item_block(name, block=None):
    w(f'models/item/{name}.json', {'parent': f'raft:block/{block or name}'})

def item_flat(name, tex, handheld=False):
    w(f'models/item/{name}.json', {'parent':'minecraft:item/generated','textures':{'layer0':tex}})

def rotate_variants(model, props_prefix=''):
    v={}
    for facing,y in [('north',0),('east',90),('south',180),('west',270)]:
        key=f'{props_prefix}facing={facing}'.lstrip(',')
        e={'model':model}
        if y: e['y']=y
        v[key]=e
    return v

# ---------------- rope ladder ----------------
w('models/block/rope_ladder.json',{
  'ambientocclusion':False,
  'textures':{'particle':'raft:block/rope_ladder','texture':'raft:block/rope_ladder'},
  'elements':[box([0,0,15.2],[16,16,15.2],{
      'north':face('#texture',[0,0,16,16]),
      'south':face('#texture',[16,0,0,16])},shade_direction_override='up')]})
w('blockstates/rope_ladder.json',{'variants':rotate_variants('raft:block/rope_ladder')})
item_flat('rope_ladder','raft:block/rope_ladder')

# ---------------- rope coil ----------------
w('models/block/rope_coil.json',{
  'parent':'minecraft:block/block',
  'textures':{'particle':'raft:block/rope_coil','coil':'raft:block/rope_coil'},
  'elements':[box([2,0,2],[14,6,14],{
      'up':face('#coil',[2,2,14,14]),
      'down':face('#coil',[2,2,14,14],'down'),
      'north':face('#coil',[10,4,12,6]),
      'south':face('#coil',[10,4,12,6]),
      'east':face('#coil',[10,4,12,6]),
      'west':face('#coil',[10,4,12,6])})]})
w('blockstates/rope_coil.json',{'variants':{'':{'model':'raft:block/rope_coil'}}})
item_block('rope_coil')

# ---------------- ship wheel (wall, front faces north) ----------------
SIDE=[7,7,9,9]
w('models/block/ship_wheel.json',{
  'parent':'minecraft:block/block',
  'textures':{'particle':'raft:block/ship_wheel','wheel':'raft:block/ship_wheel'},
  'elements':[
    box([0,0,13],[16,16,14],{'north':face('#wheel',[0,0,16,16]),'south':face('#wheel',[16,0,0,16]),
        'up':face('#wheel',SIDE),'down':face('#wheel',SIDE),'east':face('#wheel',SIDE),'west':face('#wheel',SIDE)}),
    box([6,6,11],[10,10,13],{'north':face('#wheel',[6,6,10,10]),
        'up':face('#wheel',SIDE),'down':face('#wheel',SIDE),'east':face('#wheel',SIDE),'west':face('#wheel',SIDE)}),
    box([7,7,14],[9,9,16],{'up':face('#wheel',SIDE),'down':face('#wheel',SIDE),'east':face('#wheel',SIDE),'west':face('#wheel',SIDE),'north':face('#wheel',SIDE),'south':face('#wheel',SIDE,'south')})]})
w('blockstates/ship_wheel.json',{'variants':rotate_variants('raft:block/ship_wheel')})
item_flat('ship_wheel','raft:block/ship_wheel')

# ---------------- shark jaw trophy ----------------
w('models/block/shark_jaw_trophy.json',{
  'parent':'minecraft:block/block',
  'textures':{'particle':'raft:block/shark_jaw_trophy','trophy':'raft:block/shark_jaw_trophy'},
  'elements':[
    box([0,0,14],[16,16,15],{'north':face('#trophy',[0,0,16,16]),'south':face('#trophy',[16,0,0,16]),
        'up':face('#trophy',[0,0,16,1]),'down':face('#trophy',[0,0,16,1]),'east':face('#trophy',[0,0,1,16]),'west':face('#trophy',[0,0,1,16])}),
    box([3,4,13],[13,12,14],{'north':face('#trophy',[3,5,13,13]),
        'up':face('#trophy',[3,5,13,6]),'down':face('#trophy',[3,5,13,6]),'east':face('#trophy',[3,5,4,13]),'west':face('#trophy',[3,5,4,13])})]})
w('blockstates/shark_jaw_trophy.json',{'variants':rotate_variants('raft:block/shark_jaw_trophy')})
item_flat('shark_jaw_trophy','raft:block/shark_jaw_trophy')

# ---------------- raft flag ----------------
POLE=[0,0,2,16]
w('models/block/raft_flag.json',{
  'parent':'minecraft:block/block',
  'textures':{'particle':'raft:block/raft_flag_pole','pole':'raft:block/raft_flag_pole','flag':'raft:block/raft_flag'},
  'elements':[
    box([7,0,7],[9,16,9],{'north':face('#pole',POLE),'south':face('#pole',POLE),'east':face('#pole',POLE),'west':face('#pole',POLE),
        'up':face('#pole',[0,0,2,2]),'down':face('#pole',[0,0,2,2])}),
    box([8,3,-5],[8,15,7],{'east':face('#flag',[0,0,16,16]),'west':face('#flag',[16,0,0,16])})]})
w('blockstates/raft_flag.json',{'variants':rotate_variants('raft:block/raft_flag')})
item_flat('raft_flag','raft:block/raft_flag')

# ---------------- coconut lantern ----------------
def lantern(hanging):
    off=3 if hanging else 0
    els=[box([4,off,4],[12,off+10,12],{
            'north':face('#lantern',[0,2,8,12]),'south':face('#lantern',[0,2,8,12]),
            'east':face('#lantern',[0,2,8,12]),'west':face('#lantern',[0,2,8,12]),
            'up':face('#lantern',[0,0,8,8]),'down':face('#lantern',[0,0,8,8])})]
    if hanging:
        els.append(box([7.5,off+10,7.5],[8.5,16,8.5],{d:face('#lantern',[12,2,13,5]) for d in ['north','south','east','west']}))
        els.append(box([6,off+10,6],[10,off+11,10],{d:face('#lantern',[8,0,12,1]) for d in ['north','south','east','west','up']}))
    else:
        els.append(box([6,10,6],[10,11,10],{d:face('#lantern',[8,0,12,1]) for d in ['north','south','east','west','up']}))
    return {'parent':'minecraft:block/block','textures':{'particle':'raft:block/coconut_lantern','lantern':'raft:block/coconut_lantern'},'elements':els}
w('models/block/coconut_lantern.json',lantern(False))
w('models/block/coconut_lantern_hanging.json',lantern(True))
w('blockstates/coconut_lantern.json',{'variants':{'hanging=false':{'model':'raft:block/coconut_lantern'},'hanging=true':{'model':'raft:block/coconut_lantern_hanging'}}})
item_block('coconut_lantern')

# ---------------- crop plot ----------------
w('models/block/crop_plot.json',{'parent':'minecraft:block/template_cube_bottom_top_indented',
   'textures':{'bottom':'raft:block/crop_plot_side','side':'raft:block/crop_plot_side','top':'raft:block/crop_plot_top'}})
w('blockstates/crop_plot.json',{'variants':{'':{'model':'raft:block/crop_plot'}}})
item_block('crop_plot')

# ---------------- water purifier ----------------
for suffix,front in [('','front'),('_on','front_on')]:
    w(f'models/block/water_purifier{suffix}.json',{'parent':'minecraft:block/orientable_with_bottom',
      'textures':{'top':'raft:block/water_purifier_top','bottom':'raft:block/water_purifier_bottom',
                  'side':'raft:block/water_purifier_side','front':f'raft:block/water_purifier_{front}'}})
v={}
for facing,y in [('north',0),('east',90),('south',180),('west',270)]:
    for lit in ['false','true']:
        e={'model':'raft:block/water_purifier'+('_on' if lit=='true' else '')}
        if y: e['y']=y
        v[f'facing={facing},lit={lit}']=e
w('blockstates/water_purifier.json',{'variants':v})
item_block('water_purifier')

# ---------------- simple grill ----------------
def grill(on):
    top='#top_on' if on else '#top'
    els=[]
    for x0,z0 in [(1,1),(13,1),(1,13),(13,13)]:
        els.append(box([x0,0,z0],[x0+2,4,z0+2],{d:face('#side',[0,10,2,14]) for d in ['north','south','east','west']}))
    els.append(box([1,4,1],[15,10,15],{
        'north':face('#side',[0,0,16,6]),'south':face('#side',[0,0,16,6]),'east':face('#side',[0,0,16,6]),'west':face('#side',[0,0,16,6]),
        'up':face(top,[0,0,16,16]),'down':face('#side',[0,0,16,16])}))
    return {'parent':'minecraft:block/block','textures':{'particle':'raft:block/simple_grill_side','side':'raft:block/simple_grill_side',
            'top':'raft:block/simple_grill_top','top_on':'raft:block/simple_grill_top_on'},'elements':els}
w('models/block/simple_grill.json',grill(False))
w('models/block/simple_grill_on.json',grill(True))
w('blockstates/simple_grill.json',{'variants':{'lit=false':{'model':'raft:block/simple_grill'},'lit=true':{'model':'raft:block/simple_grill_on'}}})
item_block('simple_grill')

# ---------------- scarecrow ----------------
WOOD=[8,8,10,16]
STRAW=[0,8,8,16]
HEAD=[0,0,8,8]
HAT=[8,0,16,8]
def sc(frm,to,uv_by_dir):
    return box(frm,to,{d:face('#scarecrow',uv) for d,uv in uv_by_dir.items()})
lower=[
  sc([7,0,7],[9,16,9],{d:WOOD for d in ['north','south','east','west','down']}),
  sc([4,3,5],[12,16,11],{d:STRAW for d in ['north','south','east','west','up','down']}),
  sc([0,10,7],[16,13,9],{d:[0,8,8,11] for d in ['north','south','east','west','up','down']}),
]
upper=[
  sc([7,0,7],[9,4,9],{d:WOOD for d in ['north','south','east','west','up','down']}),
  box([4,4,4],[12,12,12],{'north':face('#scarecrow',HEAD),'south':face('#scarecrow',HAT),'east':face('#scarecrow',HAT),
       'west':face('#scarecrow',HAT),'up':face('#scarecrow',HAT),'down':face('#scarecrow',HAT)}),
  sc([2,12,2],[14,13,14],{d:[8,0,16,2] for d in ['north','south','east','west','up','down']}),
  sc([5,13,5],[11,16,11],{d:[8,0,14,3] for d in ['north','south','east','west','up','down']}),
]
for name,els in [('scarecrow_lower',lower),('scarecrow_upper',upper)]:
    w(f'models/block/{name}.json',{'parent':'minecraft:block/block','textures':{'particle':'raft:block/scarecrow','scarecrow':'raft:block/scarecrow'},'elements':els})
v={}
for half in ['lower','upper']:
    for facing,y in [('north',0),('east',90),('south',180),('west',270)]:
        e={'model':f'raft:block/scarecrow_{half}'}
        if y: e['y']=y
        v[f'half={half},facing={facing}']=e
w('blockstates/scarecrow.json',{'variants':v})
item_flat('scarecrow','raft:item/scarecrow')

# scarecrow item icon, drawn from the block texture palette
sc_img=Image.open(os.path.join(R,'textures/block/scarecrow.png')).convert('RGBA')
def px(x,y): return sc_img.getpixel((x,y))
icon=Image.new('RGBA',(16,16),(0,0,0,0))
hat=px(12,3); straw=px(3,12); wood=px(12,12); skin=px(3,3); dark=(40,28,20,255)
for x in range(5,11):
    for y in range(0,3): icon.putpixel((x,y),hat)
for x in range(3,13): icon.putpixel((x,3),hat)
for x in range(4,12):
    for y in range(4,8): icon.putpixel((x,y),skin)
icon.putpixel((5,5),dark); icon.putpixel((9,5),dark); icon.putpixel((6,7),dark); icon.putpixel((7,7),dark); icon.putpixel((8,7),dark)
for x in range(1,15):
    for y in range(9,11): icon.putpixel((x,y),straw)
for x in range(5,11):
    for y in range(11,14): icon.putpixel((x,y),straw)
for y in range(8,16):
    for x in (7,8): icon.putpixel((x,y),wood)
for x in range(6,10): icon.putpixel((x,15),wood)
icon.save(os.path.join(R,'textures/item/scarecrow.png'))

# raft teleporter: add a particle texture (phase 1 note)
p=os.path.join(R,'models/item/raft_teleporter.json')
s=open(p).read()
if '"particle"' not in s:
    s=s.replace('"textures": {\n\t\t"3": "raft:item/raft_teleporter"','"textures": {\n\t\t"particle": "raft:item/raft_teleporter",\n\t\t"3": "raft:item/raft_teleporter"',1)
    open(p,'w').write(s)
print('done')
