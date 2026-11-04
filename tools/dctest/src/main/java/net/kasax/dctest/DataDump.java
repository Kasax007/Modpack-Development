package net.kasax.dctest;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.serialization.JsonOps;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.attribute.EnvironmentAttributes;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraft.world.level.storage.loot.LootTable;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * What the running pack really gives, after every mod changed it in code (-Pdata=FILE in the qrun scene):
 * "loot": the items each loot table can drop (encoded from the final tables, so pools that mods add with Fabric's
 * loot events are included); "spawns": for every mob, the biomes (per dimension) whose natural spawn lists have it.
 * tools/qsource.py --game-data FILE uses it for the quest item check.
 */
final class DataDump {
    private DataDump() {
    }

    static void write(MinecraftServer server, Path file) throws Exception {
        JsonObject root = new JsonObject();
        var ops = server.registryAccess().createSerializationContext(JsonOps.INSTANCE);
        JsonObject loot = new JsonObject();
        int[] failed = {0};
        server.reloadableRegistries().lookup().lookupOrThrow(Registries.LOOT_TABLE).listElements().forEach(h -> {
            var enc = LootTable.DIRECT_CODEC.encodeStart(ops, h.value());
            if (enc.result().isEmpty()) {
                failed[0]++;
                return;
            }
            Set<String> items = new TreeSet<>();
            collect(enc.result().get(), items);
            if (items.isEmpty()) return;
            JsonArray a = new JsonArray();
            items.forEach(a::add);
            loot.add(h.key().identifier().toString(), a);
        });
        root.add("loot", loot);
        TreeMap<String, TreeSet<String>> spawns = new TreeMap<>();
        for (ServerLevel level : server.getAllLevels()) {
            String dim = level.dimension().identifier().toString();
            for (Holder<Biome> b : level.getChunkSource().getGenerator().getBiomeSource().possibleBiomes()) {
                for (MobCategory cat : MobCategory.values()) {
                    var mobs = b.value().getAttributes().applyModifier(EnvironmentAttributes.NATURAL_MOB_SPAWNS, MobSpawnSettings.EMPTY);
                    for (var w : mobs.getMobsToSpawn(cat).unwrap()) {
                        String e = BuiltInRegistries.ENTITY_TYPE.getKey(w.value().type()).toString();
                        spawns.computeIfAbsent(e, k -> new TreeSet<>()).add(dim + " " + b.getRegisteredName());
                    }
                }
            }
        }
        JsonObject sp = new JsonObject();
        spawns.forEach((k, v) -> {
            JsonArray a = new JsonArray();
            v.forEach(a::add);
            sp.add(k, a);
        });
        root.add("spawns", sp);
        Files.createDirectories(file.getParent());
        Files.writeString(file, new GsonBuilder().setPrettyPrinting().create().toJson(root), StandardCharsets.UTF_8);
        PackTest.LOG.info("[dctest] data dump: {} loot tables with items ({} could not be encoded), {} mobs with natural spawns -> {}",
                loot.size(), failed[0], sp.size(), file);
    }

    /** Every string in the encoded table that names an item. */
    private static void collect(JsonElement e, Set<String> out) {
        if (e.isJsonPrimitive() && e.getAsJsonPrimitive().isString()) {
            String s = e.getAsString();
            if (s.startsWith("#")) {
                if (s.indexOf(':') > 0) out.add(s);
            } else if (s.indexOf(':') > 0) {
                Identifier id = Identifier.tryParse(s);
                if (id != null && BuiltInRegistries.ITEM.containsKey(id)) out.add(s);
            }
        } else if (e.isJsonArray()) {
            for (JsonElement c : e.getAsJsonArray()) collect(c, out);
        } else if (e.isJsonObject()) {
            for (var en : e.getAsJsonObject().entrySet()) collect(en.getValue(), out);
        }
    }
}
