"""Dreamcraft 26.3 quest book: the story chapters and the side paths.

python3 tools/dc_quests.py OUT_DIR writes the book (data.snbt, chapters/, reward_tables/). The quest ids are hashes of
"<chapter key>:<quest key>", so keep the keys: renaming one resets that quest for everybody. Rewards are numbered in
order, so add new rewards at the end of a list instead of changing the old ones (players who claimed them keep them).
Chapter 6 (Beach Craft) is in dc_quests_raft.py, the Tamacraft side path in dc_quests_pets.py and the Island Life
side path (Beach Craft 3.2 and 3.3) in dc_quests_island.py.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from qlib import *

B = Book()
STORY = B.group('story', '&d✦ The Dream', 'questsicons:icon_moon')
PATHS = B.group('paths', '&b✦ Side Paths', 'questsicons:icon_map')

KEEPER = '&d&o'   # the Dreamkeeper's voice
TIP = '&7'
STAR = '&d✦ Dream Star:&7 '   # marks the ingredients of the endgame trophy

# =====================================================================================================
# Prologue
p = B.chapter('prologue', '&dPrologue: A Strange Dream', 'questsicons:icon_moon',
              ['&7You fell asleep... and woke up somewhere else.'], STORY, 'circle')
p.quest('wake', '&dA Strange Dream', 0, 0, [
    KEEPER + '"Welcome, Dreamer. I am the Dreamkeeper. This world is a dream - yours now."',
    '',
    TIP + 'This is your &eQuest Book&7. Open it any time with &eJ&7, the book in your inventory or the button in the top-left corner of your inventory.',
    TIP + 'Click a quest to read it. Finished quests turn &agreen&7 and their rewards wait behind the &eClaim&7 button.',
    TIP + 'Tick the box below to begin your journey.'],
    [check('I am ready to dream')], [rxp(25), give('minecraft:bread', 6)], icon='questsicons:quest_book', shape='star', size=1.6)
p.quest('wood', 'Punch a Tree', 2.5, 0, [
    KEEPER + '"Every dream begins with something simple. Wood."',
    '',
    TIP + 'Chop any logs. &eFallingTree&7 is installed: break the bottom log with an axe and the whole tree comes down. Sneak while chopping to take only one log.'],
    [item('#minecraft:logs', 16)], [give('minecraft:apple', 4)], deps=['wake'])
p.quest('table', 'The First Workbench', 4.5, -1.5, [
    TIP + 'Craft a crafting table.',
    '',
    TIP + 'Not sure how something is made? Hover over any item in your inventory and press &eR&7 for its recipes or &eU&7 for its uses (&eJEI&7). The search bar at the bottom of the screen finds every item in the pack.'],
    [item('minecraft:crafting_table')], [give('minecraft:stick', 16)], deps=['wood'])
p.quest('stone', 'Stone Age', 4.5, 1.5, [
    TIP + 'Get some cobblestone and craft a stone pickaxe.',
    '',
    TIP + 'Look at any block to see what it is and which tool mines it (&eJade&7, top of the screen).'],
    [item('minecraft:cobblestone', 32), item('minecraft:stone_pickaxe')], [give('minecraft:torch', 16)], deps=['wood'])
p.quest('carry', 'Carry On', 4.5, -3.3, [
    TIP + 'Moving house? Sneak and right-click a chest, a furnace or a small animal with &eboth hands empty&7: you pick it up, with everything inside (&eCarry On&7).',
    TIP + 'Right-click a spot to set it down again.',
    '',
    TIP + 'Tick the box once you carried something.'],
    [check('I carried something')], [rxp(30)], deps=['table'], optional=True)
p.quest('food', 'Hunger Pangs', 6.5, -1.5, [
    KEEPER + '"Even dreamers get hungry."',
    '',
    TIP + 'Collect some food. &eAppleSkin&7 shows how much hunger and saturation a food restores right on your hunger bar.'],
    [item('#c:foods', 8)], [give('farmersdelight:flint_knife')], deps=['table'])
p.quest('bed', 'A Place to Sleep', 6.5, 1.5, [
    TIP + 'Craft a bed. Sleeping skips the night and sets your respawn point.',
    '',
    TIP + 'Night in the dream is dangerous: new monsters roam the dark.'],
    [item('#minecraft:beds')], [give('minecraft:lantern', 3)], deps=['stone'])
p.quest('campfire', 'A Warm Fire', 4.5, 3.3, [
    TIP + 'A lit campfire slowly &eheals&7 everyone who stands close to it (&eHealing Campfire&7). Put one in the middle of your camp and rest there after a fight.',
    TIP + 'Campfires also cook food without fuel.'],
    [item('minecraft:campfire')], [give('minecraft:cooked_chicken', 4)], deps=['stone'], optional=True)
p.quest('night', 'Survive the Night', 8.5, 0, [
    KEEPER + '"The nightmares are restless. Show them you are not afraid."',
    '',
    TIP + 'Defeat 5 undead monsters. Better Combat makes every weapon swing differently: try a sword and an axe and feel the difference. Press &eR&7 in combat to do a quick &edodge roll&7 (Combat Roll).'],
    [kill('#minecraft:undead', 5)], [give('minecraft:iron_ingot', 3), rxp(50)], deps=['food', 'bed'], shape='diamond')
p.quest('map', 'Where Am I?', 8.5, -2.5, [
    TIP + 'You have a &eminimap&7 in the corner. Press &eM&7 for the full world map, &eB&7 to add a waypoint, &eY&7 for the waypoint list.',
    TIP + 'Middle-click with &ePing Wheel&7 to mark a spot for your friends.',
    '',
    TIP + 'Tick the box when you found your way around.'],
    [check()], [crate('common')], deps=['night'], optional=True)
p.quest('backpack', 'Pack Your Bags', 8.5, 2.5, [
    TIP + 'A &eTraveler\'s Backpack&7 holds a lot of items, two fluid tanks and upgrades (crafting grid, furnace, magnet...).',
    TIP + 'Wear it on your back and open it with &eB&7, or place it like a chest. Sneak + right-click a placed backpack to pick it up.'],
    [item('#travelersbackpack:custom_travelers_backpack')], [rxp(60)], deps=['night'], optional=True)
p.quest('iron', 'Iron Will', 10.5, 0, [
    KEEPER + '"Iron. Now you can truly begin."',
    '',
    TIP + 'Mine iron ore and smelt it. Caves are bigger now (&eTerralith&7, &eTectonic&7): bring torches.'],
    [item('#c:ingots/iron', 12)], [crate('common', 2)], deps=['night'], shape='hexagon')
p.quest('call', '&dThe Dream Calls', 13, 0, [
    KEEPER + '"Listen. Do you hear it? The Dream is breaking apart. Nightmares leak in from below, the seas have swallowed the land, and something old waits beyond the End."',
    KEEPER + '"Gather your strength, Dreamer. Each chapter of this book is a part of the Dream that needs you."',
    '',
    TIP + 'New chapters are now open on the left. The &dThe Dream&7 chapters tell the story, the &bSide Paths&7 are optional and explain the other mods.',
    TIP + 'At the very end waits the &dDream Star&7, the trophy of Dreamcraft. Its recipe needs treasures from the whole pack, so every chapter brings you closer.'],
    [], [crate('rare'), rxp(100)], icon='questsicons:quest_portal_two', deps=['iron'], shape='star', size=1.8)

# =====================================================================================================
# Chapter 1 - The Settler
s = B.chapter('settler', '&a1. The Settler', 'questsicons:icon_house',
              ['&7A home, a farm and a full belly.'], STORY, 'rsquare')
s.quest('start', '&aA Home in the Dream', 0, 0, [
    KEEPER + '"A dreamer without a home wanders forever. Settle down."',
    '',
    TIP + 'This chapter is about your first base: farming, cooking, animals, villagers and travel.'],
    [], [rxp(20)], icon='questsicons:icon_house', deps=['prologue:call'], shape='star', size=1.4)
s.quest('hoe', 'Till the Soil', 2, -2, [
    TIP + 'Craft a hoe and plant some wheat. &eRightClickHarvest&7 is installed: right-click a ripe crop to harvest and replant it in one go.'],
    [item('#minecraft:hoes'), item('minecraft:wheat', 16)], [give('minecraft:bone_meal', 16)], deps=['start'])
s.quest('watering', 'Watering Can', 0, -2.4, [
    TIP + 'A &eWatering Can&7 (Additional Additions) makes crops grow faster. Fill it at any water, then hold right-click over your field and watch the water drops fall.'],
    [item('additionaladditions:watering_can')], [give('minecraft:bone_meal', 16)], deps=['hoe'], optional=True)
s.quest('wild', 'Wild Crops', 4, -3, [
    TIP + '&eFarmer\'s Delight&7 adds wild cabbages, tomatoes, onions and rice. Look for them in plains, beaches and swamps and plant their seeds.'],
    [item('farmersdelight:cabbage', 4), item('farmersdelight:onion', 4)], [give('farmersdelight:rice', 4)], deps=['hoe'])
s.quest('board', 'Knife and Board', 4, -1, [
    TIP + 'Place a &eCutting Board&7 and right-click it with an ingredient, then with a knife. It slices food, strips logs (giving bark) and cuts more items than a crafting table can.'],
    [item('farmersdelight:cutting_board'), item('#c:tools/knife')], [give('farmersdelight:tomato_seeds', 4)], deps=['hoe'])
s.quest('pot', 'The Cooking Pot', 6, -2, [
    TIP + 'The &eCooking Pot&7 makes hearty meals. It needs heat: place it on a campfire, a fire or a &eStove&7.',
    TIP + 'Put up to 6 ingredients in, add a bowl, and wait. Meals give long saturation and the &eComfort&7 or &eNourishment&7 effect.'],
    [item('farmersdelight:cooking_pot'), item('farmersdelight:stove')], [give('farmersdelight:dumplings', 4)], deps=['wild', 'board'], shape='hexagon')
s.quest('soil', 'Rich Soil', 8, -3, [
    TIP + 'Mix dirt, straw, rotten flesh and bone meal into &eOrganic Compost&7. It slowly turns into &eRich Soil&7, which grows crops faster and lets mushrooms spread.'],
    [item('farmersdelight:organic_compost', 4)], [give('farmersdelight:rich_soil', 8)], deps=['pot'], optional=True)
s.quest('feast', 'A Feast for Friends', 6.4, -0.5, [
    TIP + 'Feasts are placed as blocks and serve several portions. Cook one and share it.'],
    [item('farmersdelight:roast_chicken_block')], [crate('common')], deps=['pot'], optional=True)
s.quest('animals', 'Animal Husbandry', 2, 2, [
    TIP + 'Breed some animals. &eFarming for Blockheads&7 adds a &eFeeding Trough&7: fill it with food and nearby animals breed on their own.'],
    [item('farmingforblockheads:feeding_trough')], [give('minecraft:lead', 2), give('minecraft:wheat', 16)], deps=['start'])
s.quest('market', 'The Market', 4, 3, [
    TIP + 'The &eMarket&7 sells seeds, saplings, flowers and animal eggs for emeralds. A great way to get crops from biomes you have not found yet.'],
    [item('farmingforblockheads:market')], [give('minecraft:emerald', 6)], deps=['animals'])
s.quest('nest', 'Chicken Nest', 2, 4.2, [
    TIP + 'Chickens near a &eChicken Nest&7 lay their eggs right into it. No more eggs lying around in the grass.'],
    [item('farmingforblockheads:chicken_nest')], [give('minecraft:wheat_seeds', 16)], deps=['market'], optional=True)
s.quest('lasso', 'Catch Them All', 6, 3, [
    TIP + 'A &eGolden Lasso&7 (Mob Lassos) picks up a passive animal; right-click again to release it. Moving animals has never been easier.',
    TIP + 'Villagers need an &eEmerald Lasso&7 and a &eContract&7.'],
    [item('moblassos:golden_lasso')], [give('minecraft:golden_carrot', 8)], deps=['market'], optional=True)
s.quest('bucket', 'A Villager in a Bucket', 6, 1, [
    TIP + 'Right-click a villager with an empty bucket to scoop it up (&eVillager In A Bucket&7). Place it wherever you need it.',
    TIP + 'With &eTrading Post&7 you can trade with all villagers around you from one block.'],
    [item('villagerinabucket:villager_in_a_bucket'), item('tradingpost:trading_post')], [give('minecraft:emerald', 12)], deps=['animals'])
s.quest('jobs', 'New Jobs in Town', 7.6, 2.6, [
    TIP + '&eMore Villagers&7 adds new professions. Place a new workstation near a villager without a job: the &eForestry Bench&7, &eMining Bench&7, &eGardening Table&7, &eHunting Post&7, &eOceanography Table&7 and &eBlueprint Table&7 make foresters, miners, florists, hunters, oceanographers and engineers.',
    TIP + 'Bad offers? &eTrade Cycling&7 adds a button to the trading screen that rolls new offers, as long as nobody has traded with that villager yet.',
    '',
    TIP + 'Tick the box when a villager took one of the new jobs.'],
    [check('A villager took a new job')], [give('minecraft:emerald', 8)], deps=['bucket'], optional=True)
s.quest('house', 'Home Sweet Home', 0, 4, [
    TIP + 'Build a real house. The &eMacaw\'s&7 mods add furniture, roofs, windows, doors, lights, paths and bridges. Press &eR&7 on a log or plank in your inventory to see everything you can make from it.',
    '',
    TIP + 'Tick the box when your house is done - and be proud of it!'],
    [check('My house is built')], [give('minecraft:lantern', 6), crate('common')], deps=['start'], shape='square')
s.quest('waystone', 'Waystones', 10, 0, [
    KEEPER + '"The Dream is vast. Waystones are its shortcuts."',
    '',
    TIP + '&eWaystones&7 appear in villages and in the wild. Right-click one to activate it, then use it to teleport to any waystone you have activated (costs a little XP).',
    TIP + 'A &eWarp Stone&7 lets you teleport from anywhere.'],
    [item('waystones:warp_stone')], [give('waystones:return_scroll', 3)], deps=['pot', 'market'], shape='star', size=1.3)
s.quest('kitchen', 'A Proper Kitchen', 12, -1.5, [
    TIP + 'Build a &eCooking Table&7 (Cooking for Blockheads). Next to a &eFridge&7, &eSink&7, oven and counters it forms a kitchen that shows every meal you can cook with what you have.'],
    [item('cookingforblockheads:cooking_table')], [give('cookingforblockheads:recipe_book')], deps=['waystone'], optional=True)
s.quest('done', '&aSettled In', 12, 1.5, [
    KEEPER + '"Good. A full belly and a warm bed. Now - deeper."'],
    [item('minecraft:cooked_beef', 16)], [crate('rare'), rxp(150)], deps=['waystone'], shape='star', size=1.4, icon='questsicons:quest_crown')

# =====================================================================================================
# Chapter 2 - Into the Deep
d = B.chapter('deep', '&62. Into the Deep', 'questsicons:icon_pickaxe', ['&7Ores, storage and the magic of enchanting.'], STORY, 'hexagon')
d.quest('start', '&6Into the Deep', 0, 0, [
    KEEPER + '"Below every dream lies a deeper one. Dig."'],
    [item('minecraft:iron_pickaxe')], [give('minecraft:torch', 32)], icon='questsicons:icon_pickaxe', deps=['prologue:call'], shape='star', size=1.4)
d.quest('coal', 'Fuel for the Fire', 2, -2, [TIP + 'Collect coal. You will need a lot of it for furnaces and torches.'],
        [item('minecraft:coal', 32)], [give('minecraft:furnace', 2)], deps=['start'])
d.quest('copper', 'Copper Shine', 2, 2, [TIP + 'Copper is everywhere in the deep. It is used for pipes, hoppers and much more.'],
        [item('#c:ingots/copper', 24)], [rxp(40)], deps=['start'])
d.quest('gold', 'Gold Rush', 4, -2, [TIP + 'Gold is softer than iron but loved by piglins and needed for golden carrots and apples.'],
        [item('#c:ingots/gold', 12)], [give('minecraft:golden_carrot', 6)], deps=['coal'])
d.quest('necoium', 'Necoium', 4, -4, [
    TIP + '&eMythic Upgrades&7 hides &eNecoium Ore&7 deep in the overworld. Smelt the raw necoium into ingots.',
    TIP + 'Its gems grow in crystal geodes: aquamarine, citrine, topaz and peridot underground, ruby and sapphire in the Nether, ametrine and jade in the End. &e4 gems and 4 necoium ingots&7 make one mythic ingot, which upgrades netherite gear.'],
    [item('mythicupgrades:necoium_ingot', 4)], [rxp(80)], deps=['gold'], optional=True)
d.quest('deepslate', 'Deepslate', 4, 0, [TIP + 'Below Y=0 the stone turns to deepslate. Ores are richer here - and so are the monsters.'],
        [item('minecraft:cobbled_deepslate', 64)], [give('minecraft:iron_ingot', 4)], deps=['start'])
d.quest('hammer', 'Smash It', 4, 2, [
    TIP + 'A &eHammer&7 (JustHammers) mines a 3x3 area at once. Perfect for tunnels and big rooms.',
    TIP + 'Sneak to mine a single block.'],
    [item('justhammers:iron_hammer')], [give('minecraft:iron_ingot', 3)], deps=['copper'])
d.quest('diamond', '&bDiamonds!', 6, 0, [
    KEEPER + '"The Dream hides its brightest treasures in the deepest dark."',
    '',
    TIP + 'Diamonds are most common around Y=-58. Mine them with an iron pickaxe or better.'],
    [item('#c:gems/diamond', 5)], [crate('rare')], deps=['deepslate', 'gold'], shape='diamond', size=1.3)
d.quest('magnet', 'Magnetic Personality', 6, 2.5, [
    TIP + 'A &eBasic Magnet&7 (Simple Magnets) pulls nearby items to you. Right-click to switch it on and off.'],
    [item('simplemagnets:basicmagnet')], [rxp(50)], deps=['hammer'], optional=True)
d.quest('torch', 'Keep the Dark Away', 6, -2.5, [
    TIP + 'A &eMagnum Torch&7 stops hostile monsters from spawning in a large area around it. Great for your base.'],
    [item('magnumtorch:diamond_magnum_torch')], [crate('common')], deps=['diamond'], optional=True)
d.quest('storage', 'Organized Chaos', 8, 2, [
    TIP + 'Too many chests? &eTom\'s Simple Storage&7: connect your chests with &eInventory Cable&7 to an &eInventory Connector&7, then place a &eStorage Terminal&7 next to it. Now you see and search every item in all chests from one screen.',
    TIP + 'The &eCrafting Terminal&7 even crafts straight from storage.'],
    [item('toms_storage:inventory_connector'), item('toms_storage:storage_terminal')], [give('toms_storage:inventory_cable', 16)], deps=['diamond'], shape='square')
d.quest('terminal', 'Crafting Terminal', 8, 4, [
    TIP + 'Swap your Storage Terminal for a &eCrafting Terminal&7: it has a crafting grid that takes the ingredients straight out of your connected chests, and JEI\'s &e+&7 button fills it for you.'],
    [item('toms_storage:crafting_terminal')], [give('toms_storage:inventory_cable', 16)], deps=['storage'], optional=True)
d.quest('drawers', 'Drawers', 10, 3, [
    TIP + '&eStorage Drawers&7 hold huge amounts of a single item each. Click a drawer to insert, punch it to take out.',
    TIP + 'Upgrades raise their capacity. A &eDrawer Controller&7 links all drawers so you can insert into all of them at once.'],
    [item('#storagedrawers:drawers'), item('storagedrawers:controller')], [give('storagedrawers:iron_storage_upgrade', 2)], deps=['storage'], optional=True)
d.quest('enchant', 'Enchanted', 8, -1, [
    TIP + 'Build an enchanting table. Surround it with 15 bookshelves for the best enchantments.',
    TIP + '&eEasy Magic&7 is installed: the table keeps its lapis and items, and you can re-roll the offers with a click.'],
    [item('minecraft:enchanting_table'), item('minecraft:bookshelf', 15)], [give('minecraft:lapis_lazuli', 32)], deps=['diamond'])
d.quest('infuser', 'The Enchanting Infuser', 10, -2, [
    TIP + 'The &eEnchanting Infuser&7 lets you pick exactly which enchantments you want - for more XP. Place bookshelves around it (up to two layers) for stronger enchantments.',
    TIP + 'A &eGrindstone&7 can move enchantments from an item onto a book (Grind Enchantments).'],
    [item('enchantinginfuser:enchanting_infuser')], [levels(10)], deps=['enchant'], shape='hexagon')
d.quest('anvil', 'A Kinder Anvil', 10, -4, [
    TIP + 'With &eEasy Anvils&7, renaming costs nothing, there is no "Too Expensive!" limit any more and enchanted books cost half the levels. Items you leave in the anvil stay in it.',
    TIP + 'A damaged anvil? Right-click it with an iron block to repair it by one stage.'],
    [item('minecraft:anvil')], [give('minecraft:experience_bottle', 8)], deps=['infuser'], optional=True)
d.quest('xpbook', 'A Book of Experience', 12, -2, [
    TIP + 'The &eBook of Experience&7 (XP Storage) stores your XP safely. Right-click to store, sneak + right-click to take it out.'],
    [item('xp_storage:xp_book')], [rxp(200)], deps=['infuser'], optional=True)
d.quest('archeology', 'Dig Up the Past', 10, 0.5, [
    TIP + 'Brush suspicious sand and gravel to find relics. &eBetter Archeology&7 adds fossils, artifacts and an &eArcheology Table&7 that identifies artifact shards.',
    TIP + 'Look for archeologist camps and buried ruins.'],
    [item('minecraft:brush'), item('betterarcheology:archeology_table')], [crate('common')], deps=['diamond'], optional=True)
d.quest('loot', 'Loot for Everyone', 12, 1, [
    TIP + 'Dungeon chests are &eLootr&7 chests: every player gets their own loot, so nobody steals your treasure.',
    TIP + 'Find a dungeon, a mineshaft or a tavern and open its chest.'],
    [struct('#minecraft:mineshaft', 'Explore a mineshaft')], [crate('rare')], deps=['archeology', 'storage'], any_dep=True)
d.quest('done', '&6Master of the Deep', 14, 0, [KEEPER + '"The deep has given you its gifts. Use them well."'],
        [item('minecraft:diamond_pickaxe')], [crate('rare', 2), rxp(300)], deps=['loot', 'infuser'], shape='star', size=1.5, icon='questsicons:quest_crown')

# =====================================================================================================
# Chapter 3 - Sparks of Industry (Tech Reborn and friends)
t = B.chapter('industry', '&e3. Sparks of Industry', 'questsicons:icon_gear', ['&7Machines, power and automation.'], STORY, 'gear')
t.quest('start', '&eSparks of Industry', 0, 0, [
    KEEPER + '"Some dreamers dream of magic. Others dream of machines that never sleep."',
    '',
    TIP + 'This chapter teaches &eTech Reborn&7: machines run on energy (E), cables carry it, and every machine doubles or improves something you already do by hand.',
    TIP + 'Open the &eTech Reborn Manual&7 for details - every machine also explains itself in JEI.'],
    [item('#c:ingots/iron', 32)], [give('techreborn:manual')], icon='questsicons:icon_gear', deps=['deep:done'], shape='star', size=1.4)
t.quest('rubber', 'Rubber Trees', 2, -2, [
    TIP + 'Rubber trees grow in forests and swamps. Use a &eTree Tap&7 on the sap spots of a rubber log to collect &eSap&7, then smelt or extract it into rubber.'],
    [item('techreborn:treetap'), item('techreborn:sap', 8)], [give('techreborn:rubber_sapling', 4)], deps=['start'])
t.quest('refined', 'Refined Iron', 2, 0, [
    TIP + 'Smelt iron ingots once more to get &eRefined Iron&7, the backbone of every Tech Reborn machine.'],
    [item('techreborn:refined_iron_ingot', 16)], [give('minecraft:coal_block', 2)], deps=['start'])
t.quest('circuit', 'Electronic Circuits', 4, -1, [
    TIP + 'Circuits need copper cables (insulated with rubber), redstone and refined iron. Use the &eR&7 key in JEI to see every step.'],
    [item('techreborn:electronic_circuit', 4)], [give('minecraft:redstone', 32)], deps=['rubber', 'refined'])
t.quest('frame', 'Machine Frame', 4, 1, [TIP + 'Every basic machine starts with a &eBasic Machine Frame&7.'],
        [item('techreborn:basic_machine_frame', 2)], [give('techreborn:refined_iron_ingot', 8)], deps=['refined'])
t.quest('generator', 'Let There Be Power', 6, 0, [
    TIP + 'The &eGenerator&7 burns any fuel and makes energy. Put it next to a machine or connect it with &eInsulated Copper Cable&7.',
    TIP + 'Store power in a &eBattery&7 or a &eBattery Box&7.'],
    [item('techreborn:solid_fuel_generator')], [give('techreborn:insulated_copper_cable', 16)], deps=['circuit', 'frame'], shape='diamond', size=1.3)
t.quest('furnace', 'Electric Furnace', 8, -2, [TIP + 'Smelts faster than a furnace and never needs coal.'],
        [item('techreborn:electric_furnace')], [rxp(80)], deps=['generator'])
t.quest('grinder', 'Ore Doubling', 8, 0, [
    TIP + 'The &eGrinder&7 turns one ore into two dusts. Smelt the dusts and you get twice the ingots.'],
    [item('techreborn:grinder')], [give('minecraft:raw_iron', 16)], deps=['generator'], shape='hexagon')
t.quest('solar', 'Free Energy', 8, 2, [
    TIP + 'A &eSolar Panel&7 makes energy during the day without fuel. Raft players can also use the makeshift solar panels and wind turbines of the sea (see &bThe Endless Sea&7).'],
    [item('techreborn:basic_solar_panel', 2)], [give('techreborn:red_cell_battery')], deps=['generator'])
t.quest('storage', 'Battery Bank', 10, 2, [TIP + 'A &eBattery Box&7 stores lots of energy and feeds it to your machines.'],
        [item('techreborn:low_voltage_su')], [rxp(100)], deps=['solar'])
t.quest('mfe', 'Bigger Batteries', 10, 4, [
    TIP + 'The &eMFE&7 holds far more energy than a Battery Box and moves it faster (medium voltage). Its big brothers are the &eMFSU&7 and, with a Lapotronic Orb, the &eAdjustable SU&7.'],
    [item('techreborn:medium_voltage_su')], [rxp(150)], deps=['storage'], optional=True)
t.quest('alloy', 'Alloys', 10, -2, [TIP + 'The &eAlloy Smelter&7 combines metals - bronze, electrum and the advanced alloys used for better machines.'],
        [item('techreborn:alloy_smelter')], [give('techreborn:refined_iron_ingot', 16)], deps=['furnace'])
t.quest('tools', 'Power Tools', 6, 3.5, [
    TIP + 'The &eBasic Drill&7 and &eBasic Chainsaw&7 run on energy instead of durability. Charge them in a Battery Box (or wirelessly, see below) and dig through stone and trees in no time.'],
    [item('techreborn:basic_drill'), item('techreborn:basic_chainsaw')], [give('techreborn:red_cell_battery')], deps=['generator'], optional=True)
t.quest('quarry', 'Let the Machines Dig', 12, 0, [
    TIP + '&eQuarry Plus&7 (Additional Enchanted Miner) digs out a whole area for you. Place &eMarker Plus&7 blocks on the corners, put the quarry next to a marker and give it energy.',
    TIP + 'Enchant it like a pickaxe (Efficiency, Fortune, Silk Touch) with the &eEnchantment Mover&7. Modules add a pump, a void filter or bedrock removal.'],
    [item('quarryplus:quarry'), item('quarryplus:marker', 4)], [crate('rare')], deps=['grinder', 'storage'], shape='gear', size=1.4)
t.quest('quarry_reborn', 'Quarry Reborn', 13.5, 0, [
    TIP + 'The other quarry of the pack: &eQuarry Reborn&7 digs a square hole below it, one layer after the other. Its screen takes &eQuarry Tubes&7, filler blocks for the hole and upgrades.',
    TIP + 'Upgrades extend the range or add Fortune or Silk Touch.'],
    [item('quarrymod:quarry')], [give('quarrymod:drill_tube', 16)], deps=['quarry'], optional=True)
t.quest('collect', 'Item Collectors', 12, 2.5, [TIP + 'An &eItem Collector&7 picks up dropped items around it and puts them into the chest next to it.'],
        [item('itemcollectors:basic_collector')], [give('minecraft:hopper', 2)], deps=['quarry'], optional=True)
t.quest('trash', 'Take Out the Trash', 12, 4.5, [
    TIP + 'A &eTrash Can&7 deletes everything you put into it - items, liquids or energy. Connect it behind a quarry to get rid of cobblestone.'],
    [item('trashcans:item_trash_can')], [rxp(60)], deps=['collect'], optional=True)
t.quest('pipes', 'Copper Hoppers', 12, -2.5, [TIP + 'A &eCopper Hopper&7 only moves the items that match its filter slot - perfect for sorting. It oxidizes over time; wax it to keep it shiny.'],
        [item('copperhopper:copper_hopper', 4)], [give('minecraft:copper_ingot', 16)], deps=['quarry'], optional=True)
t.quest('chunk', 'Never Sleeping', 14, -1.5, [
    TIP + 'A &eChunk Loader&7 keeps the chunks around it loaded even when you are far away - your machines keep working.'],
    [item('chunkloaders:single_chunk_loader')], [crate('rare')], deps=['quarry'])
t.quest('elevator', 'Going Up', 14, 1.5, [
    TIP + 'Stack &eElevator Controllers&7 (Moving Elevators) on different floors. Stand on one and use its screen to ride smoothly to another floor.'],
    [item('movingelevators:elevator_block', 2)], [rxp(100)], deps=['quarry'], optional=True)
t.quest('tesseract', 'Tesseract', 14, 3.5, [
    TIP + 'Two &eTesseracts&7 on the same channel share items, fluids and energy over any distance, even across dimensions. Set the channel in its screen and make it private or public.'],
    [item('tesseract:tesseract', 2)], [rxp(150)], deps=['elevator'], optional=True)
t.quest('charger', 'Wireless Charging', 16, 1.5, [TIP + 'A &eWireless Player Charger&7 refills energy items in your inventory while you are near it.'],
        [item('wirelesschargers:basic_wireless_player_charger')], [rxp(120)], deps=['elevator', 'chunk'], any_dep=True, optional=True)
t.quest('vector', 'Plates of Power', 16, 3.5, [
    TIP + '&eDark Utilities&7 adds plates for every farm: &eVector Plates&7 push mobs and items in a direction, &eDamage Plates&7 hurt mobs standing on them and &eFilters&7 decide who may pass.',
    TIP + 'Combine them with an Item Collector for a mob farm.'],
    [item('darkutils:vector_plate', 4)], [give('darkutils:blank_plate', 8)], deps=['tesseract', 'charger'], any_dep=True, optional=True)
t.quest('done', '&eThe Dream Never Sleeps', 16, -1.5, [KEEPER + '"Your machines hum through the night. The Dream grows stronger."'],
        [item('techreborn:industrial_centrifuge')], [crate('epic'), rxp(400)], deps=['chunk'], shape='star', size=1.5, icon='questsicons:quest_crown')
# --- the high-tech line up to the Lapotronic Energy Orb (an ingredient of the Dream Star)
t.quest('compressor', 'Squeeze and Extract', 6, -4, [
    TIP + 'The &eCompressor&7 presses plates and dense materials, the &eExtractor&7 turns sap into rubber (three times as much as smelting). Most advanced parts start in one of them.'],
    [item('techreborn:compressor'), item('techreborn:extractor')], [give('techreborn:refined_iron_ingot', 8)], deps=['generator'])
t.quest('advanced_circuit', 'Advanced Circuits', 8, -4, [
    TIP + 'An &eAdvanced Circuit&7 is an electronic circuit with glowstone, lapis and redstone around it. Almost every high-tier machine needs them.'],
    [item('techreborn:advanced_circuit', 4)], [give('minecraft:glowstone_dust', 16)], deps=['compressor'])
t.quest('industrial_grinder', 'Industrial Grinder', 8, -6, [
    TIP + 'Industrial machines are &emultiblocks&7: they need a frame of &eMachine Casings&7 around them. Open the machine and press the &ehologram&7 button - it shows where every casing goes.',
    TIP + 'The &eIndustrial Grinder&7 needs water and gets even more out of each ore than the grinder, plus rare by-products.'],
    [item('techreborn:industrial_grinder')], [give('techreborn:basic_machine_casing', 8)], deps=['advanced_circuit'], shape='hexagon')
t.quest('blast', 'Industrial Blast Furnace', 10, -6, [
    TIP + 'Hotter than any furnace: the &eIndustrial Blast Furnace&7 melts &esteel&7, titanium and iridium. It is a multiblock too - heating coils in its casing raise the heat.'],
    [item('techreborn:industrial_blast_furnace')], [give('techreborn:cupronickel_heating_coil', 4)], deps=['industrial_grinder'], shape='hexagon')
t.quest('assembler', 'The Assembling Machine', 10, -4, [
    TIP + 'The &eAssembling Machine&7 joins two parts into one: industrial circuits, energy crystals, data chips and more.'],
    [item('techreborn:assembly_machine')], [rxp(200)], deps=['advanced_circuit'])
t.quest('chemical', 'Chemical Reactor', 12, -4, [
    TIP + 'The &eChemical Reactor&7 mixes elements. Feed it 32 redstone and a diamond to grow a &eSynthetic Redstone Crystal&7.'],
    [item('techreborn:chemical_reactor'), item('techreborn:synthetic_redstone_crystal', 2)], [give('minecraft:redstone_block', 4)], deps=['assembler'])
t.quest('energy_crystal', 'Energy Crystal', 14, -4, [
    TIP + 'In the Assembling Machine, 2 synthetic redstone crystals and a silicon plate become an &eEnergy Crystal&7, a battery with a lot of room.'],
    [item('techreborn:energy_crystal')], [rxp(250)], deps=['chemical'])
t.quest('iridium', 'Iridium', 12, -6, [
    TIP + '&eIridium Ore&7 is rare and only found deep below Y=0. Smelt the raw iridium in the blast furnace, press the ingots into &eIridium Plates&7 and combine them with advanced alloy plates and diamond dust into an &eIridium Alloy Ingot&7.'],
    [item('techreborn:raw_iridium', 4)], [crate('rare')], deps=['blast'], shape='diamond')
t.quest('implosion', 'Implosion Compressor', 14, -6, [
    TIP + 'Only an explosion is strong enough: the &eImplosion Compressor&7 (a multiblock) squeezes an iridium alloy ingot with 8 TNT into an &eIridium Alloy Plate&7.'],
    [item('techreborn:implosion_compressor'), item('techreborn:iridium_alloy_plate')], [give('minecraft:tnt', 16)], deps=['iridium'], shape='hexagon')
t.quest('industrial_circuit', 'Industrial Circuits', 16, -4, [
    TIP + 'An advanced circuit and a &eplatinum plate&7 make an &eIndustrial Circuit&7 in the Assembling Machine. Platinum comes from sheldonite ore in the End, or as a by-product when the Industrial Grinder grinds iridium ore.'],
    [item('techreborn:industrial_circuit', 2)], [rxp(250)], deps=['energy_crystal'])
t.quest('lapotron', 'Lapotron Crystal', 18, -4, [
    TIP + 'Six &eLazurite Plates&7, two industrial circuits and an energy crystal make a &eLapotron Crystal&7. Lazurite dust comes from lapis: spin it in the Industrial Centrifuge, or grind lapis ore in the Industrial Grinder.'],
    [item('techreborn:lapotron_crystal')], [crate('epic')], deps=['industrial_circuit'], shape='diamond')
t.quest('orb', '&dLapotronic Energy Orb', 19.5, -5.5, [
    KEEPER + '"A whole storm of energy, caught in a sphere."',
    '',
    TIP + 'Surround an &eIridium Alloy Plate&7 with &e8 Lapotron Crystals&7. The &eLapotronic Energy Orb&7 stores an enormous amount of energy and is the heart of the best Tech Reborn gear.',
    '',
    STAR + 'the orb is one of its ingredients. Keep one for the epilogue.'],
    [item('techreborn:lapotronic_orb')], [crate('legendary'), rxp(500)], deps=['lapotron', 'implosion'], shape='star', size=1.5)

# =====================================================================================================
# Chapter 4 - Paths of Power (RPG series)
m = B.chapter('power', '&54. Paths of Power', 'questsicons:icon_magic', ['&7Wizard, paladin, archer or rogue?'], STORY, 'octagon')
m.quest('start', '&5Paths of Power', 0, 0, [
    KEEPER + '"Every dreamer carries a power. Which one is yours?"',
    '',
    TIP + 'The RPG series adds four classes. Each has its own &eworkbench&7, weapons, armor and &espells&7. Weapons show their spells in their tooltip; the spells appear on a &espell hotbar&7 above your item bar.',
    TIP + 'You may follow one path or all of them.'],
    [check('Show me the paths')], [rxp(50)], icon='questsicons:icon_magic', deps=['deep:diamond'], shape='star', size=1.5)
m.quest('binding', 'The Spell Binding Table', 0, 2.6, [
    TIP + 'At the &eSpell Binding Table&7 you bind &eSpell Scrolls&7 to a &eSpell Book&7 for levels and lapis. Hold the book in your offhand and its spells join your weapon\'s spells.',
    TIP + 'Spell books are also found in loot chests.'],
    [item('spell_engine:spell_binding')], [give('minecraft:lapis_lazuli', 32), levels(5)], deps=['start'], shape='square')
m.quest('spellbook', 'A Book of Spells', 1.5, 4.2, [
    TIP + 'Craft or find a &eSpell Book&7, bind a scroll to it and hold it in your offhand: its spells join the spells of your weapon. Every class has its own books and scrolls.'],
    [item('#spell_engine:spell_books')], [give('minecraft:lapis_lazuli', 16), levels(5)], deps=['binding'], optional=True)
# Wizard
m.quest('wizard', '&9Path of the Wizard', 3, -3, [
    TIP + 'Wizards cast &eArcane&7, &eFire&7 and &eFrost&7 spells from wands and staves. Hold right-click to cast; the spell hotbar shows what each key does.',
    TIP + 'Wizard towers in the world sell spell books.'],
    [item('wizards:staff_arcane')], [give('wizards:wand_arcane')], deps=['start'], icon='wizards:staff_arcane')
m.quest('wizard_robe', 'Robes of Power', 5, -4, [TIP + 'Wizard robes boost spell power of their school. Wear a full set.'],
        [item('wizards:arcane_robe_head'), item('wizards:arcane_robe_chest'), item('wizards:arcane_robe_legs'), item('wizards:arcane_robe_feet')],
        [give('minecraft:amethyst_shard', 16)], deps=['wizard'], optional=True)
m.quest('wizard_school', 'Fire and Frost', 5, -2.4, [TIP + 'Craft a staff of a second school. Fire burns, frost slows - mix them as you like.'],
        [item('wizards:staff_fire'), item('wizards:staff_frost')], [crate('rare')], deps=['wizard'], optional=True)
# Paladin
m.quest('paladin', '&ePath of the Paladin', 3, -1, [
    TIP + 'Paladins fight with claymores, maces and great hammers and protect allies with &eholy&7 spells. Priests heal with holy wands and staves.',
    TIP + 'Craft gear at the &eMonk Workbench&7.'],
    [item('paladins:monk_workbench'), item('paladins:iron_claymore')], [give('minecraft:golden_apple')], deps=['start'], icon='paladins:iron_claymore')
m.quest('paladin_armor', 'Crusader Plate', 5, -0.6, [TIP + 'The &eCrusader armor&7 is heavy but blessed.'],
        [item('paladins:crusader_armor_chest')], [give('paladins:iron_kite_shield')], deps=['paladin'], optional=True)
# Archer
m.quest('archer', '&aPath of the Archer', 3, 1, [
    TIP + 'Archers use longbows, shortbows, crossbows and spears. Bow spells like &eBarrage&7 and &eEntangling Roots&7 trigger while you draw.',
    TIP + 'The &eAuto-Fire Hook&7 makes crossbows reload by themselves.'],
    [item('archers:archers_workbench'), item('archers:composite_longbow')], [give('minecraft:arrow', 64)], deps=['start'], icon='archers:composite_longbow')
m.quest('archer_armor', 'Ranger Gear', 5, 1.4, [TIP + 'Ranger armor raises your ranged damage.'],
        [item('archers:archer_armor_chest')], [give('archers:auto_fire_hook')], deps=['archer'], optional=True)
# Rogue
m.quest('rogue', '&cPath of the Rogue', 3, 3, [
    TIP + 'Rogues strike fast with daggers and sickles and vanish into the shadows; warriors smash with double axes and glaives.',
    TIP + 'Craft gear at the &eArms Workbench&7.'],
    [item('rogues:arms_workbench'), item('rogues:iron_dagger')], [give('minecraft:iron_ingot', 6)], deps=['start'], icon='rogues:iron_dagger')
m.quest('rogue_armor', 'Assassin or Berserker', 5, 3.4, [TIP + 'Assassin armor makes you quicker, berserker armor makes you hit harder.'],
        [item('rogues:assassin_armor_chest')], [give('rogues:iron_sickle')], deps=['rogue'], optional=True)
# Netherite staves (any one of them is an ingredient of the Dream Star)
NSTAFF = [TIP + 'Put the staff into a &esmithing table&7 with a &eNetherite Upgrade Template&7 and a netherite ingot. Netherite staves have more spell power than the plain ones.',
          '', STAR + 'any netherite staff of a wizard or the Netherite Holy Staff of a priest is one of its ingredients.']
m.quest('netherite', 'Netherite Mastery', 7, -3, [
    TIP + 'The strongest magic weapons are made of netherite. You need a &eNetherite Upgrade Template&7: bastions in the Nether hide them, and a template, 7 diamonds and a netherrack make two.',
    TIP + 'Then upgrade a staff: the quests around this one.'],
    [item('minecraft:netherite_upgrade_smithing_template')], [give('minecraft:diamond', 4)], deps=['wizard_school', 'paladin_armor'], any_dep=True, shape='diamond')
m.quest('staff_arcane', 'Netherite Arcane Staff', 9, -4.4, ['&7An &eArcane Staff&7 upgraded with netherite.', ''] + NSTAFF,
        [item('wizards:staff_netherite_arcane')], [crate('rare')], deps=['netherite'], optional=True)
m.quest('staff_fire', 'Netherite Fire Staff', 9, -3.28, ['&7A &eFire Staff&7 upgraded with netherite.', ''] + NSTAFF,
        [item('wizards:staff_netherite_fire')], [crate('rare')], deps=['netherite'], optional=True)
m.quest('staff_frost', 'Netherite Frost Staff', 9, -2.16, ['&7A &eFrost Staff&7 upgraded with netherite.', ''] + NSTAFF,
        [item('wizards:staff_netherite_frost')], [crate('rare')], deps=['netherite'], optional=True)
m.quest('staff_holy', 'Netherite Holy Staff', 9, -1.04, ['&7A &eDiamond Holy Staff&7 (iron and diamonds) upgraded with netherite.', ''] + NSTAFF,
        [item('paladins:netherite_holy_staff')], [crate('rare')], deps=['netherite'], optional=True)
# Jewelry, runes, relics, legendary gear
m.quest('runes', 'Runes', 7, 0.6, [
    TIP + 'Many spells cost &erunes&7. Craft them cheaply at the &eRune Crafting Altar&7 and keep them in a &eRune Pouch&7 (equipped in an accessory slot) so spells take them automatically.'],
    [item('runes:crafting_altar'), item('runes:small_rune_pouch')], [give('runes:arcane_stone', 16)], deps=['wizard', 'paladin', 'archer', 'rogue'], any_dep=True, hide_lines=True)
m.quest('jewels', 'Gems and Jewelry', 7, 2.6, [
    TIP + 'Find gems like &cRuby&7, &9Sapphire&7 and &aJade&7 (Jewelry). Cut them at the &eJeweler\'s Kit&7, then add a &eSocket Mount&7 to armor at an anvil and insert the cut gem.',
    TIP + 'Rings and necklaces go into your accessory slots for extra spell power, health or speed.'],
    [item('jewelry:jewelers_kit'), item('jewelry:ruby')], [give('jewelry:gold_ring')], deps=['wizard', 'paladin', 'archer', 'rogue'], any_dep=True, hide_lines=True)
m.quest('relic', 'Relics', 9, 3.6, [
    TIP + '&eRelics&7 (RPG Series) are trinkets you find in loot chests: lesser, medium, greater and superior relics. Some give a passive bonus, others an ability you use from the spell hotbar.',
    TIP + 'Wear them in your accessory slots.'],
    [item('#relics_rpgs:all')], [crate('rare')], deps=['jewels'], optional=True)
m.quest('legend', 'Legendary Arsenal', 11, -1, [
    TIP + 'Unique weapons of the &eArsenal&7 are only found in the world - in dungeon chests and on bosses. Each one has its own spell.',
    TIP + 'Find or claim one of them.'],
    [item('arsenal:unique_claymore_1')], [crate('epic')], deps=['runes', 'jewels'], optional=True)
m.quest('armory', 'Epic Armor', 7, -4.4, [
    TIP + '&eArmory&7 (RPG Series) turns netherite class armor into epic sets at a smithing table: an &eEpic Armor Upgrade&7 template plus a &eLost&7 or &eForgotten Crystal&7 of your class. Templates and crystals are rare loot; diamonds copy a template.'],
    [item('armory_rpgs:epic_armor_upgrade')], [crate('epic')], deps=['netherite'], optional=True)
m.quest('done', '&5Awakened Power', 13.6, 0.6, [KEEPER + '"Your power is awake. Now carry it into the fire."'],
        [xp(20)], [crate('epic'), choice(('jewelry:ruby_ring', 1), ('jewelry:sapphire_ring', 1), ('jewelry:jade_ring', 1), ('jewelry:citrine_ring', 1))],
        deps=['runes', 'jewels'], shape='star', size=1.5, icon='questsicons:quest_crown')

# =====================================================================================================
# Chapter 5 - Through the Fire (Nether)
n = B.chapter('nether', '&c5. Through the Fire', 'questsicons:quest_portal_two', ['&7The burning layer of the Dream.'], STORY, 'pentagon')
n.quest('start', '&cThrough the Fire', 0, 0, [
    KEEPER + '"Beneath the Dream burns its fever. Light a portal and step through."',
    '',
    TIP + 'Build a nether portal (obsidian frame, 4x5) and light it with flint and steel.'],
    [item('minecraft:obsidian', 10), item('minecraft:flint_and_steel')], [give('minecraft:golden_carrot', 8)], deps=['deep:diamond'], shape='star', size=1.4, icon='questsicons:quest_portal_two')
n.quest('enter', 'Into the Nether', 2, 0, [
    TIP + '&eBetterNether&7 fills the Nether with new biomes, plants, mobs and ruined cities. Bring a bed? Better not - it explodes here.'],
    [dim('minecraft:the_nether', 'Enter the Nether')], [rxp(100)], deps=['start'])
n.quest('quartz', 'Quartz and Gold', 4, -2, [TIP + 'Nether quartz and nether gold ore are everywhere. Piglins love gold - wear at least one golden armor piece.'],
        [item('minecraft:quartz', 32), item('minecraft:golden_helmet')], [give('minecraft:gold_ingot', 8)], deps=['enter'])
n.quest('ruby', 'Nether Rubies', 4, -3.6, [
    TIP + '&eBetterNether&7 hides &cNether Ruby Ore&7 in the Nether. Rubies make BetterNether tools and armor, and the &eRuby Fire Staff&7 and &eRuby Holy Staff&7 of the RPG classes. &eCincinnasite&7 makes tools, lanterns, bars and the Cincinnasite Forge.'],
    [item('betternether:nether_ruby', 4)], [rxp(120)], deps=['quartz'], optional=True)
n.quest('fortress', 'The Fortress', 4, 0, [TIP + 'Find a nether fortress. Blazes guard it - their rods power brewing stands and eyes of ender.'],
        [struct('minecraft:fortress', 'Find a nether fortress'), item('minecraft:blaze_rod', 8)], [crate('rare')], deps=['enter'], shape='hexagon')
n.quest('brewing', 'Potion Master', 6, -2, [TIP + 'Brew a potion. Nether wart grows in fortresses.'],
        [item('minecraft:brewing_stand'), item('minecraft:nether_wart', 8)], [give('minecraft:glass_bottle', 16)], deps=['fortress'])
n.quest('naga', 'Strange Locals', 6, -3.6, [
    TIP + 'BetterNether brings its own creatures: &eNagas&7 that shoot at you from afar, &eJungle Skeletons&7 in the nether jungles, floating &eHydrogen Jellyfish&7 and even &eFlying Pigs&7.',
    TIP + 'Defeat a naga.'],
    [kill('betternether:naga')], [crate('rare')], deps=['ruby', 'brewing'], any_dep=True, optional=True)
n.quest('bastion', 'Bastion Remnant', 4, 2, [TIP + 'Bastions are full of piglins and treasure. Careful with the brutes. Their chests also hold the &eNetherite Upgrade Template&7.'],
        [struct('minecraft:bastion_remnant', 'Find a bastion')], [crate('rare')], deps=['enter'])
n.quest('city', 'A City in the Fire', 4, 3.6, [
    TIP + 'Huge, crumbling &eNether Cities&7 (BetterNether) and the &eMega Fortress&7 of Moog\'s Nether Structures are worth a long walk. Lootr keeps their chests fresh for every player.'],
    [struct('betternether:nether_city', 'Find a nether city')], [crate('epic')], deps=['bastion'], optional=True)
n.quest('debris', 'Ancient Debris', 6, 2, [TIP + 'Ancient debris hides near Y=15. Beds and TNT help - or a lot of patience.'],
        [item('minecraft:ancient_debris', 4)], [give('minecraft:gold_ingot', 16)], deps=['bastion', 'fortress'])
n.quest('netherite', '&8Netherite', 8, 1, [TIP + 'Combine four netherite scrap and four gold into a netherite ingot. Upgrade diamond gear at a smithing table.'],
        [item('minecraft:netherite_ingot')], [give('minecraft:netherite_upgrade_smithing_template')], deps=['debris'], shape='diamond', size=1.3)
n.quest('advanced', 'Advanced Netherite', 10, 1, [
    TIP + '&eAdvanced Netherite&7 upgrades netherite tools and armor further with iron, gold, emerald or diamond: each tier gives more durability and special bonuses.'],
    [item('advancednetherite:netherite_diamond_ingot')], [crate('epic')], deps=['netherite'], optional=True)
n.quest('pup', 'A Friend in the Flames', 10, -2, [
    TIP + 'In some nether fortresses lives the &6Ember Pup&7, one of the rare pets of &eTamacraft&7. It swims through lava and keeps you from burning. See the &dTamacraft&7 side path.',
    '',
    TIP + 'Spot an Ember Pup.'],
    [observe('tamacraft:ember_pup', 40, entity=True, title='Spot an Ember Pup')], [give('tamacraft:ember_jerky', 4)], deps=['wither_skull'], optional=True)
n.quest('wither_skull', 'Skulls of the Wither', 8, -1, [TIP + 'Wither skeletons in fortresses sometimes drop their skulls. Three of them... you know.'],
        [item('minecraft:wither_skeleton_skull', 3)], [crate('rare')], deps=['fortress'])
n.quest('done', '&cForged in Fire', 12, 0, [KEEPER + '"The fever cools. Now find the place where the Dream ends."'],
        [item('minecraft:ender_pearl', 12)], [crate('epic'), rxp(400)], deps=['wither_skull', 'netherite'], shape='star', size=1.5, icon='questsicons:quest_crown')

# =====================================================================================================
# Chapter 7 - The End of the Dream
e = B.chapter('end', '&57. The End of the Dream', 'questsicons:end_lock', ['&7Find the stronghold. Face the dragon.'], STORY, 'circle')
e.quest('eyes', '&5Eyes of Ender', 0, 0, [
    KEEPER + '"The dragon is the last nightmare. It holds the Dream captive at the edge of the world."',
    '',
    TIP + 'Craft eyes of ender from pearls and blaze powder. Throw one - it flies towards the nearest stronghold.'],
    [item('minecraft:ender_eye', 12)], [give('minecraft:ender_pearl', 4)], deps=['nether:done'], shape='star', size=1.4, icon='minecraft:ender_eye')
e.quest('stronghold', 'The Stronghold', 2, 0, [TIP + 'Follow the eyes and find the stronghold below ground.'],
        [struct('minecraft:stronghold', 'Find the stronghold')], [crate('rare')], deps=['eyes'])
e.quest('portal', 'The End Portal', 4, 0, [TIP + 'Fill the frame with eyes of ender and jump in. Bring blocks, food, a bow and slow-falling if you can.'],
        [dim('minecraft:the_end', 'Enter the End')], [rxp(200)], deps=['stronghold'], icon='questsicons:quest_portal_five')
e.quest('dragon', '&5The Last Nightmare', 6, 0, [
    KEEPER + '"Now, Dreamer!"',
    '',
    TIP + 'Destroy the healing crystals on the pillars, then defeat the &5Ender Dragon&7.'],
    [kill('minecraft:ender_dragon')], [crate('legendary'), levels(30)], deps=['portal'], shape='heart', size=2.0, icon='minecraft:dragon_head')
e.quest('egg', 'The Dragon Egg', 6, -2.5, [
    TIP + 'After the first fight the &5Dragon Egg&7 sits on top of the exit portal. It teleports away when you hit it, so push it with a piston: then it drops as an item.',
    '',
    STAR + 'a Dragon Egg or a Dragon Head is one of its ingredients. There is only one egg per world, so on a server a friend may want a head instead.'],
    [item('minecraft:dragon_egg')], [crate('epic')], deps=['dragon'], optional=True, icon='minecraft:dragon_egg')
e.quest('outer', 'The Outer Islands', 8, -2, [
    TIP + 'Throw a pearl into the gateway that appears. &eBetterEnd&7 turns the outer End into a whole world of biomes, from glowing forests to sulphuric lakes.'],
    [biome('betterend:foggy_mushroomland', 'Visit the Foggy Mushroomland')], [crate('rare')], deps=['dragon'])
e.quest('smelter', 'Metals of the End', 10, -2, [
    TIP + 'Build an &eEnd Stone Smelter&7 (BetterEnd). It alloys iron and ender dust into &eTerminite&7, and terminite with netherite into &eAeternium&7, the toughest metal of the End.',
    TIP + 'Thallasium ore lies in the End stone too.'],
    [item('betterend:end_stone_smelter'), item('betterend:terminite_ingot', 4)], [crate('rare')], deps=['outer'])
e.quest('aeternium', 'Aeternium', 12, -3.6, [
    TIP + 'An &eAeternium Ingot&7 makes the best tools, hammers and armor of BetterEnd. Many RPG Series weapons also take it as repair material.'],
    [item('betterend:aeternium_ingot')], [crate('epic')], deps=['smelter'], optional=True)
e.quest('eternal', 'On Eternal Paths', 12, -2, [
    TIP + 'Somewhere in the End stands an &eEternal Portal&7, a ruin of runed flavolite. Light it with an &eEternal Crystal&7 (made in an &eInfusion Ritual&7) and it takes you between worlds.',
    '',
    TIP + 'Find one of these ancient portals.'],
    [adv('betterend:portal', 'Discover an eternal portal', icon='betterend:eternal_crystal')], [crate('epic')], deps=['smelter'], optional=True)
e.quest('city', 'End City', 8, 2, [TIP + 'End cities float in the outer End. Shulkers guard elytra and great loot.'],
        [struct('minecraft:end_city', 'Find an End city'), item('minecraft:shulker_shell', 4)], [crate('epic')], deps=['dragon'])
e.quest('elytra', '&bWings', 10, 2, [TIP + 'Find an elytra in an End ship. Fireworks give you a boost while flying.'],
        [item('minecraft:elytra')], [give('minecraft:firework_rocket', 32)], deps=['city'], shape='diamond')
e.quest('head', 'A Dragon\'s Head', 10, 3.6, [
    TIP + 'The bow of every &eEnd ship&7 carries a &5Dragon Head&7. Wear it, hang it on a wall, or power it with redstone and watch its jaw move.',
    '',
    STAR + 'a Dragon Head or the Dragon Egg is one of its ingredients. Every End ship has a head, so there is one for everybody.'],
    [item('minecraft:dragon_head')], [crate('rare')], deps=['city'], optional=True, icon='minecraft:dragon_head')
e.quest('shulker', 'Boxes in Boxes', 8, 3.6, [
    TIP + 'Two shulker shells and a chest make a &eShulker Box&7 that keeps its contents when you break it. With &eEasy Shulker Boxes&7 you can look into one and take items out right from your inventory.'],
    [item('minecraft:shulker_box')], [give('minecraft:shulker_shell', 2)], deps=['city'], optional=True)
e.quest('kitten', 'A Kitten from the Void', 6, 3.6, [
    TIP + 'In some End cities waits the &5Void Kitten&7, one of the rarest pets of &eTamacraft&7: it pulls dropped items into its backpack. See the &dTamacraft&7 side path.',
    '',
    TIP + 'Spot a Void Kitten.'],
    [observe('tamacraft:void_kitten', 40, entity=True, title='Spot a Void Kitten')], [give('tamacraft:fish_crackers', 4)], deps=['city'], optional=True)
e.quest('done', '&5The Dream Is Free', 12, 0, [
    KEEPER + '"You did it. The dragon is gone and the Dream breathes again. But dreams never truly end..."',
    '',
    TIP + 'Continue with the &dEpilogue&7 for the hardest challenges and the Dream Star.'],
    [], [crate('legendary'), rxp(1000)], deps=['outer', 'elytra'], shape='star', size=2.0, icon='questsicons:quest_crown')

# =====================================================================================================
# Epilogue - Lucid Dreamer, and the Dream Star
x = B.chapter('epilogue', '&6Epilogue: Lucid Dreamer', 'questsicons:icon_trophy', ['&7For those who never want to wake up.'], STORY, 'star')
x.quest('start', '&6Lucid Dreamer', 0, 0, [KEEPER + '"You can shape the Dream now. Show me how strong you have become."'],
        [], [rxp(100)], deps=['end:done'], shape='star', size=1.5, icon='questsicons:icon_trophy')
x.quest('wither', 'The Wither', 2, -2, [
    TIP + 'Summon and defeat the Wither. Fight it underground so it cannot fly away.',
    '',
    STAR + 'its &eNether Star&7 is one of the ingredients. Build your beacon with this one and fight it again later, or keep it.'],
    [kill('minecraft:wither')], [crate('epic')], deps=['start'], shape='heart', icon='minecraft:nether_star')
x.quest('beacon', 'A Beacon in the Dream', 4, -2, [TIP + 'Build a beacon on a pyramid of mineral blocks.'],
        [item('minecraft:beacon')], [give('minecraft:diamond_block', 2)], deps=['wither'])
x.quest('mythic', 'Mythic Upgrades', 2, 2, [
    TIP + '&eMythic Upgrades&7 grows crystal geodes underground (aquamarine, citrine, topaz, peridot), in the Nether (ruby, sapphire) and in the End (ametrine, jade). Four gems and four necoium ingots make a mythic ingot, and its smithing template upgrades netherite gear with powerful effects.'],
    [item('mythicupgrades:ametrine_ingot')], [crate('epic')], deps=['start'], optional=True)
x.quest('warden', 'The Warden', 4, 2, [TIP + 'Defeat a warden in the deep dark. Sneak, it is blind but hears everything.'],
        [kill('minecraft:warden')], [crate('legendary')], deps=['start'], shape='heart', optional=True)
x.quest('crate', 'Crate Collector', 6, 0, [TIP + 'Open a &6Legendary Crate&7. You earned it.'],
        [item('questsicons:legendary_crate', 1, consume=True)], [crate('legendary')], deps=['beacon'], optional=True)
x.quest('master', '&6Master of Dreams', 8, 0, [
    KEEPER + '"You are no longer a dreamer. You are the Dream itself. Thank you for playing Dreamcraft."',
    '',
    TIP + 'Your reward includes &etwo Quest Crowns&7. The &dDream Star&7 uses one of them up, so the other one stays with you.'],
    [check('Finish the journey')], [crate('legendary', 2), give('questsicons:quest_crown'), give('questsicons:quest_crown')],
    deps=['beacon', 'wither'], shape='star', size=2.2, icon='questsicons:quest_crown')
# --- The Dream Star: like the ATM Star, one quest per ingredient around the craft
x.quest('dream', '&dThe Dream Star', 10.5, 0, [
    KEEPER + '"One dream is left, Dreamer. Gather a treasure from every corner of the Dream and bind them into a star."',
    '',
    TIP + 'The &dDream Star&7 is the trophy of Dreamcraft. It shines, cannot burn and never despawns. Its recipe uses eight treasures from the whole pack:',
    TIP + '&e2 Ametrine Ingots&7, a &eQuest Crown&7, a &enetherite staff&7, a &eNether Star&7, a &eLapotronic Energy Orb&7, a &eTamacraft Heart&7, a &eDragon Egg or Dragon Head&7 and the &eHeart of the Tide&7.',
    TIP + 'The quests around the star tell you where each one comes from. Press &eR&7 on the Dream Star in JEI to see the recipe.'],
    [], [rxp(500)], deps=['master'], shape='star', size=1.6, icon='questsicons:dream_star')
STAR_X, STAR_Y, RING = 15, 0, 2.6
def ring(deg):
    """A place on the ring around the star; the ring leaves the line to the pedestal free (angles in degrees, 0 = right)."""
    import math
    a = math.radians(deg)
    return round(STAR_X + RING * math.cos(a), 2), round(STAR_Y + RING * math.sin(a), 2)
x.quest('star_crown', 'The Quest Crown', *ring(-67.5), [
    TIP + 'The &eQuest Crown&7 has no recipe. It is your reward for &6Master of Dreams&7, which gave you two: one for the star, one to keep.'],
    [item('questsicons:quest_crown')], [rxp(100)], deps=['dream'], hide_lines=True, hide=False, icon='questsicons:quest_crown')
x.quest('star_ametrine', 'Ametrine Ingots', *ring(-112.5), [
    TIP + '&eAmetrine&7 (Mythic Upgrades) is the gem of the End: its ore and its crystal geodes hide in the End stone. Mine the ore for Ametrine.',
    TIP + '&eNecoium Ore&7 lies deep in the overworld; smelt the raw necoium. &e4 Ametrine + 4 Necoium Ingots&7 make one Ametrine Ingot. You need &etwo&7.'],
    [item('mythicupgrades:ametrine_ingot', 2)], [rxp(200)], deps=['dream'], hide_lines=True)
x.quest('star_orb', 'Lapotronic Energy Orb', *ring(-22.5), [
    TIP + 'The top of Tech Reborn: 8 Lapotron Crystals around an Iridium Alloy Plate. Chapter &e3. Sparks of Industry&7 walks you there step by step.'],
    [item('techreborn:lapotronic_orb')], [rxp(200)], deps=['dream'], hide_lines=True)
x.quest('star_tide', 'Heart of the Tide', *ring(22.5), [
    TIP + 'The &bLeviathan&7 at the bottom of the Endless Sea guards it. Follow the story of &e6. The Endless Sea&7 to the Abyssal Sanctum and win it back.',
    TIP + 'Placed as a block it gives every swimmer nearby Conduit Power - but the star needs it in your hand.'],
    [item('raft:heart_of_the_tide')], [rxp(200)], deps=['dream'], hide_lines=True)
x.quest('star_dragon', 'A Dragon\'s Treasure', *ring(67.5), [
    TIP + 'A &eDragon Egg&7 or a &eDragon Head&7. This quest completes when you have finished &eThe Dragon Egg&7 or &eA Dragon\'s Head&7 in chapter 7: the egg waits on the exit portal after the first dragon fight, a head hangs on every End ship.'],
    [], [rxp(200)], deps=['end:egg', 'end:head'], any_dep=True, icon='minecraft:dragon_egg')
x.quest('star_heart', 'Tamacraft Heart', *ring(112.5), [
    TIP + 'Five red dye around an amethyst shard. It tames the rare pets of the &dTamacraft&7 side path - craft a fresh one for the star.'],
    [item('tamacraft:tamacraft_heart')], [rxp(100)], deps=['dream'], hide_lines=True)
x.quest('star_staff', 'A Netherite Staff', *ring(-157.5), [
    TIP + 'A &eNetherite Arcane, Fire or Frost Staff&7 of a wizard or the &eNetherite Holy Staff&7 of a priest. This quest completes when you have finished one of the netherite staff quests in &e4. Paths of Power&7.'],
    [], [rxp(200)], deps=['power:staff_arcane', 'power:staff_fire', 'power:staff_frost', 'power:staff_holy'], any_dep=True, icon='wizards:staff_netherite_arcane')
x.quest('star_nether', 'Nether Star', *ring(157.5), [
    TIP + 'Summon the &eWither&7 once more and defeat it. Its star is the bright centre of the Dream Star.'],
    [item('minecraft:nether_star')], [rxp(200)], deps=['dream'], hide_lines=True)
x.quest('star', '&d✦ Living the Dream ✦', STAR_X, STAR_Y, [
    KEEPER + '"Eight treasures, one star. This is what your journey looks like, Dreamer."',
    '',
    TIP + 'Craft the &dDream Star&7: Ametrine, Crown, Ametrine on top, staff, Nether Star and Lapotronic Orb in the middle, Tamacraft Heart, Dragon Egg or Head and Heart of the Tide at the bottom.',
    TIP + 'It unlocks the challenge &5Living the Dream&7.'],
    [item('questsicons:dream_star')], [crate('legendary'), levels(30)],
    deps=['star_crown', 'star_ametrine', 'star_orb', 'star_tide', 'star_dragon', 'star_heart', 'star_staff', 'star_nether'],
    shape='star', size=2.4, icon='questsicons:dream_star')
x.quest('pedestal', 'A Place of Honour', 19, 0, [
    TIP + 'Craft a &eDream Star Pedestal&7 (gold, amethyst, a quartz pillar and polished blackstone) and right-click it with the star. It floats, turns slowly, sparkles and lights up the room. Take it back with an empty hand.',
    '',
    TIP + 'Look at your star on its pedestal for a moment.'],
    [item('questsicons:dream_star_pedestal'), observe('questsicons:dream_star_pedestal', 60, title='Admire your Dream Star on its pedestal')],
    [crate('legendary')], deps=['star'], shape='hexagon', size=1.4, icon='questsicons:dream_star_pedestal')
x.quest('finale', '&6&lThe Dreamer\'s Legacy', 21, 0, [
    KEEPER + '"The star shines, and so does the Dream. Wherever you go next, Dreamer - you can always come back here."',
    '',
    TIP + 'You finished Dreamcraft. Thank you for playing! Show your star to your friends, and share a screenshot with us on Discord.'],
    [check('Thank you, Dreamkeeper')], [crate('legendary', 3), levels(50), give('minecraft:enchanted_golden_apple', 2), give('minecraft:firework_rocket', 64)],
    deps=['pedestal'], shape='star', size=1.8, icon='questsicons:icon_trophy')

# =====================================================================================================
# Side path - Kitchen and Farm
k = B.chapter('kitchen', '&2Kitchen & Farm', 'questsicons:icon_food', ['&7Everything about food, farming and cooking.'], PATHS, 'circle')
k.quest('start', '&2Kitchen & Farm', 0, 0, [TIP + 'Good food keeps you alive in the Dream. This side path shows every cooking and farming mod in the pack.'],
        [item('#c:foods', 32)], [rxp(30)], icon='questsicons:icon_food', deps=['settler:start'], shape='star', size=1.3)
k.quest('skillet', 'The Skillet', 2, -2, [TIP + 'Hold a &eSkillet&7 (Farmer\'s Delight) over a campfire or stove to fry food in your hand - or swing it as a weapon.'],
        [item('farmersdelight:skillet')], [give('minecraft:egg', 8)], deps=['start'])
k.quest('rice', 'Rice Paddies', 0, -2.4, [
    TIP + 'Plant &eRice&7 in shallow water, one block deep. It grows up out of the water into &eRice Panicles&7. Cooked rice is the base of many Farmer\'s Delight and Ube\'s Delight meals.'],
    [item('farmersdelight:rice_panicle', 8)], [give('farmersdelight:rice_bag')], deps=['skillet'], optional=True)
k.quest('more', 'More Delight', 4, -2, [TIP + '&eMore Delight&7 adds sandwiches, pasta, salads and loaded burgers. Check the cooking pot in JEI.'],
        [item('moredelight:loaded_hamburger')], [give('farmersdelight:tomato', 6)], deps=['skillet'], optional=True)
k.quest('rustic', 'Rustic Delight', 4, 0, [TIP + '&eRustic Delight&7 brings cotton, bell peppers, coffee and calamari. Look for wild crops.'],
        [item('rusticdelight:bell_pepper_green')], [crate('common')], deps=['start'], optional=True)
k.quest('coffee', 'Morning Coffee', 6, 1.5, [
    TIP + 'Find &eCoffee Beans&7 in the jungle (Rustic Delight), roast them in a furnace and brew &eCoffee&7 in the cooking pot from 3 roasted beans. Try the coffee cookies and cheesecake too.'],
    [item('rusticdelight:coffee')], [give('farmersdelight:cabbage', 4)], deps=['rustic'], optional=True)
k.quest('ube', 'Ube\'s Delight', 6, -1, [TIP + 'Purple yams, lemongrass and sweet treats from the Philippines (Ube\'s Delight).'],
        [item('ubesdelight:ube', 4)], [crate('common')], deps=['rustic', 'more'], any_dep=True, optional=True)
k.quest('sweets', 'Sweet Little Things', 6, -2.6, [
    TIP + '&eAdditional Additions&7 cooks up quick snacks: &eFried Eggs&7, &eChicken Nuggets&7, &eHoneyed Apples&7 and &eBerry Pie&7.'],
    [item('additionaladditions:berry_pie'), item('additionaladditions:honeyed_apple')], [give('minecraft:sweet_berries', 16)], deps=['more'], optional=True)
k.quest('maple', 'Maple Syrup', 8, -2.6, [
    TIP + '&eEcologics&7: put a &eSpile&7 into a sappy maple log and collect the &eMaple Sap&7 with a bucket. Pour it into a cauldron above something hot (a campfire or a stove works) and fill a bottle with the syrup. Pancakes, maple cookies and maple pie are waiting.'],
    [item('ecologics:maple_syrup_bottle')], [give('minecraft:sugar', 16)], deps=['sweets'], optional=True)
k.quest('crates', 'Crate and Barrel', 2, 2, [TIP + 'Store crops in crates (Farmer\'s Delight) and decorate your pantry with &eStorage Delight&7 cabinets and drawers.'],
        [item('farmersdelight:carrot_crate')], [give('farmersdelight:canvas', 4)], deps=['start'])
k.quest('fertilizer', 'Fertilizer', 4, 2.5, [TIP + 'Farming for Blockheads fertilizers make farmland rich (more crops), healthy (faster growth) or stable (never trampled).'],
        [item('farmingforblockheads:green_fertilizer', 4)], [give('minecraft:bone_meal', 32)], deps=['crates'])
k.quest('sprinkler', 'Sprinkler', 6, 3.5, [TIP + 'A &eSprinkler&7 waters and speeds up crops around it. Feed it water through a pipe or bucket.'],
        [item('farmingforblockheads:sprinkler')], [crate('common')], deps=['fertilizer'], optional=True)
k.quest('fridge', 'Kitchen Multiblock', 8, 0, [TIP + 'Place a &eFridge&7, &eSink&7 and &eCounter&7 next to your &eCooking Table&7. The cooking table now sees their contents and offers every recipe you can make.'],
        [item('cookingforblockheads:sink'), item('cookingforblockheads:counter')], [crate('rare')], deps=['ube', 'sprinkler'], any_dep=True)
k.quest('oven', 'Ovens and Toasters', 10.6, -1.5, [
    TIP + 'Add a &eToaster&7, a &eSpice Rack&7 and a &eMilk Jar&7 to the kitchen. The cooking table counts what is in them, and a &eCow in a Jar&7 (JEI tells you how) keeps the milk coming.'],
    [item('cookingforblockheads:toaster'), item('cookingforblockheads:milk_jar')], [give('minecraft:milk_bucket')], deps=['fridge'], optional=True)
k.quest('chef', 'Master Chef', 10.6, 1.5, [
    TIP + 'Earn the &eChef\'s Hat&7. Cook a meal from three different add-ons and tick the box - you are the best cook of the Dream.'],
    [item('cookingforblockheads:chef_hat'), check('I cooked my way through the add-ons')], [crate('rare'), rxp(150)], deps=['fridge'], shape='star', size=1.2, icon='questsicons:quest_crown')

# =====================================================================================================
# Side path - Builder's Dream
b = B.chapter('builder', '&6Builder\'s Dream', 'questsicons:icon_house', ['&7Blocks, furniture and the tools to build big.'], PATHS, 'square')
b.quest('start', '&6Builder\'s Dream', 0, 0, [TIP + 'Dreamcraft has thousands of building blocks. Here is how to find and place them quickly.'],
        [item('#minecraft:planks', 64)], [rxp(30)], icon='questsicons:icon_house', deps=['settler:house'], shape='star', size=1.3)
b.quest('chisel', 'The Chisel', 2, -2, [TIP + 'Put blocks into a &eChisel&7 (Rechiseled) and pick one of many variants. Right-click with the chisel to open it.'],
        [item('rechiseled:chisel')], [give('minecraft:stone_bricks', 64)], deps=['start'])
b.quest('stoneworks', 'Stoneworks', 4, -3, [
    TIP + '&eStoneworks&7 gives every stone bricks, tiles, pavers, shingles and plates. Put any stone into a &estonecutter&7 and browse.'],
    [item('minecraft:stonecutter'), item('stoneworks:andesite_tiles', 16)], [give('minecraft:andesite', 64)], deps=['chisel'], optional=True)
b.quest('wand', 'Building Wand', 2, 0, [TIP + 'A &eBuilding Wand&7 extends a whole wall at once using blocks from your inventory. Sneak + scroll changes the mode.'],
        [item('constructionwand:iron_wand')], [give('minecraft:cobblestone', 64)], deps=['start'])
b.quest('effortless', 'Effortless Building', 4, -1, [TIP + 'Press &eAlt&7 (Effortless Building) for build modes: lines, walls, floors, cubes, circles and mirrors.'],
        [check('I tried a build mode')], [give('minecraft:glass', 32)], deps=['wand'])
b.quest('chalk', 'Chalk Marks', 2, 2, [TIP + 'Draw on any block with &eChalk&7. Glowing chalk shines in the dark - great for marking cave paths.'],
        [item('chalk:white_chalk')], [give('chalk:white_glow_chalk')], deps=['start'], optional=True)
b.quest('macaw', 'Macaw\'s Collection', 4, 1, [TIP + 'Craft a piece from every Macaw\'s mod: a roof, a window, a bridge and a lamp.'],
        [item('mcwroofs:oak_roof'), item('mcwwindows:oak_window'), item('mcwbridges:oak_log_bridge_middle')], [crate('common')], deps=['start'])
b.quest('furniture', 'Furnish It', 6, 2.5, [
    TIP + '&eMacaw\'s Furniture&7 makes chairs, tables, desks, wardrobes, drawers and whole kitchens from every wood. Drawers and wardrobes are real storage.'],
    [item('mcwfurnitures:oak_chair', 2), item('mcwfurnitures:oak_table')], [give('minecraft:oak_planks', 32)], deps=['macaw'])
b.quest('details', 'In the Details', 8, 2.5, [
    TIP + 'Doors, fences, stairs and trapdoors of the Macaw\'s mods, paths and pavings for your streets, and &eBeautify&7 blinds, trellises and picture frames. Diagonal fences, walls and glass panes (Diagonal Fences, Walls and Windows) connect by themselves.'],
    [item('mcwdoors:oak_barn_door'), item('mcwpaths:andesite_flagstone', 16), item('beautify:oak_blinds')], [crate('common')], deps=['furniture'], optional=True)
b.quest('lanterns', 'Light It Up', 6, 1, [TIP + '&eAdditional Lanterns&7 makes lanterns from every material and color.'],
        [item('additionallanterns:amethyst_lantern', 4)], [give('minecraft:torch', 32)], deps=['macaw'], optional=True)
b.quest('magic_vibe', 'Magic Vibes', 6, -3, [
    TIP + '&eMagic Vibe Decorations&7 is pure atmosphere: crystal lamps, fairy lights, witchy bookshelves, crystal balls and plushies. Look through its creative tab or JEI.'],
    [item('magic_vibe_decorations:ametrine_crystal_lamp')], [give('minecraft:amethyst_shard', 16)], deps=['dawn'], optional=True)
b.quest('dawn', 'Dawn of Time', 6, -1, [TIP + '&eDawn of Time&7 adds historic blocks from many cultures: Roman, Japanese, Persian, Gothic... Browse them in JEI.'],
        [check('I found a style I like')], [crate('common')], deps=['effortless', 'chisel'], optional=True)
b.quest('chains', 'Hang in There', 8, -2, [
    TIP + 'Right-click a fence or wall with an &eiron chain&7, then another one: &eReconnectible Chains&7 hangs a chain between them, sagging like a real one.',
    TIP + '&eArmor Statues&7: sneak and right-click an armor stand with an empty hand to pose it.'],
    [item('minecraft:iron_chain', 8), item('minecraft:armor_stand')], [give('minecraft:lantern', 4)], deps=['dawn', 'lanterns'], any_dep=True, optional=True)
b.quest('done', '&6Master Builder', 10, 0, [TIP + 'Show off your best build to a friend - then tick the box.'],
        [check('My dream build is done')], [crate('rare'), rxp(200)], deps=['dawn', 'lanterns'], any_dep=True, shape='star', size=1.3, icon='questsicons:quest_crown')

# =====================================================================================================
# Side path - Explorer's Atlas
a = B.chapter('atlas', '&3Explorer\'s Atlas', 'questsicons:icon_map', ['&7Biomes, structures and how to find them.'], PATHS, 'diamond')
a.quest('start', '&3Explorer\'s Atlas', 0, 0, [TIP + 'Terralith and Tectonic reshape the world. Hundreds of new structures wait out there.'],
        [item('minecraft:compass')], [give('minecraft:map', 4)], icon='questsicons:icon_map', deps=['prologue:map'], shape='star', size=1.3)
a.quest('nature', 'Nature\'s Compass', 2, -2, [TIP + 'Open the &eNature\'s Compass&7, pick any biome and it points the way.'],
        [item('naturescompass:naturescompass')], [rxp(60)], deps=['start'])
a.quest('explorer', 'Explorer\'s Compass', 2, 2, [TIP + 'The &eExplorer\'s Compass&7 does the same for structures: villages, taverns, towers, temples...'],
        [item('explorerscompass:explorerscompass')], [rxp(60)], deps=['start'])
a.quest('wits', 'What Is This Place?', 2, 3.4, [
    TIP + 'Standing in ruins and wondering what they are? Type &e/wits&7 (What Is This Structure?): it tells you the name of the structure around you and the mod it comes from.',
    '',
    TIP + 'Tick the box when you tried it.'],
    [check('I asked /wits')], [rxp(40)], deps=['explorer'], optional=True)
a.quest('glider', 'Hang Glider', 4, 0, [TIP + 'Jump off a cliff with a &eHang Glider&7 and soar. Updrafts over fire lift you up.'],
        [item('hangglider:hang_glider')], [give('minecraft:feather', 16)], deps=['nature', 'explorer'], any_dep=True)
a.quest('village', 'A Village', 4, 2, [TIP + 'Find a village. &eTowns and Towers&7 and &eMoog\'s&7 structures make them bigger and more varied.'],
        [struct('#minecraft:village', 'Find a village')], [give('minecraft:emerald', 8)], deps=['explorer'])
a.quest('tavern', 'The Tavern', 6, 2, [TIP + 'Taverns (Dungeons and Taverns) have traders, food and a cartographer who sells maps to rare structures.'],
        [struct('nova_structures:tavern_birch', 'Find a tavern')], [crate('rare')], deps=['village'], optional=True)
a.quest('outpost', 'Pillagers!', 6, 3.4, [
    TIP + '&eTowns and Towers&7 gives every biome its own pillager outpost. Clear one and loot its tower. Their captains drop Ominous Bottles: drink one only if you want a raid.'],
    [struct('#minecraft:pillager_outpost', 'Find a pillager outpost')], [crate('rare')], deps=['village'], optional=True)
a.quest('canyon', 'Bryce Canyon', 4, -2, [TIP + 'Terralith biomes can be breathtaking. Visit a canyon.'],
        [biome('terralith:bryce_canyon', 'Visit a Bryce Canyon')], [crate('common')], deps=['nature'], optional=True)
a.quest('peaks', 'Above the Clouds', 4, -3.4, [
    TIP + '&eTectonic&7 raises huge mountain ranges and carves deep valleys. Climb one of its peaks and enjoy the view.'],
    [biome('#minecraft:is_mountain', 'Stand on a mountain')], [give('minecraft:spyglass')], deps=['canyon'], optional=True)
a.quest('graveyard', 'A Graveyard', 6, -2, [TIP + 'Graveyards (The Graveyard) are full of undead and loot. Some hide a crypt with a dangerous boss.'],
        [struct('graveyard:large_graveyard', 'Find a large graveyard')], [crate('rare')], deps=['canyon', 'glider'], any_dep=True, optional=True)
a.quest('castle', 'Castles and Keeps', 8, -2, [
    TIP + '&eATi Structures&7, &eStructory&7 and &eMoog\'s&7 structures add castles, keeps, towers and ruined forts. Find a ruined castle.'],
    [struct('ati_structures:ruined_castle', 'Find a ruined castle')], [crate('epic')], deps=['graveyard'], optional=True)
a.quest('skies', 'Islands in the Sky', 8, -3.4, [
    TIP + '&eMoog\'s Soaring Structures&7 hangs islands, towers and castles high in the air, and &eExplorations&7 adds floating islands too. Bring a hang glider for the way down.'],
    [struct('mss:castle_tower', 'Visit a sky castle tower')], [crate('epic')], deps=['castle'], optional=True)
a.quest('trial', 'Trial Chambers', 8, 3.4, [
    TIP + 'Deep below the surface lie the copper halls of the &eTrial Chambers&7. Beat the trial spawners for &eTrial Keys&7 and open the vaults.',
    TIP + 'Rare pets of the &dTamacraft&7 path hide here (the Mimic) and in woodland mansions.'],
    [struct('minecraft:trial_chambers', 'Find the trial chambers'), item('minecraft:trial_key')], [crate('epic')], deps=['outpost', 'tavern'], any_dep=True, optional=True)
a.quest('relics', 'Lost Relics', 11, 2, [
    TIP + '&eLost Relics&7 hides old artifacts with strange powers in &ejungle pyramids&7, like the &eSmoking Mirror&7, the &eCursed Amulet&7 or the &eTurquoise Eye&7. Read their tooltips before you use them...'],
    [item('#lost_relics:relics')], [crate('rare')], deps=['done'], optional=True)
a.quest('done', '&3World Traveller', 11, 0, [TIP + 'Travel 10 km (walking, flying or boating).'],
        [stat('minecraft:walk_one_cm', 1000000, 'Walk 10 km')], [crate('epic'), rxp(300)], deps=['glider'], shape='star', size=1.3, icon='questsicons:quest_crown')

# =====================================================================================================
# Side path - Creatures and Companions
c = B.chapter('creatures', '&aCreatures & Companions', 'questsicons:icon_heart', ['&7Friends, foes and fearsome mutants.'], PATHS, 'heart')
c.quest('start', '&aCreatures & Companions', 0, 0, [TIP + '&eNaturalist&7, &eFriends&&Foes&7, &eEcologics&7 and more fill the world with animals - and monsters.'],
        [check()], [rxp(30)], icon='questsicons:icon_heart', deps=['settler:animals'], shape='star', size=1.3)
c.quest('butterfly', 'Butterflies', 2, -2, [TIP + 'Catch a butterfly in a bucket... or just watch it. Naturalist animals react to you, sleep at night and hunt each other.'],
        [observe('naturalist:butterfly', 40, entity=True, title='Watch a butterfly')], [give('minecraft:honey_bottle', 2)], deps=['start'])
c.quest('bear', 'Bear Country', 4, -2, [TIP + 'Bears guard their berries. Find one in a forest - from a safe distance.'],
        [observe('naturalist:bear', 40, entity=True, title='Spot a bear')], [give('minecraft:sweet_berries', 16)], deps=['butterfly'], optional=True)
c.quest('safari', 'Safari', 6, -3, [
    TIP + 'Naturalist brings the savanna to life: &eelephants&7, &egiraffes&7, &ezebras&7, &erhinos&7 and &elions&7 roam the grasslands. Lions are not as friendly as they look.'],
    [observe('naturalist:elephant', 40, entity=True, title='Spot an elephant'), observe('naturalist:giraffe', 40, entity=True, title='Spot a giraffe')],
    [give('minecraft:hay_block', 4)], deps=['bear'], optional=True)
c.quest('net', 'Bug Net', 6, -1.5, [
    TIP + 'A &eCapture Net&7 (Naturalist) catches butterflies, fireflies and other small critters. Release them in your garden.'],
    [item('naturalist:capture_net')], [give('minecraft:glass_bottle', 4)], deps=['bear'], optional=True)
c.quest('moobloom', 'Moobloom', 2, 2, [TIP + 'A cow covered in flowers (Friends&&Foes). Bees love it.'],
        [observe('friendsandfoes:moobloom', 40, entity=True, title='Find a moobloom')], [give('minecraft:sunflower', 4)], deps=['start'], optional=True)
c.quest('golems', 'Little Helpers', 4, 4, [
    TIP + '&eFriends&&Foes&7 brings back the mob vote losers: the &eTuff Golem&7 holds and shows off an item you give it, and the grumpy &eGlare&7 floats to dark spots where monsters could spawn. You can even tame a glare.'],
    [observe('friendsandfoes:glare', 40, entity=True, title='Find a glare')], [give('minecraft:copper_ingot', 16)], deps=['moobloom'], optional=True)
c.quest('penguin', 'Penguins', 4, 2, [TIP + 'Penguins waddle on cold beaches (Ecologics). Squirrels and coconut crabs live in warmer places.'],
        [observe('ecologics:penguin', 40, entity=True, title='Find a penguin')], [give('minecraft:cod', 8)], deps=['moobloom', 'start'], any_dep=True, optional=True)
c.quest('snail', 'The Slow Lane', 6, 2, [
    TIP + 'Snails (&eLovely Snails&7) can be saddled and ridden - slowly. With a chest on their back they carry your things.'],
    [observe('lovely_snails:snail', 40, entity=True, title='Find a snail')], [give('minecraft:saddle')], deps=['penguin'], optional=True)
c.quest('pet', 'A Loyal Friend', 2, 0, [TIP + 'Tame a wolf or cat. With &eRespawnable Pets&7 your pet comes back to life if it dies.',
                                         TIP + 'Want something rarer? The &dTamacraft&7 side path is all about the ten rare pets of the Dream.'],
        [item('minecraft:bone', 8)], [give('minecraft:name_tag')], deps=['start'])
c.quest('walkers', 'Walk in Their Shoes', 0, 2.5, [
    TIP + '&eWoodwalkers&7 lets you become a mob. Look at a creature and hold &eU&7 for a few seconds: it becomes your second shape. Press &eG&7 to turn into it and back.',
    TIP + 'Fly as a bat, swim as a dolphin, climb as a spider. The keys are under Controls > Woodwalkers.',
    '',
    TIP + 'Tick the box after your first transformation.'],
    [check('I walked as a mob')], [rxp(100)], deps=['start'], optional=True)
c.quest('variants', 'New Faces in the Dark', 0, 4.5, [
    TIP + '&eVariants&&Ventures&7 adds new undead: the icy &eGelid&7, the leafy &eThicket&7, the swampy &eMurk&7 and the mossy &eVerdant&7. Each has its own trick.',
    TIP + 'Defeat a Gelid in the snow.'],
    [kill('variantsandventures:gelid')], [crate('common')], deps=['walkers'], optional=True)
c.quest('mutant', 'Mutant Zombie', 8, 0, [TIP + '&eMutant Monsters&7 are huge, fast and dangerous. A Mutant Zombie gets back up after it falls: kill it while it burns (Fire Aspect, flint and steel, lava) or knock it down again until it stays down. Its drops make legendary gear like the Hulk Hammer.'],
        [kill('mutantmonsters:mutant_zombie')], [crate('epic')], deps=['pet'], shape='heart')
c.quest('mutants', 'The Whole Mutant Family', 10, -2, [
    TIP + 'The &eMutant Skeleton&7 drops bones for its own armor, the &eMutant Creeper&7 leaves &eCreeper Shards&7, and the &eMutant Enderman&7 throws blocks at you. Defeat one of each.'],
    [kill('mutantmonsters:mutant_skeleton'), kill('mutantmonsters:mutant_creeper'), kill('mutantmonsters:mutant_enderman')],
    [crate('legendary')], deps=['mutant'], shape='heart', optional=True)
c.quest('wildfire', 'The Wildfire', 10, 2, [
    TIP + 'In the Nether, the &eWildfire&7 (Friends&&Foes) commands its blazes from a &ecitadel&7. Break its shields, defeat it and claim the fiery &eWildfire Crown&7.'],
    [kill('friendsandfoes:wildfire')], [crate('epic')], deps=['mutant'], shape='heart', optional=True)
c.quest('lich', 'The Lich', 12, 0, [TIP + 'Deep in a crypt waits the &5Lich&7 (The Graveyard), the most dangerous undead of all.'],
        [kill('graveyard:lich')], [crate('legendary')], deps=['mutant'], shape='heart', size=1.4, optional=True)

# =====================================================================================================
# Loot crates (reward tables): what the crates in the rewards can contain. Balanced to help, not to skip.
B.table('common_crate', '&fCommon Crate', 'questsicons:common_crate', [
    ('minecraft:bread', 8, 20), ('minecraft:cooked_beef', 6, 15), ('minecraft:torch', 32, 20), ('minecraft:iron_ingot', 4, 15),
    ('minecraft:coal', 16, 15), ('minecraft:arrow', 24, 10), ('minecraft:bone_meal', 16, 10), ('minecraft:leather', 6, 8),
    ('minecraft:gold_ingot', 3, 8), ('minecraft:apple', 6, 10), ('minecraft:name_tag', 1, 2), ('minecraft:emerald', 3, 6),
    ('farmersdelight:rope', 12, 5), ('minecraft:lantern', 4, 6), ('tamacraft:pet_kibble', 8, 4), ('raft:rope', 8, 4)])
B.table('rare_crate', '&9Rare Crate', 'questsicons:rare_crate', [
    ('minecraft:diamond', 2, 15), ('minecraft:emerald', 8, 15), ('minecraft:golden_apple', 2, 12), ('minecraft:ender_pearl', 4, 12),
    ('minecraft:iron_block', 2, 10), ('minecraft:gold_block', 1, 8), ('minecraft:saddle', 1, 6), ('minecraft:name_tag', 2, 6),
    ('minecraft:experience_bottle', 16, 10), ('minecraft:lapis_block', 2, 8), ('minecraft:obsidian', 8, 8), ('minecraft:trial_key', 1, 6),
    ('jewelry:ruby', 2, 5), ('jewelry:sapphire', 2, 5), ('tamacraft:tamacraft_heart', 1, 4), ('raft:titanium_ingot', 3, 4)])
B.table('epic_crate', '&5Epic Crate', 'questsicons:epic_crate', [
    ('minecraft:diamond', 5, 15), ('minecraft:netherite_scrap', 1, 10), ('minecraft:totem_of_undying', 1, 8),
    ('minecraft:enchanted_golden_apple', 1, 3), ('minecraft:diamond_block', 1, 8), ('minecraft:shulker_shell', 2, 8),
    ('minecraft:ancient_debris', 2, 8), ('minecraft:experience_bottle', 48, 12), ('minecraft:heart_of_the_sea', 1, 4),
    ('minecraft:nautilus_shell', 3, 5), ('minecraft:wither_skeleton_skull', 1, 4), ('minecraft:ominous_trial_key', 1, 5),
    ('minecraft:emerald_block', 2, 10), ('minecraft:netherite_upgrade_smithing_template', 1, 4), ('raft:ancient_crystal', 1, 4)])
B.table('legendary_crate', '&6Legendary Crate', 'questsicons:legendary_crate', [
    ('minecraft:netherite_ingot', 2, 12), ('minecraft:totem_of_undying', 2, 12), ('minecraft:enchanted_golden_apple', 2, 10),
    ('minecraft:elytra', 1, 6), ('minecraft:nether_star', 1, 6), ('minecraft:beacon', 1, 4), ('minecraft:netherite_upgrade_smithing_template', 2, 8),
    ('minecraft:diamond_block', 4, 12), ('minecraft:heavy_core', 1, 3), ('minecraft:music_disc_pigstep', 1, 4), ('minecraft:dragon_breath', 8, 5)])

HERE = os.path.dirname(__file__)
for extra in ('dc_quests_raft.py', 'dc_quests_pets.py', 'dc_quests_island.py'):
    if os.path.exists(os.path.join(HERE, extra)):
        exec(open(os.path.join(HERE, extra)).read())

# =====================================================================================================
# Side path - Quality of Life (since V1.4)
UIC = 'upgraded-iron-chests:'
q = B.chapter('qol', '&eQuality of Life', UIC + 'diamond_chest', ['&7Little helpers that save time: storage, sorting, maps and more.'], PATHS, 'hexagon')
q.quest('start', '&eQuality of Life', 0, 0, [
    TIP + 'Dreamcraft is full of small helpers that save you a lot of time. This path shows the best of them, one by one.'],
    [item('minecraft:chest', 2)], [rxp(30)], icon=UIC + 'iron_chest', deps=['prologue:table'], shape='star', size=1.3)
q.quest('iron_chest', 'Iron Chest', 2, -2, [
    TIP + '&eUpgraded Iron Chests&7: surround a chest with eight iron ingots and you get an &eIron Chest&7 with much more room. Two side by side make a double chest.'],
    [item(UIC + 'iron_chest')], [give('minecraft:iron_ingot', 8)], deps=['start'])
q.quest('gold_chest', 'Gold Chest', 4, -3, [
    TIP + 'Upgrade it: four gold ingots and four iron ingots around an Iron Chest make a &eGold Chest&7.'],
    [item(UIC + 'gold_chest')], [give('minecraft:gold_ingot', 4)], deps=['iron_chest'])
q.quest('diamond_chest', 'Diamond Chest', 6, -3, [
    TIP + 'Diamonds and gold around a Gold Chest give a &eDiamond Chest&7. Every upgraded chest is immune to fire and lava.'],
    [item(UIC + 'diamond_chest')], [crate('common')], deps=['gold_chest'])
q.quest('netherite_chest', 'Netherite Chest', 8, -3, [
    TIP + 'The biggest of them all: netherite ingots and diamonds around a Diamond Chest make a &eNetherite Chest&7.'],
    [item(UIC + 'netherite_chest')], [crate('rare')], deps=['diamond_chest'], optional=True)
q.quest('safe', 'Safe Chest', 4, -1, [
    TIP + 'A &eSafe Chest&7 (iron bars, gold and iron around an Iron Chest) is locked with a passcode. Other players cannot break it, and hoppers or pipes cannot reach into it. The &eDiamond Safe Chest&7 holds even more.'],
    [item(UIC + 'safe_chest')], [give('minecraft:gold_ingot', 4)], deps=['iron_chest'], optional=True)
q.quest('search', 'Find My Item', 6, -1, [
    TIP + 'Open an upgraded chest: the search field finds any item, the rarity filter sorts by rarity, and &eQuick Stack&7 and &eDump&7 move your items into nearby chests with one click.',
    TIP + 'Link chests to see their contents from one place and let the chest point you to the item you are looking for.'],
    [check('I tried the search and Quick Stack')], [rxp(60)], deps=['iron_chest'])
q.quest('drawers', 'Bigger Drawers', 8, -1, [
    TIP + '&eStorage Drawers&7 grow with &eStorage Upgrades&7 from obsidian (I) up to netherite (VII). Open a drawer and put the upgrades into its slots. A &eDrawer Key&7 locks a drawer to its item.'],
    [item('storagedrawers:iron_storage_upgrade')], [give('minecraft:obsidian', 4)], deps=['search'], optional=True)
q.quest('sorting', 'Tidy Up', 2, 2, [
    TIP + '&eInventory Profiles Next&7 sorts your inventory and any open chest with one key (see Controls). &eMouse Tweaks&7: hold right-click and drag to spread items, scroll over a stack to move it, shift-drag to move many stacks.'],
    [check('I sorted a chest')], [rxp(40)], deps=['start'])
q.quest('crafting', 'Crafting Tweaks', 4, 2, [
    TIP + '&eCrafting Tweaks&7 adds small buttons next to every crafting grid: rotate the recipe, spread the items evenly or clear the grid. JEI\'s &e+&7 button fills the grid for you.'],
    [check('I used the crafting buttons')], [rxp(40)], deps=['sorting'])
q.quest('shulker', 'Boxes in Boxes', 4, 3.5, [
    TIP + '&eShulker Box Tooltip&7 shows what is inside a shulker box when you hover over it, and &eEasy Shulker Boxes&7 opens a shulker box straight from your inventory.'],
    [check('I looked into a shulker box')], [rxp(40)], deps=['sorting'], optional=True)
q.quest('harvest', 'Easy Harvest', 6, 2, [
    TIP + '&eRightClickHarvest&7: right-click ripe crops to harvest and replant them in one go. &eFallingTree&7: chop the lowest log and the whole tree comes down (sneak to cut a single log).'],
    [check('I harvested with a right-click')], [give('minecraft:bone_meal', 16)], deps=['crafting'])
q.quest('minimap', 'Never Lost', 2, 4, [
    TIP + '&eXaero\'s Minimap&7 shows the land around you, &eXaero\'s World Map&7 (key &eM&7) everything you have explored. Set a waypoint at your base and at every place you want to find again.'],
    [check('I set a waypoint')], [give('minecraft:compass')], deps=['start'])
q.quest('light', 'Light and Safety', 6, 4, [
    TIP + 'With &eLambDynamicLights&7 a torch in your hand lights up the area around you. A &eMagnum Torch&7 stops monsters from spawning in a wide area around your base.'],
    [item('magnumtorch:diamond_magnum_torch')], [crate('common')], deps=['minimap', 'harvest'], any_dep=True, optional=True)
q.quest('glance', 'At a Glance', 8, 2, [
    TIP + '&eAppleSkin&7 shows how much a food fills you up, right on the hunger bar. &eZoomify&7 zooms in with &eC&7 - scroll to zoom further.'],
    [check('I zoomed in')], [rxp(30)], deps=['harvest'], optional=True)
q.quest('done', '&eLife Made Easy', 10, 0, [TIP + 'Big chests, sorted inventories and a map full of waypoints: life in the dream just got a lot easier.'],
        [check('My base is tidy')], [crate('rare'), rxp(150)], deps=['diamond_chest', 'harvest'], shape='star', size=1.3, icon='questsicons:quest_crown')


def task_icons():
    """By default the book shows wheat for advancement tasks and a spyglass for looking at a mob: use fitting icons."""
    for ch in B.chapters:
        for qq in ch.quests:
            for tk in qq['tasks']:
                if 'icon' in tk: continue
                if tk['type'] == 'observation' and tk.get('entity'):
                    ns, path = tk['observe'].split(':')
                    tk['icon'] = {'tamacraft': f'{ns}:{path}_plush', 'betternether': f'{ns}:spawn_egg_{path}'}.get(ns, f'{ns}:{path}_spawn_egg')
                elif tk['type'] == 'advancement' and qq.get('icon'):
                    tk['icon'] = qq['icon']
task_icons()

# Story chapters first, then side paths (sidebar order).
order = ['prologue', 'settler', 'deep', 'industry', 'power', 'nether', 'sea', 'end', 'epilogue', 'kitchen', 'builder', 'atlas', 'creatures', 'pets', 'qol']
B.chapters.sort(key=lambda ch: order.index(ch.key) if ch.key in order else 99)

DATA = {'title': '&dDreamcraft &7- Quest Book', 'icon': 'questsicons:quest_book', 'default_quest_shape': 'circle',
        'default_reward_team': False, 'give_book_on_first_join': True}

if __name__ == '__main__':
    out = sys.argv[1]
    B.write(out, DATA)
    n = sum(len(c.quests) for c in B.chapters)
    print('chapters', len(B.chapters), 'quests', n)
    for c in B.chapters:
        print(f'  {c.key:10} {len(c.quests):3}  {sum(1 for q in c.quests if q.get("optional"))} optional')
