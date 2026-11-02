# dctest – client test and film harness for Dreamcraft 26.3

A tiny Fabric mod that runs the whole pack in a client game test (`./gradlew runPack`).
`tools/dc_prepare.py` copies the pack's mods and configs into `build/run/client` first.

- `-Pscene=boot|smoke|quests|film` – boot only, create a world and look around, open the quest book, or film shots
- `-Pshots=a,b,c -Pout=DIR` – film shots (portrait frames at 30 fps of game time + a landscape still each), see `Film.java`
- `-Pxmx=5G` – heap of the test client (more than 6 GB once got the process killed in the container)

`KeyFix` fills key bindings that are registered late, so the game test's option reset does not crash.
