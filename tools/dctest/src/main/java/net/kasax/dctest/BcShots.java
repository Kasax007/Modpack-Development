package net.kasax.dctest;

import com.mojang.blaze3d.platform.InputConstants;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.client.CameraType;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.gamerules.GameRules;

import java.util.HashMap;
import java.util.Map;

/**
 * Review shots of Beach Craft (the Raft mod), names bc_*: every feature shown working, so the author can check it.
 * Most shots play on a small raft stage in the raft dimension (see {@link #stage}); each stage sits at its own spot.
 * Actions run at fixed game ticks inside a shot ({@link #film}); frames are 30 fps of game time (3 frames = 2 ticks).
 */
final class BcShots {
    private final Film f;
    private final ClientGameTestContext ctx;
    private final TestSingleplayerContext sp;

    BcShots(Film f, ClientGameTestContext ctx, TestSingleplayerContext sp) {
        this.f = f;
        this.ctx = ctx;
        this.sp = sp;
    }

    // ------------------------------------------------------------------ helpers

    /** Absolute command in the raft dimension. */
    private void r(String... cs) {
        for (String c : cs) f.cmd("execute in raft:raftdim run " + c);
    }

    private void c(String... cs) {
        f.cmds(cs);
    }

    private static String fmt(String pattern, Object... args) {
        return String.format(java.util.Locale.ROOT, pattern, args);
    }

    /**
     * A 13x13 raft of foundations on open water in the raft dimension around (x, 99, z): water from Y 88 to 99 and air
     * from 100 to 115 in a 33x33 square, so islands or old builds never get in the way. The player stands on the middle.
     */
    private int[] stage(int x0, int z0, String mode) {
        int[] p = sea(x0, z0);
        int x = p[0], z = p[1];
        r(fmt("tp @p %d.5 120 %d.5", x, z));
        ctx.waitTicks(60);
        r(fmt("fill %d 88 %d %d 99 %d minecraft:water", x - 16, z - 16, x + 16, z + 16),
                fmt("fill %d 100 %d %d 115 %d minecraft:air", x - 16, z - 16, x + 16, z + 16),
                fmt("fill %d 99 %d %d 99 %d raft:raft_foundation", x - 6, z - 6, x + 6, z + 6),
                fmt("tp @p %d.5 100 %d.5 180 20", x, z),
                fmt("kill @e[type=!minecraft:player,x=%d,y=100,z=%d,distance=..60]", x, z));
        c("gamemode " + mode + " @p", "effect clear @p", "clear @p");
        ctx.waitTicks(20);
        return p;
    }

    /** Stage centres used in this run: a new stage keeps 80 blocks away from them. */
    private static final java.util.List<int[]> USED = new java.util.ArrayList<>();

    /**
     * The raft dimension uses the overworld's terrain noise with the sea at Y 100, so mountains stand out of the sea as
     * huge stone islands. The nearest spot (rings every 64 blocks) whose sea floor stays below Y 96 within 64 blocks, by
     * the generator's base heights (nothing is generated while searching).
     */
    private int[] sea(int x, int z) {
        int[] best = sp.getServer().computeOnServer(server -> {
            var level = server.getLevel(net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.DIMENSION,
                    net.minecraft.resources.Identifier.parse("raft:raftdim")));
            if (level == null) return new int[]{x, z};
            var gen = level.getChunkSource().getGenerator();
            var rs = level.getChunkSource().randomState();
            var floorT = net.minecraft.world.level.levelgen.Heightmap.Types.OCEAN_FLOOR_WG;
            for (int r = 0; r <= 3000; r += 64) {
                int n = Math.max(1, (int) (2 * Math.PI * r / 64));
                for (int i = 0; i < n; i++) {
                    double a = 2 * Math.PI * i / n;
                    int cx = x + (int) Math.round(Math.cos(a) * r), cz = z + (int) Math.round(Math.sin(a) * r);
                    boolean free = true;
                    for (int[] u : USED) {
                        if (Math.abs(u[0] - cx) < 80 && Math.abs(u[1] - cz) < 80) {
                            free = false;
                            break;
                        }
                    }
                    for (int dx = -64; free && dx <= 64; dx += 16) {
                        for (int dz = -64; free && dz <= 64; dz += 16) {
                            if (gen.getBaseHeight(cx + dx, cz + dz, floorT, level, rs) > 96) free = false;
                        }
                    }
                    if (free) return new int[]{cx, cz};
                }
            }
            return new int[]{x, z};
        });
        USED.add(best);
        if (best[0] != x || best[1] != z) PackTest.LOG.info("[dctest] stage {} {} moved to open sea at {} {}", x, z, best[0], best[1]);
        return best;
    }

    private void tp(double x, double y, double z, float yaw, float pitch) {
        r(fmt("tp @p %.2f %.2f %.2f %.1f %.1f", x, y, z, yaw, pitch));
    }

    private void look(int x, int y, int z) {
        ctx.getInput().lookAt(new BlockPos(x, y, z));
    }

    /** Right click through the key mapping: 26.3 uses SDL, where mouse button 1 is the LEFT button (right is 3). */
    private void use() {
        ctx.getInput().pressKey(o -> o.keyUse);
    }

    private void holdUse() {
        ctx.getInput().holdKey(o -> o.keyUse);
    }

    private void releaseUse() {
        ctx.getInput().releaseKey(o -> o.keyUse);
    }

    private void attack() {
        ctx.getInput().pressKey(o -> o.keyAttack);
    }

    private void closeScreen() {
        ctx.setScreen(() -> null);
    }

    private void slot(int n) {
        ctx.getInput().pressKey(InputConstants.KEY_1 + n);
    }

    /** Films {@code frames} frames; {@code at} maps a game tick of the shot to an action. */
    private void film(String name, int frames, Map<Integer, Runnable> at) {
        int[] t = {0};
        f.frames(name, frames, () -> {
            Runnable a = at.get(t[0]);
            if (a != null) a.run();
            t[0]++;
        });
    }

    private void film(String name, int frames) {
        film(name, frames, Map.of());
    }

    /** One landscape still for the end card / the description, then back to portrait. */
    private void still(String name) {
        f.landscape();
        ctx.waitTicks(10);
        f.still(name);
        f.portrait();
        ctx.waitTicks(5);
    }

    private void first(boolean hud) {
        f.camera(CameraType.FIRST_PERSON);
        f.hud(hud);
    }

    private void third(boolean hud) {
        f.camera(CameraType.THIRD_PERSON_BACK);
        f.hud(hud);
    }

    // ------------------------------------------------------------------ shots

    void shot(String name) {
        f.portrait();
        switch (name) {
            case "bc_raft_tour" -> raftTour();
            case "bc_beach" -> beach();
            case "bc_loot" -> loot();
            case "bc_energy" -> energy();
            case "bc_craft_portal" -> craftPortal();
            case "bc_portal" -> portal();
            case "bc_teleporter" -> teleporter();
            case "bc_island" -> island();
            case "bc_debris" -> debris();
            case "bc_hook" -> hook();
            case "bc_catcher" -> catcher();
            case "bc_trash" -> trash();
            case "bc_rope" -> rope();
            case "bc_ladder" -> ladder();
            case "bc_purifier" -> purifier();
            case "bc_drinks" -> drinks();
            case "bc_grill" -> grill();
            case "bc_crops" -> crops();
            case "bc_scarecrow" -> scarecrow();
            case "bc_shark" -> shark();
            case "bc_shark_attack" -> sharkAttack();
            case "bc_shark_drops" -> sharkDrops();
            case "bc_receiver" -> receiver();
            case "bc_paddle" -> paddle();
            case "bc_titanium" -> titanium();
            case "bc_armor" -> armor();
            case "bc_detector" -> detector();
            case "bc_disc" -> disc();
            case "bc_power" -> power();
            case "bc_quarry" -> quarry();
            case "bc_furnaces" -> furnaces();
            case "bc_deco" -> deco();
            default -> PackTest.LOG.warn("[dctest] unknown review shot {}", name);
        }
        closeScreen();
        releaseUse();
        ctx.getInput().releaseKey(o -> o.keyAttack);
        c("gamemode creative @p", "effect clear @p");
    }

    /** Intro: a fully furnished raft on the open sea with two sharks around it. */
    private void raftTour() {
        int[] st = stage(3000, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("fill %d 100 %d %d 105 %d minecraft:stripped_oak_log", x, z - 4, x, z - 4),
                fmt("fill %d 102 %d %d 105 %d raft:sail_canvas_red_striped", x - 2, z - 4, x + 2, z - 4),
                fmt("setblock %d 106 %d raft:raft_flag[facing=east]", x, z - 4),
                fmt("fill %d 100 %d %d 100 %d raft:crop_plot", x - 5, z - 2, x - 4, z + 1),
                fmt("fill %d 101 %d %d 101 %d minecraft:wheat[age=7]", x - 5, z - 2, x - 4, z + 1),
                fmt("setblock %d 100 %d raft:scarecrow[half=lower,facing=east]", x - 5, z + 3),
                fmt("setblock %d 101 %d raft:scarecrow[half=upper,facing=east]", x - 5, z + 3),
                fmt("setblock %d 100 %d raft:water_purifier[facing=west]", x + 4, z - 1),
                fmt("setblock %d 100 %d raft:simple_grill[facing=west]", x + 4, z + 1),
                fmt("setblock %d 100 %d raft:coconut_lantern", x + 4, z - 3),
                fmt("setblock %d 100 %d raft:rope_coil", x + 2, z - 3),
                fmt("fill %d 100 %d %d 102 %d raft:palm_planks", x + 6, z + 3, x + 6, z + 5),
                fmt("setblock %d 101 %d raft:ship_wheel[facing=west]", x + 5, z + 4),
                fmt("fill %d 103 %d %d 103 %d raft:palm_thatch_slab", x + 3, z + 2, x + 6, z + 6),
                fmt("fill %d 100 %d %d 102 %d raft:palm_fence", x + 3, z + 6, x + 3, z + 6),
                fmt("summon raft:shark %d 96 %d {PersistenceRequired:1b}", x - 9, z - 8),
                fmt("summon raft:shark %d 96 %d {PersistenceRequired:1b}", x + 9, z - 10),
                fmt("tp @p %d.5 100 %d.5 160 12", x, z + 4));
        c("item replace entity @p weapon.mainhand with raft:plastic_hook");
        third(false);
        f.settle(300);
        film("bc_raft_tour", 150, Map.of(), 0.35f);
        still("raft_tour");
    }

    /** Overworld beach: driftwood stumps and the driftwood sapling. */
    private void beach() {
        c("execute in minecraft:overworld run tp @p -800 200 800");
        f.findLand(java.util.List.of("minecraft:beach", "minecraft:snowy_beach"), 3);
        c("execute as @p at @p run tp @p ~ ~ ~ 0 25", "gamemode creative @p");
        c("execute as @p at @p rotated ~ 0 run fill ^-4 ^ ^-2 ^4 ^6 ^8 minecraft:air",
                "execute as @p at @p rotated ~ 0 run fill ^-4 ^-5 ^-2 ^4 ^-2 ^8 minecraft:sandstone",
                "execute as @p at @p rotated ~ 0 run fill ^-4 ^-1 ^-2 ^4 ^-1 ^8 minecraft:sand",
                "execute as @p at @p rotated ~ 0 run fill ^2 ^ ^6 ^2 ^1 ^6 raft:driftwood_log",
                "execute as @p at @p rotated ~ 0 run setblock ^-3 ^ ^7 raft:driftwood_log",
                "item replace entity @p weapon.mainhand with minecraft:bone_meal 64");
        first(true);
        f.settle(300);
        int[] base = new int[3];
        sp.getServer().runOnServer(s -> {
            var p = s.getPlayerList().getPlayers().getFirst();
            base[0] = p.getBlockX();
            base[1] = p.getBlockY();
            base[2] = p.getBlockZ();
        });
        int bx = base[0], by = base[1], bz = base[2];          // facing +z: the sapling stands 3 blocks ahead
        // the sapling is set inside the shot: set before the settle wait, it had already grown by itself
        Map<Integer, Runnable> at = new HashMap<>();
        at.put(1, () -> c(fmt("execute in minecraft:overworld run setblock %d %d %d raft:driftwood_sapling", bx, by, bz + 3)));
        at.put(2, () -> look(bx, by, bz + 3));
        for (int i = 0; i < 10; i++) at.put(22 + i * 8, this::use);
        at.put(110, () -> {
            // straight south beside the new stump: from the camera behind, the stump stands left of the player, not hidden behind
            c(fmt("execute in minecraft:overworld run tp @p %.1f %d %.1f 0 15", bx - 1.5, by, bz - 0.5));
            f.camera(CameraType.THIRD_PERSON_BACK);
        });
        film("bc_beach", 210, at);
    }

    /** Shipwreck treasure with the mod's ancient items. */
    private void loot() {
        int[] st = stage(3200, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("setblock %d 100 %d minecraft:chest[facing=south]", x, z - 2));
        for (int i = 0; i < 3; i++) r(fmt("loot insert %d 100 %d loot minecraft:chests/shipwreck_treasure", x, z - 2));
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(false);
        f.settle(200);
        film("bc_loot", 120, Map.of(5, () -> {
            look(x, 100, z - 2);
            use();
        }));
    }

    /** Ancient broken rings smelt into ancient energy (blast furnace). */
    private void energy() {
        int[] st = stage(3400, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("setblock %d 100 %d minecraft:blast_furnace[facing=south]", x, z - 2));
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(false);
        f.settle(200);
        film("bc_energy", 180, Map.of(
                1, () -> {
                    r(fmt("item replace block %d 100 %d container.0 with raft:ancient_broken_ring 3", x, z - 2),
                            fmt("item replace block %d 100 %d container.1 with minecraft:coal 1", x, z - 2),
                            fmt("data merge block %d 100 %d {cooking_time_spent:40s}", x, z - 2));
                    look(x, 100, z - 2);
                    use();
                }));
    }

    /** Crafter: four portal frames, then the energy staff. */
    private void craftPortal() {
        int[] st = stage(3600, 3000, "creative");
        int x = st[0], z = st[1];
        String b = fmt("%d 100 %d", x, z - 2);
        r("setblock " + b + " minecraft:crafter[orientation=up_south]");
        r("item replace block " + b + " container.1 with raft:driftwood_log", "item replace block " + b + " container.3 with raft:driftwood_log",
                "item replace block " + b + " container.5 with raft:driftwood_log", "item replace block " + b + " container.7 with raft:driftwood_log",
                "item replace block " + b + " container.4 with raft:ancient_energy");
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(false);
        f.settle(200);
        film("bc_craft_portal", 180, Map.of(
                3, () -> {
                    look(x, 100, z - 2);
                    use();
                },
                60, () -> {
                    for (int i = 0; i < 9; i++) r("item replace block " + b + " container." + i + " with minecraft:air");
                    r("item replace block " + b + " container.1 with raft:ancient_energy", "item replace block " + b + " container.4 with raft:ancient_crystal",
                            "item replace block " + b + " container.7 with minecraft:stick");
                }));
    }

    /** Overworld: the staff's hints, lighting the frame, the trip and the arrival platform high above the sea. */
    private void portal() {
        c("execute in minecraft:overworld run tp @p 900 200 -900");
        f.findLand(Film.FLAT, 2);
        c("execute as @p at @p run tp @p ~ ~ ~ 0 0", "gamemode creative @p",
                "fill ~-4 ~ ~1 ~4 ~6 ~7 minecraft:air", "fill ~-4 ~-1 ~1 ~4 ~-1 ~7 minecraft:smooth_stone",
                "fill ~-1 ~ ~4 ~2 ~4 ~4 raft:driftwood_portal_frame", "fill ~ ~1 ~4 ~1 ~3 ~4 minecraft:air",
                "setblock ~ ~4 ~4 minecraft:air", "item replace entity @p weapon.mainhand with raft:energy_staff");
        first(true);
        f.settle(300);
        int[] base = new int[3];
        sp.getServer().runOnServer(s -> {
            var p = s.getPlayerList().getPlayers().getFirst();
            base[0] = p.getBlockX();
            base[1] = p.getBlockY();
            base[2] = p.getBlockZ();
        });
        int bx = base[0], by = base[1], bz = base[2];
        film("bc_portal_light", 210, Map.of(
                5, () -> {
                    look(bx, by - 1, bz + 2);
                    use();
                },
                50, () -> {
                    look(bx, by, bz + 4);
                    use();
                },
                95, () -> c(fmt("execute in minecraft:overworld run setblock %d %d %d raft:driftwood_portal_frame", bx, by + 4, bz + 4)),
                100, () -> {
                    look(bx, by, bz + 4);
                    use();
                }));
        still("portal_light");
        // the trip: survival, standing in the portal (the swirl needs the HUD)
        c("gamemode survival @p", "clear @p", "effect give @p minecraft:resistance 60 4 true",
                fmt("execute in minecraft:overworld run tp @p %.1f %d %.1f 0 0", bx + 1.5, by + 1, bz + 4.5));   // not "%d.5": wrong for negative z
        first(true);
        BlockPos inPortal = new BlockPos(bx + 1, by + 1, bz + 4);
        film("bc_portal_trip", 120, Map.of(40, () -> portalDiag("t40", null), 78, () -> portalDiag("t78", null)));
        ctx.waitTicks(40);
        portalDiag("after", inPortal);
        f.settle(600);
        c("gamemode creative @p");
        third(false);
        // the arrival portal stands along X (like the one at home) on a platform from 2 blocks north to 1 block south:
        // step to the north edge and face the portal, the camera floats behind over the sea
        c("execute as @p at @p run tp @p ~ ~ ~-2.4 0 12");
        film("bc_portal_arrive", 150, Map.of(), 0.3f);
    }

    /** Logs the player's portal state; with {@code portalPos} (overworld) also what the portal block would teleport to. */
    private void portalDiag(String tag, BlockPos portalPos) {
        sp.getServer().runOnServer(s -> {
            var p = s.getPlayerList().getPlayers().getFirst();
            var pp = p.portalProcess;
            ServerLevel lvl = (ServerLevel) p.level();
            String dest = "-";
            if (portalPos != null && lvl.dimension() == net.minecraft.world.level.Level.OVERWORLD) {
                var st = lvl.getBlockState(portalPos);
                if (st.getBlock() instanceof net.minecraft.world.level.block.Portal portal) {
                    try {
                        var t = portal.getPortalDestination(lvl, p, portalPos);
                        dest = t == null ? "null" : t.newLevel().dimension() + " " + t.position();
                    } catch (Throwable e) {
                        dest = "threw " + e;
                        PackTest.LOG.warn("[dctest] portal destination threw", e);
                    }
                } else {
                    dest = "no portal block: " + st;
                }
            }
            PackTest.LOG.info("[dctest] portal {}: dim={} pos={} cooldown={} process={} time={} inside={} delay={} canUse={} dest={}", tag,
                    lvl.dimension(), p.position(), p.getPortalCooldown(), pp != null, pp == null ? -1 : pp.getPortalTime(),
                    pp != null && pp.isInsidePortalThisTick(), lvl.getGameRules().get(GameRules.PLAYERS_NETHER_PORTAL_DEFAULT_DELAY),
                    p.canUsePortal(false), dest);
        });
    }

    private void film(String name, int frames, Map<Integer, Runnable> at, float yawPerTick) {
        Map<Integer, Runnable> all = new HashMap<>(at);
        int ticks = frames * 2 / 3 + 2;
        for (int i = 0; i < ticks; i++) {
            Runnable prev = all.get(i);
            all.put(i, () -> {
                if (prev != null) prev.run();
                f.cmd(fmt("execute as @p at @p run tp @p ~ ~ ~ ~%.2f ~", yawPerTick));
            });
        }
        film(name, frames, all);
    }

    /** The Raft Teleporter: from the overworld straight onto a stone block in the raft ocean. */
    private void teleporter() {
        c("execute in minecraft:overworld run tp @p 700 200 -700");
        f.findLand(Film.FLAT, 2);
        c("execute as @p at @p run tp @p ~ ~ ~ 0 -10", "gamemode survival @p", "clear @p",
                "effect give @p minecraft:resistance 60 4 true", "item replace entity @p weapon.mainhand with raft:raft_teleporter");
        first(true);
        f.settle(300);
        film("bc_teleporter", 60, Map.of(10, this::use));
        ctx.waitTicks(40);
        f.settle(600);
        third(true);
        film("bc_teleporter_arrive", 120, Map.of(), 0.3f);
        c("gamemode creative @p");
    }

    /** A sand islet: a palm grows from a sapling, and a coconut is picked from the leaves. */
    private void island() {
        int[] st = stage(3800, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("fill %d 90 %d %d 99 %d minecraft:sandstone", x - 8, z - 12, x + 8, z - 2),
                fmt("fill %d 100 %d %d 100 %d minecraft:sand", x - 8, z - 12, x + 8, z - 2),
                fmt("place feature raft:palmwood %d 101 %d", x + 4, z - 9),
                fmt("setblock %d 101 %d raft:palm_sapling", x - 2, z - 5),
                fmt("setblock %d 100 %d raft:palm_log", x + 2, z - 1),
                fmt("setblock %d 101 %d raft:palm_log", x + 2, z - 1),
                fmt("setblock %d 102 %d raft:palm_coconut_leaves[persistent=false,distance=1]", x + 2, z - 1));
        c("item replace entity @p weapon.mainhand with minecraft:bone_meal 64");
        tp(x - 1.5, 101, z - 2.5, 180, 30);                    // on the islet, 2 blocks from the sapling (reach is 5)
        first(true);
        f.settle(300);
        Map<Integer, Runnable> at = new HashMap<>();
        at.put(2, () -> look(x - 2, 101, z - 5));
        for (int i = 0; i < 10; i++) at.put(10 + i * 8, this::use);
        at.put(90, () -> {
            c("gamemode survival @p", "item replace entity @p weapon.mainhand with minecraft:air");
            tp(x + 2.5, 100, z + 1.5, 180, -40);
        });
        at.put(96, () -> {
            look(x + 2, 102, z - 1);
            use();
        });
        film("bc_island", 210, at);
        c("gamemode creative @p");
    }

    /** Debris drifting in from the west past the raft. */
    private void debris() {
        int[] st = stage(4000, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("fill %d 99 %d %d 99 %d raft:raft_foundation", x - 1, z - 1, x + 1, z + 1),
                fmt("fill %d 99 %d %d 99 %d minecraft:water", x - 6, z - 6, x + 6, z + 6),
                fmt("fill %d 99 %d %d 99 %d raft:raft_foundation", x - 1, z - 1, x + 1, z + 1));
        String[] items = {"raft:plastic", "raft:scrap_metal", "raft:driftwood_planks", "raft:palm_leaves", "raft:plastic", "raft:coconut",
                "raft:driftwood_planks", "raft:scrap_metal", "raft:palm_leaves", "raft:plastic"};
        tp(x - 0.5, 100, z + 0.5, 90, 24);                      // west edge of the little raft, looking west into the current
        first(false);
        f.settle(200);
        // the debris is summoned during the shot (the server runs ahead of the film clock: items summoned before the
        // settle wait had already drifted onto the raft): a few out on the water at once, then one every 10 ticks
        Map<Integer, Runnable> at = new HashMap<>();
        for (int i = 0; i < 14; i++) {
            int k = i;
            double dx = k < 4 ? 7.5 + k * 3.0 : 16.5, dz = ((k % 5) - 2) * 1.4;
            Runnable summon = () -> r(fmt("summon minecraft:item %.1f 99.6 %.1f {Item:{id:\"%s\",count:%d},Tags:[\"raft_debris\"]}",
                    x - dx, z + 0.5 + dz, items[k % items.length], 1 + k % 2));
            at.merge(k < 4 ? 0 : (k - 3) * 10, summon, (first, second) -> () -> {
                first.run();
                second.run();
            });
        }
        film("bc_debris", 180, at);
    }

    /** The plastic hook pulls floating items in. */
    private void hook() {
        int[] st = stage(4200, 3000, "survival");
        int x = st[0], z = st[1];
        c("effect give @p minecraft:resistance 60 4 true", "item replace entity @p weapon.mainhand with raft:plastic_hook");
        r(fmt("summon minecraft:item %.1f 99.6 %.1f {Item:{id:\"raft:plastic\",count:2},Tags:[\"raft_debris\"]}", x + 0.5, z + 14.5),
                fmt("summon minecraft:item %.1f 99.6 %.1f {Item:{id:\"raft:scrap_metal\",count:1},Tags:[\"raft_debris\"]}", x + 2.0, z + 15.5),
                fmt("summon minecraft:item %.1f 99.6 %.1f {Item:{id:\"raft:driftwood_planks\",count:2},Tags:[\"raft_debris\"]}", x - 1.5, z + 13.5));
        tp(x + 0.5, 100, z + 6.5, 0, 20);
        third(true);
        f.settle(200);
        film("bc_hook", 150, Map.of(10, () -> holdUse(), 90, () -> releaseUse()));
        c("gamemode creative @p");
    }

    /** The item catcher catches debris; with a net it hauls ocean garbage. */
    private void catcher() {
        int[] st = stage(4400, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("fill %d 99 %d %d 99 %d minecraft:water", x - 12, z - 12, x + 4, z - 7),
                fmt("setblock %d 99 %d raft:item_catcher[waterlogged=true]", x, z - 9),
                fmt("summon minecraft:item %.1f 99.6 %.1f {Item:{id:\"raft:plastic\",count:2},Tags:[\"raft_debris\"]}", x - 4.5, z - 8.5),
                fmt("summon minecraft:item %.1f 99.6 %.1f {Item:{id:\"raft:plastic\",count:1},Tags:[\"raft_debris\"]}", x - 6.5, z - 8.5));
        tp(x + 0.5, 100, z - 5.5, 180, 30);
        first(false);
        f.settle(200);
        film("bc_catcher", 210, Map.of(
                115, () -> {
                    look(x, 99, z - 9);
                    use();
                }));
        closeScreen();
        r(fmt("item replace block %d 99 %d container.1 with minecraft:air", x, z - 9),
                fmt("item replace block %d 99 %d container.0 with raft:net", x, z - 9),
                fmt("data merge block %d 99 %d {\"item_collector.progress\":500}", x, z - 9));
        film("bc_catcher_net", 150, Map.of(
                5, () -> {
                    look(x, 99, z - 9);
                    use();
                }));
    }

    /** Ocean garbage smelts into trash cubes, and every cube pops out 1-3 random items. */
    private void trash() {
        int[] st = stage(4600, 3000, "survival");
        int x = st[0], z = st[1];
        c("effect give @p minecraft:resistance 60 4 true");
        r(fmt("setblock %d 100 %d minecraft:furnace[facing=south]", x, z - 2),
                fmt("item replace block %d 100 %d container.0 with raft:unrefined_ocean_garbage 3", x, z - 2),
                fmt("item replace block %d 100 %d container.1 with minecraft:coal 1", x, z - 2),
                fmt("data merge block %d 100 %d {cooking_time_spent:150s}", x, z - 2));
        // a full inventory: the items from the cubes stay on the raft where the camera sees them
        for (int i = 1; i < 9; i++) c("item replace entity @p hotbar." + i + " with minecraft:cobblestone 64");
        for (int i = 0; i < 27; i++) c("item replace entity @p inventory." + i + " with minecraft:cobblestone 64");
        c("item replace entity @p weapon.mainhand with raft:trash_cube 3");
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(true);
        f.settle(200);
        film("bc_trash", 120, Map.of(3, () -> {
            look(x, 100, z - 2);
            use();
        }));
        closeScreen();
        tp(x + 0.5, 100, z + 0.5, 180, -20);
        f.camera(CameraType.THIRD_PERSON_BACK);
        film("bc_trash_open", 150, Map.of(10, this::use, 40, this::use, 70, this::use));
        c("clear @p", "gamemode creative @p");
    }

    /** Survival crafting: rope from palm leaves, a rope coil, sail canvas. */
    private void rope() {
        int[] st = stage(4800, 3000, "survival");
        int x = st[0], z = st[1];
        tp(x + 0.5, 100, z + 0.5, 180, 10);
        first(false);
        f.settle(200);
        film("bc_rope", 210, Map.of(
                3, () -> {
                    ctx.getInput().pressKey(o -> o.keyInventory);
                },
                8, () -> c("item replace entity @p player.crafting.0 with raft:palm_leaves", "item replace entity @p player.crafting.2 with raft:palm_leaves"),
                50, () -> c("item replace entity @p player.crafting.0 with raft:rope", "item replace entity @p player.crafting.1 with raft:rope",
                        "item replace entity @p player.crafting.2 with raft:rope", "item replace entity @p player.crafting.3 with raft:rope"),
                95, () -> c("item replace entity @p player.crafting.2 with minecraft:white_wool", "item replace entity @p player.crafting.3 with minecraft:white_wool")));
        closeScreen();
        c("clear @p", "gamemode creative @p");
    }

    /** Climbing a rope ladder. */
    private void ladder() {
        int[] st = stage(5000, 3000, "survival");
        int x = st[0], z = st[1];
        r(fmt("fill %d 100 %d %d 108 %d raft:raft_foundation", x, z - 4, x, z - 4),
                fmt("fill %d 100 %d %d 108 %d raft:rope_ladder[facing=south]", x, z - 3, x, z - 3),
                fmt("fill %d 110 %d %d 110 %d raft:palm_thatch_slab[type=bottom]", x, z - 4, x, z - 2),   // a roof: the climber stays on top
                fmt("setblock %d 100 %d raft:rope_coil", x - 2, z - 3), fmt("setblock %d 100 %d raft:rope_coil", x + 2, z - 3));
        c("effect give @p minecraft:resistance 60 4 true");
        tp(x + 0.5, 100, z + 0.5, 180, -15);
        third(false);
        f.settle(200);
        film("bc_ladder", 120, Map.of(5, () -> ctx.getInput().holdKey(o -> o.keyUp), 70, () -> ctx.getInput().releaseKey(o -> o.keyUp)));
        c("gamemode creative @p");
    }

    /** The water purifier turns a water bucket into three fresh water. */
    private void purifier() {
        int[] st = stage(5200, 3000, "creative");
        int x = st[0], z = st[1];
        String b = fmt("%d 100 %d", x, z - 2);
        r("setblock " + b + " raft:water_purifier[facing=south]",
                "item replace block " + b + " container.0 with minecraft:water_bucket",
                "item replace block " + b + " container.1 with minecraft:coal 2");
        tp(x + 0.5, 100, z + 0.5, 180, 25);
        first(false);
        f.settle(200);
        film("bc_purifier_out", 60);
        r("data merge block " + b + " {Progress:150}");          // the server runs ahead of the film clock: leave room to watch the arrow
        film("bc_purifier", 150, Map.of(2, () -> {
            look(x, 100, z - 2);
            use();
        }));
        still("purifier");
    }

    /** Fresh water, coconut milk and the pina colada (survival, hungry and hurt). */
    private void drinks() {
        int[] st = stage(5400, 3000, "survival");
        int x = st[0], z = st[1];
        c("difficulty normal", "effect give @p minecraft:hunger 4 200 true");
        ctx.waitTicks(90);
        c("damage @p 8", "item replace entity @p hotbar.0 with raft:fresh_water 2", "item replace entity @p hotbar.1 with raft:coconut_milk 1",
                "item replace entity @p hotbar.2 with raft:pina_colada 1");
        tp(x + 0.5, 100, z + 0.5, 180, 5);
        first(true);
        f.settle(200);
        film("bc_drinks", 270, Map.of(
                3, () -> slot(0),
                5, () -> holdUse(), 42, () -> releaseUse(),
                50, () -> slot(1),
                52, () -> holdUse(), 89, () -> releaseUse(),
                100, () -> slot(2),
                102, () -> holdUse(), 139, () -> releaseUse()));
        c("gamemode creative @p", "effect clear @p");
    }

    /** The simple grill: fuel, two foods, both cooked. */
    private void grill() {
        int[] st = stage(5600, 3000, "survival");
        int x = st[0], z = st[1];
        String b = fmt("%d 100 %d", x, z - 2);
        r("setblock " + b + " raft:simple_grill[facing=south]");
        c("effect give @p minecraft:resistance 60 4 true", "item replace entity @p hotbar.0 with minecraft:oak_planks 4",
                "item replace entity @p hotbar.1 with minecraft:beef 1", "item replace entity @p hotbar.2 with raft:shark_meat 1");
        tp(x + 0.5, 100, z + 0.5, 180, 40);
        first(true);
        f.settle(200);
        film("bc_grill", 120, Map.of(
                3, () -> look(x, 100, z - 2),
                5, () -> slot(0), 8, this::use,
                25, () -> slot(1), 28, this::use,
                45, () -> slot(2), 48, this::use));
        ctx.waitTicks(320);
        // beside the grill, so the body does not hide it from the camera behind
        tp(x + 1.8, 100, z + 0.8, 180, 30);     // looking straight north: the camera behind sees the grill left of the player
        f.camera(CameraType.THIRD_PERSON_BACK);
        film("bc_grill_done", 120);
        c("gamemode creative @p");
    }

    /** Crop plots against wet farmland: the plots grow faster, are never dry and never trampled. */
    private void crops() {
        int[] st = stage(5800, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("fill %d 99 %d %d 99 %d raft:crop_plot", x - 1, z - 6, x - 1, z - 2),
                fmt("fill %d 99 %d %d 99 %d minecraft:water", x, z - 6, x, z - 2),
                fmt("fill %d 99 %d %d 99 %d minecraft:farmland[moisture=7]", x + 1, z - 6, x + 1, z - 2),
                fmt("fill %d 100 %d %d 100 %d minecraft:wheat[age=0]", x - 1, z - 6, x - 1, z - 2),
                fmt("fill %d 100 %d %d 100 %d minecraft:wheat[age=0]", x + 1, z - 6, x + 1, z - 2));
        tp(x + 0.5, 100, z + 0.5, 180, 32);
        third(false);
        f.settle(200);
        c("gamerule random_tick_speed 600");
        film("bc_crops", 180);
        c("gamerule random_tick_speed 3");
        // trampling: jump onto a plot and onto plain farmland
        r(fmt("fill %d 100 %d %d 100 %d minecraft:air", x - 1, z - 6, x + 1, z - 2),
                fmt("fill %d 99 %d %d 99 %d raft:crop_plot", x - 1, z - 3, x - 1, z - 3),
                fmt("fill %d 99 %d %d 99 %d minecraft:farmland[moisture=7]", x + 1, z - 3, x + 1, z - 3));
        c("gamemode survival @p", "effect give @p minecraft:resistance 60 4 true");
        film("bc_trample", 120, Map.of(
                5, () -> tp(x - 0.5, 102.5, z - 2.5, 180, 70),
                45, () -> tp(x + 1.5, 102.5, z - 2.5, 180, 70)));
        c("gamemode creative @p");
    }

    /** Placing scarecrows from different sides: the head now faces the player every time. */
    private void scarecrow() {
        int[] st = stage(6000, 3000, "creative");
        int x = st[0], z = st[1];
        c("item replace entity @p weapon.mainhand with raft:scarecrow 4");
        tp(x + 0.5, 100, z + 2.5, 180, 30);
        first(false);
        f.settle(200);
        film("bc_scarecrow", 180, Map.of(
                5, () -> {
                    look(x - 2, 99, z - 1);
                    use();
                },
                35, () -> {
                    look(x + 2, 99, z - 1);
                    use();
                },
                65, () -> {
                    tp(x + 3.5, 100, z - 0.5, 90, 0);
                    f.camera(CameraType.THIRD_PERSON_BACK);
                }));
    }

    /** Bruce swims around the raft (creative players are never attacked). */
    private void shark() {
        int[] st = stage(6200, 3000, "creative");
        int x = st[0], z = st[1];
        // under water next to the raft (from above, the water surface hides him); conduit power clears the view
        c("effect give @p minecraft:conduit_power 60 0 true", "effect give @p minecraft:night_vision 60 0 true");
        r(fmt("summon raft:shark %d 94 %d {PersistenceRequired:1b}", x - 3, z - 13));   // ahead-left: not hidden behind the player
        tp(x + 0.5, 94, z - 9.5, 180, 0);
        third(false);
        f.settle(200);
        film("bc_shark", 150);
    }

    /** In survival, swimming next to the raft: Bruce attacks. */
    private void sharkAttack() {
        int[] st = stage(6400, 3000, "survival");
        int x = st[0], z = st[1];
        c("difficulty normal", "effect give @p minecraft:resistance 60 2 true", "effect give @p minecraft:regeneration 60 2 true",
                "effect give @p minecraft:conduit_power 60 0 true");
        r(fmt("summon raft:shark %d 94 %d {PersistenceRequired:1b}", x, z - 16));
        tp(x + 0.5, 95, z - 9.5, 180, 0);                      // swimming beside the raft, seen under water
        third(true);
        f.settle(200);
        film("bc_shark_attack", 180);
        still("shark_attack");
        c("gamemode creative @p", "effect clear @p");
        r(fmt("kill @e[type=raft:shark,x=%d,y=99,z=%d,distance=..40]", x, z));
    }

    /** Shark drops (meat, teeth), the trophy recipe and the trophy on a wall. */
    private void sharkDrops() {
        int[] st = stage(6600, 3000, "survival");
        int x = st[0], z = st[1];
        c("effect give @p minecraft:resistance 60 4 true", "item replace entity @p weapon.mainhand with minecraft:diamond_sword");
        r(fmt("summon raft:shark %d 100 %d {PersistenceRequired:1b,NoAI:1b}", x, z - 3),
                fmt("tp @p %.1f 100 %.1f 180 20", x + 1.8, z + 1.0));   // straight north: the shark is left of the player, not behind
        third(true);
        f.settle(200);
        film("bc_shark_drops", 120, Map.of(15, () -> {
            attack();
            c("damage @e[type=raft:shark,limit=1,sort=nearest] 40 minecraft:player_attack by @p");
        }));
        c("gamemode creative @p");
        String b = fmt("%d 100 %d", x + 3, z - 2);
        r("setblock " + b + " minecraft:crafter[orientation=up_south]",
                "item replace block " + b + " container.0 with minecraft:oak_planks", "item replace block " + b + " container.1 with minecraft:oak_planks",
                "item replace block " + b + " container.2 with minecraft:oak_planks", "item replace block " + b + " container.3 with raft:shark_tooth",
                "item replace block " + b + " container.4 with raft:shark_tooth", "item replace block " + b + " container.5 with raft:shark_tooth",
                fmt("fill %d 100 %d %d 102 %d raft:driftwood_planks", x - 3, z - 5, x - 1, z - 5),
                fmt("setblock %d 101 %d raft:shark_jaw_trophy[facing=south]", x - 2, z - 4));
        first(false);
        film("bc_trophy", 150, Map.of(
                3, () -> {
                    look(x + 3, 100, z - 2);
                    use();
                },
                70, () -> {
                    closeScreen();
                    tp(x - 1.5, 100, z - 1.5, 180, 5);
                }));
    }

    /** The receiver points to the nearest floating driftwood. */
    private void receiver() {
        r("tp @p 110.5 120 110.5");
        ctx.waitTicks(60);
        r("setblock 110 99 110 raft:driftwood_planks", "tp @p 110.5 100 110.5 135 -5");
        c("gamemode creative @p", "item replace entity @p weapon.mainhand with raft:receiver");
        first(true);
        f.settle(400);
        film("bc_receiver", 180, Map.of(5, this::use, 90, () -> f.camera(CameraType.THIRD_PERSON_BACK)));
    }

    /** The paddle shoves a boat forward. */
    private void paddle() {
        int[] st = stage(6800, 3000, "survival");
        int x = st[0], z = st[1];
        r(fmt("fill %d 99 %d %d 99 %d minecraft:water", x - 6, z - 6, x + 6, z + 6),
                fmt("summon minecraft:oak_boat %d.5 99.6 %d.5 {Rotation:[180f,0f]}", x, z + 10));
        for (int k = 0; k < 7; k++) {                           // buoys left and right of the course: the push is seen
            r(fmt("setblock %d 99 %d raft:raft_foundation", x - 2, z + 8 - 4 * k), fmt("setblock %d 99 %d raft:raft_foundation", x + 3, z + 6 - 4 * k));
        }
        tp(x + 0.5, 100, z + 10.5, 180, 10);
        ctx.waitTicks(10);
        c("ride @p mount @e[type=minecraft:oak_boat,limit=1,sort=nearest]", "item replace entity @p weapon.mainhand with raft:paddle");
        third(true);
        f.settle(200);
        Map<Integer, Runnable> at = new HashMap<>();
        for (int t : new int[]{10, 45, 80, 115}) at.put(t, this::use);
        for (int t : new int[]{9, 11, 13, 17, 25}) at.put(t, () -> boatDiag("t" + t));
        film("bc_paddle", 180, at);
        c("ride @p dismount", "gamemode creative @p");
    }

    /** Logs the boat under the player on both sides: who simulates it and whether the paddle moved it. */
    private void boatDiag(String tag) {
        String client = ctx.computeOnClient(mc -> {
            var v = mc.player == null ? null : mc.player.getVehicle();
            if (v == null) return "no vehicle";
            return fmt("pos=%.2f,%.2f vel=%.3f,%.3f authoritative=%s controller=%s cooldown=%s", v.getX(), v.getZ(),
                    v.getDeltaMovement().x, v.getDeltaMovement().z, v.isLocalInstanceAuthoritative(), v.getControllingPassenger(),
                    mc.player.getCooldowns().isOnCooldown(mc.player.getMainHandItem()));
        });
        String server = sp.getServer().computeOnServer(s -> {
            var v = s.getPlayerList().getPlayers().getFirst().getVehicle();
            if (v == null) return "no vehicle";
            return fmt("pos=%.2f,%.2f vel=%.3f,%.3f authoritative=%s", v.getX(), v.getZ(), v.getDeltaMovement().x, v.getDeltaMovement().z,
                    v.isLocalInstanceAuthoritative());
        });
        PackTest.LOG.info("[dctest] boat {}: client {} | server {}", tag, client, server);
    }

    /** Titanium ore with a diamond pickaxe, the blast furnace, the storage blocks and grates. */
    private void titanium() {
        int[] st = stage(7000, 3000, "survival");
        int x = st[0], z = st[1];
        r(fmt("setblock %d 100 %d raft:deepslate_titanium_ore", x, z - 2),
                fmt("setblock %d 100 %d raft:titanium_block", x - 2, z - 3), fmt("setblock %d 100 %d raft:raw_titanium_block", x + 2, z - 3),
                fmt("setblock %d 100 %d raft:titanium_grates", x - 3, z - 3), fmt("setblock %d 100 %d raft:titanium_grates", x + 3, z - 3));
        c("effect give @p minecraft:resistance 60 4 true", "item replace entity @p weapon.mainhand with minecraft:diamond_pickaxe");
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(true);
        f.settle(200);
        film("bc_titanium", 150, Map.of(3, () -> {
            look(x, 100, z - 2);
            ctx.getInput().holdKey(o -> o.keyAttack);
        }, 60, () -> ctx.getInput().releaseKey(o -> o.keyAttack)));
        c("gamemode creative @p");
        String b = fmt("%d 100 %d", x, z - 2);
        r("setblock " + b + " minecraft:blast_furnace[facing=south]", "item replace block " + b + " container.0 with raft:raw_titanium 6",
                "item replace block " + b + " container.1 with minecraft:coal 2", "data merge block " + b + " {cooking_time_spent:60s}");
        film("bc_titanium_smelt", 120, Map.of(2, () -> {
            look(x, 100, z - 2);
            use();
        }));
    }

    /** Putting on titanium armor: the full set gives water breathing, dolphin's grace and conduit power. */
    private void armor() {
        int[] st = stage(7200, 3000, "survival");
        int x = st[0], z = st[1];
        c("item replace entity @p armor.head with raft:titanium_helmet", "item replace entity @p armor.chest with raft:titanium_chestplate",
                "item replace entity @p armor.legs with raft:titanium_leggings");
        tp(x + 0.5, 100, z + 0.5, 180, 10);
        third(true);
        f.settle(200);
        film("bc_armor", 180, Map.of(40, () -> c("item replace entity @p armor.feet with raft:titanium_boots"),
                90, () -> tp(x + 0.5, 97, z - 8.5, 180, 10)));
        c("gamemode creative @p", "effect clear @p");
    }

    /** The metal detector reports titanium ore under the clicked block. */
    private void detector() {
        int[] st = stage(7400, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("setblock %d 90 %d raft:titanium_ore", x, z - 2));
        c("item replace entity @p weapon.mainhand with raft:metal_detector");
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(true);
        f.settle(200);
        film("bc_detector", 150, Map.of(5, () -> {
            look(x, 99, z - 2);
            use();
        }, 70, () -> {
            look(x + 2, 99, z - 2);
            use();
        }));
    }

    /** One of the three music discs in a jukebox. */
    private void disc() {
        int[] st = stage(7600, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("setblock %d 100 %d minecraft:jukebox", x, z - 2));
        c("item replace entity @p hotbar.0 with raft:lofi_beat_music_disc", "item replace entity @p hotbar.1 with raft:crystal_castles_music_disc",
                "item replace entity @p hotbar.2 with raft:some_game_music_music_disc");
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(true);
        f.settle(200);
        film("bc_disc", 150, Map.of(3, () -> slot(0), 10, () -> {
            look(x, 100, z - 2);
            use();
        }));
    }

    /** Solar panels and the battery (its screen fills up), with a Tech Reborn lamp. */
    private void power() {
        int[] st = stage(7800, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("setblock %d 100 %d raft:makeshift_battery{Energy:0L}", x, z - 2),
                fmt("fill %d 100 %d %d 100 %d raft:makeshift_solar_panel{Energy:100000L}", x - 1, z - 3, x + 1, z - 3),
                fmt("setblock %d 101 %d techreborn:lamp_incandescent[facing=up]", x + 2, z - 2),
                fmt("setblock %d 100 %d raft:copper_cable", x + 2, z - 2), fmt("setblock %d 100 %d raft:copper_cable", x + 1, z - 2));
        tp(x + 3.2, 100, z + 2.5, 180, 22);     // straight north: battery, panels and lamp left of the player, not behind
        third(false);
        f.settle(200);
        film("bc_power", 90);
        tp(x + 0.5, 100, z + 1.5, 180, 25);
        first(false);
        film("bc_battery", 150, Map.of(3, () -> {
            look(x, 100, z - 2);
            use();
        }));
    }

    /** The quarry digs out its 11x11 area block by block. */
    private void quarry() {
        int[] st = stage(8000, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("fill %d 88 %d %d 99 %d minecraft:air", x - 6, z - 14, x + 6, z - 2),
                fmt("fill %d 95 %d %d 99 %d minecraft:glass", x - 6, z - 14, x + 6, z - 2),
                fmt("fill %d 99 %d %d 99 %d minecraft:lime_wool", x - 5, z - 13, x + 5, z - 3),
                fmt("fill %d 95 %d %d 98 %d minecraft:air", x - 5, z - 13, x + 5, z - 3),
                // the quarry mines each column down to the bottom of the world (1000 FE a block, one a second) and
                // skips water: with water under the wool it moves on to the next column at once, so the wool is
                // seen going block by block (with the real sea floor below, the first column alone takes minutes)
                fmt("fill %d -63 %d %d 87 %d minecraft:water", x - 5, z - 13, x + 5, z - 3),
                fmt("setblock %d 100 %d raft:quarry[facing=south]{Energy:0L}", x, z - 8),
                fmt("setblock %d 101 %d minecraft:chest[facing=south]", x, z - 8));
        // north of the pit, looking south: the first row (z - 13, dug from west to east) right in front, the quarry
        // and its chest behind it on the left
        r(fmt("setblock %d 103 %d minecraft:barrier", x - 2, z - 16),
                fmt("tp @p %.1f 104 %.1f 0 38", x - 1.5, z - 15.5));
        third(false);
        f.settle(200);
        Map<Integer, Runnable> at = new HashMap<>();
        for (int t = 0; t < 160; t += 10) at.put(t, () -> r(fmt("data merge block %d 100 %d {Energy:10000L}", x, z - 8)));
        film("bc_quarry", 240, at);
    }

    /** Brick furnace and titanium furnace against a vanilla furnace. */
    private void furnaces() {
        int[] st = stage(8200, 3000, "creative");
        int x = st[0], z = st[1];
        r(fmt("setblock %d 100 %d raft:titanium_furnace[facing=south]", x, z - 2),
                fmt("item replace block %d 100 %d container.0 with minecraft:raw_iron 32", x, z - 2),
                fmt("item replace block %d 100 %d container.1 with minecraft:coal 2", x, z - 2),
                fmt("setblock %d 100 %d raft:brick_furnace[facing=south]", x - 2, z - 2), fmt("setblock %d 100 %d minecraft:furnace[facing=south]", x + 2, z - 2));
        tp(x + 0.5, 100, z + 0.5, 180, 30);
        first(false);
        f.settle(200);
        film("bc_furnaces", 150, Map.of(2, () -> {
            look(x, 100, z - 2);
            use();
        }));
    }

    /** The decoration blocks and both wood sets on one raft. */
    private void deco() {
        int[] st = stage(8400, 3000, "creative");
        int x = st[0], z = st[1];
        String[] wall = {"raft:palm_log", "raft:palm_wood", "raft:palm_planks", "raft:stripped_palm_log", "raft:driftwood_log", "raft:driftwood_wood",
                "raft:driftwood_planks", "raft:stripped_driftwood_log", "raft:scrap_metal_block", "raft:plastic_block", "raft:palm_thatch",
                "raft:sail_canvas", "raft:sail_canvas_red_striped", "raft:reinforced_foundation", "raft:titanium_block"};
        for (int i = 0; i < wall.length; i++) {
            r(fmt("setblock %d %d %d %s", x - 5 + (i % 5) * 2 + (i / 5 % 2), 100 + i / 5, z - 5, wall[i]));
        }
        r(fmt("fill %d 100 %d %d 102 %d raft:palm_planks", x - 6, z - 6, x + 6, z - 6),
                fmt("setblock %d 101 %d raft:ship_wheel[facing=south]", x - 3, z - 4), fmt("setblock %d 101 %d raft:shark_jaw_trophy[facing=south]", x + 3, z - 4),
                fmt("setblock %d 100 %d raft:raft_flag[facing=east]", x - 4, z - 2), fmt("setblock %d 100 %d raft:coconut_lantern", x + 4, z - 2),
                fmt("setblock %d 100 %d raft:rope_coil", x - 1, z - 2), fmt("setblock %d 100 %d raft:palm_thatch_stairs[facing=south]", x + 1, z - 2),
                fmt("setblock %d 100 %d raft:palm_door[facing=south,half=lower]", x, z - 4), fmt("setblock %d 101 %d raft:palm_door[facing=south,half=upper]", x, z - 4),
                fmt("setblock %d 100 %d raft:driftwood_fence", x - 6, z - 1), fmt("setblock %d 100 %d raft:palm_fence_gate[facing=south]", x + 6, z - 1));
        tp(x + 0.5, 100, z + 3.5, 180, 8);
        third(false);
        f.settle(200);
        film("bc_deco", 180, Map.of(), 0.0f);
    }
}
