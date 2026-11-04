# dctest – client test and film harness for Dreamcraft 26.3

A tiny Fabric mod that runs the whole pack in a client game test (`./gradlew runPack`).
`tools/dc_prepare.py` copies the pack's mods and configs into `build/run/client` first.

## Options

- `-Pscene=boot|smoke|quests|film`: boot only, create a world and look around, open the quest book, or film shots.
- `-Pshots=a,b,c -Pout=DIR`: film shots. Each shot gives portrait frames at 30 fps of game time plus a landscape still.
  See `Film.java`.
- `-Prd=12`: render distance (simulation distance at most 12). Before every shot, `settle()` waits until all chunks
  around the player are loaded and drawn, so nothing loads in on screen.
- `-Pnostills=1`: no landscape stills. With shaders, every window resize costs native memory.
- `-Pxmx=5G`: heap of the test client. More than 6 GB once got the process killed in the container.
- Quest scene (`-Pscene=quests`):
  - `-Pchapters=all` (or chapter file names): one screenshot per chapter of the quest book, as a click in the chapter
    list shows it. `-Pwin=1920x1080 -Pgui=4,2` sets the window and the GUI scales, one round of screenshots per scale
    (4 is what 1920×1080 gets on "Auto").
  - `-Pquests=<hex ids>`: opens these quests one by one.
  - `-Pvisit=raft:raftdim -Plocate=raft:old_lighthouse,...`: teleports into a dimension, waits for the chunks, takes
    a screenshot and runs `/locate structure` there (the answers are in the log).
  - `-Pdump=FILE`: writes the ids the running pack has (items, mobs, advancements, structures, biomes, dimensions,
    tags) as JSON, logs whether the Dream Star recipes loaded and whether an item with components (a bookmarked
    almanac) parses. `tools/qcheck.py --game FILE` checks the quests against the dump.

## Shots

- `Film.java`: the Dreamcraft TikTok (castle, village, magic, mutant, kitchen, tech, raft, shark, nether, end, menu,
  questbook).
- `BcShots.java`: the Beach Craft review, every feature of the mod. These shots are named `bc_*`, and most of them
  play on a 13×13 raft stage in the raft dimension. `sea()` moves a stage to open sea, because the raft dimension has
  big stone islands.
- `FilmSound` + `mixin/SoundLogMixin`: write `sounds.jsonl` / `shot.json` per shot. Every sound the game starts is
  logged with its position, so the video can be mixed from the real game sounds.

## Pitfalls (26.3)

- `mixin/ScreenshotLeakMixin` fixes a native memory leak. The Fabric game test API (6.0.11) never closes the
  screenshot `NativeImage`, which costs 8 MB per frame, so a long run got OOM-killed.
- 26.3 uses SDL, where mouse button 1 is the left button. Clicks therefore go through the key mappings, e.g.
  `pressKey(o -> o.keyUse)`, never `pressMouse(1)`.
- The integrated server ticks in real time while a frame takes 0.5–2 s to render. Server-side processes run ahead of
  the film clock.
- `KeyFix` fills key bindings that are registered late, so the game test's option reset does not crash.

## Quest check and checklist tests (added 4.11.2026, first full run still to do)

- `-Pscene=qrun -Pplan=FILE -Pout=DIR [-Pqonly=chapter,chapter:key] [-Pdata=FILE]`: `QuestRun` works through all
  quests of `tools/qrun_plan.py` in dependency order and fulfils every task like a player (items, kills by the player,
  located structures/biomes/dimensions visited, creatures looked at, checkmarks and hand-ins through the book's own
  network action), waits for Quest Icons to complete the quest and claims the rewards. Report `DIR/qrun_report.json`,
  `[qrun]` lines in the log. `-Pdata` (`DataDump`) writes the final loot tables (with what mods add in code) and the
  natural spawns per biome.
- `-Pscene=bccheck -Pout=DIR [-Pchecks=deck,hammock,compressor,sounds,boss,structures,trench,pets,dreamstar]`:
  `BcCheck` runs the Beach Craft / Dreamcraft checklist tests (raft deck carrying in turns, hammock, compressor crank,
  Leviathan fight in survival, trench mobs, natural structures, Tamagotchi pet homes, Dream Star, sounds).
  Report `DIR/bccheck_report.json`. BcCheck has not been compiled yet.
- `dcrun.sh NAME [-P...]`: one locked run (Xvfb :96); `DC_TIMEOUT=5400` for the long quest run.
- Static part: `tools/qsource.py` (survival source of every quest item from all pack jars).
- Upgrade test: `tools/prodtest/mk121.py` makes a V1.2.1 copy of the installed V1.3 instance (hard links).
