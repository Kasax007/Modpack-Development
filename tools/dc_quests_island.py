# Side path - Island Life (Beach Craft 3.2 and 3.3, mod id raft). Executed inside dc_quests.py (shares its names).
# Facts follow the mod's changelogs 3.2.0 and 3.3.0 (Kasax_Raft_Mod docs/curseforge) and its almanac.
# The Scavenger Chief and the Reef Warden are elite scavengers and reef guardians (no entity type of their own), so
# their quests are a checkbox.
# Layout: the start in the middle; danger (guards and mini-bosses) below it, sailing to the right, cozy living above,
# the island kitchen at the top, gear and gadgets to the left.

il = B.chapter('island', '&bIsland Life', 'raft:thatch_parasol',
               ['&7Guards and pirates, sails and anchors, a cozy home, an island kitchen and new gear.'], PATHS, 'hexagon')
il.quest('start', '&bIsland Life', 0, 0, [
    KEEPER + '"The sea is more than a road to the Leviathan, Dreamer. Stay a while."',
    '',
    TIP + 'This path shows what the islands of the &bEndless Sea&7 offer besides the story: guarded places and their captains, a sail for your own raft, a cozy home that heals you, crops and a kitchen, and gear for an islander.'],
    [check('Off to the islands')], [rxp(30)], deps=['sea:castaway'], shape='star', size=1.3, icon='raft:thatch_parasol')

# --------------------------------------------------------------------------------------------- danger (below)
il.quest('guards', 'Guarded Places', 1.8, 1.8, [
    TIP + 'Most places of the sea are guarded. The first time you come close, a warning sounds - a shout, a horn, the hum of the reef - and two seconds later the guards appear around the unopened chests.',
    TIP + 'The guards get tougher the further the story leads you: scavengers with fists, wooden blades or bows at the start, stone blades and reef guardians in the middle, corsair crews at the end. Easy has one guard less, Hard one more; Saltmere, the castaway camp and the sanctum stay quiet.'],
    [kill('raft:scavenger', 3)], [give('raft:gold_coin', 6), rxp(80)], deps=['start'], icon='raft:scavenger_spawn_egg')
il.quest('reef_guardian', 'Reef Guardians', 3.6, 1.8, [
    TIP + 'A &eReef Guardian&7 is a guardian overgrown with coral. It charges its beam for a few seconds before it hits - watch the glow and break its line of sight. Its spikes hurt.',
    TIP + 'They guard the sunken ruins, the wrecks, the Helix Station, the rusted rigs and the Coral Temple. They drop prismarine, sea glass and pearls.'],
    [kill('raft:reef_guardian', 2)], [give('minecraft:prismarine_shard', 8), rxp(100)], deps=['guards'], icon='raft:reef_guardian_spawn_egg')
il.quest('chief', 'The Scavenger Chief', 3.6, 3.4, [
    TIP + 'The elite of a scavenger gang wears iron armour and swings an iron sword. He guards the rusted rig and Port Solace, with a boss bar of his own.',
    TIP + 'He drops gold, scrap metal and often a harpoon gun.'],
    [check('Defeat the Scavenger Chief')], [crate('rare'), rxp(150)], deps=['guards'], optional=True, icon='minecraft:iron_sword')
il.quest('captain', 'The Corsair Captain', 5.4, 1.8, [
    TIP + 'Saltjaw\'s cove and the galleon wreck are held by corsair crews and their &eCorsair Captain&7: bigger, armoured, with a cutlass. At half health he blows his horn, and two corsairs climb out of the deep to help him.',
    TIP + 'He always drops his cutlass and a purse of gold, often a harpoon.'],
    [kill('raft:corsair_captain')], [crate('rare'), give('raft:gold_coin', 12)], deps=['reef_guardian'], optional=True, icon='raft:cutlass')
il.quest('warden', 'The Reef Warden', 7.2, 1.8, [
    TIP + 'A huge reef guardian keeps the &5Coral Temple&7: 80 health, armour 8 and a beam that hits for 7. Fight it from cover and strike while its beam charges elsewhere.',
    TIP + 'It drops pearls, sea glass, prismarine and now and then Ancient Energy.'],
    [check('Defeat the Reef Warden')], [crate('epic'), rxp(250)], deps=['captain'], optional=True, icon='raft:reef_guardian_spawn_egg')

# --------------------------------------------------------------------------------------------- sailing (right)
il.quest('mast', 'Sail and Mast', 1.8, 0, [
    TIP + 'For a raft you built yourself (see &bYour Own Raft&7 in the Endless Sea): a &eMast&7 is a pole you stack as high as you like. Set &eSails&7 next to it, side by side and on top of each other: they join into one big sheet, and every block of sail adds wind power.',
    TIP + 'Use a sail with an empty hand to furl it - the canvas rolls up under the yard and the raft no longer catches the wind. Use it again to set it.'],
    [item('raft:mast', 4), item('raft:sail', 4)], [give('raft:rope', 8), rxp(80)], deps=['start'], icon='raft:sail')
il.quest('winch', 'Anchor Winch', 3.6, 0, [
    TIP + 'Set an &eAnchor Winch&7 on the deck edge, anchor over the side. Use it to drop the anchor: a sailing raft stops and holds its position, even when the helmsman pushes on. Use it again to raise it and sail on.',
    TIP + 'To moor, use the wheel while you steer (or sneak and use it): the raft becomes blocks again.'],
    [item('raft:anchor_winch')], [give('minecraft:iron_ingot', 4), rxp(80)], deps=['mast'])

# --------------------------------------------------------------------------------------------- cozy living (above)
il.quest('comfort', 'Make Yourself at Home', 1.8, -1.8, [
    TIP + 'Sit on any seat or cushion, or lie in a hammock or bed: after 3 seconds you are &eRested&7. You heal half a heart every 4 seconds and get hungry 25% slower.',
    TIP + 'Rested lasts 2 minutes plus 1 minute per comfort point. Every kind of cozy thing within 6 blocks adds one: seats, tables, lights, fires, rugs, plants, shade, music, storage, wall decor and a view of the water. The old decorations count too.'],
    [item('raft:palm_bench'), item('raft:hurricane_lantern')], [give('raft:shell_candle', 2), rxp(60)], deps=['start'], icon='raft:palm_bench')
il.quest('music', 'Island Music', 3.6, -1.8, [
    TIP + 'The &eSteel Drum&7 plays the next note of an island tune with every right-click or redstone pulse. The &eConch Shell&7 blows a horn that carries far over the water. Both count as music for your comfort.'],
    [item('raft:steel_drum'), item('raft:conch_shell')], [rxp(60)], deps=['comfort'], optional=True)
il.quest('storage', 'Shelves and Baskets', 0, -1.8, [
    TIP + 'Palm, teak and weathered &eShelves&7 show three items and work like vanilla shelves. The &eWicker Basket&7 holds 9 stacks and keeps them when you pick it up, like a shulker box.',
    TIP + 'Put a &eServing Plate&7 on a table: it holds up to 4 portions of one food. Right-click with an empty hand to eat one when you are hungry.'],
    [item('raft:wicker_basket'), item('raft:serving_plate')], [rxp(60)], deps=['comfort'], optional=True)

# --------------------------------------------------------------------------------------------- the island kitchen (top)
il.quest('crops', 'Island Crops', 1.8, -3.6, [
    TIP + 'Wild &eSweet Potatoes&7, &eChili&7, &eBananas&7 and &eRice&7 grow on the palm, jungle, mangrove and volcanic isles (in newly explored chunks). Seeds also come with flotsam barrels, supply barrels, island chests and overworld shipwrecks.',
    TIP + 'Plant them on farmland or a crop plot; each has four stages. A raw chili gives 10 seconds of Fire Resistance.'],
    [item('raft:sweet_potato'), item('raft:chili_pepper'), item('raft:banana'), item('raft:rice')], [give('minecraft:bone_meal', 16), rxp(80)],
    deps=['comfort'], icon='raft:banana')
il.quest('sea_grapes', 'Sea Grapes', 0, -3.6, [
    TIP + '&eSea Grapes&7 grow under water in the Coral Shallows and the Glowing Lagoon. Plant them on sand or gravel in the sea; when ripe, right-click to pick 2 or 3 bunches - they grow back.'],
    [item('raft:sea_grapes', 3)], [rxp(60)], deps=['crops'], optional=True)
il.quest('pot', 'The Cooking Pot', 3.6, -3.6, [
    TIP + 'Set the &eCooking Pot&7 on a campfire, fire, brazier, simple grill, magma or lava and add the ingredients one by one: it only takes what fits a dish and tells you what is still missing. It cooks in 10 seconds; serve with bowls. Sneak-use with an empty hand gives everything back.',
    TIP + '&eIsland Curry&7: cooked rice, chili, sweet potato and coconut (3 bowls, Regeneration). &eSeafood Chowder&7: a fish, crab claw or eel fillet, sweet potato, kelp and sea grapes (3 bowls, Water Breathing).'],
    [item('raft:cooking_pot'), item('raft:island_curry')], [give('minecraft:bowl', 8), rxp(100)], deps=['crops'], icon='raft:island_curry')
il.quest('trap', 'Fish Trap', 5.4, -3.6, [
    TIP + 'Put a &eFish Trap&7 in open water (at least 12 water blocks around it). Every 1 to 2 minutes it catches cod, salmon, tropical fish, crab claws, shells, kelp or sea grapes. Bait inside makes it twice as fast, and hoppers can empty it.'],
    [item('raft:fish_trap')], [give('raft:fish_bait', 8), rxp(80)], deps=['pot'])

# --------------------------------------------------------------------------------------------- gear and gadgets (left)
il.quest('boomerang', 'Driftwood Boomerang', -1.8, 1.8, [
    TIP + 'Throw the &eDriftwood Boomerang&7: it flies about 18 blocks, hits for 5 and comes back to you, even through walls. On the way it picks up to 3 stacks of floating items, so it fetches debris from the water.'],
    [item('raft:boomerang')], [rxp(80)], deps=['start'])
il.quest('blades', 'Machete and Spear', -3.6, 1.8, [
    TIP + 'The &eMachete&7 swings fast (5.5 damage) and cuts leaves, plants, bamboo, vines and crops in a blink. The &eShark Tooth Spear&7 jabs and charges like any spear, as strong as an iron one.'],
    [item('raft:machete'), item('raft:shark_tooth_spear')], [rxp(100)], deps=['boomerang'], optional=True)
il.quest('shell_armor', 'Shell Armour', -1.8, -1.8, [
    TIP + '&eShell Armour&7 from seashells: 13 armour points, between chainmail and iron, with a little toughness. The full set gives Resistance I while you are in water.'],
    [item('raft:shell_helmet'), item('raft:shell_chestplate'), item('raft:shell_leggings'), item('raft:shell_boots')], [crate('rare')], deps=['start'],
    icon='raft:shell_chestplate')
il.quest('explorer', 'Explorer\'s Outfit', -3.6, -1.8, [
    TIP + 'Hat, jacket, trousers and boots from sail canvas: 7 armour points like leather. The full outfit makes you 10% faster and gives Luck I for better fishing and loot.'],
    [item('raft:explorer_helmet'), item('raft:explorer_chestplate'), item('raft:explorer_leggings'), item('raft:explorer_boots')], [crate('rare')],
    deps=['shell_armor'], optional=True, icon='raft:explorer_helmet')
il.quest('finders', 'Finders Keepers', -1.8, 0, [
    TIP + 'Right-click the &eWreck Compass&7 and its needle turns to the nearest shipwreck within about 1000 blocks - galleons, cargo ships, fishing boats, sunken planes and overworld wrecks - and it tells you how far it is.',
    TIP + 'The &eCaptain\'s Spyglass&7 zooms twice as far as a spyglass and shows the distance to what you look at.'],
    [item('raft:wreck_compass'), item('raft:captains_spyglass')], [rxp(100)], deps=['start'], icon='raft:wreck_compass')
il.quest('lure', 'Tackle Box', -3.6, 0, [
    TIP + 'Craft a &eDriftwood Fishing Rod&7 (3 driftwood planks, 2 string) and sneak-use it: its &etackle box&7 has one slot for &eFish Bait&7 and one for &eGolden Lures&7. Every cast uses one of each that is loaded.',
    TIP + 'Bait makes fish bite sooner (like Lure I); the Golden Lure also brings better treasure (like Luck of the Sea II). A plain rod still uses them from your off hand or bag.'],
    [item('raft:driftwood_fishing_rod'), item('raft:golden_lure')], [give('raft:fish_bait', 16)], deps=['finders'], optional=True,
    icon='raft:driftwood_fishing_rod')
