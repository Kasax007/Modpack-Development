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
