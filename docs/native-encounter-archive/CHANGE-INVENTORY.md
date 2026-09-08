# Native boss changes made during the Playerbots audit

## Verified count

**79 distinct dungeon/raid boss encounters** have direct native code or boss-data changes in the current published baselines. Counting each affected encounter once per core gives **145 core/encounter combinations**. This is not a count of individual fixes: several bosses received multiple corrections.

| Core | Raid encounters | Dungeon encounters | Total |
| --- | ---: | ---: | ---: |
| Classic | 16 | 1 | 17 |
| Tbc | 30 | 19 | 49 |
| Wotlk | 43 | 36 | 79 |

Unique encounters across expansions: 43 raid encounters and 36 dungeon encounters.

## Counting method and limits

- Reviewed the full reachable and first-parent native-script audit history, plus database migrations. The attributable native encounter audit commits begin on 6 September 2026 and continue through 8 September. Earlier history back through 20 August was checked to distinguish upstream merges and portable utilities from this audit.
- Compared each core from before its first native encounter audit commit to its current published head. Verified that the union of files touched by those commits equals the net file inventory; no reverted native file was silently omitted.
- 31 core commits contain direct native-script/ScriptDev SQL changes. Commit count is separate from boss count.
- Counted multi-boss council/duo fights as one encounter. Counted Eadric and Paletress separately because they are distinct alternative encounters in one source file. Counted the two Kael’thas fights separately. Counted the Classic/Wrath version of the same named encounter once in the unique total, but separately per core.
- Included database-only Arlokk, Gothik and Garfrost changes. Associated Ahn’kahet instance changes with Volazj. Associated Yogg keeper changes with Yogg-Saron rather than adding Hodir’s separate fight.
- This counts direct changes to bosses, their adds, phases, spells and cleanup; it does not imply every boss was redesigned.
- Excluded Playerbots-only routines, upstream boss changes that predate this audit, the separate ICC restoration task, portable utilities, training dummies, dual spec, trash-only spell-list repairs, and general core/spawn/path/vehicle changes. Those general changes can affect encounters more broadly and are not represented as additional named bosses.
- The newest unreleased Volazj/Lich King/Kazzak/Taerar edits were set aside and are excluded from the committed total. Within dungeon/raid scope, they add no newly named encounter to this list: Volazj and Lich King already had earlier committed changes. Kazzak and Taerar were additional world-boss edits, never committed or deployed.

## Published heads used

- classic: `52613042b5919be549a76cff784bd9b07ec45dc9` → `24839af7bdaa71c716f755f5888107a7b9cdb609`
- tbc: `9e99cc98c707b8a9bc75d237dd2578624de82c9c` → `ecea10ca95df777c067a49aefb4b1272b14b420f`
- wotlk: `0a89cc988c810447b06d346c9ef0be4f7afc3bee` → `a56cb6bf7d2e7b72fe4df18c799e5fbfe44ac9ed`

## Complete encounter list

✓ means that core contains a direct change to this encounter, including earlier-expansion content.

| # | Encounter | Instance | Type | Classic | TBC | Wrath |
| ---: | --- | --- | --- | :---: | :---: | :---: |
| 1 | Amanitar | Ahnkahet | Dungeon | — | — | ✓ |
| 2 | Herald Volazj | Ahnkahet | Dungeon | — | — | ✓ |
| 3 | Jedoga Shadowseeker | Ahnkahet | Dungeon | — | — | ✓ |
| 4 | Harbinger Skyriss | Arcatraz | Dungeon | — | ✓ | ✓ |
| 5 | Soccothrates | Arcatraz | Dungeon | — | ✓ | ✓ |
| 6 | Kelidan The Breaker | Blood Furnace | Dungeon | — | ✓ | ✓ |
| 7 | The Prophet Tharon’ja | Draktharon Keep | Dungeon | — | — | ✓ |
| 8 | Devourer Of Souls | Forge Of Souls | Dungeon | — | — | ✓ |
| 9 | Drakkari Colossus | Gundrak | Dungeon | — | — | ✓ |
| 10 | Ionar | Halls Of Lightning | Dungeon | — | — | ✓ |
| 11 | Krystallus | Halls Of Stone | Dungeon | — | — | ✓ |
| 12 | Nazan and Vazruden | Hellfire Ramparts | Dungeon | — | ✓ | ✓ |
| 13 | Kael’thas — Magisters’ Terrace | Magisters Terrace | Dungeon | — | ✓ | ✓ |
| 14 | Priestess Delrissa | Magisters Terrace | Dungeon | — | ✓ | ✓ |
| 15 | Selin Fireheart | Magisters Terrace | Dungeon | — | ✓ | ✓ |
| 16 | Vexallus | Magisters Terrace | Dungeon | — | ✓ | ✓ |
| 17 | Grand Magus Telestra | Nexus | Dungeon | — | — | ✓ |
| 18 | Ormorok the Tree-Shaper | Nexus | Dungeon | — | — | ✓ |
| 19 | Scourgelord Tyrannus | Pit Of Saron | Dungeon | — | — | ✓ |
| 20 | Forgemaster Garfrost | Pit of Saron | Dungeon | — | — | ✓ |
| 21 | Headless Horseman | Scarlet Monastery | Dungeon | — | ✓ | ✓ |
| 22 | Mograine and Whitemane | Scarlet Monastery | Dungeon | ✓ | ✓ | ✓ |
| 23 | Anzu | Sethekk Halls | Dungeon | — | ✓ | ✓ |
| 24 | Darkweaver Syth | Sethekk Halls | Dungeon | — | ✓ | ✓ |
| 25 | Ambassador Hellmaw | Shadow Labyrinth | Dungeon | — | ✓ | ✓ |
| 26 | Blackheart The Inciter | Shadow Labyrinth | Dungeon | — | ✓ | ✓ |
| 27 | Nethekurse | Shattered Halls | Dungeon | — | ✓ | ✓ |
| 28 | Warbringer Omrogg | Shattered Halls | Dungeon | — | ✓ | ✓ |
| 29 | Warchief Kargath Bladefist | Shattered Halls | Dungeon | — | ✓ | ✓ |
| 30 | Warlord Kalithresh | Steam Vault | Dungeon | — | ✓ | ✓ |
| 31 | Argent Confessor Paletress | Trial Of The Champion | Dungeon | — | — | ✓ |
| 32 | Black Knight | Trial Of The Champion | Dungeon | — | — | ✓ |
| 33 | Eadric the Pure | Trial Of The Champion | Dungeon | — | — | ✓ |
| 34 | Grand Champions | Trial Of The Champion | Dungeon | — | — | ✓ |
| 35 | Swamplord Muselek | Underbog | Dungeon | — | ✓ | ✓ |
| 36 | Ingvar the Plunderer | Utgarde Keep | Dungeon | — | — | ✓ |
| 37 | Illidan | Black Temple | Raid | — | ✓ | ✓ |
| 38 | Reliquary Of Souls | Black Temple | Raid | — | ✓ | ✓ |
| 39 | Shade Of Akama | Black Temple | Raid | — | ✓ | ✓ |
| 40 | Chromaggus | Blackwing Lair | Raid | ✓ | ✓ | ✓ |
| 41 | Gruul | Gruuls Lair | Raid | — | ✓ | ✓ |
| 42 | Lady Deathwhisper | Icecrown Citadel | Raid | — | — | ✓ |
| 43 | Lord Marrowgar | Icecrown Citadel | Raid | — | — | ✓ |
| 44 | Sindragosa | Icecrown Citadel | Raid | — | — | ✓ |
| 45 | The Lich King | Icecrown Citadel | Raid | — | — | ✓ |
| 46 | Netherspite | Karazhan | Raid | — | ✓ | ✓ |
| 47 | Prince Malchezaar | Karazhan | Raid | — | ✓ | ✓ |
| 48 | Shade Of Aran | Karazhan | Raid | — | ✓ | ✓ |
| 49 | Terestian Illhoof | Karazhan | Raid | — | ✓ | ✓ |
| 50 | Magtheridon | Magtheridons Lair | Raid | — | ✓ | ✓ |
| 51 | Majordomo Executus | Molten Core | Raid | ✓ | ✓ | ✓ |
| 52 | Ragnaros | Molten Core | Raid | ✓ | ✓ | ✓ |
| 53 | Gothik the Harvester | Naxxramas | Raid | — | — | ✓ |
| 54 | Maexxna | Naxxramas | Raid | ✓ | ✓ | ✓ |
| 55 | Thaddius | Naxxramas | Raid | ✓ | ✓ | ✓ |
| 56 | Halion | Ruby Sanctum | Raid | — | — | ✓ |
| 57 | Ayamiss the Hunter | Ruins Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 58 | Ossirian the Unscarred | Ruins Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 59 | Lady Vashj | Serpent Shrine | Raid | — | ✓ | ✓ |
| 60 | Felmyst | Sunwell Plateau | Raid | — | ✓ | ✓ |
| 61 | Kiljaeden | Sunwell Plateau | Raid | — | ✓ | ✓ |
| 62 | Battleguard Sartura | Temple Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 63 | Bug Trio (Kri, Vem and Yauj) | Temple Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 64 | C’Thun | Temple Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 65 | Ouro | Temple Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 66 | The Prophet Skeram | Temple Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 67 | Viscidus | Temple Of Ahnqiraj | Raid | ✓ | ✓ | ✓ |
| 68 | High Astromancer Solarian | The Eye | Raid | — | ✓ | ✓ |
| 69 | Kael’thas — Tempest Keep | The Eye | Raid | — | ✓ | ✓ |
| 70 | Assembly of Iron | Ulduar | Raid | — | — | ✓ |
| 71 | Auriaya | Ulduar | Raid | — | — | ✓ |
| 72 | Freya | Ulduar | Raid | — | — | ✓ |
| 73 | Kologarn | Ulduar | Raid | — | — | ✓ |
| 74 | Thorim | Ulduar | Raid | — | — | ✓ |
| 75 | Yogg-Saron (including keeper support) | Ulduar | Raid | — | — | ✓ |
| 76 | Emalon | Vault Of Archavon | Raid | — | — | ✓ |
| 77 | High Priest Thekal | Zulgurub | Raid | ✓ | ✓ | ✓ |
| 78 | Renataki | Zulgurub | Raid | ✓ | ✓ | ✓ |
| 79 | High Priestess Arlokk | Zul’Gurub | Raid | ✓ | ✓ | ✓ |

## File and commit evidence

### Amanitar

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/azjol-nerub/ahnkahet/boss_amanitar.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Herald Volazj

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/azjol-nerub/ahnkahet/boss_volazj.cpp`, `src/game/AI/ScriptDevAI/scripts/northrend/azjol-nerub/ahnkahet/ahnkahet.cpp`, `src/game/AI/ScriptDevAI/scripts/northrend/azjol-nerub/ahnkahet/ahnkahet.h`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Jedoga Shadowseeker

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/azjol-nerub/ahnkahet/boss_jedoga.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Harbinger Skyriss

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/arcatraz/boss_harbinger_skyriss.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/arcatraz/boss_harbinger_skyriss.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Soccothrates

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/arcatraz/boss_soccothrates.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/arcatraz/boss_soccothrates.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Kelidan The Breaker

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/blood_furnace/boss_kelidan_the_breaker.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/blood_furnace/boss_kelidan_the_breaker.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### The Prophet Tharon’ja

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/draktharon_keep/boss_tharonja.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Devourer Of Souls

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/icecrown_citadel/frozen_halls/forge_of_souls/boss_devourer_of_souls.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Drakkari Colossus

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/gundrak/boss_colossus.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Ionar

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/halls_of_lightning/boss_ionar.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Krystallus

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/halls_of_stone/halls_of_stoneScripts.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Nazan and Vazruden

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/hellfire_ramparts/boss_nazan_and_vazruden.cpp`
  Commits: `ff75862d2 Guard empty encounter target lists and stale helper references`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/hellfire_ramparts/boss_nazan_and_vazruden.cpp`
  Commits: `a7c53fc9cf Guard empty encounter target lists and stale helper references`

### Kael’thas — Magisters’ Terrace

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_felblood_kaelthas.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_felblood_kaelthas.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Priestess Delrissa

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_priestess_delrissa.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_priestess_delrissa.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Selin Fireheart

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_selin_fireheart.cpp`
  Commits: `e644c0d3b Fix Selin crystal approach and missing-distiller transition`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_selin_fireheart.cpp`
  Commits: `e0a3079852 Fix Selin crystal approach and missing-distiller transition`

### Vexallus

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_vexallus.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/magisters_terrace/boss_vexallus.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Grand Magus Telestra

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/nexus/nexus/boss_telestra.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Ormorok the Tree-Shaper

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/nexus/nexus/boss_ormorok.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Scourgelord Tyrannus

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/icecrown_citadel/frozen_halls/pit_of_saron/boss_scourgelord_tyrannus.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Forgemaster Garfrost

- wotlk: `Updates/5876_mantech_permafrost_cover.sql`
  Commits: `46494bc7 Restore encounter spell lists and required spell bindings`

### Headless Horseman

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/scarlet_monastery/boss_headless_horseman.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/scarlet_monastery/boss_headless_horseman.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Mograine and Whitemane

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/scarlet_monastery/boss_mograine_and_whitemane.cpp`
  Commits: `149bd4ef0 Repair encounter transitions and pin the updated Playerbots baseline`; `a6ac50f5d Integrate recent encounter fixes and pin the Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/scarlet_monastery/boss_mograine_and_whitemane.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`; `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/scarlet_monastery/boss_mograine_and_whitemane.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`; `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Anzu

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/sethekk_halls/boss_anzu.cpp`
  Commits: `297d683f4 Fix Anzu brood scheduling and initialize bird pulse timer`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/sethekk_halls/boss_anzu.cpp`
  Commits: `51747c25ef Fix Anzu brood scheduling and initialize bird pulse timer`

### Darkweaver Syth

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/sethekk_halls/boss_darkweaver_syth.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/sethekk_halls/boss_darkweaver_syth.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Ambassador Hellmaw

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/shadow_labyrinth/boss_ambassador_hellmaw.cpp`
  Commits: `36672ede8 Pin encounter route fixes and correct Hellmaw event handling`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/shadow_labyrinth/boss_ambassador_hellmaw.cpp`
  Commits: `2a2f62f81d Pin encounter route fixes and correct Hellmaw event handling`

### Blackheart The Inciter

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/shadow_labyrinth/boss_blackheart_the_inciter.cpp`
  Commits: `ecea10ca9 Repair encounter lifecycles and pin reviewed bot responses`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/auchindoun/shadow_labyrinth/boss_blackheart_the_inciter.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Nethekurse

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/shattered_halls/boss_nethekurse.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/shattered_halls/boss_nethekurse.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Warbringer Omrogg

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/shattered_halls/boss_warbringer_omrogg.cpp`
  Commits: `1596745d9 Fix encounter selection and phase initialization; pin tested bot rescues`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/shattered_halls/boss_warbringer_omrogg.cpp`
  Commits: `abe73e2d99 Fix encounter selection and phase initialization; pin tested bot rescues`

### Warchief Kargath Bladefist

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/shattered_halls/boss_warchief_kargath_bladefist.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/shattered_halls/boss_warchief_kargath_bladefist.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Warlord Kalithresh

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/coilfang_reservoir/steam_vault/boss_warlord_kalithresh.cpp`
  Commits: `e644c0d3b Fix Selin crystal approach and missing-distiller transition`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/coilfang_reservoir/steam_vault/boss_warlord_kalithresh.cpp`
  Commits: `e0a3079852 Fix Selin crystal approach and missing-distiller transition`

### Argent Confessor Paletress

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/crusaders_coliseum/trial_of_the_champion/boss_argent_challenge.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Black Knight

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/crusaders_coliseum/trial_of_the_champion/boss_black_knight.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Eadric the Pure

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/crusaders_coliseum/trial_of_the_champion/boss_argent_challenge.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Grand Champions

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/crusaders_coliseum/trial_of_the_champion/boss_grand_champions.cpp`
  Commits: `abe73e2d99 Fix encounter selection and phase initialization; pin tested bot rescues`

### Swamplord Muselek

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/coilfang_reservoir/underbog/boss_swamplord_muselek.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/coilfang_reservoir/underbog/boss_swamplord_muselek.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Ingvar the Plunderer

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/utgarde_keep/utgarde_keep/boss_ingvar.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Illidan

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/black_temple/boss_illidan.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/black_temple/boss_illidan.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Reliquary Of Souls

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/black_temple/boss_reliquary_of_souls.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/black_temple/boss_reliquary_of_souls.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Shade Of Akama

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/black_temple/boss_shade_of_akama.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/black_temple/boss_shade_of_akama.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Chromaggus

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/blackwing_lair/boss_chromaggus.cpp`
  Commits: `149bd4ef0 Repair encounter transitions and pin the updated Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/blackwing_lair/boss_chromaggus.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/blackwing_lair/boss_chromaggus.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Gruul

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/gruuls_lair/boss_gruul.cpp`
  Commits: `ecea10ca9 Repair encounter lifecycles and pin reviewed bot responses`; `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/gruuls_lair/boss_gruul.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`; `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Lady Deathwhisper

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/icecrown_citadel/icecrown_citadel/boss_lady_deathwhisper.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Lord Marrowgar

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/icecrown_citadel/icecrown_citadel/boss_lord_marrowgar.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Sindragosa

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/icecrown_citadel/icecrown_citadel/boss_sindragosa.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`; `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### The Lich King

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/icecrown_citadel/icecrown_citadel/boss_the_lich_king.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Netherspite

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_netherspite.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_netherspite.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Prince Malchezaar

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_prince_malchezaar.cpp`
  Commits: `1596745d9 Fix encounter selection and phase initialization; pin tested bot rescues`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_prince_malchezaar.cpp`
  Commits: `abe73e2d99 Fix encounter selection and phase initialization; pin tested bot rescues`

### Shade Of Aran

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_shade_of_aran.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`; `1596745d9 Fix encounter selection and phase initialization; pin tested bot rescues`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_shade_of_aran.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`; `abe73e2d99 Fix encounter selection and phase initialization; pin tested bot rescues`

### Terestian Illhoof

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_terestian_illhoof.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/karazhan/boss_terestian_illhoof.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Magtheridon

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/magtheridons_lair/boss_magtheridon.cpp`
  Commits: `ba21a8b06 Restore native Magtheridon cube user ownership and channel admission`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/hellfire_citadel/magtheridons_lair/boss_magtheridon.cpp`
  Commits: `04a40439e0 Restore native Magtheridon cube user ownership and channel admission`

### Majordomo Executus

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core/boss_majordomo_executus.cpp`
  Commits: `149bd4ef0 Repair encounter transitions and pin the updated Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core/boss_majordomo_executus.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core/boss_majordomo_executus.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Ragnaros

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core/boss_ragnaros.cpp`
  Commits: `149bd4ef0 Repair encounter transitions and pin the updated Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core/boss_ragnaros.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core/boss_ragnaros.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Gothik the Harvester

- wotlk: `Updates/5875_mantech_encounter_spell_lists.sql`
  Commits: `46494bc7 Restore encounter spell lists and required spell bindings`

### Maexxna

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/naxxramas/boss_maexxna.cpp`
  Commits: `fa278904f Fix depleted raid Web Wrap selection and pin rescue behavior`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/naxxramas/boss_maexxna.cpp`
  Commits: `ca2197bf1 Fix depleted raid Web Wrap selection and pin rescue behavior`
- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/naxxramas/boss_maexxna.cpp`
  Commits: `e40c7e59f5 Fix depleted raid Web Wrap selection and pin rescue behavior`

### Thaddius

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/naxxramas/boss_thaddius.cpp`
  Commits: `24839af7b Repair encounter lifecycles and pin reviewed bot responses`; `4e8a2a723 Correct native Thaddius lifecycle and update tested support spells`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/naxxramas/boss_thaddius.cpp`
  Commits: `ecea10ca9 Repair encounter lifecycles and pin reviewed bot responses`; `d6819f05a Correct native Thaddius lifecycle and update tested support spells`
- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/naxxramas/boss_thaddius.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`; `c83b405b30 Integrate native cast signature and guard Wrath charge caster lifetime`; `14cae75753 Correct native Thaddius lifecycle and update tested support spells`

### Halion

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ruby_sanctum/boss_halion.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Ayamiss the Hunter

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/ruins_of_ahnqiraj/boss_ayamiss.cpp`
  Commits: `a6ac50f5d Integrate recent encounter fixes and pin the Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/ruins_of_ahnqiraj/boss_ayamiss.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/ruins_of_ahnqiraj/boss_ayamiss.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Ossirian the Unscarred

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/ruins_of_ahnqiraj/boss_ossirian.cpp`
  Commits: `a6ac50f5d Integrate recent encounter fixes and pin the Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/ruins_of_ahnqiraj/boss_ossirian.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/ruins_of_ahnqiraj/boss_ossirian.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Lady Vashj

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/coilfang_reservoir/serpent_shrine/boss_lady_vashj.cpp`
  Commits: `1596745d9 Fix encounter selection and phase initialization; pin tested bot rescues`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/coilfang_reservoir/serpent_shrine/boss_lady_vashj.cpp`
  Commits: `abe73e2d99 Fix encounter selection and phase initialization; pin tested bot rescues`

### Felmyst

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/sunwell_plateau/boss_felmyst.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/sunwell_plateau/boss_felmyst.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Kiljaeden

- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/sunwell_plateau/boss_kiljaeden.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/sunwell_plateau/boss_kiljaeden.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Battleguard Sartura

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_sartura.cpp`
  Commits: `a6ac50f5d Integrate recent encounter fixes and pin the Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_sartura.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_sartura.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Bug Trio (Kri, Vem and Yauj)

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_bug_trio.cpp`
  Commits: `a6ac50f5d Integrate recent encounter fixes and pin the Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_bug_trio.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_bug_trio.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### C’Thun

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_cthun.cpp`
  Commits: `a6ac50f5d Integrate recent encounter fixes and pin the Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_cthun.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_cthun.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Ouro

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_ouro.cpp`
  Commits: `149bd4ef0 Repair encounter transitions and pin the updated Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_ouro.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_ouro.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### The Prophet Skeram

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_skeram.cpp`
  Commits: `149bd4ef0 Repair encounter transitions and pin the updated Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_skeram.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_skeram.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Viscidus

- classic: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_viscidus.cpp`
  Commits: `a6ac50f5d Integrate recent encounter fixes and pin the Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_viscidus.cpp`
  Commits: `38b5cc92f Integrate recent encounter fixes and pin the Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/kalimdor/temple_of_ahnqiraj/boss_viscidus.cpp`
  Commits: `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### High Astromancer Solarian

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/the_eye/boss_astromancer.cpp`
  Commits: `ce9c750c0 Guard native Solarian split state and pin TK bot handling`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/the_eye/boss_astromancer.cpp`
  Commits: `10540878e3 Guard native Solarian split state and pin TK bot handling`

### Kael’thas — Tempest Keep

- tbc: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/the_eye/boss_kaelthas.cpp`
  Commits: `ecea10ca9 Repair encounter lifecycles and pin reviewed bot responses`; `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/outland/tempest_keep/the_eye/boss_kaelthas.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`; `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Assembly of Iron

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/ulduar/assembly_of_iron.cpp`
  Commits: `abe73e2d99 Fix encounter selection and phase initialization; pin tested bot rescues`

### Auriaya

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/ulduar/boss_auriaya.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Freya

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/ulduar/boss_freya.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`; `5c0fbeb277 Integrate recent encounter fixes and pin the Playerbots baseline`

### Kologarn

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/ulduar/boss_kologarn.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Thorim

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/ulduar/boss_thorim.cpp`
  Commits: `a7c53fc9cf Guard empty encounter target lists and stale helper references`

### Yogg-Saron (including keeper support)

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/ulduar/ulduar/boss_yogg_saron.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### Emalon

- wotlk: `src/game/AI/ScriptDevAI/scripts/northrend/vault_of_archavon/boss_emalon.cpp`
  Commits: `a56cb6bf7d Repair encounter lifecycles and pin reviewed bot responses`

### High Priest Thekal

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/zulgurub/boss_thekal.cpp`
  Commits: `149bd4ef0 Repair encounter transitions and pin the updated Playerbots baseline`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/zulgurub/boss_thekal.cpp`
  Commits: `805480376 Repair encounter transitions and pin the updated Playerbots baseline`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/zulgurub/boss_thekal.cpp`
  Commits: `c184dee81f Repair encounter transitions and pin the updated Playerbots baseline`

### Renataki

- classic: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/zulgurub/boss_renataki.cpp`
  Commits: `41a3a14a9 Guard empty encounter target lists and stale helper references`
- tbc: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/zulgurub/boss_renataki.cpp`
  Commits: `ff75862d2 Guard empty encounter target lists and stale helper references`
- wotlk: `src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/zulgurub/boss_renataki.cpp`
  Commits: `a7c53fc9cf Guard empty encounter target lists and stale helper references`

### High Priestess Arlokk

- classic: `sql/scriptdev2/spell.sql`
  Commits: `24839af7bdaa71c716f755f5888107a7b9cdb609`
- tbc: `sql/scriptdev2/spell.sql`
  Commits: `ecea10ca95df777c067a49aefb4b1272b14b420f`
- wotlk: `sql/scriptdev2/spell.sql`
  Commits: `a56cb6bf7d2e7b72fe4df18c799e5fbfe44ac9ed`
