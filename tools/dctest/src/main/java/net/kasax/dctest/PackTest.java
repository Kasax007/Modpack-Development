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

    /** Opens chapters and quests of the real quest book through reflection-free key presses and commands. */
    private void questScene(ClientGameTestContext ctx) {
        try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(s -> {
            s.setGameMode(WorldCreationUiState.SelectedGameMode.CREATIVE);
            s.setAllowCommands(true);
        }).create()) {
            ctx.waitTicks(100);
            sp.getServer().runCommand("quests complete 69EBF5E4D7E44EE2 @a");
            ctx.waitTicks(20);
            String[] chapters = {"14B4AA34E0B85D82"};
            ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_J);
            ctx.waitTicks(30);
            ctx.takeScreenshot("q_00_book");
            Class<?> screenClass;
            try {
                screenClass = Class.forName("net.kasax.questsicons.client.gui.QuestBookScreen");
            } catch (ClassNotFoundException e) {
                throw new RuntimeException(e);
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
}
