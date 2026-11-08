package net.kasax.dctest;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.JsonOps;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.AABB;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.function.Predicate;

/**
 * Beach Craft and Dreamcraft checks from the test checklist, in the full pack (-Pscene=bccheck -Pout=DIR, optional
 * -Pchecks=deck,hammock,... to run only some): every check writes a result with numbers into OUT/bccheck_report.json
 * and "[bccheck]" lines into the log, plus screenshots.
 * <ul>
 * <li>deck: a player standing on the deck of a turning, moving Expedition Raft (the raft moved by the server, as for a
 * second player whose friend steers) stays on the deck, also at a corner; a mob on the deck too</li>
 * <li>hammock: sleeping through the night in the overworld; in the nether nothing happens (no explosion)</li>
 * <li>compressor: an oxygen tank put in, the hand crank by sneak-use with an empty hand and by the GUI button</li>
 * <li>boss: Leviathan summoned with the key, fought in survival (phases, tideling cap, drops, advancement), a second
 * summon needs an Ancient Crystal, it heals after 30 s without players</li>
 * <li>trench: which creatures spawn in the abyssal trench (anglerfish against glow squid)</li>
 * <li>structures: natural Beach Craft structures in the real world, screenshots from above and inside</li>
 * <li>pets: Tamacraft pet homes resolved in the pack (look-alike structures of other mods), a pet in one of them</li>
 * <li>dreamstar: recipe loaded with its ingredients, the "Living the Dream" advancement when holding the star</li>
 * <li>sounds: whale song and bubble vent sounds really play (sound log, the test client has no audio device)</li>
 * </ul>
 */
final class BcCheck {
    private final ClientGameTestContext ctx;
    private final TestSingleplayerContext sp;
    private final Path out;
    private final JsonObject report = new JsonObject();

    BcCheck(ClientGameTestContext ctx, TestSingleplayerContext sp, Path out) {
        this.ctx = ctx;
        this.sp = sp;
        this.out = out;
    }

    void run() throws Exception {
        Files.createDirectories(out);
        String only = System.getProperty("dc.checks", "");
        List<String> want = only.isBlank() ? List.of() : Arrays.asList(only.split(","));
        Map<String, Check> checks = new java.util.LinkedHashMap<>();
        checks.put("dreamstar", this::dreamStar);
        checks.put("pets", this::pets);
        checks.put("deck", this::deck);
        checks.put("hammock", this::hammock);
        checks.put("compressor", this::compressor);
        checks.put("sounds", this::sounds);
        checks.put("boss", this::boss);
        checks.put("structures", this::structures);
        checks.put("trench", this::trench);
        cmd("time set day");
        cmd("weather clear");
        for (var e : checks.entrySet()) {
            if (!want.isEmpty() && !want.contains(e.getKey())) continue;
            long t0 = System.currentTimeMillis();
            JsonObject r;
            try {
                cmd("gamemode creative @a");
                cmd("effect clear @a");
                cmd("clear @a");
                r = e.getValue().run();
            } catch (Throwable t) {
                PackTest.LOG.warn("[bccheck] {} crashed", e.getKey(), t);
                r = new JsonObject();
                r.addProperty("result", "ERROR " + t);
            }
            r.addProperty("seconds", (System.currentTimeMillis() - t0) / 1000.0);
            report.add(e.getKey(), r);
            PackTest.LOG.info("[bccheck] {} -> {}", e.getKey(), r);
            Files.writeString(out.resolve("bccheck_report.json"), new GsonBuilder().setPrettyPrinting().create().toJson(report), StandardCharsets.UTF_8);
        }
        PackTest.LOG.info("[bccheck] done -> {}", out.resolve("bccheck_report.json"));
    }

    @FunctionalInterface
    private interface Check {
        JsonObject run() throws Exception;
    }

    // ------------------------------------------------------------------------------------------------ deck

    private JsonObject deck() throws Exception {
        JsonObject r = new JsonObject();
        // a glass pool high in the sky of the overworld, 31 x 31, two blocks of water
        int cx = 0, cz = 400, y = 200;
        srv(s -> {
            ServerLevel l = s.overworld();
            for (int x = cx - 16; x <= cx + 16; x++)
                for (int z = cz - 16; z <= cz + 16; z++) {
                    boolean edge = Math.abs(x - cx) == 16 || Math.abs(z - cz) == 16;
                    l.setBlockAndUpdate(new BlockPos(x, y - 1, z), Blocks.GLASS.defaultBlockState());
                    for (int h = 0; h < 3; h++) {
                        l.setBlockAndUpdate(new BlockPos(x, y + h, z), edge ? Blocks.GLASS.defaultBlockState()
                                : h < 2 ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState());
                    }
                }
            return null;
        });
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld run tp @a %d.5 %d %d.5", cx, y + 6, cz - 6));
        waitDrawn(30);
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld run summon raft:expedition_raft %d.5 %d %d.5", cx, y + 2, cz));
        ctx.waitTicks(60);
        // a villager on the far corner, the player on the near corner (survival, so nothing flies)
        cmd("gamemode survival @a");
        double[] raft = srv(s -> {
            Entity e = raft(s);
            return e == null ? null : new double[]{e.getX(), e.getY(), e.getZ(), e.getYRot(), e.getBoundingBox().maxY};
        });
        if (raft == null) {
            r.addProperty("result", "FAIL no raft entity");
            return r;
        }
        double top = raft[4];
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld run tp @a %.3f %.3f %.3f 0 20", raft[0] + 1.15, top + 0.05, raft[2] + 1.15));
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld run summon minecraft:villager %.3f %.3f %.3f {NoAI:0b,Silent:1b}", raft[0] - 1.1, top + 0.05, raft[2] - 1.1));
        ctx.waitTicks(40);
        ctx.takeScreenshot("bc_deck_start");
        JsonArray samples = new JsonArray();
        boolean playerOk = true, mobOk = true;
        double speed = 0.12, turn = 2.5;   // blocks and degrees per tick: a tight circle, hard on the corners
        for (int t = 1; t <= 240; t++) {
            final int tick = t;
            srv(s -> {
                Entity e = raft(s);
                if (e == null) return null;
                float yaw = e.getYRot() + (tick > 120 ? -(float) turn : (float) turn);   // left circle, then right
                double rad = Math.toRadians(yaw);
                e.setYRot(yaw);
                e.setPos(e.getX() - Math.sin(rad) * speed, e.getY(), e.getZ() + Math.cos(rad) * speed);
                e.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
                return null;
            });
            ctx.waitTicks(1);
            if (t % 20 == 0) {
                double[] rel = srv(s -> {
                    Entity e = raft(s);
                    ServerPlayer p = s.getPlayerList().getPlayers().get(0);
                    Entity v = s.overworld().getEntitiesOfClass(net.minecraft.world.entity.npc.villager.Villager.class,
                            e.getBoundingBox().inflate(6)).stream().findFirst().orElse(null);
                    double yawRad = Math.toRadians(-e.getYRot());
                    double[] o = new double[7];
                    double dx = p.getX() - e.getX(), dz = p.getZ() - e.getZ();
                    o[0] = dx * Math.cos(yawRad) - dz * Math.sin(yawRad);
                    o[1] = dx * Math.sin(yawRad) + dz * Math.cos(yawRad);
                    o[2] = p.getY() - e.getBoundingBox().maxY;
                    if (v != null) {
                        double vx = v.getX() - e.getX(), vz = v.getZ() - e.getZ();
                        o[3] = vx * Math.cos(yawRad) - vz * Math.sin(yawRad);
                        o[4] = vx * Math.sin(yawRad) + vz * Math.cos(yawRad);
                        o[5] = v.getY() - e.getBoundingBox().maxY;
                        o[6] = 1;
                    }
                    return o;
                });
                JsonObject smp = new JsonObject();
                smp.addProperty("tick", t);
                smp.addProperty("player", String.format(Locale.ROOT, "%.2f %.2f dy %.2f", rel[0], rel[1], rel[2]));
                smp.addProperty("villager", rel[6] == 0 ? "gone" : String.format(Locale.ROOT, "%.2f %.2f dy %.2f", rel[3], rel[4], rel[5]));
                samples.add(smp);
                if (Math.abs(rel[0]) > 1.55 || Math.abs(rel[1]) > 1.55 || rel[2] < -0.35 || rel[2] > 1.0) playerOk = false;
                if (rel[6] == 0 || Math.abs(rel[3]) > 1.55 || Math.abs(rel[4]) > 1.55 || rel[5] < -0.35 || rel[5] > 1.0) mobOk = false;
                if (t == 100) ctx.takeScreenshot("bc_deck_turning");
            }
        }
        ctx.takeScreenshot("bc_deck_end");
        r.add("samples", samples);
        r.addProperty("player_stayed_on_deck", playerOk);
        r.addProperty("villager_stayed_on_deck", mobOk);
        r.addProperty("result", playerOk && mobOk ? "OK" : "FAIL");
        cmd("gamemode creative @a");
        cmd("execute in minecraft:overworld run kill @e[type=raft:expedition_raft]");
        cmd("execute in minecraft:overworld run kill @e[type=minecraft:villager,distance=..1000]");
        return r;
    }

    private static Entity raft(MinecraftServer s) {
        EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getValue(Identifier.parse("raft:expedition_raft"));
        for (Entity e : s.overworld().getAllEntities()) if (e.getType() == type) return e;
        return null;
    }

    // ------------------------------------------------------------------------------------------------ hammock

    private JsonObject hammock() throws Exception {
        JsonObject r = new JsonObject();
        r.add("overworld", hammockIn("minecraft:overworld", 60, 200, 0, true));
        r.add("nether", hammockIn("minecraft:the_nether", 60, 110, 0, false));
        boolean ok = r.getAsJsonObject("overworld").get("ok").getAsBoolean() && r.getAsJsonObject("nether").get("ok").getAsBoolean();
        r.addProperty("result", ok ? "OK" : "FAIL");
        cmd("time set day");
        return r;
    }

    private JsonObject hammockIn(String dim, int x, int y, int z, boolean expectSleep) throws Exception {
        JsonObject r = new JsonObject();
        srv(s -> {
            ServerLevel l = s.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
            for (int dx = -3; dx <= 4; dx++)
                for (int dz = -3; dz <= 3; dz++) {
                    l.setBlockAndUpdate(new BlockPos(x + dx, y - 1, z + dz), Blocks.GLASS.defaultBlockState());
                    for (int h = 0; h < 3; h++) l.setBlockAndUpdate(new BlockPos(x + dx, y + h, z + dz), Blocks.AIR.defaultBlockState());
                }
            return null;
        });
        cmd("execute in " + dim + " run setblock " + x + " " + y + " " + z + " raft:hammock[facing=east,part=foot]");
        cmd("execute in " + dim + " run setblock " + (x + 1) + " " + y + " " + z + " raft:hammock[facing=east,part=head]");
        cmd("gamemode survival @a");
        if (expectSleep) cmd("time set 13000");
        cmd(String.format(Locale.ROOT, "execute in %s as @a anchored eyes run tp @s %d.5 %d %d.5 facing %d.5 %d.3 %d.5", dim, x - 2, y, z, x, y, z));
        waitDrawn(20);
        float hp = srv(s -> s.getPlayerList().getPlayers().get(0).getHealth());
        long before = srv(s -> s.overworld().getOverworldClockTime());
        ctx.getInput().pressKey(o -> o.keyUse);
        ctx.waitTicks(30);
        boolean sleeping = srv(s -> s.getPlayerList().getPlayers().get(0).isSleeping());
        ctx.takeScreenshot("bc_hammock_" + dim.substring(dim.indexOf(':') + 1));
        r.addProperty("sleeping", sleeping);
        if (expectSleep) {
            long now = before;
            for (int i = 0; i < 30; i++) {
                ctx.waitTicks(20);
                now = srv(s -> s.overworld().getOverworldClockTime());
                if (now % 24000 < 12000 || now - before > 12000) break;
            }
            r.addProperty("day_time_before", before % 24000);
            r.addProperty("day_time_after", now % 24000);
            boolean skipped = now % 24000 < 12000;
            r.addProperty("night_skipped", skipped);
            r.addProperty("ok", sleeping && skipped);
        } else {
            boolean blockThere = srv(s -> {
                ServerLevel l = s.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
                return BuiltInRegistries.BLOCK.getKey(l.getBlockState(new BlockPos(x, y, z)).getBlock()).toString().equals("raft:hammock");
            });
            float hpAfter = srv(s -> s.getPlayerList().getPlayers().get(0).getHealth());
            r.addProperty("hammock_still_there", blockThere);
            r.addProperty("health_before", hp);
            r.addProperty("health_after", hpAfter);
            r.addProperty("ok", !sleeping && blockThere && hpAfter >= hp);
        }
        cmd("gamemode creative @a");
        cmd("execute in minecraft:overworld run tp @a 0.5 250 0.5");
        return r;
    }

    // ------------------------------------------------------------------------------------------------ compressor

    private JsonObject compressor() throws Exception {
        JsonObject r = new JsonObject();
        int x = 80, y = 200, z = 0;
        srv(s -> {
            ServerLevel l = s.overworld();
            for (int dx = -3; dx <= 3; dx++)
                for (int dz = -3; dz <= 3; dz++) l.setBlockAndUpdate(new BlockPos(x + dx, y - 1, z + dz), Blocks.GLASS.defaultBlockState());
            return null;
        });
        cmd("setblock " + x + " " + y + " " + z + " raft:air_compressor[facing=west]");
        cmd("gamemode survival @a");
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld as @a anchored eyes run tp @s %d.5 %d %d.5 facing %d.5 %d.5 %d.5", x - 2, y, z, x, y, z));
        cmd("item replace entity @a hotbar.0 with raft:oxygen_tank");
        cmd("item replace entity @a hotbar.1 with minecraft:air");
        waitDrawn(20);
        ctx.runOnClient(mc -> mc.player.getInventory().setSelectedSlot(0));
        ctx.waitTicks(5);
        ctx.getInput().pressKey(o -> o.keyUse);
        ctx.waitTicks(10);
        int[] air0 = tankAir(x, y, z);
        r.addProperty("tank_in_compressor", air0 != null);
        if (air0 == null) {
            r.addProperty("result", "FAIL the tank did not go into the compressor");
            ctx.setScreen(() -> null);
            return r;
        }
        ctx.setScreen(() -> null);
        ctx.runOnClient(mc -> mc.player.getInventory().setSelectedSlot(1));
        ctx.waitTicks(5);
        ctx.getInput().holdKey(o -> o.keyShift);
        ctx.waitTicks(5);
        ctx.getInput().pressKey(o -> o.keyUse);
        ctx.waitTicks(10);
        ctx.getInput().releaseKey(o -> o.keyShift);
        int[] air1 = tankAir(x, y, z);
        r.addProperty("air_before", air0[0]);
        r.addProperty("air_after_sneak_crank", air1[0]);
        r.addProperty("capacity", air0[1]);
        // the crank button in the GUI
        ctx.waitTicks(30);   // crank cooldown
        ctx.getInput().pressKey(o -> o.keyUse);
        ctx.waitTicks(10);
        ctx.takeScreenshot("bc_compressor_gui");
        double[] btn = ctx.computeOnClient(mc -> {
            if (mc.gui.screen() == null) return null;
            for (var w : net.fabricmc.fabric.api.client.screen.v1.Screens.getWidgets(mc.gui.screen())) {
                if (w.getClass().getSimpleName().contains("Crank")) {
                    return new double[]{w.getX() + w.getWidth() / 2.0, w.getY() + w.getHeight() / 2.0, mc.getWindow().getGuiScale()};
                }
            }
            return null;
        });
        int guiAir = -1;
        if (btn != null) {
            ctx.getInput().setCursorPos(btn[0] * btn[2], btn[1] * btn[2]);
            ctx.waitTicks(2);
            ctx.getInput().pressMouse(com.mojang.blaze3d.platform.InputConstants.MOUSE_BUTTON_LEFT);
            ctx.waitTicks(10);
            ctx.takeScreenshot("bc_compressor_crank");
            guiAir = tankAir(x, y, z)[0];
        }
        r.addProperty("crank_button_found", btn != null);
        r.addProperty("air_after_gui_crank", guiAir);
        ctx.setScreen(() -> null);
        boolean ok = air1[0] > air0[0] && guiAir > air1[0];
        r.addProperty("result", ok ? "OK" : "FAIL");
        cmd("gamemode creative @a");
        cmd("setblock " + x + " " + y + " " + z + " air");
        return r;
    }

    /** {air, capacity} of the tank in the compressor at x y z, or null without a tank. */
    private int[] tankAir(int x, int y, int z) throws Exception {
        return srv(s -> {
            BlockEntity be = s.overworld().getBlockEntity(new BlockPos(x, y, z));
            if (be == null) return null;
            ItemStack st = (ItemStack) be.getClass().getMethod("getItem", int.class).invoke(be, 0);
            if (st.isEmpty()) return null;
            Class<?> tank = Class.forName("net.kasax.raft.content.diving.item.OxygenTankItem");
            return new int[]{(Integer) tank.getMethod("getAir", ItemStack.class).invoke(null, st),
                    (Integer) tank.getMethod("capacity", ItemStack.class).invoke(null, st)};
        });
    }

    // ------------------------------------------------------------------------------------------------ boss

    private JsonObject boss() throws Exception {
        JsonObject r = new JsonObject();
        int ax = 300, ay = 150, az = 0;          // the altar, facing east; the boss rises 9 east and 4 below it
        srv(s -> {
            ServerLevel l = s.overworld();
            for (int x = ax - 4; x <= ax + 30; x++)
                for (int z = az - 16; z <= az + 16; z++)
                    for (int y = ay - 12; y <= ay + 6; y++) {
                        boolean inPool = x > ax + 1 && x < ax + 30 && Math.abs(z - az) < 16 && y > ay - 12 && y < ay;
                        boolean floor = y == ay - 12 || (x <= ax + 1 && y == ay - 1) || x == ax + 30 || Math.abs(z - az) == 16
                                || (x == ax + 1 && y < ay);
                        BlockState st = inPool ? Blocks.WATER.defaultBlockState() : floor && y <= ay - 1 ? Blocks.GLASS.defaultBlockState()
                                : Blocks.AIR.defaultBlockState();
                        l.setBlockAndUpdate(new BlockPos(x, y, z), st);
                    }
            return null;
        });
        cmd("setblock " + ax + " " + ay + " " + az + " raft:leviathan_altar[facing=east]");
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld as @a anchored eyes run tp @s %d.5 %d %d.5 facing %d.5 %d.4 %d.5", ax - 2, ay, az, ax, ay, az));
        waitDrawn(30);
        cmd("gamemode survival @a");
        cmd("effect give @a minecraft:resistance infinite 4 true");
        cmd("effect give @a minecraft:regeneration infinite 2 true");
        cmd("effect give @a minecraft:water_breathing infinite 0 true");
        cmd("effect give @a minecraft:saturation infinite 0 true");
        cmd("item replace entity @a hotbar.0 with raft:tidewarden_key");
        ctx.runOnClient(mc -> mc.player.getInventory().setSelectedSlot(0));
        ctx.waitTicks(10);
        ctx.getInput().pressKey(o -> o.keyUse);
        ctx.waitTicks(40);
        Float hp0 = bossHealth();
        r.addProperty("first_summon", hp0 != null);
        if (hp0 == null) {
            r.addProperty("result", "FAIL the key did not summon the Leviathan");
            return r;
        }
        ctx.takeScreenshot("bc_boss_summoned");
        // fight: hits from the player, a few ticks apart (hurt time)
        JsonArray fight = new JsonArray();
        int maxTidelings = 0;
        for (int hit = 0; hit < 40; hit++) {
            Float hp = bossHealth();
            if (hp == null || hp <= 0) break;
            srv(s -> {
                ServerPlayer p = s.getPlayerList().getPlayers().get(0);
                LivingEntity b = boss(s);
                if (b != null) b.hurtServer(s.overworld(), p.damageSources().playerAttack(p), 45.0f);
                return null;
            });
            ctx.waitTicks(14);
            int tid = srv(s -> count(s.overworld(), "raft:tideling", new AABB(ax - 40, ay - 40, az - 40, ax + 60, ay + 40, az + 40)));
            maxTidelings = Math.max(maxTidelings, tid);
            Float after = bossHealth();
            fight.add(String.format(Locale.ROOT, "hit %d: %.0f -> %s, tidelings %d", hit + 1, hp, after == null ? "dead" : String.format(Locale.ROOT, "%.0f", after), tid));
            if (hit == 6) ctx.takeScreenshot("bc_boss_fight");
        }
        for (int i = 0; i < 20 && bossHealth() != null; i++) ctx.waitTicks(10);
        ctx.waitTicks(60);
        boolean dead = bossHealth() == null;
        List<String> drops = srv(s -> {
            List<String> d = new ArrayList<>();
            for (ItemEntity it : s.overworld().getEntitiesOfClass(ItemEntity.class, new AABB(ax - 40, ay - 40, az - 40, ax + 60, ay + 40, az + 40))) {
                d.add(BuiltInRegistries.ITEM.getKey(it.getItem().getItem()) + " x" + it.getItem().getCount());
            }
            return d;
        });
        boolean adv = advancementDone("raft:story/leviathan");
        r.add("fight", fight);
        r.addProperty("max_tidelings", maxTidelings);
        r.addProperty("dead", dead);
        r.addProperty("drops", String.join(", ", drops));
        r.addProperty("advancement_leviathan", adv);
        ctx.takeScreenshot("bc_boss_dead");
        cmd("execute in minecraft:overworld run kill @e[type=raft:tideling]");
        cmd("execute in minecraft:overworld run kill @e[type=item,x=" + ax + ",y=" + ay + ",z=" + az + ",distance=..80]");
        // second summon: without a crystal nothing happens, with one it works and the crystal is used up
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld as @a anchored eyes run tp @s %d.5 %d %d.5 facing %d.5 %d.4 %d.5", ax - 2, ay, az, ax, ay, az));
        ctx.waitTicks(20);
        ctx.getInput().pressKey(o -> o.keyUse);
        ctx.waitTicks(40);
        boolean summonedWithoutCrystal = bossHealth() != null;
        cmd("give @a raft:ancient_crystal 1");
        ctx.waitTicks(10);
        ctx.getInput().pressKey(o -> o.keyUse);
        ctx.waitTicks(40);
        boolean secondSummon = bossHealth() != null;
        int crystalsLeft = srv(s -> {
            ServerPlayer p = s.getPlayerList().getPlayers().get(0);
            int n = 0;
            for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
                ItemStack st = p.getInventory().getItem(i);
                if (BuiltInRegistries.ITEM.getKey(st.getItem()).toString().equals("raft:ancient_crystal")) n += st.getCount();
            }
            return n;
        });
        r.addProperty("second_summon_without_crystal", summonedWithoutCrystal);
        r.addProperty("second_summon_with_crystal", secondSummon);
        r.addProperty("crystals_left", crystalsLeft);
        // healing: hurt it, walk away (out of its arena, chunks still loaded), wait 35 s
        boolean healed = false;
        if (secondSummon) {
            for (int hit = 0; hit < 6; hit++) {
                srv(s -> {
                    ServerPlayer p = s.getPlayerList().getPlayers().get(0);
                    LivingEntity b = boss(s);
                    if (b != null) b.hurtServer(s.overworld(), p.damageSources().playerAttack(p), 45.0f);
                    return null;
                });
                ctx.waitTicks(14);
            }
            Float hurt = bossHealth();
            cmd(String.format(Locale.ROOT, "execute in minecraft:overworld run tp @a %d.5 %d %d.5", ax - 60, ay + 20, az));
            for (int i = 0; i < 40; i++) ctx.waitTicks(20);
            Float later = bossHealth();
            healed = hurt != null && later != null && later > hurt && later >= 599;
            r.addProperty("health_hurt", hurt);
            r.addProperty("health_after_35s_alone", later);
        }
        r.addProperty("healed_without_players", healed);
        boolean ok = dead && adv && maxTidelings <= 5 && !summonedWithoutCrystal && secondSummon && crystalsLeft == 0 && healed;
        r.addProperty("result", ok ? "OK" : "FAIL");
        cmd("execute in minecraft:overworld run kill @e[type=raft:leviathan]");
        cmd("execute in minecraft:overworld run kill @e[type=raft:tideling]");
        cmd("effect clear @a");
        cmd("gamemode creative @a");
        return r;
    }

    private static LivingEntity boss(MinecraftServer s) {
        EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getValue(Identifier.parse("raft:leviathan"));
        for (Entity e : s.overworld().getAllEntities()) if (e.getType() == type && e instanceof LivingEntity l && l.isAlive()) return l;
        return null;
    }

    private Float bossHealth() throws Exception {
        return srv(s -> {
            LivingEntity b = boss(s);
            return b == null ? null : b.getHealth();
        });
    }

    // ------------------------------------------------------------------------------------------------ trench

    private JsonObject trench() throws Exception {
        JsonObject r = new JsonObject();
        JsonArray spots = new JsonArray();
        int[][] origins = {{0, 0}, {3000, -2000}};
        for (int[] o : origins) {
            String where = srv(s -> {
                ServerLevel l = level(s, "raft:raftdim");
                ResourceKey<Biome> key = ResourceKey.create(Registries.BIOME, Identifier.parse("raft:abyssal_trench"));
                Pair<BlockPos, Holder<Biome>> p = l.findClosestBiome3d(h -> h.is(key), new BlockPos(o[0], 40, o[1]), 6400, 32, 64);
                return p == null ? null : p.getFirst().getX() + " " + p.getFirst().getY() + " " + p.getFirst().getZ();
            });
            JsonObject spot = new JsonObject();
            if (where == null) {
                spot.addProperty("result", "no abyssal trench found");
                spots.add(spot);
                continue;
            }
            String[] w = where.split(" ");
            cmd("execute in raft:raftdim run tp @a " + w[0] + " " + w[1] + " " + w[2]);
            waitDrawn(240);
            for (int i = 0; i < 90; i++) ctx.waitTicks(20);    // 90 s for natural spawning
            ctx.takeScreenshot("bc_trench_" + w[0] + "_" + w[2]);
            Map<String, Integer> counts = srv(s -> {
                ServerPlayer p = s.getPlayerList().getPlayers().get(0);
                Map<String, Integer> c = new TreeMap<>();
                for (Entity e : p.level().getEntities((Entity) null, p.getBoundingBox().inflate(128, 128, 128), e -> e instanceof Mob)) {
                    c.merge(BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).toString(), 1, Integer::sum);
                }
                return c;
            });
            spot.addProperty("at", where);
            JsonObject cj = new JsonObject();
            counts.forEach(cj::addProperty);
            spot.add("mobs_within_128", cj);
            spots.add(spot);
        }
        r.add("spots", spots);
        r.addProperty("result", "INFO");
        cmd("execute in minecraft:overworld run tp @a 0.5 250 0.5");
        return r;
    }

    // ------------------------------------------------------------------------------------------------ structures

    private JsonObject structures() throws Exception {
        JsonObject r = new JsonObject();
        String[] ids = {"raft:pirate_cove", "raft:old_lighthouse", "raft:castaway_camp", "raft:sunken_plane", "raft:wreck_fishing_boat",
                "raft:port_solace"};
        cmd("gamemode spectator @a");
        for (String id : ids) {
            JsonObject one = new JsonObject();
            String found = srv(s -> {
                ServerLevel l = level(s, "raft:raftdim");
                Registry<Structure> reg = s.registryAccess().lookupOrThrow(Registries.STRUCTURE);
                var h = reg.get(ResourceKey.create(Registries.STRUCTURE, Identifier.parse(id)));
                if (h.isEmpty()) return "!unknown";
                Pair<BlockPos, Holder<Structure>> p = l.getChunkSource().getGenerator().findNearestMapStructure(l, HolderSet.direct(h.get()),
                        BlockPos.ZERO, 100, false);
                if (p == null) return "!not found within 100 chunks";
                ChunkAccess ch = l.getChunk(p.getFirst().getX() >> 4, p.getFirst().getZ() >> 4, ChunkStatus.STRUCTURE_STARTS);
                StructureStart st = ch.getStartForStructure(h.get().value());
                if (st == null || !st.isValid()) return "!no start at " + p.getFirst();
                BoundingBox bb = st.getBoundingBox();
                StringBuilder sb = new StringBuilder();
                sb.append(bb.minX()).append(' ').append(bb.minY()).append(' ').append(bb.minZ()).append(' ')
                        .append(bb.maxX()).append(' ').append(bb.maxY()).append(' ').append(bb.maxZ());
                // pieces worth a look inside (Port Solace: offices and the city hall)
                for (StructurePiece piece : st.getPieces()) {
                    String name = piece.toString();
                    if (name.contains("city_hall") || name.contains("glass_tower") || name.contains("deco_tower") || name.contains("lighthouse")) {
                        BlockPos c = piece.getBoundingBox().getCenter();
                        sb.append(" | ").append(name.replaceAll(".*raft:", "").replaceAll("[\\]\\s].*", "")).append('@')
                                .append(c.getX()).append(',').append(c.getY()).append(',').append(c.getZ());
                    }
                }
                return sb.toString();
            });
            one.addProperty("found", found);
            if (!found.startsWith("!")) {
                String[] b = found.split(" \\| ")[0].split(" ");
                int x0 = Integer.parseInt(b[0]), y0 = Integer.parseInt(b[1]), z0 = Integer.parseInt(b[2]);
                int x1 = Integer.parseInt(b[3]), y1 = Integer.parseInt(b[4]), z1 = Integer.parseInt(b[5]);
                int mx = (x0 + x1) / 2, mz = (z0 + z1) / 2;
                int span = Math.max(x1 - x0, z1 - z0);
                String name = id.substring(5);
                cmd(String.format(Locale.ROOT, "execute in raft:raftdim run tp @a %d %d %d facing %d %d %d", mx - span, y1 + span / 2 + 8, mz - span, mx, (y0 + y1) / 2, mz));
                waitDrawn(240);
                ctx.takeScreenshot("bc_struct_" + name + "_overview");
                cmd(String.format(Locale.ROOT, "execute in raft:raftdim run tp @a %d %d %d facing %d %d %d", mx, y1 + 30, mz + 1, mx, y0, mz));
                waitDrawn(120);
                ctx.takeScreenshot("bc_struct_" + name + "_top");
                // inside the interesting pieces (no night vision: as dark as a player sees it)
                String[] parts = found.split(" \\| ");
                for (int i = 1; i < parts.length && i <= 4; i++) {
                    String[] pc = parts[i].substring(parts[i].indexOf('@') + 1).split(",");
                    cmd("execute in raft:raftdim run tp @a " + pc[0] + " " + pc[1] + " " + pc[2] + " 45 10");
                    waitDrawn(60);
                    ctx.takeScreenshot("bc_struct_" + name + "_inside_" + i);
                }
            }
            r.add(id, one);
        }
        cmd("gamemode creative @a");
        cmd("execute in minecraft:overworld run tp @a 0.5 250 0.5");
        r.addProperty("result", "SCREENSHOTS");
        return r;
    }

    // ------------------------------------------------------------------------------------------------ pets

    private JsonObject pets() throws Exception {
        JsonObject r = new JsonObject();
        JsonObject homes = srv(s -> {
            JsonObject h = new JsonObject();
            Registry<Structure> reg = s.registryAccess().lookupOrThrow(Registries.STRUCTURE);
            reg.getTags().forEach(named -> {
                String tag = named.key().location().toString();
                if (!tag.startsWith("tamacraft:pet_home/")) return;
                JsonArray a = new JsonArray();
                named.stream().forEach(holder -> a.add(holder.getRegisteredName()));
                h.add(tag, a);
            });
            return h;
        });
        r.add("pet_home_tags", homes);
        // a look-alike home of another mod in the real world
        JsonArray tries = new JsonArray();
        String[] lookAlikes = {"repurposed_structures:pyramid_badlands", "repurposed_structures:witch_hut_oak", "repurposed_structures:igloo_grassy"};
        cmd("gamemode spectator @a");
        for (String id : lookAlikes) {
            String where = srv(s -> {
                Registry<Structure> reg = s.registryAccess().lookupOrThrow(Registries.STRUCTURE);
                var h = reg.get(ResourceKey.create(Registries.STRUCTURE, Identifier.parse(id)));
                if (h.isEmpty()) return "!" + id + " not in this pack";
                ServerLevel l = s.overworld();
                Pair<BlockPos, Holder<Structure>> p = l.getChunkSource().getGenerator().findNearestMapStructure(l, HolderSet.direct(h.get()),
                        BlockPos.ZERO, 100, false);
                if (p == null) return "!" + id + " not found within 100 chunks";
                ChunkAccess ch = l.getChunk(p.getFirst().getX() >> 4, p.getFirst().getZ() >> 4, ChunkStatus.STRUCTURE_STARTS);
                StructureStart st = ch.getStartForStructure(h.get().value());
                BlockPos c = st != null && st.isValid() && !st.getPieces().isEmpty() ? st.getPieces().get(0).getBoundingBox().getCenter() : p.getFirst();
                return c.getX() + " " + c.getY() + " " + c.getZ();
            });
            JsonObject t = new JsonObject();
            t.addProperty("structure", id);
            t.addProperty("at", where);
            if (!where.startsWith("!")) {
                cmd("execute in minecraft:overworld run tp @a " + where);
                waitDrawn(120);
                ctx.waitTicks(100);
                String[] w = where.split(" ");
                int px = Integer.parseInt(w[0]), py = Integer.parseInt(w[1]), pz = Integer.parseInt(w[2]);
                String pets = srv(s -> {
                    StringBuilder sb = new StringBuilder();
                    for (Entity e : s.overworld().getEntities((Entity) null, new AABB(px - 48, py - 48, pz - 48, px + 48, py + 48, pz + 48),
                            e -> BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getNamespace().equals("tamacraft"))) {
                        sb.append(BuiltInRegistries.ENTITY_TYPE.getKey(e.getType())).append(' ');
                    }
                    return sb.toString().trim();
                });
                t.addProperty("pets_nearby", pets.isEmpty() ? "none (each home only has a chance)" : pets);
                ctx.takeScreenshot("dc_pet_home_" + id.substring(id.indexOf(':') + 1));
            }
            tries.add(t);
        }
        cmd("gamemode creative @a");
        cmd("execute in minecraft:overworld run tp @a 0.5 250 0.5");
        r.add("look_alike_homes", tries);
        boolean rs = homes.has("tamacraft:pet_home/desert_dragon") && homes.getAsJsonArray("tamacraft:pet_home/desert_dragon").toString().contains("repurposed_structures");
        r.addProperty("result", rs ? "OK" : "FAIL pet homes miss the Repurposed Structures look-alikes");
        return r;
    }

    // ------------------------------------------------------------------------------------------------ dream star

    private JsonObject dreamStar() throws Exception {
        JsonObject r = new JsonObject();
        String recipe = srv(s -> {
            var key = ResourceKey.create(Registries.RECIPE, Identifier.parse("questsicons:dream_star"));
            var holder = s.getRecipeManager().byKey(key);
            if (holder.isEmpty()) return "!not loaded";
            var ops = s.registryAccess().createSerializationContext(JsonOps.INSTANCE);
            return net.minecraft.world.item.crafting.Recipe.DIRECT_CODEC.encodeStart(ops, holder.get().value()).result().map(Object::toString).orElse("?");
        });
        r.addProperty("recipe", recipe);
        boolean vanilla = srv(s -> s.getRecipeManager().byKey(ResourceKey.create(Registries.RECIPE, Identifier.parse("questsicons:dream_star_vanilla"))).isPresent());
        r.addProperty("fallback_recipe_loaded", vanilla);
        cmd("gamemode survival @a");
        cmd("give @a questsicons:dream_star");
        ctx.waitTicks(40);
        boolean adv = advancementDone("questsicons:dream_star");
        r.addProperty("advancement_living_the_dream", adv);
        r.addProperty("result", !recipe.startsWith("!") && !vanilla && adv ? "OK" : "FAIL");
        cmd("clear @a");
        cmd("gamemode creative @a");
        return r;
    }

    // ------------------------------------------------------------------------------------------------ sounds

    private JsonObject sounds() throws Exception {
        JsonObject r = new JsonObject();
        int cx = 0, cz = -400, y = 150;
        srv(s -> {
            ServerLevel l = s.overworld();
            for (int x = cx - 12; x <= cx + 12; x++)
                for (int z = cz - 12; z <= cz + 12; z++)
                    for (int h = -1; h <= 8; h++) {
                        boolean edge = Math.abs(x - cx) == 12 || Math.abs(z - cz) == 12 || h == -1;
                        l.setBlockAndUpdate(new BlockPos(x, y + h, z), edge ? Blocks.GLASS.defaultBlockState()
                                : h < 8 ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState());
                    }
            return null;
        });
        cmd("setblock " + (cx + 2) + " " + y + " " + cz + " raft:bubble_vent");
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld run tp @a %d.5 %d %d.5", cx, y + 3, cz - 2));
        cmd(String.format(Locale.ROOT, "summon raft:whale %d.5 %d %d.5", cx - 4, y + 3, cz + 4));
        waitDrawn(30);
        Path dir = out.resolve("bc_sounds");
        long gt = ctx.computeOnClient(mc -> mc.level.getGameTime());
        FilmSound.start(dir, 20, gt);
        boolean whale = false, bubbles = false;
        for (int i = 0; i < 160 && !(whale && bubbles); i++) {
            ctx.waitTicks(20);
            if (i % 5 == 4) {
                String log = Files.exists(dir.resolve("sounds.jsonl")) ? Files.readString(dir.resolve("sounds.jsonl")) : "";
                whale = log.contains("raft:entity.whale.song");
                bubbles = log.contains("bubble_column.upwards_ambient");
            }
        }
        FilmSound.stop();
        r.addProperty("whale_song_played", whale);
        r.addProperty("bubble_vent_sound_played", bubbles);
        r.addProperty("result", whale && bubbles ? "OK" : "FAIL");
        cmd("execute in minecraft:overworld run kill @e[type=raft:whale]");
        cmd("execute in minecraft:overworld run tp @a 0.5 250 0.5");
        return r;
    }

    // ------------------------------------------------------------------------------------------------ helpers

    private boolean advancementDone(String id) throws Exception {
        return srv(s -> {
            AdvancementHolder h = s.getAdvancements().get(Identifier.parse(id));
            return h != null && s.getPlayerList().getPlayers().get(0).getAdvancements().getOrStartProgress(h).isDone();
        });
    }

    private static int count(ServerLevel l, String id, AABB box) {
        EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getValue(Identifier.parse(id));
        return l.getEntities((Entity) null, box, e -> e.getType() == type && e.isAlive()).size();
    }

    private static ServerLevel level(MinecraftServer s, String dim) {
        return s.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
    }

    /** Waits until the client has drawn the chunks around the player (at most maxSeconds). */
    private void waitDrawn(int maxSeconds) {
        for (int i = 0; i < maxSeconds; i++) {
            ctx.waitTicks(20);
            if (i > 2 && ctx.computeOnClient(mc -> mc.levelRenderer.hasRenderedAllSections())) return;
        }
    }

    private void cmd(String c) {
        sp.getServer().runCommand(c);
    }

    private <T> T srv(ServerCall<T> f) throws Exception {
        return sp.getServer().computeOnServer(s -> f.call(s));
    }

    @FunctionalInterface
    private interface ServerCall<T> {
        T call(MinecraftServer s) throws Exception;
    }

    @SuppressWarnings("unused")
    private static Predicate<Holder<Biome>> biome(String id) {
        TagKey<Biome> t = id.startsWith("#") ? TagKey.create(Registries.BIOME, Identifier.parse(id.substring(1))) : null;
        ResourceKey<Biome> k = t == null ? ResourceKey.create(Registries.BIOME, Identifier.parse(id)) : null;
        return h -> t != null ? h.is(t) : h.is(k);
    }

    @SuppressWarnings("unused")
    private static Block block(String id) {
        return BuiltInRegistries.BLOCK.getValue(Identifier.parse(id));
    }
}
