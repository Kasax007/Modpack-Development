## Dreamcraft 26.3 V1.6.3 - Attack through gaps

Bug fixes.

- **Your attacks hit what you aim at.** Until now Better Combat only counted a hit when it could see the mob from your
  eyes. Crouching behind a wall with a one-block gap, you saw the swing but the mobs behind the gap took no damage.
  This check is now switched off, so you hit mobs through gaps again.
- Note: with the check off, a weapon swing also reaches mobs behind a wall if they are within your weapon's reach.

Your worlds and quest progress are kept.

### Server
- The server pack contains the new file config/bettercombat/server.json5.
- To update an existing server: copy config/bettercombat/server.json5 from the server pack (or set
  "allow_attacking_thru_walls" to true in that file), then restart the server. The server sends the setting to all
  players.
