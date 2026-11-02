# Dreamcraft – Development

Development page of my modpack **Dreamcraft [FABRIC]** on CurseForge:
https://www.curseforge.com/minecraft/modpacks/dreamcraft-new

If you have any issues with the pack, feel free to create an issue - and don't forget to upload your crash log!

## Branch `26.3` – Dreamcraft for Minecraft 26.3

| Path | Content |
| --- | --- |
| `modlist-26.3.md` | all mods of the pack (CurseForge file, client or both sides) |
| `pack/overrides/` | everything the pack ships besides the mods: configs, main menu and loading screen (FancyMenu, Drippy), the quest book (`config/questsicons/quests`) |
| `pack/mods.json` | project and file ids of every mod (the source of `manifest.json`) |
| `pack/removed.md` | mods of 1.20.1 V4 that are left out on 26.3, and why |
| `pack/client_only.json` | mods that are not put into the server pack |
| `tools/` | build scripts: `pack.py` (find and download the 26.3 files), `mkpack.py` (client zip + server pack), `dc_quests.py` + `dc_quests_raft.py` (the quest story), `menu_gen.py` (menu images and layouts), `srv.sh` (test server) |
| `docs/curseforge/` | description, changelog and the images of the CurseForge page (`make_images.py`) |

Minecraft 26.3, Fabric Loader 0.20.1, Java 25. Quests run on my mod
[Quest Icons](https://www.curseforge.com/minecraft/mc-mods/quest-icons) (FTB Quests is not available for 26.3),
the raft ocean is my mod [Beach Craft](https://www.curseforge.com/minecraft/mc-mods/beach-craft).
