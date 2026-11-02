# Chapter 6 - The Endless Sea (the Raft mod). Executed inside dc_quests.py (shares its names).
r = B.chapter('sea', '&b6. The Endless Sea', 'questsicons:icon_raft', ['&7A drowned dream: rafts, sharks and floating treasure.'], STORY, 'hexagon')
r.quest('start', '&bThe Endless Sea', 0, 0, [
    KEEPER + '"Part of the Dream has drowned. Only an ocean is left, and the people who lived there now drift on rafts."',
    '',
    TIP + 'This chapter is the &eRaft&7 mod: a whole dimension of open sea, inspired by the survival game Raft. To get there you need a portal of &edriftwood&7, lit with an &eEnergy Staff&7.'],
    [item('minecraft:fishing_rod')], [give('minecraft:cod', 6)], icon='questsicons:icon_raft', deps=['settler:done'], shape='star', size=1.5)
r.quest('ring', 'Ancient Broken Ring', 2, -2, [
    TIP + 'Strange old rings lie on the sea floor of the Dream. You can find them in &eshipwreck treasure&7, &eburied treasure&7, &eocean ruins&7 - and sometimes while fishing.'],
    [item('raft:ancient_broken_ring')], [give('minecraft:map', 2)], deps=['start'])
r.quest('energy', 'Ancient Energy', 4, -2, [TIP + 'Smelt the ring. What is left is pure &eAncient Energy&7.'],
        [item('raft:ancient_energy', 3)], [rxp(80)], deps=['ring'])
r.quest('crystal', 'Ancient Crystal', 2, 2, [TIP + 'Shipwreck treasure chests often hold an &eAncient Crystal&7. Look for wrecks on beaches and in oceans.'],
        [item('raft:ancient_crystal')], [give('minecraft:heart_of_the_sea') if False else rxp(80)], deps=['start'])
r.quest('driftwood', 'Driftwood', 4, 2, [
    TIP + 'Dark &eDriftwood&7 stumps stand on sandy beaches. Chop the logs - you will need plenty.'],
    [item('raft:driftwood_log', 12)], [give('raft:driftwood_sapling', 2) if False else give('minecraft:bone_meal', 16)], deps=['start'])
r.quest('staff', 'The Energy Staff', 6, -1, [TIP + 'An &eEnergy Staff&7 channels ancient energy. It lights the portal to the sea.'],
        [item('raft:energy_staff')], [give('minecraft:glowstone_dust', 8)], deps=['energy', 'crystal'], shape='diamond')
r.quest('frame', 'Portal Frames', 6, 1, [
    TIP + 'Four driftwood logs around one ancient energy give &e4 Driftwood Portal Frames&7. Build a frame like a nether portal (at least 4 wide and 5 high, corners not needed).'],
    [item('raft:driftwood_portal_frame', 10)], [rxp(100)], deps=['energy', 'driftwood'])
r.quest('enter', '&bBeyond the Horizon', 8, 0, [
    KEEPER + '"Breathe in. Smell the salt? Welcome to the Endless Sea."',
    '',
    TIP + 'Right-click the frame with the Energy Staff and step through. You arrive on a small driftwood platform high above the waves.'],
    [dim('raft:raftdim', 'Enter the Raft dimension')], [give('raft:rope', 8), give('raft:raft_foundation', 8)], deps=['staff', 'frame'], shape='star', size=1.4,
    icon='raft:driftwood_portal_frame')
r.quest('rope', 'Rope', 10, -3, [TIP + 'Two palm leaves (or string) make &eRope&7. Palm leaves sometimes drop rope by themselves.'],
        [item('raft:rope', 8)], [give('minecraft:string', 8)], deps=['enter'])
r.quest('foundation', 'Expand the Raft', 12, -3, [
    TIP + '&eRaft Foundations&7 (planks bound with rope) float your base. &eReinforced Foundations&7 are sturdier.'],
    [item('raft:raft_foundation', 32)], [give('raft:palm_thatch', 16)], deps=['rope'])
r.quest('catcher', 'Item Catcher', 10, -1, [
    TIP + 'Debris drifts past you all the time: planks, palm leaves, plastic and scrap. An &eItem Catcher&7 in the water catches it for you.',
    TIP + 'Put a &eNet&7 into it and it also fishes &eUnrefined Ocean Garbage&7 out of the sea. Smelt it into a &eTrash Cube&7 and right-click to see what is inside.'],
    [item('raft:item_catcher'), item('raft:net')], [give('raft:plastic', 8)], deps=['enter'], shape='hexagon', icon='raft:net')
r.quest('hook', 'Plastic Hook', 12, -1, [TIP + 'Hold right-click with the &ePlastic Hook&7 to pull floating debris to you, like in the real game.'],
        [item('raft:plastic_hook')], [give('raft:scrap_metal', 6)], deps=['catcher'])
r.quest('water', 'Fresh Water', 10, 1, [
    TIP + 'Sea water is no good. A &eWater Purifier&7 turns water bottles into &eFresh Water&7 (a bucket gives three). Fresh water fills you up a little.'],
    [item('raft:water_purifier'), item('raft:fresh_water', 3)], [give('minecraft:glass_bottle', 8)], deps=['enter'])
r.quest('grill', 'Simple Grill', 12, 1, [TIP + 'The &eSimple Grill&7 cooks two foods at once, 50% faster than a campfire. It burns planks, logs or coal.'],
        [item('raft:simple_grill')], [give('minecraft:cod', 8)], deps=['water'])
r.quest('farm', 'A Floating Farm', 10, 3, [
    TIP + '&eCrop Plots&7 are always watered and can never be trampled - perfect for a raft. A &eScarecrow&7 keeps monsters from spawning within 24 blocks and protects crops around it.'],
    [item('raft:crop_plot', 4), item('raft:scarecrow')], [give('raft:coconut', 4)], deps=['water'])
r.quest('drinks', 'Island Drinks', 12, 3, [TIP + 'Coconut milk heals over time. A Piña Colada... well, try it.'],
        [item('raft:coconut_milk'), item('raft:pina_colada')], [crate('common')], deps=['farm'], optional=True)
r.quest('shark', '&cBruce', 14, -2, [
    KEEPER + '"Something circles your raft. It is patient. It is hungry."',
    '',
    TIP + '&cBruce the shark&7 attacks swimmers. Defeat him for shark meat and teeth - and keep your feet out of the water.'],
    [kill('raft:shark')], [give('raft:cooked_shark_meat', 4), crate('rare')], deps=['hook'], shape='heart', size=1.3)
r.quest('trophy', 'Shark Trophy', 16, -2, [TIP + 'Hang a &eShark Jaw Trophy&7 on your wall. Bruce would be proud.'],
        [item('raft:shark_jaw_trophy')], [rxp(100)], deps=['shark'], optional=True)
r.quest('receiver', 'Receiver', 14, 0, [
    TIP + 'Right-click the &eReceiver&7 to get the direction and distance to the nearest floating driftwood. Out at sea it is the best source of driftwood logs.'],
    [item('raft:receiver')], [rxp(150)], deps=['hook', 'grill'])
r.quest('island', 'Driftwood Ahoy!', 16, 0, [TIP + 'Follow the receiver to the floating driftwood and haul the logs aboard. On the way, dive down: shipwrecks on the sea floor hide treasure.'],
        [item('raft:driftwood_log', 16)], [crate('rare')], deps=['receiver'], shape='diamond')
r.quest('paddle', 'Paddle Power', 14, 2, [TIP + 'In a boat, right-click with a &ePaddle&7 for a push forward. Island hopping made easy.'],
        [item('raft:paddle')], [give('minecraft:oak_boat') if False else rxp(80)], deps=['grill'])
r.quest('titanium', 'Titanium', 18, 0, [TIP + 'Titanium ore hides deep under the sea floor - you need a diamond pickaxe. The &eMetal Detector&7 tells you how deep it is. Smelt the raw titanium into ingots.'],
        [item('raft:titanium_ingot', 12)], [crate('rare')], deps=['island'])
r.quest('armor', 'Titanium Armor', 20, -1.5, [TIP + 'A full set of titanium armor is as strong as diamond and gives Water Breathing, Dolphin\'s Grace and Conduit Power.'],
        [item('raft:titanium_helmet'), item('raft:titanium_chestplate'), item('raft:titanium_leggings'), item('raft:titanium_boots')],
        [crate('epic')], deps=['titanium'], optional=True)
r.quest('solar', 'Sun Power', 20, 1.5, [
    TIP + 'Raft has its own energy: a &eMakeshift Solar Panel&7 makes 10 FE per tick, a &eMakeshift Battery&7 stores 1,000,000 FE, cables carry it - and they also work with Tech Reborn machines.'],
    [item('raft:makeshift_solar_panel'), item('raft:makeshift_battery')], [give('raft:copper_cable', 16)], deps=['titanium'])
r.quest('quarry', 'Raft Quarry', 22, 1.5, [TIP + 'The raft &eQuarry&7 mines an 11x11 area for 1000 FE per block.'],
        [item('raft:quarry')], [crate('epic')], deps=['solar'], optional=True)
r.quest('discs', 'Songs of the Sea', 18, 3, [TIP + 'Three music discs hide in shipwrecks. Collect them all.'],
        [item('raft:lofi_beat_music_disc'), item('raft:crystal_castles_music_disc'), item('raft:some_game_music_music_disc')],
        [crate('epic')], deps=['island'], optional=True)
r.quest('done', '&bMaster of the Sea', 24, 0, [KEEPER + '"The sea respects you now. The Dream is almost whole."'],
        [item('raft:raft_flag')], [crate('epic'), rxp(400)], deps=['titanium', 'shark'], shape='star', size=1.5, icon='questsicons:quest_crown')
