# Side path - Tamacraft (the pet mod, formerly Tamagotchi; mod id tamacraft). Executed inside dc_quests.py (shares its names).
# Facts follow the mod's README and its Tamacon texts (repository tamagotchi, tools/data/gen_data.py).
import math

g = B.chapter('pets', '&dTamacraft', 'tamacraft:tamacraft_heart', ['&7Ten rare pets hide in the world. Find them all!'], PATHS, 'heart')
g.quest('start', '&dTamacraft', 0, 0, [
    KEEPER + '"Not every creature of the Dream is wild. Some only wait for a friend."',
    '',
    TIP + '&eTamacraft&7 adds ten rare pets. Find one, tame it with a &eTamacraft Heart&7 and look after it - feed it, play with it, keep it clean and let it sleep - and it follows you, carries a backpack, helps you fight and has a special talent.',
    TIP + 'Craft a heart: five red dye around an amethyst shard.',
    '',
    STAR + 'a Tamacraft Heart is one of its ingredients. Hearts are cheap: craft another one for the star later.'],
    [item('tamacraft:tamacraft_heart')], [give('tamacraft:pet_kibble', 8)], deps=['settler:animals'], shape='star', size=1.4,
    icon='tamacraft:tamacraft_heart')
g.quest('tamacon', 'The Tamacon', 0, -2.6, [
    TIP + 'A book, pink dye and redstone make the &eTamacon&7, the in-game guide to everything: every pet and where it lives, care, controls, toys, food and furniture.'],
    [item('tamacraft:tamacon')], [rxp(50)], deps=['start'])
g.quest('homes', 'Pets in Hiding', 4.5, 0, [
    TIP + 'Pets live in structures, but not in every one: each structure rolls once whether a pet lives there. Wild pets stay near their home and never despawn, so look inside and all around the building.',
    TIP + 'In Dreamcraft they also live in the look-alikes of these structures from other mods, like the pyramids, witch huts, mineshafts and mansions of Repurposed Structures.',
    TIP + 'Hold a Tamacraft Heart and wild pets come closer. The cute ones run away when hit; the Ember Pup, Sculk Wisp and Mimic bite back.',
    '',
    TIP + 'Around this quest are the ten pets. Spot each one in the wild.'],
    [], [rxp(50)], deps=['start'], shape='diamond', icon='questsicons:icon_map')

PETS = [  # key, name, home (chance), talent, what it does, treat item, fights with, extra
    ('desert_dragon', 'Desert Dragon', 'desert pyramids (40%)', 'Ember Roast', 'hand it raw food or raw ore and it roasts or smelts it with a little puff of flame',
     'dragon_fruit', 'a puff of fire that sets enemies alight', 'It flies after you when that is faster. Sand and sun make it happy.'),
    ('jungle_dragon', 'Jungle Dragon', 'jungle temples (40%)', 'Green Thumb', 'crops and saplings around it grow',
     'dragon_fruit', 'a poison bite', 'Leaf wings, a hibiscus flower and a very green thumb.'),
    ('tide_dragon', 'Tide Dragon', 'ocean monuments (50%)', 'Tide Blessing', 'while you swim near it you get Water Breathing and Dolphin\'s Grace',
     'fish_crackers', 'a bubble blast that knocks enemies back', 'It swims as well as it flies. Bring it along when you dive!'),
    ('frost_penguin', 'Frost Penguin', 'igloos (45%)', 'Frost Steps', 'while it follows you, water freezes under your feet',
     'fish_crackers', 'a volley of snowballs that slows enemies', 'On snow and ice it belly-slides.'),
    ('ember_pup', 'Ember Pup', 'nether fortresses (30%)', 'Warm Heart', 'when you catch fire it gives you Fire Resistance',
     'ember_jerky', 'a burning bite', 'Fire and lava cannot hurt it, and it swims through lava.'),
    ('sculk_wisp', 'Sculk Wisp', 'ancient cities (50%)', 'Echo Sense', 'its sonar ping makes hostile mobs nearby glow through walls',
     'glow_gummy', 'a sonic chirp', 'It floats, and it is so quiet that sculk sensors never notice it. Mind the warden on the way!'),
    ('void_kitten', 'Void Kitten', 'end cities (30%)', 'Item Magnet', 'while you are near, it pulls dropped items into its backpack or teleports them to you',
     'fish_crackers', 'a blink strike: it teleports next to the enemy', 'If it gets lost it simply teleports back to you.'),
    ('pebble_golem', 'Pebble Golem', 'trail ruins (35%) and mineshafts (8%)', 'Ore Sniffer', 'it sniffs out the best ore nearby, modded ores too, and makes it glow through the walls',
     'rock_candy', 'a heavy ground slam', 'Slow, but very tough.'),
    ('hex_toad', 'Hex Toad', 'swamp huts (45%)', 'Brew Buddy', 'when it is happy it brews you a random helpful potion effect now and then',
     'glow_gummy', 'a hex tongue that weakens', 'It hops everywhere and loves rain and swamps.'),
    ('mimic', 'Mimic', 'trial chambers (30%) and woodland mansions (60%)', 'Treasure Belly', 'it has 27 slots of belly storage (54 with a backpack) and coughs up little treasures',
     'golden_biscuit', 'a big chomp', 'A living chest! Do not try to open it.'),
]
HX, HY, R = 4.5, 0, 2.7
for i, (pid, name, home, talent, does, treat, fight, extra) in enumerate(PETS):
    ang = math.radians(-90 + 36 * i)
    g.quest(pid, name, round(HX + R * math.cos(ang), 2), round(HY + R * math.sin(ang), 2), [
        TIP + f'Lives in &e{home}&7.',
        TIP + f'Talent - &e{talent}&7: {does}.',
        TIP + f'Fights with {fight}. {extra}',
        '',
        TIP + f'Spot {"an" if name[0] in "AEIOU" else "a"} {name} in the wild.'],
        [observe(f'tamacraft:{pid}', 40, entity=True, title=f'Spot {"an" if name[0] in "AEIOU" else "a"} {name}')], [give(f'tamacraft:{treat}', 4)],
        deps=['homes'], optional=True, icon=f'tamacraft:{pid}_plush')

g.quest('tame', 'A New Best Friend', 9.5, 0, [
    TIP + 'Right-click a wild pet with the Tamacraft Heart to tame it. "♥ ... trusts you now!"',
    TIP + 'Right-click with an empty hand to pet it. &eSneak + right-click&7 opens the pet screen: needs, mood, bond, talent, backpack and the Sit / Follow / Wander buttons.',
    TIP + 'Leads and name tags work like on any pet.'],
    [adv('tamacraft:first_friend', 'Tame a pet')], [crate('rare'), give('tamacraft:pet_kibble', 16)], deps=['homes'], shape='star', size=1.4,
    icon='tamacraft:tamacraft_heart')
g.quest('pager', 'Beep Beep!', 11.5, -2, [
    TIP + 'Your first pet comes with a free &eTama Pager&7. Right-click your pet with it: stay or follow. Use it in the air to open the screen of your nearest pet, up to 64 blocks away.',
    TIP + 'While it is in your inventory it beeps when a pet is hungry, bored, sleepy, dirty or hurt.'],
    [adv('tamacraft:pager', 'Get a Tama Pager')], [rxp(100)], deps=['tame'], icon='tamacraft:tama_pager')
g.quest('feed', 'Feeding Time', 11.5, 2, [
    TIP + 'Every pet has four needs from 0 to 100: &eHunger&7, &eFun&7, &eEnergy&7 and &eHygiene&7. Together they make its mood. Happy pets use their talent, sad ones do not, and miserable pets refuse to fight.',
    TIP + '&ePet Kibble&7 (wheat with meat or fish) feeds every pet. A &eFood Bowl&7 filled with food feeds hungry pets by themselves. Pets eat modded food too.'],
    [item('tamacraft:pet_kibble', 8), item('tamacraft:food_bowl')], [give('tamacraft:pet_kibble', 16)], deps=['tame'])
g.quest('treats', 'Favourite Treats', 11.5, 4, [
    TIP + 'Favourite treats feed more, heal more and give bond: &eDragon Fruit&7 (the dragons), &eFish Crackers&7 (Tide Dragon, Frost Penguin, Void Kitten), &eEmber Jerky&7 (Ember Pup), &eRock Candy&7 (Pebble Golem), &eGlow Gummy&7 (Sculk Wisp, Hex Toad) and the &eGolden Biscuit&7 (Mimic).'],
    [item('tamacraft:dragon_fruit'), item('tamacraft:fish_crackers'), item('tamacraft:ember_jerky'), item('tamacraft:rock_candy'),
     item('tamacraft:glow_gummy'), item('tamacraft:golden_biscuit')], [crate('rare')], deps=['feed'], optional=True)
g.quest('play', 'Playtime', 13.5, 2, [
    TIP + 'Bored pets are sad pets. Hold right-click with the &eLaser Pointer&7 and they chase the red dot, throw the &eSqueaky Ball&7 and they fetch it, wave the &eFeather Wand&7 and they jump for it. Pets also play with each other.'],
    [item('tamacraft:laser_pointer'), item('tamacraft:squeaky_ball'), item('tamacraft:feather_wand')], [rxp(150)], deps=['feed'])
g.quest('clean', 'Squeaky Clean', 13.5, 0, [
    TIP + 'Groom your pet with a &ePet Brush&7, or fill a &ePet Bath&7 with a water bucket: dirty pets hop in and come out clean.'],
    [item('tamacraft:pet_brush'), item('tamacraft:pet_bath')], [give('minecraft:white_wool', 8)], deps=['feed'])
g.quest('sleep', 'Sweet Dreams', 15.5, 2, [
    TIP + 'Pets sleep in a &ePet Bed&7, a &ePet Basket&7 or a &eDragon Nest&7 at night or when they are tired. They rest faster next to a plush of their own kind. Click a bed or basket with a dye to recolour it.'],
    [item('tamacraft:pet_bed')], [give('tamacraft:pet_kibble', 16)], deps=['play', 'clean'], any_dep=True)
g.quest('backpack', 'A Backpack for Your Pet', 13.5, -2, [
    TIP + '&eSneak + right-click&7 your pet with a chest: it wears a backpack with 27 slots. Open it in the pet screen.',
    TIP + '&eGolden apples&7 in the backpack are special: when your health gets low, your pet runs to you and feeds you one. Other food is its own lunch box for fights.',
    TIP + 'Sneak + right-click with shears takes the backpack off - and everything inside spills out!',
    '',
    TIP + 'Tick the box when your pet wears a backpack.'],
    [item('minecraft:chest'), check('My pet wears a backpack')], [give('minecraft:golden_apple', 2)], deps=['pager'])
g.quest('talents', 'Hidden Talents', 15.5, -2, [
    TIP + 'Every pet has a &etalent&7 (the pet screen names it). A happy pet uses it by itself, and &ebond&7 - the hearts on the screen, which grow with every bit of care - makes it recharge faster.',
    TIP + 'The Desert Dragon smelts, the Jungle Dragon grows crops, the Pebble Golem sniffs out ores, the Void Kitten collects items, the Mimic stores them...',
    '',
    TIP + 'Tick the box when you saw your pet\'s talent.'],
    [check('My pet used its talent')], [crate('rare')], deps=['backpack'])
g.quest('brave', 'Brave Little Friend', 17.5, -2, [
    TIP + 'Your pet fights with you like a wolf, each pet in its own style. Below a third of its health it runs to you and eats from its backpack to heal.',
    TIP + 'A tamed pet never dies: it faints and curls up into a &eTama Egg&7 that keeps its name, needs, bond and backpack. Use the egg on a block to wake it up - or put it in a &ePet Incubator&7, which hatches it fully healed in thirty seconds.'],
    [item('tamacraft:pet_incubator')], [crate('rare')], deps=['talents'], optional=True)
g.quest('furniture', 'Pet Paradise', 17.5, 2, [
    TIP + 'Pets use furniture by themselves: bored pets bounce on the &eBouncy Mushroom&7 (so can you!), run in the &eRunning Wheel&7 (it gives a redstone signal) and scratch the &eScratching Post&7. The &ePet House&7 shelters them from rain and thunder.'],
    [item('tamacraft:bouncy_mushroom'), item('tamacraft:running_wheel'), item('tamacraft:scratching_post'), item('tamacraft:pet_house')],
    [crate('rare')], deps=['sleep'], optional=True)
g.quest('gadgets', 'Pet Gadgets', 17.5, 4, [
    TIP + 'The &eTreat Dispenser&7 shoots a treat to the hungriest pet on a redstone pulse, and the pet jumps and catches it. Bored pets open the &eToy Box&7 and play with the toys inside. The &ePet Flap&7 lets your pets through a wall and blocks everyone else.'],
    [item('tamacraft:treat_dispenser'), item('tamacraft:toy_box'), item('tamacraft:pet_flap')], [crate('rare')], deps=['furniture'], optional=True)
g.quest('decor', 'Plushies and Portraits', 15.5, 4, [
    TIP + 'There is a plush of every pet: squeeze it, and lonely pets come and cuddle it. Hang a &ePet Portrait&7 and click it: it paints your nearest pet with its name. The &eEgg Lamp&7 is a cosy night light.'],
    [item('tamacraft:pet_portrait'), item('tamacraft:egg_lamp')], [rxp(100)], deps=['sleep'], optional=True)
g.quest('all', '&dGotta Pet \'Em All', 9.5, 3.6, [
    KEEPER + '"Ten pets, ten friends. The Dream has never been so cosy."',
    '',
    TIP + 'Tame all ten pets. The rarest live in only three of ten &eend cities&7 (Void Kitten), &enether fortresses&7 (Ember Pup) and &etrial chambers&7 (Mimic, more often in woodland mansions). The Pebble Golem hides in trail ruins and, rarely, mineshafts.',
    TIP + 'Use the Explorer\'s Compass, and keep a few hearts with you.'],
    [adv('tamacraft:all_pets', 'Tame all ten pets', icon='tamacraft:tamacraft_heart')], [crate('legendary', 2), rxp(1000)], deps=['tame'], shape='heart', size=1.8, icon='questsicons:quest_crown')
