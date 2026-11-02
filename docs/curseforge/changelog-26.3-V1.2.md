## Dreamcraft 26.3 V1.2 - main menu fixes

A fix update. The pack was installed from CurseForge like a launcher does it and played on a normal client and a dedicated server. Everything below came up in that test.

### Fixed
- **The main menu fits every window size.** Before, smaller windows cut off the lower buttons. On the default 854x480 window no button could be clicked at all, and on 1366x768 "Quit Game" was missing. The menu now scales with the window.
- **Mods and Rent a Server buttons work.** They did nothing when clicked.
- **The loading bar is purple**, like the rest of the loading screen.
- **You start in first person.** Shoulder Surfing put new players into its shoulder camera. It is still there on F5.
- **Quest Icons 1.0.1:** joining someone's team with `/quests team join` no longer gives you a second Quest Book on your next login.
- **Quests** name JEI, the recipe viewer of the pack. A few still said REI.

### Removed
- **Just Enough Resources.** Its JEI plugin does not work with the Nether biomes of BetterNether and showed no pages at all. JEI and Just Enough Professions stay.

### Server
- The server pack contains Quest Icons 1.0.1.
- To update a V1.1 server, replace `mods/QuestIcons-*.jar` and remove `mods/JustEnoughResources-*.jar` if you added it yourself.
