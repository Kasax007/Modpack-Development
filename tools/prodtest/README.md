# prodtest – test the pack the way players get it

The client game test in `tools/dctest` runs inside Loom, a development environment. It skips Neruina, whose test mixins
throw in a development run, and it skips the server-only mods. These scripts test the published pack the way the
CurseForge app installs it, with the real production launcher (Fabric Loader without Loom).

1. **Install like a launcher:** `python3 -I cf_install.py 9409459 9409463` (client and server file ids, here V1.2).
   - Loads the modpack zip from CurseForge.
   - Downloads every manifest file by project and file id (`https://www.curseforge.com/api/v1/mods/<pid>/files/<fid>/download`).
   - Unpacks the overrides into `instance/`.
   - Writes `report.json` with the sha1 of every jar.
   - Move the two shader pack zips from `mods/` to `shaderpacks/`, as the app does.
2. **Start the client:** `DISPLAY=:98 SDL_VIDEO_FORCE_EGL=1 python3 -I launch.py INSTANCE --width 854 --height 480`.
   - Minecraft 26.3 + Fabric Loader 0.20.1.
   - Classpath from the Fabric profile (meta.fabricmc.net) and the Mojang version JSON from the Loom cache.
   - Assets from the Loom cache.
3. **Look and click:**
   - `shot.sh OUT.png` grabs the Xvfb screen.
   - `xin.py move X Y | click | key j` sends input over XTEST (python-xlib).
   - `xwin.py W H` resizes the game window, to test the main menu at different sizes.
4. **Server pack:** unzip it, run `start.sh` once (it asks for the EULA), set `eula=true`, and start it again.

What this test found in V1.1 (fixed in V1.2):
- The main menu cut off its buttons on small windows.
- The Mods and Rent a Server buttons had no action.
- Shoulder Surfing started in the shoulder camera.
- Just Enough Resources failed on BetterNether's biomes.
