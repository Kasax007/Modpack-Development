# Chapter 6 - The Endless Sea (Beach Craft 3.0, mod id raft). Executed inside dc_quests.py (shares its names).
# Facts and numbers follow the mod's own guide (Kasax_Raft_Mod tools/content/guide/texts.py) and docs/design/beachcraft3.md.
# Layout: the story runs along y=0 (sigils one row above), life on the raft above it, sailing, diving and the places of
# the sea below it, building in the top-left corner, creatures in the bottom-left corner, technology in the top right.


def almanac(page):
    """A Seafarer's Almanac that opens at one chapter or page (custom data {almanac:"<chapter>[/<page>]"})."""
    return {'id': 'raft:seafarers_almanac', 'components': {'minecraft:custom_data': {'almanac': page}}}


r = B.chapter('sea', '&b6. The Endless Sea', 'questsicons:icon_raft',
              ['&7A drowned dream: rafts, reefs and wrecks.'], STORY, 'hexagon')
SEA = '&3'   # the sea's own colour for place names in descriptions

# --------------------------------------------------------------------------------------------- the way there (overworld)
r.quest('start', '&bThe Endless Sea', 0, 0, [
    KEEPER + '"Part of the Dream has drowned. Only an ocean is left: islands, reefs and wrecks, and the people who once lived there are gone."',
    '',
    TIP + 'This chapter is &eBeach Craft&7: a whole ocean dimension with islands, coral reefs and deep trenches, its own creatures, a story and a boss at the bottom of the sea.',
    TIP + 'To get there you need a portal of &edriftwood&7, lit with an &eEnergy Staff&7. Its parts come from the oceans of the overworld.'],
    [item('minecraft:fishing_rod')], [give('minecraft:cod', 6)], icon='questsicons:icon_raft', deps=['settler:done'], shape='star', size=1.5)
r.quest('ring', 'Ancient Broken Ring', 1.5, -1.2, [
    TIP + 'Strange old rings lie on the sea floor of the Dream. You find them in &eshipwreck treasure&7, &eburied treasure&7 and &eocean ruins&7 - and sometimes they bite on your fishing line.'],
    [item('raft:ancient_broken_ring')], [give('minecraft:map', 2)], deps=['start'])
r.quest('crystal', 'Ancient Crystal', 3, 0, [TIP + 'Shipwreck treasure chests often hold an &eAncient Crystal&7. Look for wrecks on beaches and in oceans.'],
        [item('raft:ancient_crystal')], [rxp(80)], deps=['start'])
r.quest('energy', 'Ancient Energy', 3, -1.2, [TIP + 'Smelt the ring. What is left is pure &eAncient Energy&7. You need one for the staff and one for every four portal frames.'],
        [item('raft:ancient_energy', 3)], [rxp(80)], deps=['ring'])
r.quest('driftwood', 'Driftwood', 1.5, 1.2, [
    TIP + 'Short, dark &eDriftwood&7 stumps stand on sandy beaches. Chop the logs - you will need plenty.'],
    [item('raft:driftwood_log', 12)], [give('minecraft:bone_meal', 16)], deps=['start'])
r.quest('staff', 'The Energy Staff', 4.5, -1.2, [
    TIP + 'Ancient Energy on top, an Ancient Crystal in the middle and a stick at the bottom: the &eEnergy Staff&7 channels ancient energy. It lights portals 64 times.'],
    [item('raft:energy_staff')], [give('minecraft:glowstone_dust', 8)], deps=['energy', 'crystal'], shape='diamond')
r.quest('frame', 'Portal Frames', 4.5, 1.2, [
    TIP + 'Four driftwood logs around one Ancient Energy make &e4 Driftwood Portal Frames&7. Build the frame like a nether portal, with at least 2 by 3 empty blocks inside.'],
    [item('raft:driftwood_portal_frame', 10)], [rxp(100)], deps=['driftwood'])
r.quest('enter', '&bBeyond the Horizon', 6, 0, [
    KEEPER + '"Breathe in. Smell the salt? Welcome to the Endless Sea."',
    '',
    TIP + 'Right-click the frame with the Energy Staff and step through. You land on a driftwood platform high above the waves, with a portal back home.',
    TIP + 'On a new platform a castaway\'s chest is waiting for you. Open it!',
    TIP + 'Later, the &eRaft Dimension Teleporter&7 (5 titanium ingots and 2 Ancient Energy) takes you to the sea and back home without a portal, 64 times.'],
    [dim('raft:raftdim', 'Enter the Endless Sea')], [give('raft:rope', 8), give('raft:raft_foundation', 8)], deps=['staff', 'frame'], shape='star', size=1.4,
    icon='raft:driftwood_portal_frame')

# --------------------------------------------------------------------------------------------- the story: Tides of the Deep
STORY_TIP = TIP + 'Every story chest holds a chart to the next place. Lost it? Sneak and use the &eExpedition Journal&7 at sea for a fresh chart (once every 5 minutes).'
r.quest('castaway', 'The Castaway', 7.6, 0, [
    KEEPER + '"Someone was here before you. They left you a chest."',
    '',
    TIP + 'Open the chest on your arrival platform: a note, a chart, food, a paddle, a hook and the &eExpedition Journal&7.',
    TIP + 'Use the journal to read your current goal and a hint. It follows your progress by itself.',
    TIP + 'Your platform is older than Beach Craft 3? Then craft the journal: a book, a compass and paper.',
    '',
    TIP + 'The story chapters of the sea follow below, one quest each. Reward: an almanac that opens at its spoiler-free story chapter.'],
    [adv('raft:story/castaway', 'Find the Expedition Journal')], [give(almanac('story')), rxp(100)], deps=['enter'], icon='raft:expedition_journal')
r.quest('lighthouse', 'Keeper of the Light', 9.4, 0, [
    TIP + 'Follow the chart from the castaway chest to the ' + SEA + 'Old Lighthouse&7 on a rocky isle. Climb it, look around and read what the keeper left behind.',
    '', STORY_TIP],
    [adv('raft:story/lighthouse', 'Reach the Old Lighthouse')], [crate('common'), rxp(100)], deps=['castaway'], icon='raft:lighthouse_lens')
r.quest('saltmere', 'Saltmere', 11.2, 0, [
    TIP + 'The next chart leads to ' + SEA + 'Saltmere&7, a fishing village on stilts above a glowing reef. Walk its decks and huts, and take what was left for whoever comes next - a &eDiving Helmet&7 among it.'],
    [adv('raft:story/saltmere', 'Visit Saltmere')], [crate('common'), rxp(150)], deps=['lighthouse'], icon='raft:paper_lantern_orange')
r.quest('coral_sigil', 'The Coral Sigil', 11.2, -1.5, [
    TIP + 'The first of four &eTide Sigils&7 is kept somewhere in Saltmere. Sigils are too precious to lose: dropped, they never despawn, burn or explode.'],
    [adv('raft:story/coral_sigil', 'Take the Coral Sigil')], [rxp(200)], deps=['saltmere'], icon='raft:coral_sigil', shape='diamond')
r.quest('helix', 'Deep Science', 13, 0, [
    TIP + 'Now the story goes below the waves: dive to ' + SEA + 'Helix Research Station&7 on the sea floor. Wear the helmet, bring an &eOxygen Tank&7 and a light - the deep is dark. Look for the airlock.'],
    [adv('raft:story/helix', 'Dive to Helix Research Station')], [crate('rare'), rxp(200)], deps=['saltmere'], icon='raft:research_terminal')
r.quest('pearl_sigil', 'The Pearl Sigil', 13, -1.5, [
    TIP + 'The second sigil is locked away inside the station. Read the &eResearch Terminals&7: the people of Helix wrote down a lot.'],
    [adv('raft:story/pearl_sigil', 'Recover the Pearl Sigil')], [rxp(250)], deps=['helix', 'coral_sigil'], icon='raft:pearl_sigil', shape='diamond')
r.quest('port_solace', 'The Drowned City', 14.8, 0, [
    TIP + SEA + 'Port Solace&7 lies on the drowned shelf, a whole city under water. Its towers reach up to the surface. Its streets are not empty, so come prepared.'],
    [adv('raft:story/port_solace', 'Explore Port Solace')], [crate('rare'), rxp(250)], deps=['helix'], icon='raft:asphalt_line')
r.quest('storm_sigil', 'The Storm Sigil', 14.8, -1.5, [
    TIP + 'The third sigil waits in the city. A hint: look up, not down.'],
    [adv('raft:story/storm_sigil', 'Claim the Storm Sigil')], [rxp(300)], deps=['port_solace', 'pearl_sigil'], icon='raft:storm_sigil', shape='diamond')
r.quest('ashen_forge', 'Through Fire', 16.6, 0, [
    TIP + 'On a volcanic isle of black sand and ash stands the ' + SEA + 'Ashen Forge&7. Lava runs through its halls and ember crabs guard it: bring Fire Resistance.'],
    [adv('raft:story/ashen_forge', 'Enter the Ashen Forge')], [crate('rare'), rxp(300)], deps=['port_solace'], icon='raft:glowing_tidestone')
r.quest('ember_sigil', 'The Ember Sigil', 16.6, -1.5, [
    TIP + 'The last sigil is hidden deep in the forge. Mind the lava!'],
    [adv('raft:story/ember_sigil', 'Carry the Ember Sigil out')], [rxp(350)], deps=['ashen_forge', 'storm_sigil'], icon='raft:ember_sigil', shape='diamond')
r.quest('coral_temple', 'The Coral Temple', 18.4, 0, [
    TIP + 'On the reef floor an old temple of the Tidewardens is overgrown with coral: the ' + SEA + 'Coral Temple&7. Moray eels live in its walls.'],
    [adv('raft:story/coral_temple', 'Find the Coral Temple')], [crate('epic'), rxp(350)], deps=['ashen_forge'], icon='raft:tidestone_pillar')
r.quest('key', 'The Tidewarden Key', 18.4, -1.5, [
    TIP + 'Put the four sigils into the &eTidewarden Altar&7 one by one. With all four inside it forges the &eTidewarden Key&7. The key is never used up; a key for a friend needs four new sigils.'],
    [adv('raft:story/tidewarden_key', 'Forge the Tidewarden Key')], [rxp(400)], deps=['coral_temple', 'ember_sigil'], icon='raft:tidewarden_key', shape='diamond', size=1.3)
r.quest('sanctum', 'The Abyssal Sanctum', 20.2, 0, [
    TIP + 'The last chart leads into the deepest trench. The ' + SEA + 'Abyssal Sanctum&7 is closed by a shimmering &eTide Seal&7 that nothing can break - only the key opens it.',
    TIP + 'Bring your best gear, food, a full tank and the helmet lamp. What waits inside is no ordinary sea creature.'],
    [adv('raft:story/abyssal_sanctum', 'Reach the Abyssal Sanctum')], [crate('epic'), rxp(400)], deps=['key'], icon='raft:tide_seal')
r.quest('leviathan', '&bThe Leviathan', 22, 0, [
    KEEPER + '"Here it is, Dreamer. The nightmare that drowned the sea."',
    '',
    TIP + 'Use the &eTidewarden Key&7 on the &eLeviathan Altar&7 at the edge of the pool to wake it, and fight on the stone ring around the water.',
    TIP + 'It cannot be hurt while it circles deep in the pool. When it lies stranded after a leap, strike! The almanac has a full chapter on the fight (it warns you first).'],
    [adv('raft:story/leviathan', 'Defeat the Leviathan')], [crate('legendary'), levels(20)], deps=['sanctum'], shape='heart', size=1.8, icon='raft:leviathan_trophy')
r.quest('heart', '&dHeart of the Tide', 24, 0, [
    TIP + 'The Leviathan leaves the &eHeart of the Tide&7, its scales and a trophy. Placed as a block, the heart gives every swimmer within 32 blocks Conduit Power and Dolphin\'s Grace.',
    TIP + 'To fight again (or with friends), bring the key and an Ancient Crystal to the altar.',
    '',
    STAR + 'the Heart of the Tide is one of its ingredients. Keep it, or pick it up again for the epilogue.'],
    [item('raft:heart_of_the_tide')], [crate('epic'), rxp(500)], deps=['leviathan'], shape='star', size=1.4, icon='raft:heart_of_the_tide')
r.quest('tidebreaker', 'Tidebreaker', 24, -1.8, [
    TIP + 'Four &eLeviathan Scales&7, a titanium ingot and a trident make the &eTidebreaker&7: 9 damage, +50% against sea creatures, and in water or rain you hold use to surge ahead.'],
    [item('raft:tidebreaker')], [crate('epic')], deps=['heart'], optional=True)
r.quest('done', '&bMaster of the Sea', 24, 1.8, [
    KEEPER + '"The sea is calm again. Raise your flag, keeper of the tides - the Dream is almost whole."'],
    [item('raft:raft_flag')], [crate('epic'), rxp(400)], deps=['heart'], shape='star', size=1.5, icon='questsicons:quest_crown')

# --------------------------------------------------------------------------------------------- life on the raft (top)
r.quest('almanac', 'The Seafarer\'s Almanac', 6.2, -3, [
    TIP + 'The moment you arrive, a &eSeafarer\'s Almanac&7 lands in your bag: the guide to the sea, from rafts and diving to every creature. Click a chapter to open it.',
    TIP + 'Lost it? Craft a new one from a book and kelp or driftwood. Some quests here give you an almanac that opens right at the page you need.'],
    [item('raft:seafarers_almanac')], [rxp(50), give('raft:fresh_water', 3)], deps=['enter'], icon='raft:seafarers_almanac', shape='diamond')
r.quest('rope', 'Rope', 7.8, -3, [TIP + 'Two palm leaves or three string make &eRope&7. Palm leaves sometimes drop rope by themselves.'],
        [item('raft:rope', 8)], [give('minecraft:string', 8)], deps=['almanac'])
r.quest('foundation', 'Expand the Raft', 9.4, -3, [
    TIP + 'Seven planks with rope in the top and bottom middle make &e4 Raft Foundations&7. They float, so build your raft outwards from the platform.'],
    [item('raft:raft_foundation', 32)], [give('raft:palm_thatch', 16)], deps=['rope'])
r.quest('reinforced', 'Shark Proof', 11, -3, [
    TIP + 'A foundation and 2 scrap metal make a &eReinforced Foundation&7. Sharks never bite them, so put them on the edges of your raft.'],
    [item('raft:reinforced_foundation', 8)], [give('raft:scrap_metal', 6)], deps=['foundation'])
r.quest('shark', '&cBruce', 12.6, -3, [
    KEEPER + '"Something circles your raft. It is patient. It is hungry."',
    '',
    TIP + '&cBruce the shark&7 hunts swimmers and circles rafts that people stand on. Every 15 to 45 seconds he bites an edge foundation, and after 4 bites it breaks. Hit him and he swims away for a while.',
    TIP + 'On a server, &e/gamerule raft:shark_bites false&7 stops the biting.'],
    [kill('raft:shark')], [give('raft:cooked_shark_meat', 4), crate('rare')], deps=['reinforced'], shape='heart', size=1.2)
r.quest('hammerhead', 'Hammerhead', 14.2, -3, [
    TIP + 'The &eHammerhead Shark&7 lives deeper in the open sea: 20 hearts, and it hits harder than Bruce.'],
    [kill('raft:hammerhead_shark')], [crate('rare')], deps=['shark'], shape='heart', optional=True)
r.quest('trophy', 'Shark Trophy', 15.8, -3, [TIP + 'Three planks on three shark teeth make a &eShark Jaw Trophy&7 for your wall. Bruce would be proud.'],
        [item('raft:shark_jaw_trophy')], [rxp(100)], deps=['shark'], optional=True)
r.quest('hook', 'Plastic Hook', 7.8, -4.5, [
    TIP + 'The current carries planks, palm leaves, plastic and scrap metal past you, from west to east. Now and then lost loot drifts by, and rarely a &eMessage in a Bottle&7 or a &eSupply Barrel&7 - use them to open them.',
    TIP + 'Hold use with the &ePlastic Hook&7 to pull floating items towards you, up to 12 blocks away.'],
    [item('raft:plastic_hook')], [give('raft:scrap_metal', 6)], deps=['almanac'])
r.quest('catcher', 'Item Catcher', 9.4, -4.5, [
    TIP + 'Put an &eItem Catcher&7 in the water and it catches the debris that drifts into it. It holds one kind of item at a time, so empty it often - hoppers can take the catch out.',
    TIP + 'With an &eItem Catcher Net&7 inside it also fishes up Unrefined Ocean Garbage about every 30 seconds. A net lasts 32 catches. Smelt the garbage into a &eTrash Cube&7 and use it for 1 to 3 surprises.'],
    [item('raft:item_catcher'), item('raft:net')], [give('raft:plastic', 8)], deps=['hook'], shape='hexagon', icon='raft:net')
r.quest('receiver', 'Receiver', 11, -4.5, [
    TIP + 'Use the &eReceiver&7 for the direction and distance to the nearest floating driftwood. Out at sea it is the best source of driftwood logs.',
    TIP + 'It needs a &eCircuit Board&7 (copper, a slime ball and plastic) and a titanium nugget.'],
    [item('raft:receiver')], [rxp(150)], deps=['catcher'])
r.quest('island', 'Driftwood Ahoy!', 12.6, -4.5, [
    TIP + 'Follow the receiver to the floating driftwood and haul the logs aboard.'],
    [item('raft:driftwood_log', 16)], [crate('rare')], deps=['receiver'], shape='diamond')
r.quest('water', 'Fresh Water', 7.8, -6, [
    TIP + 'Sea water is no good. A &eWater Purifier&7 turns water bottles into &eFresh Water&7; a water bucket gives three. It burns planks, logs, coal or charcoal.'],
    [item('raft:water_purifier'), item('raft:fresh_water', 3)], [give('minecraft:glass_bottle', 8)], deps=['almanac'])
r.quest('grill', 'Simple Grill', 9.4, -6, [
    TIP + 'The &eSimple Grill&7 cooks two foods at once, 50% faster than a campfire. Use it with fuel first, then with raw food.'],
    [item('raft:simple_grill')], [give('minecraft:cod', 8)], deps=['water'])
r.quest('farm', 'A Floating Farm', 11, -6, [
    TIP + '&eCrop Plots&7 are farmland that is always watered and never trampled, and crops grow about 50% faster on them.',
    TIP + 'Seagulls peck at crops and set them back one stage, unless a &eScarecrow&7 stands within 16 blocks. It also stops monsters from spawning within 24 blocks.'],
    [item('raft:crop_plot', 4), item('raft:scarecrow')], [give('raft:coconut', 4)], deps=['grill'])
r.quest('pineapple', 'Pineapples', 12.6, -6, [
    TIP + 'Wild &ePineapple Bushes&7 grow on the islands; the fruit is ready when it is golden. Plant a &ePineapple Crown&7 on farmland or a crop plot to grow your own.'],
    [item('raft:pineapple', 4)], [give('raft:pineapple_crown', 2)], deps=['farm'])
r.quest('drinks', 'Island Drinks', 14.2, -6, [
    TIP + 'Pick coconuts from palm leaves; they grow back after about 20 minutes. &eCoconut Milk&7 gives Regeneration, a &ePina Colada&7 gives Speed.'],
    [item('raft:coconut_milk'), item('raft:pina_colada')], [crate('common')], deps=['pineapple'], optional=True)

# --------------------------------------------------------------------------------------------- building (top left)
r.quest('build', 'Beach Builder', 4.6, -3, [
    TIP + 'Beach Craft has a whole harbour of new blocks; the Building and Decoration tabs show them all.',
    TIP + '&eWeathered Planks&7: 4 driftwood or palm planks around bone meal. &eTeak Planks&7: dark oak and palm planks. Both come with stairs, slabs, fences, gates, a door and a hatch.'],
    [item('raft:weathered_planks', 16), item('raft:teak_planks', 16)], [give('minecraft:bone_meal', 16)], deps=['almanac'], icon='raft:weathered_planks')
r.quest('stone', 'Coral and Tidestone', 3, -3, [
    TIP + '&eCoral Stone&7 (stone and coral blocks) comes polished and as plain or mossy bricks. &eTidestone&7 (stone and prismarine shards) also comes cracked, chiseled and as pillars, and &eGlowing Tidestone&7 shines with light 10.',
    TIP + 'Four &eSea Glass Shards&7 from the beaches make Aqua Sea Glass; dye it blue or green.'],
    [item('raft:coral_stone_bricks', 16), item('raft:tidestone_bricks', 16), item('raft:aqua_sea_glass', 4)], [give('minecraft:prismarine_shard', 16)], deps=['build'])
r.quest('cozy', 'Island Lights', 4.6, -4.5, [
    TIP + '&ePaper Lanterns&7 glow with light 14, &eString Lights&7 and neon tubes with 12, ship lanterns and jelly lamps with 15. Tiki torches, buoys and a lighthouse lens are there too.',
    TIP + 'The &eHammock&7 lets you rest by day and sleep by night, and it sets your respawn point. Chairs, cushions and the deck chair: right-click to sit.'],
    [item('raft:paper_lantern_red', 4), item('raft:string_lights_warm', 4), item('raft:hammock')], [give('raft:rope', 8)], deps=['build'])
r.quest('pirate', 'Pirate Style', 3, -4.5, [
    TIP + 'The &eShip Cannon&7 fires &eCannonballs&7 (an iron ingot and gunpowder make 4): 8 damage and no broken blocks.',
    TIP + 'Ring the Ship Bell, raise a Jolly Roger, fill a &eTreasure Chest&7 (27 stacks) and stack Gold Coins into piles, 9 coins each.'],
    [item('raft:ship_cannon'), item('raft:cannonball', 8), item('raft:treasure_chest')], [give('minecraft:gunpowder', 8)], deps=['cozy', 'stone'], any_dep=True, optional=True)
r.quest('steel', 'Steel and City', 1.4, -3, [
    TIP + 'Riveted and Rusty Hull, Corrugated Metal, Steel Beams, &eCatwalks&7, Railings, &ePortholes&7, Bulkhead Doors and Metal Hatches (both open by hand), pipes with valves, Shipping Containers, Cracked Concrete and Asphalt with lane lines.',
    TIP + 'Control panels, server racks and satellite dishes blink and hum on your walls.'],
    [item('raft:porthole', 2), item('raft:catwalk', 4)], [give('raft:scrap_metal', 8)], deps=['stone'], optional=True)
r.quest('aquarium', 'An Aquarium', 1.4, -4.5, [
    TIP + 'Glass, a tropical fish, planks and sand make an &eAquarium&7 with fish swimming inside. It glows softly in the dark.'],
    [item('raft:aquarium')], [crate('common')], deps=['pirate', 'steel'], any_dep=True, optional=True)

# --------------------------------------------------------------------------------------------- technology (top right)
r.quest('titanium', 'Titanium', 17.4, -4.5, [
    TIP + '&eTitanium Ore&7 is only found in the raft dimension, below y 20 under the sea floor. Mine it with a diamond pickaxe and smelt the raw titanium.',
    TIP + 'The &eMetal Detector&7 (titanium and a circuit board) tells you at which height the next titanium ore below you lies.'],
    [item('raft:titanium_ingot', 12)], [crate('rare')], deps=['island'], shape='diamond')
r.quest('armor', 'Titanium Armor', 19, -6, [
    TIP + 'A full set of titanium armor gives &eWater Breathing&7, &eDolphin\'s Grace&7 and &eConduit Power&7.'],
    [item('raft:titanium_helmet'), item('raft:titanium_chestplate'), item('raft:titanium_leggings'), item('raft:titanium_boots')],
    [crate('epic')], deps=['titanium'], optional=True)
r.quest('solar', 'Sun Power', 19, -3, [
    TIP + 'The sea has its own small tech line on &eFE&7, so Tech Reborn machines connect too.',
    TIP + 'A &eMakeshift Solar Panel&7 makes 10 FE per tick - and over the Endless Sea the sun never sets. A &eMakeshift Battery&7 stores 1,000,000 FE. Copper Cable carries 128 FE per tick, Titanium Cable 512.'],
    [item('raft:makeshift_solar_panel'), item('raft:makeshift_battery')], [give('raft:copper_cable', 16)], deps=['titanium'])
r.quest('turbine', 'Wind Turbine', 20.6, -3, [
    TIP + 'The &eWind Turbine&7 makes 20 FE per tick. It needs free air in the 3 by 3 area in front of its rotor and a spot above y 90. Your raft floats at y 100, so it works right on deck.'],
    [item('raft:wind_turbine')], [give('raft:circuit_board', 2)], deps=['solar'])
r.quest('quarry', 'Raft Quarry', 22.2, -3, [
    TIP + 'The raft &eQuarry&7 digs an 11 by 11 hole down to the bottom of the world for 1,000 FE per block. A chest on top collects the drops.',
    TIP + 'The &eTitanium Furnace&7 smelts 32 times faster and doubles every result.'],
    [item('raft:quarry')], [crate('epic')], deps=['turbine'], optional=True)

# --------------------------------------------------------------------------------------------- sailing (below the story)
r.quest('paddle', 'Small Boats', 7.6, 1.8, [
    TIP + 'The &ePalm Boat&7 and the &eDriftwood Raft&7 are made like vanilla boats, with a chest version too. In a boat, the &ePaddle&7 gives you a push forward.'],
    [item('raft:paddle')], [rxp(60)], deps=['castaway'])
r.quest('expedition', 'The Expedition Raft', 9.2, 1.8, [
    TIP + 'Six Raft Foundations, 2 rope and a paddle: the &eExpedition Raft&7 is a big 3 by 3 raft with four seats and 27 storage slots (sneak and use it). The first one to board sits at the helm and steers.',
    TIP + 'It never sinks, never tips over, and sharks cannot hurt it. Friends standing on the deck ride along. To pick it up, hit it 3 times within 2 seconds, or once while sneaking.',
    '',
    TIP + 'Reward: an almanac that opens at the Sailing chapter.'],
    [item('raft:expedition_raft'), adv('raft:adventure/set_sail', 'Take the helm', icon='raft:raft_sail')], [give(almanac('sailing')), rxp(150)], deps=['paddle'], shape='hexagon', size=1.2)
r.quest('sail', 'Raft Sail', 10.8, 1.8, [
    TIP + 'Use an upgrade item on the raft; each one shows on the raft. A &eRaft Sail&7 (rope, sail canvas and palm logs) makes it 50% faster sailing ahead.'],
    [item('raft:raft_sail')], [give('raft:rope', 8)], deps=['expedition'])
r.quest('engine', 'Raft Engine', 12.4, 1.8, [
    TIP + 'The &eRaft Engine&7 (titanium, scrap metal, a circuit board and a furnace) makes the raft more than twice as fast. It burns furnace fuel from the fuel slot in the raft menu while you drive.',
    TIP + 'With sail and engine your raft is more than twice as fast as a boat.'],
    [item('raft:raft_engine')], [give('minecraft:coal_block', 4)], deps=['sail'])
r.quest('cargo', 'Anchor and Cargo', 14, 1.8, [
    TIP + 'Drop the &eRaft Anchor&7 with the lever in the raft menu, and the raft stays where it is - perfect above a dive spot. A &eRaft Cargo Crate&7 adds 27 more storage slots.'],
    [item('raft:raft_anchor'), item('raft:raft_crate')], [crate('rare')], deps=['engine'])
r.quest('lanterns', 'Raft Lanterns', 15.6, 1.8, [TIP + '&eRaft Lanterns&7 add lantern posts and rope rails to your raft. Sailing at night has never looked better.'],
        [item('raft:raft_lantern')], [rxp(100)], deps=['cargo'], optional=True)

# --------------------------------------------------------------------------------------------- diving
r.quest('helmet', 'Diving Helmet', 6, 3.3, [
    TIP + 'Copper, gold and a glass pane make the &eDiving Helmet&7: under water you see much farther. With a tank you breathe from the tank. Saltmere has one waiting for you, too.',
    '',
    TIP + 'Reward: an almanac that opens at the Diving chapter.'],
    [item('raft:diving_helmet')], [give(almanac('diving')), rxp(100)], deps=['enter'])
r.quest('tank', 'Deep Breath', 7.6, 3.3, [
    TIP + 'An &eOxygen Tank&7 holds 2 minutes of air. It only works together with the helmet; the bar on the tank and a gauge on the screen show what is left.',
    TIP + 'It refills when your head is above the water, or in a bubble column: a normal tank is full again in 3 seconds. Bubble Vents and soul sand make bubble columns.'],
    [item('raft:oxygen_tank'), adv('raft:adventure/deep_breath', 'Wear helmet and tank', icon='raft:diving_helmet')], [rxp(150)], deps=['helmet'])
r.quest('suit', 'Wetsuit and Flippers', 9.2, 3.3, [
    TIP + 'The &eWetsuit&7 lets you mine three times faster under water, and jellyfish cannot sting you. &eFlippers&7 make you swim much faster, but walk 25% slower on land.',
    TIP + 'Wear helmet, tank, wetsuit and flippers for Dolphin\'s Grace while swimming.'],
    [item('raft:wetsuit'), item('raft:flippers')], [give('minecraft:dried_kelp', 16)], deps=['tank'])
r.quest('compressor', 'Air Compressor', 10.8, 3.3, [
    TIP + 'Put a tank in the &eAir Compressor&7 and it fills it with FE from a neighbour: a cable, battery, solar panel or wind turbine. No power? Sneak and use it with an empty hand, or press the crank in its menu. Each turn adds 5 seconds of air.'],
    [item('raft:air_compressor')], [rxp(150)], deps=['suit'])
r.quest('lamp', 'Helmet Lamp', 12.4, 3.3, [
    TIP + '&eAnglerfish&7 lurk in the dark of the Abyssal Trench and drop an &eAngler Lure&7. Craft your Diving Helmet with the lure: under water you can then see in the dark deep sea.',
    '',
    TIP + 'Defeat an anglerfish, then tick the box when your helmet has its lamp.'],
    [kill('raft:anglerfish'), check('My helmet has a lamp', icon='raft:diving_helmet')], [crate('rare')], deps=['compressor'], icon='raft:angler_lure')
r.quest('harpoon', 'Harpoon Gun', 14, 3.3, [
    TIP + 'The &eHarpoon Gun&7 shoots harpoons from your inventory: 8 damage under water, 4 in the air, one shot per second. Pick the harpoons up again after the hunt.',
    TIP + 'Iron, a stick and string make 4 harpoons; an Urchin Spine, a stick and string make 2.'],
    [item('raft:harpoon_gun'), item('raft:harpoon', 8)], [give('raft:harpoon', 8)], deps=['lamp'])
r.quest('scooter', 'Deep Diver', 15.6, 3.3, [
    TIP + 'Hold use under water and the &eSea Scooter&7 pulls you where you look; its 3,000 FE last about 75 seconds (charge it in the compressor).',
    TIP + 'The &eTitanium Oxygen Tank&7 holds 6 minutes of air and protects like an iron chestplate.'],
    [item('raft:sea_scooter'), item('raft:titanium_oxygen_tank')], [crate('epic')], deps=['harpoon'], optional=True)

# --------------------------------------------------------------------------------------------- the places of the sea
r.quest('ruins', 'Sunken Ruins', 6, 4.8, [
    TIP + 'Away from the story there are many smaller places, with loot, logs and a bit of danger. Small Tidewarden ruins lie on the reefs.',
    TIP + 'Not sure where you are? The almanac\'s &eIslands & Wrecks&7 chapter lists them all.'],
    [struct('raft:sunken_ruins', 'Find sunken ruins')], [crate('common')], deps=['helmet'])
r.quest('cargo_ship', 'The Broken Freighter', 7.6, 4.8, [
    TIP + 'A rusty cargo ship lies broken in two on the sea floor, with shipping containers everywhere.'],
    [struct('raft:wreck_cargo_ship', 'Explore a cargo ship wreck')], [crate('rare')], deps=['ruins'])
r.quest('plane', 'Lost Flight', 8.4, 6.3, [TIP + 'Some planes never arrived: their wrecks rest in the kelp forests and on the open sea floor.'],
        [struct('raft:sunken_plane', 'Find a sunken plane')], [crate('rare')], deps=['cargo_ship'], optional=True)
r.quest('galleon', 'Ghost Ship', 9.2, 4.8, [
    TIP + 'Old pirate galleons lie tilted on the floor of the wreck graveyards, full of drowned corsairs. Their chests sometimes hold &eSaltjaw\'s Treasure Chart&7.'],
    [adv('raft:adventure/ghost_ship', 'Explore a galleon wreck', icon='raft:jolly_roger'), adv('raft:adventure/pirate_gold', 'Find a pirate gold coin', icon='raft:gold_coin')], [crate('rare')], deps=['cargo_ship'])
r.quest('cove', 'Saltjaw\'s Gold', 10.8, 4.8, [
    TIP + 'Follow the treasure chart to the hidden &ePirate Cove&7 of "Saltjaw" Brannigan, carved into an island. Corsairs guard the gold.'],
    [adv('raft:adventure/saltjaws_gold', 'Find the pirate cove', icon='raft:treasure_chest')], [crate('epic'), give('raft:gold_coin', 9)], deps=['galleon'], shape='diamond')
r.quest('rig', 'Rusted Giant', 12.4, 4.8, [
    TIP + 'Giant old &eRusted Rigs&7 stand on steel legs in the open sea, with cranes, containers, terminals and a radio. Listen to what the radio says.'],
    [adv('raft:adventure/rusted_giant', 'Climb aboard a rig', icon='raft:rusty_pipe_valve')], [crate('rare')], deps=['cove'])
r.quest('iceberg', 'Cold Outpost', 14, 4.8, [
    TIP + 'In the frost floes, researchers left a hut on an iceberg. Penguins keep it company now.'],
    [struct('raft:iceberg_outpost', 'Find an iceberg outpost')], [crate('rare')], deps=['rig'], optional=True)
r.quest('discs', 'Songs of the Sea', 15.6, 4.8, [
    TIP + 'Three music discs hide in the beach shacks of the islands and in the apartments and shops of Port Solace. Collect them all.'],
    [item('raft:lofi_beat_music_disc'), item('raft:crystal_castles_music_disc'), item('raft:some_game_music_music_disc')],
    [crate('epic')], deps=['iceberg', 'rig'], any_dep=True, optional=True)

# --------------------------------------------------------------------------------------------- creatures (bottom left)
r.quest('crab', 'Crab Dinner', 4.4, 3.3, [
    TIP + 'The sea is full of life. Most creatures are peaceful; a few bite back. The almanac has a page for each one.',
    TIP + '&eCrabs&7 scuttle sideways along the beaches; sprint close and they dig into the sand, hit one and it pinches back. Cook a &eCrab Claw&7 and eat it.',
    '',
    TIP + 'Reward: an almanac that opens at the Creatures chapter.'],
    [observe('raft:crab', 40, entity=True, title='Watch a crab'), adv('raft:adventure/crab_dinner', 'Eat a cooked crab claw', icon='raft:cooked_crab_claw')],
    [give(almanac('creatures')), give('raft:cooked_crab_claw', 4)], deps=['enter'], icon='raft:crab_claw')
r.quest('seagull', 'Seagulls', 2.8, 3.3, [
    TIP + '&eSeagulls&7 fly in flocks over islands and rafts. They peck at crops without a scarecrow nearby - and they snatch food that lies on the ground!'],
    [observe('raft:seagull', 40, entity=True, title='Watch a seagull')], [give('minecraft:feather', 8)], deps=['crab'])
r.quest('penguin', 'Penguins on Ice', 1.2, 3.3, [
    TIP + '&ePenguins&7 waddle over the frost floes, slide on their bellies and dive for fish. Feed them cod and they have chicks: grey and fluffy.'],
    [observe('raft:penguin', 40, entity=True, title='Watch a penguin')], [give('minecraft:cod', 8)], deps=['seagull'], optional=True)
r.quest('otter', 'Sea Otters', 4.4, 4.8, [
    TIP + '&eSea Otters&7 float on their backs in the kelp forests and crack shells on their bellies with a stone. Feed one a seashell and it follows you for a while, and now and then it brings you a pearl.'],
    [observe('raft:sea_otter', 40, entity=True, title='Watch a sea otter')], [give('raft:seashell', 4)], deps=['crab'])
r.quest('reef', 'Reef Life', 2.8, 4.8, [
    TIP + '&eManta Rays&7 glide through the warm coral shallows in slow loops. &eMoray Eels&7 hide in holes of reefs and ruins with only their head out: swim within 4 blocks and they lunge.'],
    [observe('raft:manta_ray', 40, entity=True, title='Watch a manta ray'), observe('raft:moray_eel', 40, entity=True, title='Spot a moray eel')],
    [give('raft:pearl', 2)], deps=['otter'])
r.quest('jellyfish', 'Jellyfish', 1.2, 4.8, [
    TIP + '&eJellyfish&7 drift with the current: white moon jellies, red crimson jellies and glow jellies that light up the dark lagoons. Touching one stings (Poison for 3 seconds) unless you wear a wetsuit.',
    TIP + 'Two jelly blobs make a slime ball; glow jelly makes glow ink sacs and Jelly Lamps.'],
    [observe('raft:jellyfish', 40, entity=True, title='Watch a jellyfish')], [give('minecraft:slime_ball', 4)], deps=['reef'], optional=True)
r.quest('whale', 'Whale Watcher', 4.4, 6.3, [
    TIP + 'A huge, gentle &eWhale&7 cruises a few blocks below the surface of the open sea. It comes up every minute or two to breathe and spout, and sings now and then.',
    TIP + 'Watch one through a &espyglass&7.'],
    [adv('raft:adventure/whale_watcher', 'Watch a whale through a spyglass')], [crate('rare')], deps=['otter'], icon='minecraft:spyglass')
r.quest('corsair', 'Cursed Crew', 2.8, 6.3, [
    TIP + '&eDrowned Corsairs&7 are undead pirates of Saltjaw\'s crew. They swim like drowned, do not burn in the sun, fight with cutlasses and even climb onto rafts. They drop gold coins and sometimes a &eCutlass&7.'],
    [kill('raft:drowned_corsair', 3)], [give('raft:gold_coin', 6)], deps=['whale'])
