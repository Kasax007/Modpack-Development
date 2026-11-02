package net.kasax.dctest;

import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import net.minecraft.world.Difficulty;

import java.nio.file.Path;
import java.util.List;

/**
 * Footage for the Dreamcraft short: every shot is filmed frame by frame in portrait (1080x1920,
 * 30 fps of game time, rendered between ticks) plus one landscape still for the descriptions.
 * Shots: -Pscene=film -Pshots=a,b,c -Pout=DIR
 */
final class Film {
    private final ClientGameTestContext ctx;
    private final Path out;
    private TestSingleplayerContext sp;

    Film(ClientGameTestContext ctx, Path out) {
        this.ctx = ctx;
        this.out = out;
    }

    /** Runs a command; block, summon and relative commands run at the player's position. */
    void cmd(String c) {
        String first = c.split(" ")[0];
        boolean global = List.of("execute", "tp", "gamerule", "time", "weather", "item", "quests", "effect", "kill").contains(first);
        sp.getServer().runCommand(global ? c : "execute as @p at @p run " + c);
    }

    void cmds(String... cs) {
        for (String c : cs) cmd(c);
    }

    void settle(int max) {
        for (int i = 1; i <= max; i++) {
            ctx.waitTick();
            if (i >= 40 && i % 10 == 0 && ctx.computeOnClient(mc -> mc.levelRenderer.hasRenderedAllSections())) return;
        }
    }

    void portrait() {
        ctx.getInput().resizeWindow(1080, 1920);
        ctx.runOnClient(mc -> {
            mc.options.guiScale().set(4);
            mc.resizeGui();
        });
        ctx.waitTicks(3);
    }

    void landscape() {
        ctx.getInput().resizeWindow(1920, 1080);
        ctx.runOnClient(mc -> {
            mc.options.guiScale().set(3);
            mc.resizeGui();
        });
        ctx.waitTicks(3);
    }

    void hud(boolean visible) {
        ctx.runOnClient(mc -> {
            if (mc.gui.hud.isHidden() == visible) mc.gui.hud.toggle();
        });
    }

    void camera(CameraType type) {
        ctx.runOnClient(mc -> mc.options.setCameraType(type));
    }

    /** Films {@code frames} frames at 30 fps of game time into out/shot/f00000.png. */
    void frames(String shot, int frames, Runnable perTick) {
        Path dir = out.resolve(shot);
        int tick = 0;
        for (int i = 0; i < frames; i++) {
            double t = i * 20.0 / 30.0;
            int whole = (int) Math.floor(t);
            while (tick < whole) {
                if (perTick != null) perTick.run();
                ctx.waitTick();
                tick++;
            }
            ctx.takeScreenshot(TestScreenshotOptions.of(String.format("f%05d", i)).withDeltaTicks((float) (t - whole))
                    .disableCounterPrefix().withDestinationDir(dir));
        }
        PackTest.LOG.info("[dctest] filmed {} ({} frames)", shot, frames);
    }

    void still(String name) {
        ctx.takeScreenshot(TestScreenshotOptions.of(name).disableCounterPrefix().withDestinationDir(out.resolve("stills")));
    }

    /** Portrait frames, then a landscape still of the same view. */
    void shoot(String shot, int frames, Runnable perTick) {
        portrait();
        settle(200);
        frames(shot, frames, perTick);
        landscape();
        settle(120);
        still(shot);
        portrait();
    }

    void run(List<String> shots) {
        ctx.runOnClient(mc -> {
            var o = mc.options;
            o.renderDistance().set(8);
            o.fov().set(80);
            o.bobView().set(false);
            o.showAutosaveIndicator().set(false);
            o.chatVisibility().set(net.minecraft.world.entity.player.ChatVisiblity.HIDDEN);
        });
        if (shots.contains("menu")) {
            portrait();
            ctx.waitTicks(40);
            frames("menu", 45, null);
            landscape();
            ctx.waitTicks(20);
            still("menu");
        }
        sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(s -> {
            s.setSeed("dreamcraft-film");
            s.setGameMode(WorldCreationUiState.SelectedGameMode.CREATIVE);
            s.setAllowCommands(true);
            s.setDifficulty(Difficulty.NORMAL);
        }).create();
        cmds("gamerule advance_time false", "gamerule advance_weather false", "time set 6000", "weather clear",
                "gamerule send_command_feedback false", "gamerule show_advancement_messages false", "gamerule spawn_monsters false");
        ctx.waitTicks(40);
        hud(false);
        for (String shot : shots) {
            PackTest.LOG.info("[dctest] shot {}", shot);
            try {
                shot(shot);
            } catch (Exception e) {
                PackTest.LOG.warn("[dctest] shot {} failed: {}", shot, e.toString());
            }
        }
        sp.close();
    }

    private void shot(String shot) {
        if (!shot.equals("magic")) {
            cmds("item replace entity @p weapon.offhand with air", "item replace entity @p armor.head with air",
                    "item replace entity @p armor.chest with air", "item replace entity @p armor.legs with air", "item replace entity @p armor.feet with air");
        }
        switch (shot) {
            case "menu" -> {
            }
            case "vista" -> {
                // a Terralith landscape: the player on the highest spot nearby, looking into the open, slow pan
                cmds("execute in minecraft:overworld run tp @p 600 200 600");
                hands("air");
                for (String biome : List.of("terralith:skylands_summer", "terralith:skylands_spring", "terralith:skylands_autumn",
                        "terralith:mirage_isles", "terralith:amethyst_canyon", "terralith:yellowstone", "terralith:painted_mountains",
                        "terralith:bryce_canyon", "terralith:white_cliffs", "terralith:alpine_highlands")) {
                    if (findLand(List.of(biome), 30)) break;
                }
                peak(48);
                vantage(16);
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("vista", 75, () -> cmd("execute as @p at @p run tp @p ~ ~ ~ ~0.35 ~"));
            }
            case "questbook" -> {
                camera(CameraType.FIRST_PERSON);
                cmd("quests complete all @p");
                ctx.waitTicks(10);
                cmd("quests reset all @p");
                cmd("quests complete 69EBF5E4D7E44EE2 @p");
                ctx.waitTicks(10);
                portrait();
                ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_J);
                ctx.waitTicks(20);
                frames("questbook", 40, null);
                landscape();
                ctx.waitTicks(10);
                still("questbook");
                portrait();
                ctx.setScreen(() -> null);
            }
            case "raft" -> {
                cmds("execute in raft:raftdim run tp @p 0 120 0");
                ctx.waitTicks(60);
                int y = ctx.computeOnClient(mc -> mc.level.getSeaLevel());
                String yy = String.valueOf(y);
                String r = "execute in raft:raftdim run ";
                cmds(r + "fill -5 " + yy + " -6 5 " + yy + " 5 raft:raft_foundation",
                        r + "fill -5 " + (y + 1) + " -6 5 " + (y + 7) + " 5 minecraft:air",
                        // mast with a striped sail and the flag, straight ahead
                        r + "fill 0 " + (y + 1) + " -4 0 " + (y + 6) + " -4 minecraft:stripped_oak_log",
                        r + "fill -2 " + (y + 3) + " -4 2 " + (y + 6) + " -4 raft:sail_canvas_red_striped",
                        r + "setblock 0 " + (y + 7) + " -4 raft:raft_flag",
                        // farm on the left
                        r + "fill -4 " + (y + 1) + " -2 -3 " + (y + 1) + " 1 raft:crop_plot",
                        r + "fill -4 " + (y + 2) + " -2 -3 " + (y + 2) + " 1 minecraft:wheat[age=7]",
                        r + "setblock -4 " + (y + 1) + " 2 raft:scarecrow",
                        // kitchen on the right
                        r + "setblock 3 " + (y + 1) + " -1 raft:water_purifier",
                        r + "setblock 3 " + (y + 1) + " 1 raft:simple_grill",
                        r + "setblock 4 " + (y + 1) + " -3 raft:coconut_lantern",
                        r + "setblock -4 " + (y + 1) + " -4 raft:coconut_lantern",
                        r + "setblock 2 " + (y + 1) + " -3 raft:rope_coil",
                        r + "setblock 0 " + (y + 1) + " -2 raft:ship_wheel",
                        r + "summon raft:shark -3 " + (y - 1) + " -9",
                        r + "summon raft:shark 4 " + (y - 1) + " -10",
                        r + "summon raft:shark -7 " + (y - 1) + " -3",
                        r + "tp @p 0.5 " + (y + 1) + " 3.5 165 12",
                        "item replace entity @p weapon.mainhand with raft:plastic_hook", "item replace entity @p weapon.offhand with air");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("raft", 75, () -> cmd("execute as @p at @p run tp @p ~0.01 ~ ~-0.025"));
            }
            case "shark" -> {
                // under water next to the raft: Bruce swims straight at the camera
                cmds("execute in raft:raftdim run tp @p 0 120 0");
                ctx.waitTicks(60);
                int y = ctx.computeOnClient(mc -> mc.level.getSeaLevel());
                String r = "execute in raft:raftdim run ";
                cmds(r + "fill -5 " + y + " -6 5 " + y + " 5 raft:raft_foundation",
                        r + "fill -6 " + (y - 12) + " -30 6 " + (y - 1) + " -7 minecraft:water",
                        "effect give @p minecraft:night_vision 999 0 true", "effect give @p minecraft:water_breathing 999 0 true",
                        "item replace entity @p weapon.mainhand with raft:plastic_hook",
                        r + "summon raft:shark 0.5 " + (y - 4) + " -19 {NoAI:1b,NoGravity:1b,Rotation:[0f,0f]}",
                        r + "tp @p 0.5 " + (y - 4) + " -11 180 -4");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("shark", 60, () -> cmd("execute in raft:raftdim as @e[type=raft:shark,limit=1,sort=nearest] at @s run tp @s ~ ~ ~0.05"));
                cmd("effect clear @p");
            }
            case "nether" -> {
                cmds("execute in minecraft:the_nether run tp @p 0 80 0");
                ctx.waitTicks(40);
                hands("air");
                spreadIn("minecraft:the_nether", "betternether:nether_jungle");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("nether", 50, () -> cmd("execute as @p at @p run tp @p ~0.05 ~ ~"));
            }
            case "end" -> {
                cmds("execute in minecraft:the_end run tp @p 1200 120 1200");
                ctx.waitTicks(40);
                hands("air");
                spreadIn("minecraft:the_end", "betterend:glowing_grasslands");
                vantage(10);
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("end", 60, () -> cmd("execute as @p at @p run tp @p ~ ~ ~ ~0.35 ~"));
            }
            case "magic" -> {
                // fire wizard: robes, staff, fireballs flying at a few monsters
                cmds("execute in minecraft:overworld run tp @p 40 200 40");
                findLand(FLAT, 2);
                cmds("execute as @p at @p run tp @p ~ ~ ~ 180 4", "item replace entity @p weapon.mainhand with wizards:staff_fire",
                        "item replace entity @p weapon.offhand with air",
                        "item replace entity @p armor.head with wizards:fire_robe_head", "item replace entity @p armor.chest with wizards:fire_robe_chest",
                        "item replace entity @p armor.legs with wizards:fire_robe_legs", "item replace entity @p armor.feet with wizards:fire_robe_feet");
                cmds("summon minecraft:zombie ^ ^ ^9 {NoAI:1b,Rotation:[0f,0f]}", "summon minecraft:zombie ^2 ^ ^10 {NoAI:1b,Rotation:[0f,0f]}",
                        "summon minecraft:skeleton ^-2 ^ ^10 {NoAI:1b,Rotation:[0f,0f]}");
                camera(CameraType.THIRD_PERSON_BACK);
                int[] t = {0};
                Runnable cast = () -> {
                    cmd("particle minecraft:flame ~ ~1 ~ 0.5 0.7 0.5 0.01 4");
                    if (t[0]++ % 9 == 2) {
                        cmd("summon minecraft:small_fireball ^-0.5 ^1.5 ^1.2 {Motion:[0.0,0.0,-0.9],acceleration_power:0.04}");
                        cmd("particle minecraft:lava ^-0.5 ^1.5 ^1 0.2 0.2 0.2 0 4");
                    }
                };
                portrait();
                settle(160);
                frames("magic", 75, cast);
                landscape();
                settle(30);
                still("magic");
                portrait();
                cmd("execute at @p run kill @e[type=!player,distance=..30]");
            }
            case "mutant" -> {
                cmds("execute in minecraft:overworld run tp @p 80 200 80");
                findLand(FLAT, 2);
                cmds("execute as @p at @p run tp @p ~ ~ ~ 180 -14", "fill ~-7 ~ ~-10 ~7 ~14 ~6 minecraft:air", "summon mutantmonsters:mutant_zombie ^ ^ ^5 {NoAI:1b,Rotation:[0f,0f]}",
                        "item replace entity @p weapon.mainhand with minecraft:netherite_sword");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("mutant", 60, () -> cmd("execute as @p at @p run tp @p ~ ~ ~-0.03"));
                cmd("kill @e[type=mutantmonsters:mutant_zombie]");
            }
            case "kitchen" -> {
                // a little kitchen: stoves with pot and skillet, Cooking for Blockheads counters, crates, food on the island
                cmds("execute in minecraft:overworld run tp @p 120 200 120");
                findLand(FLAT, 2);
                cmds("execute as @p at @p run tp @p ~ ~ ~ 0 0", "fill ~-7 ~ ~-6 ~7 ~14 ~10 minecraft:air", "fill ~-4 ~ ~1 ~4 ~4 ~8 minecraft:air", "fill ~-4 ~-1 ~1 ~4 ~-1 ~7 minecraft:spruce_planks",
                        "fill ~-4 ~ ~7 ~4 ~2 ~7 minecraft:bricks", "fill ~-4 ~3 ~7 ~4 ~3 ~7 minecraft:spruce_slab",
                        "setblock ~-4 ~ ~6 cookingforblockheads:counter", "setblock ~-3 ~ ~6 cookingforblockheads:sink",
                        "setblock ~-2 ~ ~6 cookingforblockheads:counter", "setblock ~-2 ~1 ~6 farmersdelight:cutting_board",
                        "setblock ~-1 ~ ~6 farmersdelight:stove[lit=true]", "setblock ~-1 ~1 ~6 farmersdelight:cooking_pot",
                        "setblock ~0 ~ ~6 farmersdelight:stove[lit=true]", "setblock ~0 ~1 ~6 farmersdelight:skillet",
                        "setblock ~1 ~ ~6 cookingforblockheads:cooking_table", "setblock ~2 ~ ~6 cookingforblockheads:counter",
                        "setblock ~2 ~1 ~6 cookingforblockheads:toaster", "setblock ~3 ~ ~6 cookingforblockheads:counter",
                        "setblock ~3 ~1 ~6 cookingforblockheads:milk_jar", "setblock ~4 ~ ~6 cookingforblockheads:counter",
                        "fill ~-1 ~ ~3 ~1 ~ ~3 cookingforblockheads:counter", "setblock ~-1 ~1 ~3 farmersdelight:roast_chicken_block",
                        "setblock ~0 ~1 ~3 farmersdelight:honey_glazed_ham_block", "setblock ~1 ~1 ~3 farmersdelight:shepherds_pie_block",
                        "setblock ~-4 ~ ~2 farmersdelight:carrot_crate", "setblock ~-4 ~ ~3 farmersdelight:tomato_crate",
                        "setblock ~-4 ~1 ~2 farmersdelight:cabbage_crate", "setblock ~-4 ~ ~4 farmersdelight:onion_crate",
                        "setblock ~-3 ~ ~2 farmersdelight:rice_bale", "setblock ~-4 ~3 ~6 minecraft:lantern", "setblock ~4 ~3 ~6 minecraft:lantern",
                        "item replace entity @p weapon.mainhand with farmersdelight:iron_knife", "execute as @p at @p run tp @p ~3 ~ ~0.5 29 24");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("kitchen", 45, () -> cmd("execute as @p at @p run tp @p ~ ~ ~ ~-0.15 ~"));
            }
            case "tech" -> {
                // Tech Reborn workshop: a row of machines with cables and solar panels on top, a quarry in front
                cmds("execute in minecraft:overworld run tp @p 160 200 160");
                findLand(FLAT, 2);
                cmds("execute as @p at @p run tp @p ~ ~ ~ 0 0", "fill ~-8 ~ ~-6 ~8 ~14 ~10 minecraft:air", "fill ~-5 ~ ~1 ~5 ~4 ~8 minecraft:air", "fill ~-5 ~-1 ~1 ~5 ~-1 ~7 minecraft:polished_andesite",
                        "fill ~-5 ~-1 ~4 ~5 ~-1 ~4 techreborn:refined_iron_storage_block",
                        "setblock ~-5 ~ ~6 techreborn:solid_fuel_generator", "setblock ~-4 ~ ~6 techreborn:iron_furnace",
                        "setblock ~-3 ~ ~6 techreborn:electric_furnace", "setblock ~-2 ~ ~6 techreborn:grinder",
                        "setblock ~-1 ~ ~6 techreborn:extractor", "setblock ~0 ~ ~6 techreborn:compressor",
                        "setblock ~1 ~ ~6 techreborn:alloy_smelter", "setblock ~2 ~ ~6 techreborn:industrial_centrifuge",
                        "setblock ~3 ~ ~6 techreborn:chemical_reactor", "setblock ~4 ~ ~6 techreborn:assembly_machine",
                        "setblock ~5 ~ ~6 techreborn:low_voltage_su", "fill ~-5 ~1 ~6 ~5 ~1 ~6 techreborn:basic_solar_panel",
                        "fill ~-5 ~ ~5 ~5 ~ ~5 techreborn:insulated_copper_cable", "setblock ~-3 ~ ~3 quarrymod:quarry",
                        "setblock ~5 ~ ~3 techreborn:medium_voltage_su", "setblock ~5 ~1 ~3 techreborn:wind_mill",
                        "item replace entity @p weapon.mainhand with techreborn:basic_drill", "execute as @p at @p run tp @p ~3 ~ ~0.5 29 24");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("tech", 45, () -> cmd("execute as @p at @p run tp @p ~ ~ ~ ~-0.15 ~"));
            }
            case "castle" -> {
                // aerial view: the player stands on an invisible barrier high above, the camera pans slowly
                cmds("execute in minecraft:overworld run tp @p 400 200 -400");
                findLand(FLAT, 3);
                cmds("place structure ati_structures:catalonian_castle ~ ~ ~20");
                ctx.waitTicks(40);
                cmds("execute as @p at @p run tp @p ~-22 ~22 ~-10 -40 26", "execute as @p at @p run setblock ~ ~-1 ~ minecraft:barrier");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("castle", 60, () -> cmd("execute as @p at @p run tp @p ~ ~ ~ ~0.3 ~"));
            }
            case "village" -> {
                // the nearest real village (with all the village mods), seen from above on a barrier, slow pan
                cmds("execute in minecraft:overworld run tp @p -400 200 400");
                ctx.waitTicks(20);
                Object vp = sp.getServer().computeOnServer(server -> server.overworld().findNearestMapStructure(
                        net.minecraft.tags.StructureTags.VILLAGE, server.getPlayerList().getPlayers().getFirst().blockPosition(), 100, false));
                if (!(vp instanceof net.minecraft.core.BlockPos bp)) {
                    PackTest.LOG.warn("[dctest] no village found");
                    break;
                }
                PackTest.LOG.info("[dctest] village at {}", bp);
                cmd("execute in minecraft:overworld run tp @p " + (bp.getX() - 16) + " 200 " + (bp.getZ() - 16));
                ctx.waitTicks(60);
                sp.getServer().runOnServer(server -> {
                    var p = server.getPlayerList().getPlayers().getFirst();
                    var top = p.level().getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.blockPosition());
                    p.teleportTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5);
                });
                ctx.waitTicks(10);
                cmds("execute as @p at @p run tp @p ~ ~20 ~ -45 30", "execute as @p at @p run setblock ~ ~-1 ~ minecraft:barrier");
                camera(CameraType.THIRD_PERSON_BACK);
                shoot("village", 60, () -> cmd("execute as @p at @p run tp @p ~ ~ ~ ~-0.3 ~"));
            }
            default -> PackTest.LOG.warn("[dctest] unknown shot {}", shot);
        }
    }

    /** Creative flight on or off, so the camera can hang in the air for aerial shots. */
    private void fly(boolean on) {
        sp.getServer().runOnServer(server -> {
            var p = server.getPlayerList().getPlayers().getFirst();
            p.getAbilities().flying = on;
            p.onUpdateAbilities();
        });
        ctx.waitTicks(2);
    }

    /** Main hand item (or air), empty off hand (the starter kit's shield hides the player). */
    private void hands(String main) {
        cmds("item replace entity @p weapon.mainhand with " + main, "item replace entity @p weapon.offhand with air");
    }

    /** Moves the player to the highest dry point within {@code radius} blocks (generator heights, overworld). */
    private void peak(int radius) {
        Object pos = sp.getServer().computeOnServer(server -> {
            var p = server.getPlayerList().getPlayers().getFirst();
            var level = server.overworld();
            var gen = level.getChunkSource().getGenerator();
            var rs = level.getChunkSource().randomState();
            net.minecraft.core.BlockPos best = null;
            for (int dx = -radius; dx <= radius; dx += 4) {
                for (int dz = -radius; dz <= radius; dz += 4) {
                    int x = p.getBlockX() + dx, z = p.getBlockZ() + dz;
                    int h = gen.getBaseHeight(x, z, net.minecraft.world.level.levelgen.Heightmap.Types.WORLD_SURFACE_WG, level, rs);
                    if (h != gen.getBaseHeight(x, z, net.minecraft.world.level.levelgen.Heightmap.Types.OCEAN_FLOOR_WG, level, rs)) continue;
                    if (best == null || h > best.getY()) best = new net.minecraft.core.BlockPos(x, h, z);
                }
            }
            return best;
        });
        if (pos instanceof net.minecraft.core.BlockPos bp) {
            PackTest.LOG.info("[dctest] peak at {}", bp);
            cmd("execute in minecraft:overworld run tp @p " + bp.getX() + " " + (bp.getY() + 10) + " " + bp.getZ());
            ctx.waitTicks(40);
            sp.getServer().runOnServer(server -> {
                var p = server.getPlayerList().getPlayers().getFirst();
                var top = p.level().getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.blockPosition());
                p.teleportTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5);
            });
            ctx.waitTicks(20);
        }
    }

    /** Puts the player on the highest spot within 4 blocks, facing the most open direction (overworld / end). */
    private void vantage(float pitch) {
        sp.getServer().runOnServer(server -> {
            var p = server.getPlayerList().getPlayers().getFirst();
            var level = (net.minecraft.server.level.ServerLevel) p.level();
            var hm = net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES;
            net.minecraft.core.BlockPos best = null;
            for (int dx = -4; dx <= 4; dx++) {
                for (int dz = -4; dz <= 4; dz++) {
                    var top = level.getHeightmapPos(hm, p.blockPosition().offset(dx, 0, dz));
                    if (top.getY() > level.getMinY() + 2 && (best == null || top.getY() > best.getY())) best = top;
                }
            }
            if (best == null) return;
            float bestYaw = p.getYRot();
            int bestScore = Integer.MAX_VALUE;
            for (int k = 0; k < 16; k++) {
                double a = Math.toRadians(k * 22.5);
                int score = 0;
                for (int r = 3; r <= 24; r += 3) {
                    int x = best.getX() + (int) Math.round(-Math.sin(a) * r), z = best.getZ() + (int) Math.round(Math.cos(a) * r);
                    int h = level.getHeight(hm, x, z);
                    score = Math.max(score, h <= level.getMinY() + 2 ? 6 : h - best.getY());     // void: a little worse than flat land
                }
                if (score < bestScore) {
                    bestScore = score;
                    bestYaw = k * 22.5f;
                }
            }
            p.teleportTo(level, best.getX() + 0.5, best.getY(), best.getZ() + 0.5, java.util.Set.of(), bestYaw, pitch, true);
        });
        ctx.waitTicks(10);
    }

    static final List<String> FLAT = List.of("minecraft:plains", "minecraft:sunflower_plains", "minecraft:meadow", "terralith:steppe",
            "terralith:shrubland", "terralith:valley_clearing", "terralith:blooming_valley", "terralith:lavender_valley", "minecraft:savanna",
            "minecraft:forest", "minecraft:birch_forest");

    /**
     * Searches the overworld around the player (rings every 40 blocks up to 2400) for dry land in one of the biomes whose
     * surroundings (8 blocks around) are no more than {@code flat} blocks higher or lower, using the generator's base
     * heights (no chunks are generated while searching), then teleports the player onto the real surface there.
     */
    private boolean findLand(List<String> biomes, int flat) {
        Object pos = sp.getServer().computeOnServer(server -> {
            var p = server.getPlayerList().getPlayers().getFirst();
            var level = server.overworld();
            var gen = level.getChunkSource().getGenerator();
            var rs = level.getChunkSource().randomState();
            var surfT = net.minecraft.world.level.levelgen.Heightmap.Types.WORLD_SURFACE_WG;
            var floorT = net.minecraft.world.level.levelgen.Heightmap.Types.OCEAN_FLOOR_WG;
            var keys = biomes.stream().map(b -> net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.BIOME,
                    net.minecraft.resources.Identifier.parse(b))).toList();
            int ox = p.getBlockX(), oz = p.getBlockZ(), sea = gen.getSeaLevel();
            for (int r = 0; r <= 2400; r += 40) {
                int n = Math.max(1, (int) (2 * Math.PI * r / 40));
                for (int i = 0; i < n; i++) {
                    double a = 2 * Math.PI * i / n;
                    int x = ox + (int) Math.round(Math.cos(a) * r), z = oz + (int) Math.round(Math.sin(a) * r);
                    int surf = gen.getBaseHeight(x, z, surfT, level, rs);
                    if (surf <= sea + 1 || surf != gen.getBaseHeight(x, z, floorT, level, rs)) continue;
                    var biome = level.getUncachedNoiseBiome(net.minecraft.core.QuartPos.fromBlock(x), net.minecraft.core.QuartPos.fromBlock(surf),
                            net.minecraft.core.QuartPos.fromBlock(z));
                    if (keys.stream().noneMatch(biome::is)) continue;
                    boolean ok = true;
                    for (int[] d : new int[][] {{8, 0}, {-8, 0}, {0, 8}, {0, -8}, {8, 8}, {-8, -8}, {8, -8}, {-8, 8}}) {
                        int h = gen.getBaseHeight(x + d[0], z + d[1], surfT, level, rs);
                        if (Math.abs(h - surf) > flat || h != gen.getBaseHeight(x + d[0], z + d[1], floorT, level, rs)) {
                            ok = false;
                            break;
                        }
                    }
                    if (ok) return new net.minecraft.core.BlockPos(x, surf, z);
                }
            }
            return null;
        });
        if (!(pos instanceof net.minecraft.core.BlockPos bp)) {
            PackTest.LOG.warn("[dctest] no dry land in {}", biomes);
            return false;
        }
        PackTest.LOG.info("[dctest] land at {} ({})", bp, biomes.size() == 1 ? biomes.getFirst() : "flat");
        cmd("execute in minecraft:overworld run tp @p " + bp.getX() + " " + (bp.getY() + 20) + " " + bp.getZ());
        ctx.waitTicks(40);
        sp.getServer().runOnServer(server -> {
            var p = server.getPlayerList().getPlayers().getFirst();
            var top = p.level().getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.blockPosition());
            p.teleportTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5);
        });
        ctx.waitTicks(20);
        return true;
    }

    /** Moves the player to the nearest biome and onto its surface (overworld). */
    private void spread(String biome) {
        spreadIn("minecraft:overworld", biome);
    }

    private boolean spreadIn(String dim, String biome) {
        // locate the biome from where the player is, then teleport onto the ground there
        Object pos = sp.getServer().computeOnServer(server -> {
            var p = server.getPlayerList().getPlayers().getFirst();
            var level = server.getLevel(net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.DIMENSION,
                    net.minecraft.resources.Identifier.parse(dim)));
            if (level == null) return null;
            var key = net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.BIOME, net.minecraft.resources.Identifier.parse(biome));
            var found = level.findClosestBiome3d(h -> h.is(key), p.blockPosition(), 6400, 32, 64);
            return found == null ? null : found.getFirst();
        });
        if (pos instanceof net.minecraft.core.BlockPos bp) {
            cmd("execute in " + dim + " run tp @p " + bp.getX() + " 200 " + bp.getZ());
            ctx.waitTicks(40);
            cmd("execute in " + dim + " as @p at @p run tp @p ~ ~ ~");
            sp.getServer().runOnServer(server -> {
                var p = server.getPlayerList().getPlayers().getFirst();
                var level = p.level();
                var top = level.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.blockPosition());
                if (dim.equals("minecraft:the_nether")) {
                    // nether: find an air pocket above solid ground under the roof
                    int x = p.getBlockX(), z = p.getBlockZ();
                    for (int y = 100; y > 32; y--) {
                        var b = new net.minecraft.core.BlockPos(x, y, z);
                        if (level.getBlockState(b).isAir() && level.getBlockState(b.above()).isAir() && level.getBlockState(b.below()).isSolid()) {
                            top = b;
                            break;
                        }
                    }
                }
                p.teleportTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5);
            });
        } else {
            PackTest.LOG.warn("[dctest] biome {} not found", biome);
            return false;
        }
        ctx.waitTicks(20);
        return true;
    }
}
