# Classic dungeon and raid travel commands

Enter commands in chat. Full canonical commands also work in the addon PBTP protocol. Short aliases are case-insensitive. Existing points may be inside or outside; shared approaches require following the normal route. Each destination first requires one character on this account to enter the dungeon/raid once in this realm. That unlock survives relogs and restarts. Eligibility, native entry requirements and cooldown still apply.

| Dungeon / raid | Full command | Short command(s) | Arrival |
|---|---|---|---|
| Ragefire Chasm | `.tp ragefire_chasm` | `.tp RFC` | Inside. |
| The Deadmines | `.tp deadmines` | `.tp DM`, `.tp VC` | Outside. |
| Wailing Caverns | `.tp wailing_caverns` | `.tp WC` | Outside. |
| Shadowfang Keep | `.tp shadowfang_keep` | `.tp SFK` | Outside. |
| Blackfathom Deeps | `.tp blackfathom_deeps` | `.tp BFD` | Outside. |
| The Stockade | `.tp stockade` | `.tp STOCK`, `.tp STOCKS` | Inside. |
| Gnomeregan | `.tp gnomeregan` | `.tp GNOMER` | Outside. |
| Razorfen Kraul | `.tp razorfen_kraul` | `.tp RFK` | Outside. |
| Scarlet Monastery: Graveyard | `.tp scarlet_graveyard` | `.tp SM`, `.tp SMGY` | Outside. Shared Scarlet Monastery approach; walk to the selected wing. |
| Scarlet Monastery: Library | `.tp scarlet_library` | `.tp SMLIB` | Outside. Shared Scarlet Monastery approach; walk to the selected wing. |
| Scarlet Monastery: Armory | `.tp scarlet_armory` | `.tp SMARM` | Outside. Shared Scarlet Monastery approach; walk to the selected wing. |
| Scarlet Monastery: Cathedral | `.tp scarlet_cathedral` | `.tp SMCATH` | Outside. Shared Scarlet Monastery approach; walk to the selected wing. |
| Razorfen Downs | `.tp razorfen_downs` | `.tp RFD` | Outside. |
| Uldaman | `.tp uldaman` | `.tp ULDA` | Outside. |
| Zul'Farrak | `.tp zulfarrak` | `.tp ZF` | Outside. |
| Maraudon | `.tp maraudon` | `.tp MARA` | Outside. |
| The Temple of Atal'Hakkar | `.tp sunken_temple` | `.tp ST` | Outside. |
| Blackrock Depths | `.tp blackrock_depths` | `.tp BRD` | Outside. |
| Lower Blackrock Spire | `.tp lower_blackrock_spire` | `.tp LBRS` | Outside. |
| Upper Blackrock Spire | `.tp upper_blackrock_spire` | `.tp UBRS` | Outside. Shared Blackrock Spire entrance; follow the normal route and requirements for the upper section. |
| Dire Maul: East | `.tp dire_maul_east` | `.tp DME` | Outside. |
| Dire Maul: West | `.tp dire_maul_west` | `.tp DMW` | Outside. |
| Dire Maul: North | `.tp dire_maul_north` | `.tp DMN` | Outside. |
| Scholomance | `.tp scholomance` | `.tp SCHOLO` | Outside. |
| Stratholme | `.tp stratholme` | `.tp STRAT` | Outside. |
| Molten Core | `.tp molten_core` | `.tp MC` | Outside. Blackrock Depths approach; follow the normal route or authorized shortcut to Molten Core. |
| Onyxia's Lair (level-60 version Classic/TBC; level-80 version WotLK) | `.tp onyxias_lair` | `.tp ONY` | Outside. Level-60 encounter. |
| Blackwing Lair | `.tp blackwing_lair` | `.tp BWL` | Outside. Blackrock Spire approach; follow the normal route or authorized shortcut to Blackwing Lair. |
| Zul'Gurub | `.tp zulgurub` | `.tp ZG` | Outside. |
| Ruins of Ahn'Qiraj | `.tp ruins_ahnqiraj` | `.tp AQ20` | Outside. |
| Temple of Ahn'Qiraj | `.tp temple_ahnqiraj` | `.tp AQ40` | Outside. |
| Naxxramas level 60 (Classic/TBC ONLY; never use its old location in WotLK) | `.tp naxxramas_40` | `.tp NAXX40`, `.tp NAXX` | Outside. |

All listed canonical keys and short commands passed controlled parser/routing tests against the compiled whitelist. Coordinates and entry IDs were checked against inspected CMaNGOS world data. Actual in-game teleport/entry for every point has not been runtime-tested.
