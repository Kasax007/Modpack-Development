## Dreamcraft 26.3 V1.6.2 - Chests leave your items alone

Bug fixes.

- **Chests no longer rearrange your items.** Until now a chest pushed its stacks together as soon as you opened it or
  took something out. The cause was the setting "Keep stored items tidy" of Upgraded Iron Chests, which was switched on
  for everybody. It is now off by default: your items stay in the slots you put them in - in normal chests, barrels,
  loot chests and the upgraded chests.
- **One shift-click takes one stack.** Because the stacks slid up, a shift-click that was held a moment too long pulled
  several stacks out of a chest. That is fixed, also for players who switch the tidying on again. Dragging over several
  slots with Shift held still moves them all.
- **If you like tidy chests:** open your inventory (not in Creative mode), click the gear button below it and switch on
  "Keep stored items tidy". The setting is kept per world and per server and stays on there.
- **R only shows recipes.** Pressing R over an item shows its recipe - until now it sorted the open chest or your
  inventory at the same time, because Inventory Profiles Next used the same key. Sorting is on the small sort button
  above the top right slot of a chest or your inventory. If you want a key for it, set one under Mods > Inventory
  Profiles Next > Hotkeys.
- In a world you have already played, a short note in the chat tells you about the chest change the first time you join.
- **On a multiplayer server** the new default needs the server to be updated too (see below). If chests still tidy
  themselves there, switch it off yourself: open your inventory (not in Creative mode), click the gear button below it
  and set "Keep stored items tidy" to Off. No operator rights are needed.
- The quests "Find My Item" and "Tidy Up" (Quality of Life) say where the switches are.
- Mod update: Quest Icons 1.3.2, which brings the new default.

Your worlds and quest progress are kept.

### Server
- The server pack contains Quest Icons 1.3.2, the new file config/questsicons/pack_options.json and the two changed
  quest texts.
- To update an existing server: replace mods/QuestIcons-*.jar, add config/questsicons/pack_options.json and replace the
  folder config/questsicons/quests, all from the server pack. Then restart the server.
- Players with V1.6.2 can join a server that still runs V1.6.1.
- The setting belongs to each player. A chest is still tidied when a player who has switched it on uses that chest.
