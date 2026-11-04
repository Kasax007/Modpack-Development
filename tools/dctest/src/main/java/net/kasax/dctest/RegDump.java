package net.kasax.dctest;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.crafting.Recipe;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.stream.Collectors;

/**
 * Writes the ids the running pack really has (items with names, mobs, advancements, structures, biomes, dimensions and
 * the tags of these registries) to one JSON file. tools/qcheck.py --game FILE checks the quest book against it.
 * Also logs whether the Dream Star recipes of Quest Icons loaded (their load conditions need the pack's mods).
 */
final class RegDump {
    private RegDump() {
    }

    static void write(MinecraftServer server, Path file) throws Exception {
        JsonObject root = new JsonObject();
        JsonObject items = new JsonObject();
        TreeMap<String, Item> sorted = new TreeMap<>();
        for (Identifier id : BuiltInRegistries.ITEM.keySet()) sorted.put(id.toString(), BuiltInRegistries.ITEM.getValue(id));
        for (var e : sorted.entrySet()) {
            JsonArray a = new JsonArray();
            a.add(e.getValue().getDefaultInstance().getHoverName().getString());
            String ns = e.getKey().substring(0, e.getKey().indexOf(':'));
            a.add(FabricLoader.getInstance().getModContainer(ns).map(m -> m.getMetadata().getName()).orElse(ns));
            items.add(e.getKey(), a);
        }
        root.add("items", items);
        root.add("entity", ids(BuiltInRegistries.ENTITY_TYPE.keySet().stream().map(Identifier::toString).collect(Collectors.toCollection(TreeSet::new))));
        root.add("advancement", ids(server.getAdvancements().getAllAdvancements().stream().map(h -> h.id().toString())
                .collect(Collectors.toCollection(TreeSet::new))));
        var access = server.registryAccess();
        root.add("structure", ids(keys(access.lookupOrThrow(Registries.STRUCTURE))));
        root.add("biome", ids(keys(access.lookupOrThrow(Registries.BIOME))));
        root.add("dimension", ids(server.levelKeys().stream().map(k -> k.identifier().toString()).collect(Collectors.toCollection(TreeSet::new))));
        JsonObject tags = new JsonObject();
        tags.add("item", ids(tagIds(BuiltInRegistries.ITEM)));
        tags.add("block", ids(tagIds(BuiltInRegistries.BLOCK)));
        tags.add("entity_type", ids(tagIds(BuiltInRegistries.ENTITY_TYPE)));
        tags.add("worldgen/structure", ids(access.lookupOrThrow(Registries.STRUCTURE).listTagIds().map(t -> t.location().toString())
                .collect(Collectors.toCollection(TreeSet::new))));
        tags.add("worldgen/biome", ids(access.lookupOrThrow(Registries.BIOME).listTagIds().map(t -> t.location().toString())
                .collect(Collectors.toCollection(TreeSet::new))));
        root.add("tags", tags);
        JsonObject recipes = new JsonObject();
        for (String r : new String[]{"questsicons:dream_star", "questsicons:dream_star_vanilla", "questsicons:dream_star_pedestal"}) {
            boolean loaded = server.getRecipeManager().byKey(ResourceKey.create(Registries.RECIPE, Identifier.parse(r))).isPresent();
            recipes.addProperty(r, loaded);
            PackTest.LOG.info("[dctest] recipe {} loaded={}", r, loaded);
        }
        root.add("recipes", recipes);
        // A quest reward with item components (the bookmarked Seafarer's Almanac) goes through the same codec as here.
        var tag = net.minecraft.nbt.TagParser.parseCompoundFully(
                "{id:\"raft:seafarers_almanac\",count:1,components:{\"minecraft:custom_data\":{almanac:\"diving\"}}}");
        var stack = net.minecraft.world.item.ItemStack.CODEC.parse(access.createSerializationContext(net.minecraft.nbt.NbtOps.INSTANCE), tag)
                .result().orElse(net.minecraft.world.item.ItemStack.EMPTY);
        PackTest.LOG.info("[dctest] component reward parses as {} with {}", stack, stack.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA));
        Files.createDirectories(file.getParent());
        Files.writeString(file, new GsonBuilder().setPrettyPrinting().create().toJson(root), StandardCharsets.UTF_8);
        PackTest.LOG.info("[dctest] registry dump: {} items, {} mobs, {} advancements -> {}", items.size(),
                root.getAsJsonArray("entity").size(), root.getAsJsonArray("advancement").size(), file);
    }

    private static TreeSet<String> keys(HolderLookup.RegistryLookup<?> lookup) {
        return lookup.listElementIds().map(k -> k.identifier().toString()).collect(Collectors.toCollection(TreeSet::new));
    }

    private static TreeSet<String> tagIds(Registry<?> registry) {
        return registry.getTags().map(t -> t.key().location().toString()).collect(Collectors.toCollection(TreeSet::new));
    }

    private static JsonArray ids(TreeSet<String> set) {
        JsonArray a = new JsonArray();
        set.forEach(a::add);
        return a;
    }
}
