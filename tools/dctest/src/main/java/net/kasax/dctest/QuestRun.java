package net.kasax.dctest;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.datafixers.util.Pair;
import it.unimi.dsi.fastutil.longs.Long2LongMap;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;
import java.util.function.Predicate;

/**
 * The in-game quest check (-Pscene=qrun -Pplan=FILE): works through every quest of the book in dependency order and
 * fulfils each task the way a player does - items in the inventory, the mob killed by the player, the real structure,
 * biome or dimension visited (located like /locate, then teleported into the structure's first piece), the creature
 * or block looked at for the observation time, the checkbox ticked / items handed in through the quest book's own
 * network action. Then it waits until Quest Icons completes the quest and claims the rewards like the book's buttons.
 * A quest that does not complete is reported with the progress of each task and then force-completed, so that the
 * quests after it can still be checked. Report: OUT/qrun_report.json and "[qrun]" lines in the log.
 * -Pqonly=chapter,chapter:key limits the run (all other quests are force-completed to satisfy dependencies).
 */
final class QuestRun {
    private static final String[] DIMS = {"minecraft:overworld", "minecraft:the_nether", "minecraft:the_end", "raft:raftdim"};
    private static final int SUBMIT = 0, CLAIM = 1, CLAIM_ALL = 2;
    private static final double HX = 0.5, HY = 250, HZ = 0.5;   // the test platform in the overworld

    private final ClientGameTestContext ctx;
    private final TestSingleplayerContext sp;
    private final Path out;
    private final JsonArray report = new JsonArray();
    private int ok, failed, forced;

    QuestRun(ClientGameTestContext ctx, TestSingleplayerContext sp, Path out) {
        this.ctx = ctx;
        this.sp = sp;
        this.out = out;
    }

    void run(Path planFile) throws Exception {
        JsonArray quests = JsonParser.parseString(Files.readString(planFile)).getAsJsonObject().getAsJsonArray("quests");
        String only = System.getProperty("dc.qonly", "");
        List<String> filter = only.isBlank() ? List.of() : Arrays.asList(only.split(","));
        cmd("gamemode creative @a");
        cmd("time set day");
        cmd("weather clear");
        srv(s -> {
            ServerLevel ow = s.overworld();
            for (int x = -6; x <= 6; x++)
                for (int z = -6; z <= 6; z++)
                    ow.setBlockAndUpdate(new BlockPos(x, (int) HY - 1, z), Blocks.GLASS.defaultBlockState());
            return null;
        });
        home();
        ctx.waitTicks(100);
        long t0 = System.currentTimeMillis();
        for (JsonElement el : quests) {
            JsonObject q = el.getAsJsonObject();
            String key = q.get("key").getAsString();
            String chapter = key.substring(0, key.indexOf(':'));
            if (!filter.isEmpty() && !filter.contains(key) && !filter.contains(chapter)) {
                cmd("quests complete " + q.get("id").getAsString() + " @a");
                continue;
            }
            try {
                runQuest(q);
            } catch (Exception e) {
                PackTest.LOG.warn("[qrun] ERROR {}", key, e);
                JsonObject rec = new JsonObject();
                rec.addProperty("key", key);
                rec.addProperty("result", "ERROR " + e);
                report.add(rec);
                failed++;
                cmd("quests complete " + q.get("id").getAsString() + " @a");
                home();
            }
        }
        action(CLAIM_ALL, 0, 0);
        ctx.waitTicks(40);
        cmd("clear @a");
        home();
        ctx.waitTicks(40);
        ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_J);
        ctx.waitTicks(40);
        ctx.takeScreenshot("qrun_book_end");
        ctx.setScreen(() -> null);
        JsonObject root = new JsonObject();
        root.addProperty("ok", ok);
        root.addProperty("failed", failed);
        root.addProperty("forced_dependencies", forced);
        root.addProperty("minutes", (System.currentTimeMillis() - t0) / 60000.0);
        root.add("quests", report);
        Files.createDirectories(out);
        Files.writeString(out.resolve("qrun_report.json"), new GsonBuilder().setPrettyPrinting().create().toJson(root), StandardCharsets.UTF_8);
        PackTest.LOG.info("[qrun] done: {} ok, {} failed, {} min -> {}", ok, failed, root.get("minutes").getAsDouble(), out.resolve("qrun_report.json"));
    }

    // ------------------------------------------------------------------------------------------------ one quest

    private void runQuest(JsonObject q) throws Exception {
        String key = q.get("key").getAsString();
        long qid = hex(q.get("id").getAsString());
        long start = System.currentTimeMillis();
        JsonObject rec = new JsonObject();
        rec.addProperty("key", key);
        rec.addProperty("title", q.get("title").getAsString());
        JsonArray notes = new JsonArray();
        if (isCompleted(qid)) {     // a taskless quest, or one that finished on its own with an earlier quest's items
            rec.addProperty("result", "already complete");
            report.add(rec);
            ok++;
            return;
        }
        if (!canStart(qid)) {
            notes.add("could not start (dependencies) - forcing its dependencies");
            for (JsonElement d : q.getAsJsonArray("deps")) cmd("quests complete " + d.getAsString() + " @a");
            forced++;
            ctx.waitTicks(5);
        }
        cmd("clear @a");
        cmd("execute at @a run kill @e[type=item,distance=..40]");
        cmd("execute at @a run kill @e[type=experience_orb,distance=..40]");
        List<JsonObject> tasks = new ArrayList<>();
        for (JsonElement e : q.getAsJsonArray("tasks")) tasks.add(e.getAsJsonObject());
        // tasks that need no travel first, then looking at things on the platform, then the trips
        tasks.sort((a, b) -> Integer.compare(rank(a), rank(b)));
        for (JsonObject t : tasks) {
            String note = doTask(t);
            if (note != null) notes.add(t.get("type").getAsString() + ": " + note);
        }
        boolean done = false;
        for (int i = 0; i < 40 && !done; i++) {     // up to 20 s: advancement tasks look every 40 ticks
            ctx.waitTicks(10);
            done = isCompleted(qid);
        }
        if (!done) {
            JsonArray left = new JsonArray();
            for (JsonObject t : tasks) {
                long have = progress(hex(t.get("id").getAsString()));
                long need = maxProgress(t);
                if (have < need) left.add(t.get("type").getAsString() + " " + target(t) + " " + have + "/" + need);
            }
            rec.add("incomplete", left);
            rec.addProperty("result", "FAIL");
            failed++;
            cmd("quests complete " + q.get("id").getAsString() + " @a");
            PackTest.LOG.warn("[qrun] FAIL {} {}", key, left);
        } else {
            rec.addProperty("result", "OK");
            ok++;
        }
        // rewards: what auto-claim did not take, claim like the book's buttons (a choice reward takes its first item)
        ctx.waitTicks(5);
        for (JsonElement e : q.getAsJsonArray("rewards")) {
            JsonObject r = e.getAsJsonObject();
            long rid = hex(r.get("id").getAsString());
            if (!isClaimed(rid)) action(CLAIM, rid, r.get("type").getAsString().equals("choice") ? 0 : -1);
        }
        ctx.waitTicks(10);
        JsonArray unclaimed = new JsonArray();
        for (JsonElement e : q.getAsJsonArray("rewards")) {
            JsonObject r = e.getAsJsonObject();
            if (!isClaimed(hex(r.get("id").getAsString()))) unclaimed.add(r.get("type").getAsString() + " " + r.get("id").getAsString());
        }
        if (done && !unclaimed.isEmpty()) {
            rec.add("unclaimed", unclaimed);
            rec.addProperty("result", "REWARD");
            PackTest.LOG.warn("[qrun] REWARD {} not claimed: {}", key, unclaimed);
        }
        if (!notes.isEmpty()) rec.add("notes", notes);
        rec.addProperty("seconds", (System.currentTimeMillis() - start) / 1000.0);
        report.add(rec);
        PackTest.LOG.info("[qrun] {} {} {}", rec.get("result").getAsString(), key, notes.isEmpty() ? "" : notes);
        home();
    }

    private static int rank(JsonObject t) {
        return switch (t.get("type").getAsString()) {
            case "observation" -> 1;
            case "dimension", "biome", "structure" -> 2;
            default -> 0;
        };
    }

    private static long maxProgress(JsonObject t) {
        return switch (t.get("type").getAsString()) {
            case "item" -> t.has("count") ? t.get("count").getAsLong() : 1;
            case "kill", "xp", "stat" -> t.has("value") ? t.get("value").getAsLong() : 1;
            case "observation" -> t.has("timer") ? t.get("timer").getAsLong() : 20;
            default -> 1;
        };
    }

    private static String target(JsonObject t) {
        for (String k : new String[]{"item", "entity", "advancement", "dimension", "biome", "structure", "observe", "stat"}) {
            if (t.has(k) && t.get(k).isJsonPrimitive() && !(k.equals("entity") && t.get(k).getAsJsonPrimitive().isBoolean())) {
                return t.get(k).getAsString();
            }
        }
        return t.has("item") ? t.get("item").toString() : "";
    }

    // ------------------------------------------------------------------------------------------------ tasks

    /** Fulfils one task. Returns a note for the report (what was used, or what went wrong) or null. */
    private String doTask(JsonObject t) throws Exception {
        String type = t.get("type").getAsString();
        long tid = hex(t.get("id").getAsString());
        long need = maxProgress(t);
        switch (type) {
            case "item" -> {
                String spec = t.get("item").isJsonPrimitive() ? t.get("item").getAsString() : t.getAsJsonObject("item").get("id").getAsString();
                String used = srv(s -> {
                    Item item = resolveItem(spec);
                    if (item == null) return null;
                    ServerPlayer p = player(s);
                    long left = need;
                    int max = new ItemStack(item).getMaxStackSize();
                    while (left > 0) {
                        int n = (int) Math.min(left, max);
                        p.getInventory().add(new ItemStack(item, n));
                        left -= n;
                    }
                    return BuiltInRegistries.ITEM.getKey(item).toString();
                });
                if (used == null) return "no item for " + spec;
                if (t.has("consume_items") && t.get("consume_items").getAsBoolean()) {
                    ctx.waitTicks(5);
                    action(SUBMIT, tid, 0);
                }
                return spec.startsWith("#") ? spec + " -> " + used : null;
            }
            case "checkmark" -> {
                action(SUBMIT, tid, 0);
                return null;
            }
            case "kill" -> {
                String spec = t.get("entity").getAsString();
                return srv(s -> killAsPlayer(s, spec, need));
            }
            case "advancement" -> {
                String crit = t.has("criterion") ? " " + t.get("criterion").getAsString() : "";
                cmd("advancement grant @a only " + t.get("advancement").getAsString() + crit);
                return null;
            }
            case "xp" -> {
                boolean points = t.has("points") && t.get("points").getAsBoolean();
                cmd("xp add @a " + need + (points ? " points" : " levels"));
                return null;
            }
            case "stat" -> {
                String stat = t.get("stat").getAsString();
                srv(s -> {
                    player(s).awardStat(Identifier.parse(stat), (int) need);
                    return null;
                });
                return null;
            }
            case "observation" -> {
                return observe(t, tid, need);
            }
            case "dimension" -> {
                String dim = t.get("dimension").getAsString();
                cmd("execute in " + dim + " run tp @a 0.5 200 0.5");
                return waitTask(tid, need, 400) ? null : "not detected in " + dim;
            }
            case "biome" -> {
                String biome = t.get("biome").getAsString();
                String where = srv(s -> locateBiome(s, biome));
                if (where.startsWith("!")) return where.substring(1);
                String[] w = where.split(" ");
                cmd("execute in " + w[0] + " run tp @a " + w[1] + " " + w[2] + " " + w[3]);
                return waitTask(tid, need, 600) ? "found at " + where : "not detected at " + where;
            }
            case "structure" -> {
                String structure = t.get("structure").getAsString();
                String where = srv(s -> locateStructure(s, structure));
                if (where.startsWith("!")) return where.substring(1);
                String[] w = where.split(" ");
                cmd("execute in " + w[0] + " run tp @a " + w[1] + " " + w[2] + " " + w[3]);
                return waitTask(tid, need, 800) ? "found " + where : "not detected at " + where;
            }
            default -> {
                return "task type not handled by the harness: " + type;
            }
        }
    }

    private String observe(JsonObject t, long tid, long need) throws Exception {
        String what = t.get("observe").getAsString();
        boolean entity = t.has("entity") && t.get("entity").getAsBoolean();
        String made = srv(s -> {
            ServerPlayer p = player(s);
            ServerLevel level = p.level();
            BlockPos at = BlockPos.containing(p.getX() + 3, p.getY(), p.getZ());
            if (entity) {
                EntityType<?> type = resolveEntity(what);
                if (type == null) return "!unknown entity " + what;
                Entity e = type.create(level, EntitySpawnReason.COMMAND);
                if (e == null) return "!cannot create " + what;
                e.setPos(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
                if (e instanceof Mob m) m.setNoAi(true);
                e.setNoGravity(true);
                level.addFreshEntity(e);
                return "e";
            }
            Block b = BuiltInRegistries.BLOCK.getValue(Identifier.parse(what));
            if (b == Blocks.AIR) return "!unknown block " + what;
            level.setBlockAndUpdate(at, b.defaultBlockState());
            return "b";
        });
        if (made.startsWith("!")) return made.substring(1);
        ctx.waitTicks(5);
        if (made.equals("e")) cmd("execute as @a at @s run tp @s ~ ~ ~ facing entity @e[type=" + what + ",limit=1,sort=nearest] eyes");
        else cmd("execute as @a at @s run tp @s ~ ~ ~ facing ~3 ~0.5 ~");
        boolean seen = waitTask(tid, need, (int) need + 200);
        if (made.equals("e")) cmd("execute at @a run kill @e[type=" + what + ",distance=..10]");
        else cmd("execute at @a run setblock ~3 ~ ~ air");
        return seen ? null : "looked at " + what + " but the task did not count it";
    }

    private static String killAsPlayer(MinecraftServer s, String spec, long count) {
        EntityType<?> type = resolveEntity(spec);
        if (type == null) return "unknown entity " + spec;
        ServerPlayer p = player(s);
        ServerLevel level = p.level();
        String how = null;
        for (int i = 0; i < count; i++) {
            Entity e = type.create(level, EntitySpawnReason.COMMAND);
            if (!(e instanceof LivingEntity le)) return "cannot create a living " + spec;
            e.setPos(p.getX() + 4, p.getY(), p.getZ());
            level.addFreshEntity(e);
            DamageSource src = p.damageSources().playerAttack(p);
            le.hurtServer(level, src, 1.0e6f);
            if (le.isAlive()) le.hurtServer(level, src, 1.0e6f);
            if (le.isAlive()) {
                le.die(src);         // invulnerable phases of bosses: the death still counts for the player
                le.discard();
                how = "needed die()";
            }
        }
        String used = BuiltInRegistries.ENTITY_TYPE.getKey(type).toString();
        return spec.startsWith("#") ? spec + " -> " + used + (how == null ? "" : ", " + how) : how;
    }

    /** "dim x y z" of the closest biome of a dimension that has it, or "!reason". */
    private static String locateBiome(MinecraftServer s, String spec) {
        Predicate<Holder<Biome>> test;
        if (spec.startsWith("#")) {
            TagKey<Biome> key = TagKey.create(Registries.BIOME, Identifier.parse(spec.substring(1)));
            test = h -> h.is(key);
        } else {
            ResourceKey<Biome> key = ResourceKey.create(Registries.BIOME, Identifier.parse(spec));
            test = h -> h.is(key);
        }
        for (String dim : DIMS) {
            ServerLevel level = s.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
            if (level == null) continue;
            if (level.getChunkSource().getGenerator().getBiomeSource().possibleBiomes().stream().noneMatch(test)) continue;
            Pair<BlockPos, Holder<Biome>> r = level.findClosestBiome3d(test, BlockPos.ZERO.atY(80), 6400, 32, 64);
            if (r == null) return "!" + spec + " is possible in " + dim + " but was not found within 6400 blocks";
            BlockPos b = r.getFirst();
            return dim + " " + b.getX() + " " + b.getY() + " " + b.getZ();
        }
        return "!" + spec + " is in no dimension's biome source";
    }

    /** "dim x y z name" inside the first piece of the closest structure, or "!reason". */
    private static String locateStructure(MinecraftServer s, String spec) {
        Registry<Structure> reg = s.registryAccess().lookupOrThrow(Registries.STRUCTURE);
        HolderSet<Structure> set;
        if (spec.startsWith("#")) {
            set = reg.get(TagKey.create(Registries.STRUCTURE, Identifier.parse(spec.substring(1)))).map(h -> (HolderSet<Structure>) h).orElse(null);
        } else {
            set = reg.get(ResourceKey.create(Registries.STRUCTURE, Identifier.parse(spec))).map(h -> (HolderSet<Structure>) HolderSet.direct(h)).orElse(null);
        }
        if (set == null || set.size() == 0) return "!unknown structure " + spec;
        for (String dim : DIMS) {
            ServerLevel level = s.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
            if (level == null) continue;
            Set<Holder<Biome>> possible = level.getChunkSource().getGenerator().getBiomeSource().possibleBiomes();
            boolean fits = set.stream().anyMatch(st -> possible.stream().anyMatch(b -> st.value().biomes().contains(b)));
            if (!fits) continue;
            Pair<BlockPos, Holder<Structure>> r = level.getChunkSource().getGenerator().findNearestMapStructure(level, set, BlockPos.ZERO, 100, false);
            if (r == null) continue;
            BlockPos pos = r.getFirst();
            ChunkAccess ch = level.getChunk(pos.getX() >> 4, pos.getZ() >> 4, ChunkStatus.STRUCTURE_STARTS);
            StructureStart start = ch.getStartForStructure(r.getSecond().value());
            if (start != null && start.isValid() && !start.getPieces().isEmpty()) pos = start.getPieces().get(0).getBoundingBox().getCenter();
            return dim + " " + pos.getX() + " " + pos.getY() + " " + pos.getZ() + " " + r.getSecond().getRegisteredName();
        }
        return "!" + spec + " was not found in any dimension (search radius 100 chunks)";
    }

    // ------------------------------------------------------------------------------------------------ helpers

    private static Item resolveItem(String spec) {
        if (spec.startsWith("#")) {
            TagKey<Item> key = TagKey.create(Registries.ITEM, Identifier.parse(spec.substring(1)));
            for (Item it : BuiltInRegistries.ITEM) if (it.builtInRegistryHolder().is(key)) return it;
            return null;
        }
        Identifier id = Identifier.parse(spec);
        return BuiltInRegistries.ITEM.containsKey(id) ? BuiltInRegistries.ITEM.getValue(id) : null;
    }

    private static EntityType<?> resolveEntity(String spec) {
        if (spec.startsWith("#")) {
            TagKey<EntityType<?>> key = TagKey.create(Registries.ENTITY_TYPE, Identifier.parse(spec.substring(1)));
            EntityType<?> zombie = BuiltInRegistries.ENTITY_TYPE.getValue(Identifier.parse("minecraft:zombie"));
            if (zombie.builtInRegistryHolder().is(key)) return zombie;
            for (EntityType<?> t : BuiltInRegistries.ENTITY_TYPE) if (t.builtInRegistryHolder().is(key)) return t;
            return null;
        }
        Identifier id = Identifier.parse(spec);
        return BuiltInRegistries.ENTITY_TYPE.containsKey(id) ? BuiltInRegistries.ENTITY_TYPE.getValue(id) : null;
    }

    private boolean waitTask(long taskId, long need, int maxTicks) throws Exception {
        for (int t = 0; t < maxTicks; t += 10) {
            ctx.waitTicks(10);
            if (progress(taskId) >= need) return true;
        }
        return false;
    }

    private void home() {
        cmd(String.format(Locale.ROOT, "execute in minecraft:overworld run tp @a %.1f %.1f %.1f 0 0", HX, HY, HZ));
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

    private static ServerPlayer player(MinecraftServer s) {
        return s.getPlayerList().getPlayers().get(0);
    }

    private static long hex(String s) {
        return Long.parseUnsignedLong(s, 16);
    }

    /** Sends a quest book action from the client, exactly like a click in the book. */
    private void action(int action, long id, int extra) {
        ctx.runOnClient(mc -> {
            try {
                Class<?> c = Class.forName("net.kasax.questsicons.net.QuestNet$Action");
                Object payload = c.getConstructor(int.class, long.class, int.class).newInstance(action, id, extra);
                ClientPlayNetworking.send((CustomPacketPayload) payload);
            } catch (ReflectiveOperationException e) {
                throw new RuntimeException(e);
            }
        });
    }

    // Quest Icons' server state, read through reflection (the harness does not compile against the mod)

    private static Object questServer() throws Exception {
        return Class.forName("net.kasax.questsicons.server.QuestServer").getMethod("get").invoke(null);
    }

    private static Object team(MinecraftServer s) throws Exception {
        Object qs = questServer();
        return qs.getClass().getMethod("team", ServerPlayer.class).invoke(qs, player(s));
    }

    private boolean isCompleted(long questId) throws Exception {
        return srv(s -> {
            Object team = team(s);
            return ((Long2LongMap) team.getClass().getField("completed").get(team)).containsKey(questId);
        });
    }

    private long progress(long taskId) throws Exception {
        return srv(s -> {
            Object team = team(s);
            return ((Long2LongMap) team.getClass().getField("progress").get(team)).get(taskId);
        });
    }

    private boolean isClaimed(long rewardId) throws Exception {
        return srv(s -> {
            Object team = team(s);
            UUID me = player(s).getUUID();
            var m = team.getClass().getMethod("isRewardClaimed", UUID.class, long.class, boolean.class);
            return (Boolean) m.invoke(team, me, rewardId, false) || (Boolean) m.invoke(team, me, rewardId, true);
        });
    }

    private boolean canStart(long questId) throws Exception {
        return srv(s -> {
            Object qs = questServer();
            Object book = qs.getClass().getField("book").get(qs);
            Object quest = book.getClass().getMethod("quest", long.class).invoke(book, questId);
            if (quest == null) return false;
            Object team = team(s);
            Object view = team.getClass().getMethod("viewFor", UUID.class).invoke(team, player(s).getUUID());
            Class<?> pv = Class.forName("net.kasax.questsicons.quest.ProgressView");
            Class<?> qc = Class.forName("net.kasax.questsicons.quest.Quest");
            return (Boolean) pv.getMethod("canStart", qc).invoke(view, quest);
        });
    }
}
