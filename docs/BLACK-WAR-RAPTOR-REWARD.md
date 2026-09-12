# Black War Raptor player reward

Item 18246 (Whistle of the Black War Raptor), spell 22721, is available to all races and factions at level 40 with Apprentice Riding (75). The old PvP rank/reputation gates are removed. No riding skill is granted. The mount spell itself also enforces level 40 and riding 75, including learned/copied mounts. Item definitions are refreshed on login to replace stale cached race/level requirements.

Its base mounted speed is +60%. At level 60 or higher with Journeyman Riding (150 or higher), it becomes +100% on the next mount application. Level alone or early epic training does not unlock the faster speed. Other mounts, native movement bonuses, slows and ordinary mount-use restrictions remain unchanged. The existing client spell tooltip may still describe the original fixed epic speed; actual movement is calculated by the server. No client patch or addon change is required.

Existing non-deleted player characters of level 40+ receive one item through the startup backfill after deployment/restart. Live characters receive it at level-up from level 40 onward, and login retries missed grants. Random bot accounts are excluded using the same configured account list as the utility gifts. The mount is not sent to newly created lower-level characters.

The grant key is black_war_raptor_v1 in mantech_character_grants. Existing grant history, bag/bank/equipped ownership, pending mail, and learned mount spell 22721 all suppress duplicate delivery. The online inventory and learned spell also count before their next save. Owning the reward without local grant history records an acknowledgement rather than creating mail. The existing atomic item/mail/grant transaction and failure-defer behavior are reused.

Character-copy tooling must import inventory and learned spells before destination login/grant callbacks. Keep entry 18246 and spell 22721 when converting between expansions; Wrath uses a learned mount while Classic/TBC retain the item. Copy grant history with the destination character GUID if supported. As with the existing gifts, deleting a previously granted item does not issue a replacement automatically.

Apply sql/custom/world/20260911_01_black_war_raptor_reward.sql to each matching world database and deploy the matching binary before restarting that realm. Character schema is unchanged. Automated grant and aura tests cover eligibility, ownership, level/skill boundaries and unchanged other mounts; live mounting/mail tests remain necessary after restart.
