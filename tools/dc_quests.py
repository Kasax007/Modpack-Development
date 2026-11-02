"""Dreamcraft 26.3 quest book: the story chapters and the side paths."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from qlib import *

B = Book()
STORY = B.group('story', '&d✦ The Dream', 'questsicons:icon_moon')
PATHS = B.group('paths', '&b✦ Side Paths', 'questsicons:icon_map')

KEEPER = '&d&o'   # the Dreamkeeper's voice
TIP = '&7'

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
    TIP + 'New chapters are now open on the left. The &dThe Dream&7 chapters tell the story, the &bSide Paths&7 are optional and explain the other mods.'],
    [], [crate('rare'), rxp(100)], icon='questsicons:quest_portal_two', deps=['iron'], shape='star', size=1.8)

# =====================================================================================================
# Chapter 1 - The Settler
s = B.chapter('settler', '&a1. The Settler', 'questsicons:icon_house',
              ['&7A home, a farm and a full belly.'], STORY, 'rsquare')
s.quest('start', '&aA Home in the Dream', 0, 0, [
    KEEPER + '"A dreamer without a home wanders forever. Settle down."',
    '',
    TIP + 'This chapter is about your first base: farming, cooking, animals and travel.'],
    [], [rxp(20)], icon='questsicons:icon_house', deps=['prologue:call'], shape='star', size=1.4)
s.quest('hoe', 'Till the Soil', 2, -2, [
    TIP + 'Craft a hoe and plant some wheat. &eRightClickHarvest&7 is installed: right-click a ripe crop to harvest and replant it in one go.'],
    [item('#minecraft:hoes'), item('minecraft:wheat', 16)], [give('minecraft:bone_meal', 16)], deps=['start'])
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
s.quest('feast', 'A Feast for Friends', 8, -1, [
    TIP + 'Feasts are placed as blocks and serve several portions. Cook one and share it.'],
    [item('farmersdelight:roast_chicken_block')], [crate('common')], deps=['pot'], optional=True)
s.quest('animals', 'Animal Husbandry', 2, 2, [
    TIP + 'Breed some animals. &eFarming for Blockheads&7 adds a &eFeeding Trough&7: fill it with food and nearby animals breed on their own.'],
    [item('farmingforblockheads:feeding_trough')], [give('minecraft:lead', 2), give('minecraft:wheat', 16)], deps=['start'])
s.quest('market', 'The Market', 4, 3, [
    TIP + 'The &eMarket&7 sells seeds, saplings, flowers and animal eggs for emeralds. A great way to get crops from biomes you have not found yet.'],
    [item('farmingforblockheads:market')], [give('minecraft:emerald', 6)], deps=['animals'])
s.quest('lasso', 'Catch Them All', 6, 3, [
    TIP + 'A &eGolden Lasso&7 (Mob Lassos) picks up a passive animal; right-click again to release it. Moving animals has never been easier.',
    TIP + 'Villagers need an &eEmerald Lasso&7 and a &eContract&7.'],
    [item('moblassos:golden_lasso')], [give('minecraft:golden_carrot', 8)], deps=['market'], optional=True)
s.quest('bucket', 'A Villager in a Bucket', 6, 1, [
    TIP + 'Right-click a villager with an empty bucket to scoop it up (&eVillager In A Bucket&7). Place it wherever you need it.',
    TIP + 'With &eTrading Post&7 you can trade with all villagers around you from one block.'],
    [item('villagerinabucket:villager_in_a_bucket'), item('tradingpost:trading_post')], [give('minecraft:emerald', 12)], deps=['animals'])
s.quest('house', 'Home Sweet Home', 0, 4, [
    TIP + 'Build a real house. The &eMacaw\'s&7 mods add furniture, roofs, windows, doors, lights, paths and bridges. Press &eR&7 on a log or plank in your inventory to see everything you can make from it.',
    '',
    TIP + 'Tick the box when your house is done - and be proud of it!'],
    [check('My house is built')], [give('mcwlights:iron_wall_lantern', 4) if False else give('minecraft:lantern', 6), crate('common')], deps=['start'], shape='square')
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
d = B.chapter('deep', '&71. Into the Deep', 'questsicons:icon_pickaxe', ['&7Ores, storage and the magic of enchanting.'], STORY, 'hexagon')
d.title = '&62. Into the Deep'
d.quest('start', '&6Into the Deep', 0, 0, [
    KEEPER + '"Below every dream lies a deeper one. Dig."'],
    [item('minecraft:iron_pickaxe')], [give('minecraft:torch', 32)], icon='questsicons:icon_pickaxe', deps=['prologue:call'], shape='star', size=1.4)
d.quest('coal', 'Fuel for the Fire', 2, -2, [TIP + 'Collect coal. You will need a lot of it for furnaces and torches.'],
        [item('#c:coal', 32) if False else item('minecraft:coal', 32)], [give('minecraft:furnace', 2)], deps=['start'])
d.quest('copper', 'Copper Shine', 2, 2, [TIP + 'Copper is everywhere in the deep. It is used for pipes, hoppers and much more.'],
        [item('#c:ingots/copper', 24)], [rxp(40)], deps=['start'])
d.quest('gold', 'Gold Rush', 4, -2, [TIP + 'Gold is softer than iron but loved by piglins and needed for golden carrots and apples.'],
        [item('#c:ingots/gold', 12)], [give('minecraft:golden_carrot', 6)], deps=['coal'])
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
    TIP + 'Store power in a &eBattery&7 or a &eLow Voltage SU&7.'],
    [item('#techreborn:generators') if False else item('techreborn:solid_fuel_generator')], [give('techreborn:insulated_copper_cable', 16)], deps=['circuit', 'frame'], shape='diamond', size=1.3)
t.quest('furnace', 'Electric Furnace', 8, -2, [TIP + 'Smelts faster than a furnace and never needs coal.'],
        [item('techreborn:electric_furnace')], [rxp(80)], deps=['generator'])
t.quest('grinder', 'Ore Doubling', 8, 0, [
    TIP + 'The &eGrinder&7 turns one ore into two dusts. Smelt the dusts and you get twice the ingots.'],
    [item('techreborn:grinder')], [give('minecraft:raw_iron', 16)], deps=['generator'], shape='hexagon')
t.quest('solar', 'Free Energy', 8, 2, [
    TIP + 'A &eSolar Panel&7 makes energy during the day without fuel. Raft players can also use the makeshift solar panels of the sea (see &bThe Endless Sea&7).'],
    [item('techreborn:basic_solar_panel', 2)], [give('techreborn:red_cell_battery')], deps=['generator'])
t.quest('storage', 'Battery Bank', 10, 2, [TIP + 'A &eLow Voltage SU&7 stores lots of energy and feeds it to your machines.'],
        [item('techreborn:low_voltage_su')], [rxp(100)], deps=['solar'])
t.quest('alloy', 'Alloys', 10, -2, [TIP + 'The &eAlloy Smelter&7 combines metals - bronze, electrum and the advanced alloys used for better machines.'],
        [item('techreborn:alloy_smelter')], [give('techreborn:refined_iron_ingot', 16)], deps=['furnace'])
t.quest('quarry', 'Let the Machines Dig', 12, 0, [
    TIP + 'The &eQuarry&7 (Quarry Reborn) digs out a whole area for you. Place markers to mark the corners, put the quarry next to them and give it energy.',
    TIP + 'Modules add pumps, item filters or even bedrock removal.'],
    [item('quarryplus:quarry'), item('quarryplus:marker', 4)], [crate('rare')], deps=['grinder', 'storage'], shape='gear', size=1.4)
t.quest('collect', 'Item Collectors', 12, 2.5, [TIP + 'An &eItem Collector&7 picks up dropped items around it and puts them into the chest next to it.'],
        [item('itemcollectors:basic_collector')], [give('minecraft:hopper', 2)], deps=['quarry'], optional=True)
t.quest('pipes', 'Copper Hoppers', 12, -2.5, [TIP + 'A &eCopper Hopper&7 only moves the items that match its filter slot - perfect for sorting. It oxidizes over time; wax it to keep it shiny.'],
        [item('copperhopper:copper_hopper', 4)], [give('minecraft:copper_ingot', 16)], deps=['quarry'], optional=True)
t.quest('chunk', 'Never Sleeping', 14, -1.5, [
    TIP + 'A &eChunk Loader&7 keeps the chunks around it loaded even when you are far away - your machines keep working.'],
    [item('#chunkloaders:chunk_loaders') if False else item('chunkloaders:single_chunk_loader')], [crate('rare')], deps=['quarry'])
t.quest('elevator', 'Going Up', 14, 1.5, [
    TIP + 'Stack &eElevator Controllers&7 (Moving Elevators) on different floors. Stand on one and use its screen to ride smoothly to another floor.'],
    [item('movingelevators:elevator_block', 2)], [rxp(100)], deps=['quarry'], optional=True)
t.quest('charger', 'Wireless Charging', 16, 1.5, [TIP + 'A &eWireless Player Charger&7 refills energy items in your inventory while you are near it.'],
        [item('wirelesschargers:basic_wireless_player_charger')], [rxp(120)], deps=['elevator', 'chunk'], any_dep=True, optional=True)
t.quest('done', '&eThe Dream Never Sleeps', 16, -1.5, [KEEPER + '"Your machines hum through the night. The Dream grows stronger."'],
        [item('techreborn:industrial_grinder') if False else item('techreborn:industrial_centrifuge')], [crate('epic'), rxp(400)], deps=['chunk'], shape='star', size=1.5, icon='questsicons:quest_crown')

# =====================================================================================================
# Chapter 4 - Paths of Power (RPG series)
m = B.chapter('power', '&54. Paths of Power', 'questsicons:icon_magic', ['&7Choose your class: wizard, paladin, archer or rogue.'], STORY, 'octagon')
m.quest('start', '&5Paths of Power', 0, 0, [
    KEEPER + '"Every dreamer carries a power. Which one is yours?"',
    '',
    TIP + 'The RPG series adds four classes. Each has its own &eworkbench&7, weapons, armor and &espells&7. Weapons show their spells in their tooltip; the spells appear on a &espell hotbar&7 above your item bar.',
    TIP + 'You may follow one path or all of them.'],
    [check('Show me the paths')], [rxp(50)], icon='questsicons:icon_magic', deps=['deep:diamond'], shape='star', size=1.5)
m.quest('binding', 'The Spell Binding Table', 0, 3, [
    TIP + 'At the &eSpell Binding Table&7 you bind &eSpell Scrolls&7 to a &eSpell Book&7 for levels and lapis. Hold the book in your offhand and its spells join your weapon\'s spells.',
    TIP + 'Spell books are also found in loot chests.'],
    [item('spell_engine:spell_binding')], [give('minecraft:lapis_lazuli', 32), levels(5)], deps=['start'], shape='square')
# Wizard
m.quest('wizard', '&9Path of the Wizard', 3, -3, [
    TIP + 'Wizards cast &eArcane&7, &eFire&7 and &eFrost&7 spells from wands and staves. Hold right-click to cast; the spell hotbar shows what each key does.',
    TIP + 'Wizard towers in the world sell spell books.'],
    [item('#wizards:staves') if False else item('wizards:staff_arcane')], [give('wizards:spell_scroll/arcane')], deps=['start'], icon='wizards:staff_arcane')
m.quest('wizard_robe', 'Robes of Power', 5, -4, [TIP + 'Wizard robes boost spell power of their school. Wear a full set.'],
        [item('wizards:arcane_robe_head'), item('wizards:arcane_robe_chest'), item('wizards:arcane_robe_legs'), item('wizards:arcane_robe_feet')],
        [give('minecraft:amethyst_shard', 16)], deps=['wizard'], optional=True)
m.quest('wizard_school', 'Fire and Frost', 5, -2, [TIP + 'Craft a staff of a second school. Fire burns, frost slows - mix them as you like.'],
        [item('wizards:staff_fire'), item('wizards:staff_frost')], [crate('rare')], deps=['wizard'], optional=True)
# Paladin
m.quest('paladin', '&ePath of the Paladin', 3, -1, [
    TIP + 'Paladins fight with claymores, maces and great hammers and protect allies with &eholy&7 spells. Priests heal with holy wands and staves.',
    TIP + 'Craft gear at the &eMonk Workbench&7.'],
    [item('paladins:monk_workbench'), item('paladins:iron_claymore')], [give('minecraft:golden_apple')], deps=['start'], icon='paladins:iron_claymore')
m.quest('paladin_armor', 'Crusader Plate', 5, -0.5, [TIP + 'The &eCrusader armor&7 is heavy but blessed.'],
        [item('paladins:crusader_armor_chest')], [give('paladins:iron_kite_shield')], deps=['paladin'], optional=True)
# Archer
m.quest('archer', '&aPath of the Archer', 3, 1, [
    TIP + 'Archers use longbows, shortbows, crossbows and spears. Bow spells like &eBarrage&7 and &eEntangling Roots&7 trigger while you draw.',
    TIP + 'The &eAuto-Fire Hook&7 makes crossbows reload by themselves.'],
    [item('archers:archers_workbench'), item('archers:composite_longbow')], [give('minecraft:arrow', 64)], deps=['start'], icon='archers:composite_longbow')
m.quest('archer_armor', 'Ranger Gear', 5, 1.5, [TIP + 'Ranger armor raises your ranged damage.'],
        [item('archers:archer_armor_chest')], [give('archers:auto_fire_hook')], deps=['archer'], optional=True)
# Rogue
m.quest('rogue', '&cPath of the Rogue', 3, 3, [
    TIP + 'Rogues strike fast with daggers and sickles and vanish into the shadows; warriors smash with double axes and glaives.',
    TIP + 'Craft gear at the &eArms Workbench&7.'],
    [item('rogues:arms_workbench'), item('rogues:iron_dagger')], [give('minecraft:iron_ingot', 6)], deps=['start'], icon='rogues:iron_dagger')
m.quest('rogue_armor', 'Assassin or Berserker', 5, 3.5, [TIP + 'Assassin armor makes you quicker, berserker armor makes you hit harder.'],
        [item('rogues:assassin_armor_chest')], [give('rogues:iron_sickle')], deps=['rogue'], optional=True)
# Jewelry and runes
m.quest('runes', 'Runes', 7, -1.5, [
    TIP + 'Many spells cost &erunes&7. Craft them cheaply at the &eRune Crafting Altar&7 and keep them in a &eRune Pouch&7 (equipped in an accessory slot) so spells take them automatically.'],
    [item('runes:crafting_altar'), item('runes:small_rune_pouch')], [give('runes:arcane_stone', 16)], deps=['wizard', 'paladin', 'archer', 'rogue'], any_dep=True)
m.quest('jewels', 'Gems and Jewelry', 7, 1.5, [
    TIP + 'Find gems like &cRuby&7, &9Sapphire&7 and &aJade&7 (Jewelry). Cut them at the &eJeweler\'s Kit&7, then add a &eSocket Mount&7 to armor at an anvil and insert the cut gem.',
    TIP + 'Rings and necklaces go into your accessory slots for extra spell power, health or speed.'],
    [item('jewelry:jewelers_kit'), item('#jewelry:gems') if False else item('jewelry:ruby')], [give('jewelry:gold_ring')], deps=['wizard', 'paladin', 'archer', 'rogue'], any_dep=True)
m.quest('legend', 'Legendary Arsenal', 9, 0, [
    TIP + 'Unique weapons of the &eArsenal&7 are only found in the world - in dungeon chests and on bosses. Each one has its own spell.',
    TIP + 'Find or claim one of them.'],
    [item('#arsenal:unique_weapons') if False else item('arsenal:unique_claymore_1')], [crate('epic')], deps=['runes', 'jewels'], optional=True)
m.quest('done', '&5Awakened Power', 11, 0, [KEEPER + '"Your power is awake. Now carry it into the fire."'],
        [xp(20)], [crate('epic'), choice(('jewelry:ruby_ring', 1), ('jewelry:sapphire_ring', 1), ('jewelry:jade_ring', 1), ('jewelry:citrine_ring', 1))],
        deps=['runes', 'jewels'], shape='star', size=1.5, icon='questsicons:quest_crown')

# =====================================================================================================
# Chapter 5 - Through the Fire (Nether)
n = B.chapter('nether', '&c5. Through the Fire', 'questsicons:quest_portal_two', ['&7The burning layer of the Dream.'], STORY, 'pentagon')
n.quest('start', '&cThrough the Fire', 0, 0, [
    KEEPER + '"Beneath the Dream burns its fever. Light a portal and step through."',
    '',
    TIP + 'Build a nether portal (obsidian frame, 4x5) and light it with flint and steel.'],
    [item('minecraft:obsidian', 10), item('minecraft:flint_and_steel')], [give('minecraft:fire_resistance_potion') if False else give('minecraft:golden_carrot', 8)], deps=['deep:diamond'], shape='star', size=1.4, icon='questsicons:quest_portal_two')
n.quest('enter', 'Into the Nether', 2, 0, [
    TIP + '&eBetterNether&7 fills the Nether with new biomes, plants, mobs and ruined cities. Bring a bed? Better not - it explodes here.'],
    [dim('minecraft:the_nether', 'Enter the Nether')], [rxp(100)], deps=['start'])
n.quest('quartz', 'Quartz and Gold', 4, -2, [TIP + 'Nether quartz and nether gold ore are everywhere. Piglins love gold - wear at least one golden armor piece.'],
        [item('minecraft:quartz', 32), item('minecraft:golden_helmet')], [give('minecraft:gold_ingot', 8)], deps=['enter'])
n.quest('fortress', 'The Fortress', 4, 0, [TIP + 'Find a nether fortress. Blazes guard it - their rods power brewing stands and eyes of ender.'],
        [struct('minecraft:fortress', 'Find a nether fortress'), item('minecraft:blaze_rod', 8)], [crate('rare')], deps=['enter'], shape='hexagon')
n.quest('brewing', 'Potion Master', 6, -2, [TIP + 'Brew a potion. Nether wart grows in fortresses.'],
        [item('minecraft:brewing_stand'), item('minecraft:nether_wart', 8)], [give('minecraft:glass_bottle', 16)], deps=['fortress'])
n.quest('bastion', 'Bastion Remnant', 4, 2, [TIP + 'Bastions are full of piglins and treasure. Careful with the brutes.'],
        [struct('minecraft:bastion_remnant', 'Find a bastion')], [crate('rare')], deps=['enter'])
n.quest('debris', 'Ancient Debris', 6, 2, [TIP + 'Ancient debris hides near Y=15. Beds and TNT help - or a lot of patience.'],
        [item('minecraft:ancient_debris', 4)], [give('minecraft:gold_ingot', 16)], deps=['bastion', 'fortress'])
n.quest('netherite', '&8Netherite', 8, 1, [TIP + 'Combine four netherite scrap and four gold into a netherite ingot. Upgrade diamond gear at a smithing table.'],
        [item('minecraft:netherite_ingot')], [give('minecraft:netherite_upgrade_smithing_template')], deps=['debris'], shape='diamond', size=1.3)
n.quest('advanced', 'Advanced Netherite', 10, 1, [
    TIP + '&eAdvanced Netherite&7 upgrades netherite tools and armor further with iron, gold, emerald or diamond: each tier gives more durability and special bonuses.'],
    [item('advancednetherite:netherite_diamond_ingot')], [crate('epic')], deps=['netherite'], optional=True)
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
e.quest('outer', 'The Outer Islands', 8, -2, [
    TIP + 'Throw a pearl into the gateway that appears. &eBetterEnd&7 turns the outer End into a whole world of biomes, from glowing forests to sulphuric lakes.'],
    [biome('#betterend:end_land_biomes') if False else biome('betterend:foggy_mushroomland', 'Visit the Foggy Mushroomland')], [crate('rare')], deps=['dragon'])
e.quest('city', 'End City', 8, 2, [TIP + 'End cities float in the outer End. Shulkers guard elytra and great loot.'],
        [struct('minecraft:end_city', 'Find an End city'), item('minecraft:shulker_shell', 4)], [crate('epic')], deps=['dragon'])
e.quest('elytra', '&bWings', 10, 2, [TIP + 'Find an elytra in an End ship. Fireworks give you a boost while flying.'],
        [item('minecraft:elytra')], [give('minecraft:firework_rocket', 32)], deps=['city'], shape='diamond')
e.quest('done', '&5The Dream Is Free', 12, 0, [
    KEEPER + '"You did it. The dragon is gone and the Dream breathes again. But dreams never truly end..."',
    '',
    TIP + 'Continue with the &dEpilogue&7 for the hardest challenges.'],
    [], [crate('legendary'), rxp(1000)], deps=['outer', 'elytra'], shape='star', size=2.0, icon='questsicons:quest_crown')

# =====================================================================================================
# Epilogue - Lucid Dreamer
x = B.chapter('epilogue', '&6Epilogue: Lucid Dreamer', 'questsicons:icon_trophy', ['&7For those who never want to wake up.'], STORY, 'star')
x.quest('start', '&6Lucid Dreamer', 0, 0, [KEEPER + '"You can shape the Dream now. Show me how strong you have become."'],
        [], [rxp(100)], deps=['end:done'], shape='star', size=1.5, icon='questsicons:icon_trophy')
x.quest('wither', 'The Wither', 2, -2, [TIP + 'Summon and defeat the Wither. Fight it underground so it cannot fly away.'],
        [kill('minecraft:wither')], [crate('epic')], deps=['start'], shape='heart', icon='minecraft:nether_star')
x.quest('beacon', 'A Beacon in the Dream', 4, -2, [TIP + 'Build a beacon on a pyramid of mineral blocks.'],
        [item('minecraft:beacon')], [give('minecraft:diamond_block', 2)], deps=['wither'])
x.quest('mythic', 'Mythic Upgrades', 2, 2, [
    TIP + '&eMythic Upgrades&7 adds crystal geodes deep underground and in the Nether. Their ingots (ametrine, aquamarine, citrine...) upgrade netherite gear with powerful effects.'],
    [item('#mythicupgrades:ingots') if False else item('mythicupgrades:ametrine_ingot')], [crate('epic')], deps=['start'], optional=True)
x.quest('warden', 'The Warden', 4, 2, [TIP + 'Defeat a warden in the deep dark. Sneak, it is blind but hears everything.'],
        [kill('minecraft:warden')], [crate('legendary')], deps=['start'], shape='heart', optional=True)
x.quest('crate', 'Crate Collector', 6, 0, [TIP + 'Open a &6Legendary Crate&7. You earned it.'],
        [item('questsicons:legendary_crate', 1, consume=True)], [crate('legendary')], deps=['beacon'], optional=True)
x.quest('master', '&6Master of Dreams', 8, 0, [
    KEEPER + '"You are no longer a dreamer. You are the Dream itself. Thank you for playing Dreamcraft."'],
    [check('Finish the journey')], [crate('legendary', 2), give('questsicons:quest_crown')], deps=['beacon', 'wither'], shape='star', size=2.2, icon='questsicons:quest_crown')

# =====================================================================================================
# Side path - Kitchen and Farm
k = B.chapter('kitchen', '&2Kitchen & Farm', 'questsicons:icon_food', ['&7Everything about food, farming and cooking.'], PATHS, 'circle')
k.quest('start', '&2Kitchen & Farm', 0, 0, [TIP + 'Good food keeps you alive in the Dream. This side path shows every cooking and farming mod in the pack.'],
        [item('#c:foods', 32)], [rxp(30)], icon='questsicons:icon_food', deps=['settler:start'], shape='star', size=1.3)
k.quest('skillet', 'The Skillet', 2, -2, [TIP + 'Hold a &eSkillet&7 (Farmer\'s Delight) over a campfire or stove to fry food in your hand - or swing it as a weapon.'],
        [item('farmersdelight:skillet')], [give('minecraft:egg', 8)], deps=['start'])
k.quest('more', 'More Delight', 4, -2, [TIP + '&eMore Delight&7 adds sandwiches, pasta, salads and loaded burgers. Check the cooking pot in JEI.'],
        [item('moredelight:loaded_hamburger')], [give('farmersdelight:tomato', 6)], deps=['skillet'], optional=True)
k.quest('rustic', 'Rustic Delight', 4, 0, [TIP + '&eRustic Delight&7 brings cotton, bell peppers, coffee and calamari. Look for wild crops.'],
        [item('#c:foods', 1) if False else item('rusticdelight:cotton_seeds' if False else 'rusticdelight:bell_pepper_green')], [crate('common')], deps=['start'], optional=True)
k.quest('ube', 'Ube\'s Delight', 6, -1, [TIP + 'Purple yams, lemongrass and sweet treats from the Philippines (Ube\'s Delight).'],
        [item('ubesdelight:ube', 4)], [crate('common')], deps=['rustic', 'more'], any_dep=True, optional=True)
k.quest('crates', 'Crate and Barrel', 2, 2, [TIP + 'Store crops in crates (Farmer\'s Delight) and decorate your pantry with &eStorage Delight&7 cabinets and drawers.'],
        [item('farmersdelight:carrot_crate')], [give('farmersdelight:canvas', 4)], deps=['start'])
k.quest('fertilizer', 'Fertilizer', 4, 2, [TIP + 'Farming for Blockheads fertilizers make farmland rich (more crops), healthy (faster growth) or stable (never trampled).'],
        [item('farmingforblockheads:green_fertilizer', 4)], [give('minecraft:bone_meal', 32)], deps=['crates'])
k.quest('sprinkler', 'Sprinkler', 6, 2, [TIP + 'A &eSprinkler&7 waters and speeds up crops around it. Feed it water through a pipe or bucket.'],
        [item('farmingforblockheads:sprinkler')], [crate('common')], deps=['fertilizer'], optional=True)
k.quest('fridge', 'Kitchen Multiblock', 8, 0, [TIP + 'Place a &eFridge&7, &eSink&7 and &eCounter&7 next to your &eCooking Table&7. The cooking table now sees their contents and offers every recipe you can make.'],
        [item('cookingforblockheads:sink'), item('cookingforblockheads:counter')], [crate('rare')], deps=['ube', 'sprinkler'], any_dep=True)

# =====================================================================================================
# Side path - Builder's Dream
b = B.chapter('builder', '&6Builder\'s Dream', 'questsicons:icon_house', ['&7Blocks, furniture and the tools to build big.'], PATHS, 'square')
b.quest('start', '&6Builder\'s Dream', 0, 0, [TIP + 'Dreamcraft has thousands of building blocks. Here is how to find and place them quickly.'],
        [item('#minecraft:planks', 64)], [rxp(30)], icon='questsicons:icon_house', deps=['settler:house'], shape='star', size=1.3)
b.quest('chisel', 'The Chisel', 2, -2, [TIP + 'Put blocks into a &eChisel&7 (Rechiseled) and pick one of many variants. Right-click with the chisel to open it.'],
        [item('rechiseled:chisel')], [give('minecraft:stone_bricks', 64)], deps=['start'])
b.quest('wand', 'Building Wand', 2, 0, [TIP + 'A &eBuilding Wand&7 extends a whole wall at once using blocks from your inventory. Sneak + scroll changes the mode.'],
        [item('constructionwand:iron_wand')], [give('minecraft:cobblestone', 64)], deps=['start'])
b.quest('effortless', 'Effortless Building', 4, -1, [TIP + 'Press &eAlt&7 (Effortless Building) for build modes: lines, walls, floors, cubes, circles and mirrors.'],
        [check('I tried a build mode')], [give('minecraft:glass', 32)], deps=['wand'])
b.quest('chalk', 'Chalk Marks', 2, 2, [TIP + 'Draw on any block with &eChalk&7. Glowing chalk shines in the dark - great for marking cave paths.'],
        [item('chalk:white_chalk')], [give('chalk:yellow_glow_chalk' if False else 'chalk:yellow_chalk')], deps=['start'], optional=True)
b.quest('macaw', 'Macaw\'s Collection', 4, 1, [TIP + 'Craft a piece from every Macaw\'s mod: a roof, a window, a bridge and a lamp.'],
        [item('#mcwroofs:roofs') if False else item('mcwroofs:oak_roof'), item('mcwwindows:oak_window'), item('mcwbridges:oak_log_bridge_middle')], [crate('common')], deps=['start'])
b.quest('lanterns', 'Light It Up', 6, 1, [TIP + '&eAdditional Lanterns&7 makes lanterns from every material and color.'],
        [item('additionallanterns:stone_lantern' if False else 'additionallanterns:amethyst_lantern', 4)], [give('minecraft:torch', 32)], deps=['macaw'], optional=True)
b.quest('dawn', 'Dawn of Time', 6, -1, [TIP + '&eDawn of Time&7 adds historic blocks from many cultures: Roman, Japanese, Persian, Gothic... Browse them in JEI.'],
        [check('I found a style I like')], [crate('common')], deps=['effortless', 'chisel'], optional=True)
b.quest('done', '&6Master Builder', 8, 0, [TIP + 'Show off your best build to a friend - then tick the box.'],
        [check('My dream build is done')], [crate('rare'), rxp(200)], deps=['dawn', 'lanterns'], any_dep=True, shape='star', size=1.3, icon='questsicons:quest_crown')

# =====================================================================================================
# Side path - Explorer's Atlas
a = B.chapter('atlas', '&3Explorer\'s Atlas', 'questsicons:icon_map', ['&7Biomes, structures and how to find them.'], PATHS, 'diamond')
a.quest('start', '&3Explorer\'s Atlas', 0, 0, [TIP + 'Terralith, Tectonic and Wilder Wild reshape the world. Hundreds of new structures wait out there.'],
        [item('minecraft:compass')], [give('minecraft:map', 4)], icon='questsicons:icon_map', deps=['prologue:map'], shape='star', size=1.3)
a.quest('nature', 'Nature\'s Compass', 2, -2, [TIP + 'Open the &eNature\'s Compass&7, pick any biome and it points the way.'],
        [item('naturescompass:naturescompass')], [rxp(60)], deps=['start'])
a.quest('explorer', 'Explorer\'s Compass', 2, 2, [TIP + 'The &eExplorer\'s Compass&7 does the same for structures: villages, taverns, towers, temples...'],
        [item('explorerscompass:explorerscompass')], [rxp(60)], deps=['start'])
a.quest('glider', 'Hang Glider', 4, 0, [TIP + 'Jump off a cliff with a &eHang Glider&7 and soar. Updrafts over fire lift you up.'],
        [item('hangglider:hang_glider')], [give('minecraft:feather', 16)], deps=['nature', 'explorer'], any_dep=True)
a.quest('village', 'A Village', 4, 2, [TIP + 'Find a village. &eTowns and Towers&7 and &eMoog\'s&7 structures make them bigger and more varied.'],
        [struct('#minecraft:village', 'Find a village')], [give('minecraft:emerald', 8)], deps=['explorer'])
a.quest('tavern', 'The Tavern', 6, 2, [TIP + 'Taverns (Dungeons and Taverns) have traders, food and a cartographer who sells maps to rare structures.'],
        [struct('#nova_structures:taverns' if False else 'nova_structures:tavern_birch', 'Find a tavern')], [crate('rare')], deps=['village'], optional=True)
a.quest('canyon', 'Bryce Canyon', 4, -2, [TIP + 'Terralith biomes can be breathtaking. Visit a canyon.'],
        [biome('terralith:bryce_canyon', 'Visit a Bryce Canyon')], [crate('common')], deps=['nature'], optional=True)
a.quest('graveyard', 'A Graveyard', 6, -2, [TIP + 'Graveyards (The Graveyard) are full of undead and loot. Some hide a crypt with a dangerous boss.'],
        [struct('graveyard:large_graveyard', 'Find a large graveyard')], [crate('rare')], deps=['canyon', 'glider'], any_dep=True, optional=True)
a.quest('done', '&3World Traveller', 8, 0, [TIP + 'Travel 10 km (walking, flying or boating).'],
        [stat('minecraft:walk_one_cm', 1000000, 'Walk 10 km')], [crate('epic'), rxp(300)], deps=['glider'], shape='star', size=1.3, icon='questsicons:quest_crown')

# =====================================================================================================
# Side path - Creatures and Companions
c = B.chapter('creatures', '&aCreatures & Companions', 'questsicons:icon_heart', ['&7Friends, foes and fearsome mutants.'], PATHS, 'heart')
c.quest('start', '&aCreatures & Companions', 0, 0, [TIP + '&eNaturalist&7, &eFriends&Foes&7, &eEcologics&7 and more fill the world with animals - and monsters.'],
        [check()], [rxp(30)], icon='questsicons:icon_heart', deps=['settler:animals'], shape='star', size=1.3)
c.quest('butterfly', 'Butterflies', 2, -2, [TIP + 'Catch a butterfly in a bucket... or just watch it. Naturalist animals react to you, sleep at night and hunt each other.'],
        [kill('naturalist:butterfly', 0) if False else observe('naturalist:butterfly', 40, entity=True, title='Watch a butterfly')], [give('minecraft:honey_bottle', 2)], deps=['start'])
c.quest('bear', 'Bear Country', 4, -2, [TIP + 'Bears guard their berries. Find one in a forest - from a safe distance.'],
        [observe('naturalist:bear', 40, entity=True, title='Spot a bear')], [give('minecraft:sweet_berries', 16)], deps=['butterfly'], optional=True)
c.quest('moobloom', 'Moobloom', 2, 2, [TIP + 'A cow covered in flowers (Friends&Foes). Bees love it.'],
        [observe('friendsandfoes:moobloom', 40, entity=True, title='Find a moobloom')], [give('minecraft:sunflower', 4)], deps=['start'], optional=True)
c.quest('penguin', 'Penguins', 4, 2, [TIP + 'Penguins waddle on cold beaches (Ecologics). Squirrels and coconut crabs live in warmer places.'],
        [observe('ecologics:penguin', 40, entity=True, title='Find a penguin')], [give('minecraft:cod', 8)], deps=['moobloom', 'start'], any_dep=True, optional=True)
c.quest('pet', 'A Loyal Friend', 2, 0, [TIP + 'Tame a wolf or cat. With &eRespawnable Pets&7 your pet comes back to life if it dies.'],
        [item('minecraft:bone', 8)], [give('minecraft:name_tag')], deps=['start'])
c.quest('mutant', 'Mutant Zombie', 6, 0, [TIP + '&eMutant Monsters&7 are huge, fast and dangerous. Defeat a Mutant Zombie - their drops make legendary gear like the Hulk Hammer.'],
        [kill('mutantmonsters:mutant_zombie')], [crate('epic')], deps=['pet'], shape='heart')
c.quest('lich', 'The Lich', 8, 0, [TIP + 'Deep in a crypt waits the &5Lich&7 (The Graveyard), the most dangerous undead of all.'],
        [kill('graveyard:lich')], [crate('legendary')], deps=['mutant'], shape='heart', size=1.4, optional=True)

# =====================================================================================================
# Loot crates (reward tables): what the crates in the rewards can contain. Balanced to help, not to skip.
B.table('common_crate', '&fCommon Crate', 'questsicons:common_crate', [
    ('minecraft:bread', 8, 20), ('minecraft:cooked_beef', 6, 15), ('minecraft:torch', 32, 20), ('minecraft:iron_ingot', 4, 15),
    ('minecraft:coal', 16, 15), ('minecraft:arrow', 24, 10), ('minecraft:bone_meal', 16, 10), ('minecraft:leather', 6, 8),
    ('minecraft:gold_ingot', 3, 8), ('minecraft:apple', 6, 10), ('minecraft:name_tag', 1, 2), ('minecraft:emerald', 3, 6),
    ('farmersdelight:rope', 12, 5), ('minecraft:lantern', 4, 6)])
B.table('rare_crate', '&9Rare Crate', 'questsicons:rare_crate', [
    ('minecraft:diamond', 2, 15), ('minecraft:emerald', 8, 15), ('minecraft:golden_apple', 2, 12), ('minecraft:ender_pearl', 4, 12),
    ('minecraft:iron_block', 2, 10), ('minecraft:gold_block', 1, 8), ('minecraft:saddle', 1, 6), ('minecraft:name_tag', 2, 6),
    ('minecraft:experience_bottle', 16, 10), ('minecraft:lapis_block', 2, 8), ('minecraft:obsidian', 8, 8), ('minecraft:trial_key', 1, 6),
    ('jewelry:ruby', 2, 5), ('jewelry:sapphire', 2, 5)])
B.table('epic_crate', '&5Epic Crate', 'questsicons:epic_crate', [
    ('minecraft:diamond', 5, 15), ('minecraft:netherite_scrap', 1, 10), ('minecraft:totem_of_undying', 1, 8),
    ('minecraft:enchanted_golden_apple', 1, 3), ('minecraft:diamond_block', 1, 8), ('minecraft:shulker_shell', 2, 8),
    ('minecraft:ancient_debris', 2, 8), ('minecraft:experience_bottle', 48, 12), ('minecraft:heart_of_the_sea', 1, 4),
    ('minecraft:nautilus_shell', 3, 5), ('minecraft:wither_skeleton_skull', 1, 4), ('minecraft:ominous_trial_key', 1, 5),
    ('minecraft:emerald_block', 2, 10)])
B.table('legendary_crate', '&6Legendary Crate', 'questsicons:legendary_crate', [
    ('minecraft:netherite_ingot', 2, 12), ('minecraft:totem_of_undying', 2, 12), ('minecraft:enchanted_golden_apple', 2, 10),
    ('minecraft:elytra', 1, 6), ('minecraft:nether_star', 1, 6), ('minecraft:beacon', 1, 4), ('minecraft:netherite_upgrade_smithing_template', 2, 8),
    ('minecraft:diamond_block', 4, 12), ('minecraft:heavy_core', 1, 3), ('minecraft:music_disc_pigstep', 1, 4), ('minecraft:dragon_breath', 8, 5)])

if os.path.exists(os.path.join(os.path.dirname(__file__), 'dc_quests_raft.py')):
    exec(open(os.path.join(os.path.dirname(__file__), 'dc_quests_raft.py')).read())

# Story chapters first, then side paths (sidebar order).
order = ['prologue', 'settler', 'deep', 'industry', 'power', 'nether', 'sea', 'end', 'epilogue', 'kitchen', 'builder', 'atlas', 'creatures']
B.chapters.sort(key=lambda ch: order.index(ch.key) if ch.key in order else 99)

DATA = {'title': '&dDreamcraft &7- Quest Book', 'icon': 'questsicons:quest_book', 'default_quest_shape': 'circle',
        'default_reward_team': False, 'give_book_on_first_join': True}

if __name__ == '__main__':
    out = sys.argv[1]
    B.write(out, DATA)
    n = sum(len(c.quests) for c in B.chapters)
    print('chapters', len(B.chapters), 'quests', n)
