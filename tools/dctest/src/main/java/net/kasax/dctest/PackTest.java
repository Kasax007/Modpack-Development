package net.kasax.dctest;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import net.minecraft.world.Difficulty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Smoke test of the whole Dreamcraft pack in a real client: title screen (FancyMenu), the Drippy
 * loading overlay during a resource reload, world creation, chunk rendering, the quest book.
 */
public class PackTest implements FabricClientGameTest {
    static final Logger LOG = LoggerFactory.getLogger("dctest");

    @Override
    public void runTest(ClientGameTestContext ctx) {
        String scene = System.getProperty("dc.scene", "smoke");
        LOG.info("[dctest] scene {}", scene);
        ctx.getInput().resizeWindow(1600, 900);
        ctx.runOnClient(mc -> {
            mc.options.guiScale().set(0);
            mc.options.renderDistance().set(8);
            mc.resizeGui();
        });
        ctx.waitTicks(60);
        ctx.takeScreenshot("dc_01_title");
        ctx.runOnClient(mc -> {
            if (mc.gui.screen() != null) {
                for (var w : net.fabricmc.fabric.api.client.screen.v1.Screens.getWidgets(mc.gui.screen())) {
                    LOG.info("[dctest] widget {} '{}' at {},{} {}x{}", w.getClass().getName(), w.getMessage().getString(), w.getX(), w.getY(), w.getWidth(), w.getHeight());
                }
            }
        }); // dumpWidgets
        if (scene.equals("boot")) {
            LOG.info("[dctest] boot ok");
            return;
        }
        ctx.waitTicks(40);
        ctx.takeScreenshot("dc_02_title_later");
        String screenClass = ctx.computeOnClient(mc -> mc.gui.screen() == null ? "null" : mc.gui.screen().getClass().getName());
        LOG.info("[dctest] title screen class {}", screenClass);
        if (scene.equals("film")) {
            new Film(ctx, java.nio.file.Path.of(System.getProperty("dc.out", "film"))).run(
                    java.util.List.of(System.getProperty("dc.shots", "menu").split(",")));
            return;
        }
        if (scene.equals("quests")) {
            questScene(ctx);
            return;
        }
        // The Drippy overlay only shows while resources load: trigger a reload and catch it.
        ctx.runOnClient(mc -> { mc.reloadResourcePacks(); });
        ctx.waitTicks(2);
        ctx.takeScreenshot("dc_03_loading");
        ctx.waitTicks(10);
        ctx.takeScreenshot("dc_04_loading_later");
        ctx.waitFor(mc -> mc.gui.overlay() == null, 20 * 600);
        long t0 = System.currentTimeMillis();
        try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(s -> {
            s.setSeed("dreamcraft");
            s.setGameMode(WorldCreationUiState.SelectedGameMode.SURVIVAL);
            s.setAllowCommands(true);
            s.setDifficulty(Difficulty.NORMAL);
        }).create()) {
            LOG.info("[dctest] world created in {} s", (System.currentTimeMillis() - t0) / 1000);
            for (int i = 0; i < 60; i++) {
                ctx.waitTicks(20);
                if (i > 5 && ctx.computeOnClient(mc -> mc.levelRenderer.hasRenderedAllSections())) break;
            }
            LOG.info("[dctest] world drawn after {} s", (System.currentTimeMillis() - t0) / 1000);
            ctx.takeScreenshot("dc_05_world");
            sp.getServer().runCommand("time set day");
            sp.getServer().runCommand("weather clear");
            ctx.waitTicks(40);
            ctx.takeScreenshot("dc_06_world_day");
            ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_J);
            ctx.waitTicks(20);
            ctx.takeScreenshot("dc_07_questbook");
            ctx.setScreen(() -> null);
            ctx.waitTicks(5);
            ctx.setScreen(() -> new InventoryScreen(Minecraft.getInstance().player));
            ctx.waitTicks(20);
            ctx.takeScreenshot("dc_08_inventory");
            ctx.setScreen(() -> null);
            sp.getServer().runCommand("gamemode creative @a");
            sp.getServer().runCommand("tp @a ~ ~60 ~");
            ctx.waitTicks(60);
            ctx.takeScreenshot("dc_09_overview");
        }
        LOG.info("[dctest] done");
    }

    /**
     * Opens the real quest book: optional registry dump (-Pdump=FILE), screenshots of chapters (-Pchapters=all or
     * filenames, at -Pwin=WxH and -Pgui=scale) and of single quests (-Pquests=hex ids).
     */
    private void questScene(ClientGameTestContext ctx) {
        String win = System.getProperty("dc.win", "");
        if (win.matches("\\d+x\\d+")) {
            String[] wh = win.split("x");
            ctx.getInput().resizeWindow(Integer.parseInt(wh[0]), Integer.parseInt(wh[1]));
        }
        String[] guis = System.getProperty("dc.gui", "0").split(",");
        int gui = Integer.parseInt(guis[0].trim());
        ctx.runOnClient(mc -> {
            mc.options.guiScale().set(gui);
            mc.resizeGui();
        });
        try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(s -> {
            s.setGameMode(WorldCreationUiState.SelectedGameMode.CREATIVE);
            s.setAllowCommands(true);
        }).create()) {
            ctx.waitTicks(100);
            String dump = System.getProperty("dc.dump", "");
            if (!dump.isBlank()) {
                sp.getServer().runOnServer(server -> {
                    try {
                        RegDump.write(server, java.nio.file.Path.of(dump));
                    } catch (Exception e) {
                        LOG.warn("[dctest] registry dump failed", e);
                    }
                });
            }
            sp.getServer().runCommand("quests complete 69EBF5E4D7E44EE2 @a");
            ctx.waitTicks(20);
            ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_J);
            ctx.waitTicks(30);
            ctx.takeScreenshot("q_00_book");
            Class<?> screenClass;
            try {
                screenClass = Class.forName("net.kasax.questsicons.client.gui.QuestBookScreen");
            } catch (ClassNotFoundException e) {
                throw new RuntimeException(e);
            }
            String chapters = System.getProperty("dc.chapters", "");
            if (!chapters.isBlank()) {
                java.util.List<String> names = ctx.computeOnClient(mc -> chapterNames());
                java.util.Set<String> want = new java.util.HashSet<>(java.util.List.of(chapters.split(",")));
                for (String g : guis) {   // one round of screenshots per GUI scale
                    int scale = Integer.parseInt(g.trim());
                    ctx.runOnClient(mc -> {
                        mc.options.guiScale().set(scale);
                        mc.resizeGui();
                    });
                    ctx.waitTicks(10);
                    int c = 1;
                    for (String name : names) {
                        if (!chapters.equals("all") && !want.contains(name)) continue;
                        ctx.runOnClient(mc -> selectChapter(mc, screenClass, name));
                        ctx.waitTicks(10);
                        ctx.takeScreenshot(String.format("q_g%d_c%02d_%s", scale, c++, name));
                    }
                }
            }
            String visit = System.getProperty("dc.visit", "");
            if (!visit.isBlank()) {   // e.g. raft:raftdim: does the dimension generate in the full pack?
                ctx.setScreen(() -> null);
                sp.getServer().runCommand("execute in " + visit + " run tp @a 0 130 0");
                for (int i = 0; i < 60; i++) {
                    ctx.waitTicks(20);
                    if (i > 5 && ctx.computeOnClient(mc -> mc.levelRenderer.hasRenderedAllSections())) break;
                }
                ctx.takeScreenshot("q_visit");
                for (String s : System.getProperty("dc.locate", "").split(",")) {
                    if (!s.isBlank()) sp.getServer().runCommand("execute in " + visit + " run locate structure " + s.trim());
                }
                ctx.waitTicks(100);
                LOG.info("[dctest] visited {}", visit);
                ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_J);
                ctx.waitTicks(30);
            }
            String[] quests = System.getProperty("dc.quests", "").split(",");
            int n = 1;
            for (String q : quests) {
                if (q.isBlank()) continue;
                long id = Long.parseUnsignedLong(q.trim(), 16);
                ctx.runOnClient(mc -> {
                    var screen = mc.gui.screen();
                    if (screen != null && screenClass.isInstance(screen)) {
                        try {
                            screenClass.getMethod("openQuest", long.class).invoke(screen, id);
                        } catch (Exception e) {
                            LOG.warn("[dctest] openQuest failed", e);
                        }
                    }
                });
                ctx.waitTicks(10);
                ctx.takeScreenshot(String.format("q_%02d_%s", n++, q.trim()));
            }
        }
    }

    /** File names of the chapters of the quest book the client received, in book order. */
    private static java.util.List<String> chapterNames() {
        java.util.List<String> out = new java.util.ArrayList<>();
        try {
            Object book = Class.forName("net.kasax.questsicons.client.ClientQuests").getField("book").get(null);
            for (Object ch : (java.util.List<?>) book.getClass().getField("chapters").get(book)) {
                out.add((String) ch.getClass().getField("filename").get(ch));
            }
        } catch (Exception e) {
            LOG.warn("[dctest] reading the chapters failed", e);
        }
        return out;
    }

    /** Shows one chapter in the open quest book, the way a click on it in the chapter list does. */
    private static void selectChapter(Minecraft mc, Class<?> screenClass, String name) {
        var screen = mc.gui.screen();
        if (screen == null || !screenClass.isInstance(screen)) return;
        try {
            Object book = Class.forName("net.kasax.questsicons.client.ClientQuests").getField("book").get(null);
            for (Object ch : (java.util.List<?>) book.getClass().getField("chapters").get(book)) {
                if (!name.equals(ch.getClass().getField("filename").get(ch))) continue;
                var m = screenClass.getDeclaredMethod("selectChapter", ch.getClass());
                m.setAccessible(true);
                m.invoke(screen, ch);
                LOG.info("[dctest] chapter {} shown", name);
            }
        } catch (Exception e) {
            LOG.warn("[dctest] selectChapter failed", e);
        }
    }
}
