"""Compile actual Classic instance lifecycle methods against native-contract doubles."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile


root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
scripts = root / 'src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/blackwing_lair'
source = (scripts / 'blackwing_lair.cpp').read_text()
header = (scripts / 'blackwing_lair.h').read_text()


def block(text, marker):
    start = text.index(marker)
    opening = text.index('{', start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == '{') - (text[end] == '}')
        if not depth:
            return text[start:end + 1]
    raise AssertionError(f'Unclosed source block: {marker}')


methods = '\n'.join(block(source, marker) for marker in (
    'instance_blackwing_lair::instance_blackwing_lair(',
    'void instance_blackwing_lair::Initialize(',
    'bool instance_blackwing_lair::IsEncounterInProgress(',
    'uint32 instance_blackwing_lair::GetData(',
    'void instance_blackwing_lair::SetData(',
    'bool instance_blackwing_lair::HasActiveRazorgoreHuman(',
    'bool instance_blackwing_lair::UpdateRazorgoreAbandonment(',
    'void instance_blackwing_lair::Update(',
    'void instance_blackwing_lair::OnCreatureCreate(',
    'void instance_blackwing_lair::OnCreatureEnterCombat(',
    'void instance_blackwing_lair::OnCreatureDeath(',
    'void instance_blackwing_lair::SetData64(',
))
native_header = header[header.index('enum\n'):header.rindex('#endif')]
native_header = native_header.replace(' override', '').replace('protected:', 'public:')
states = block((root / 'src/game/AI/ScriptDevAI/include/sc_instance.h').read_text(), 'enum') + ';'

code = r'''
#include <algorithm>
#include <cassert>
#include <cstdarg>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <list>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <vector>
using uint8 = uint8_t; using uint32 = uint32_t; using uint64 = uint64_t;
using ObjectGuid = unsigned; using GuidList = std::list<ObjectGuid>; using GuidVector = std::vector<ObjectGuid>;
constexpr uint32 IN_MILLISECONDS = 1000, MINUTE = 60, HOUR = 3600;
enum { WORLD_SESSION_STATE_READY = 2, WORLD_SESSION_STATE_OFFLINE = 3,
       GO_FLAG_NO_INTERACT = 16, TRIGGERED_NONE = 0, TRIGGERED_OLD_TRIGGERED = 1, TEMPSPAWN_DEAD_DESPAWN = 2, AI_EVENT_CUSTOM_A=9 };
__STATES__
struct Position { double x, y, z, o; };
struct WorldObject {};
struct Player; struct Map;
struct WorldSession {
    Player* player = nullptr; uint32 state = WORLD_SESSION_STATE_READY; bool logout = false, socket = true;
    Player* GetPlayer() const { return player; }
    uint32 GetState() const { return state; }
    bool PlayerLogout() const { return logout; }
#if defined(BUILD_DEPRECATED_PLAYERBOT) || defined(ENABLE_PLAYERBOTS)
    bool HasClientSocket() const { return socket; }
#endif
};
struct Player {
    Map* map = nullptr; WorldSession* session = nullptr;
    bool inWorld = true, alive = true, gm = false, transferring = false, feared = false, controlling = false;
    bool IsInWorld() const { return inWorld; } bool IsAlive() const { return alive; }
    bool IsGameMaster() const { return gm; } bool IsBeingTeleported() const { return transferring; }
    Map* GetMap() const { return map; } WorldSession* GetSession() const { return session; }
};
struct CreatureAI {
    unsigned evades = 0;
    void EnterEvadeMode() { ++evades; }
    void SetCombatScriptStatus(bool) {}
    void SendAIEvent(unsigned, void*, void*) {}
};
struct Creature {
    unsigned entry=0,guid=0,casts=0,interrupts=0; bool temporary=false;
    unsigned GetEntry(){return entry;} unsigned GetObjectGuid(){return guid;}
    bool IsTemporarySummon(){return temporary;} void InterruptNonMeleeSpells(bool){++interrupts;}
    bool alive = true, despawned = false, possessed = true;
    unsigned releases = 0, resetCasts = 0, despawns = 0, respawns = 0;
    CreatureAI ai;
    bool IsAlive() const { return alive; } bool IsDespawned() const { return despawned; }
    CreatureAI* AI() { return &ai; }
    void RemoveAurasDueToSpell(uint32 spell) { assert(spell == 19832); possessed = false; ++releases; }
    void CastSpell(void*, uint32 spell, uint32) {
        ++casts;
        if (spell == 23024) { assert(!possessed); ++resetCasts; }
    }
    void ForcedDespawn(uint32 = 0) { ++despawns; despawned = true; alive = false; }
    void Respawn() { ++respawns; alive = true; despawned = false; }
    void SummonCreature(uint32, double, double, double, double, uint32, uint32, bool) {}
};
struct GameObject {
    bool spawned = false; unsigned respawns = 0;
    bool IsSpawned() const { return spawned; }
    void Respawn() { spawned = true; ++respawns; }
};
struct PlayerRef { Player* player; Player* getSource() const { return player; } };
struct Map {
    std::vector<PlayerRef> players; std::map<unsigned, Creature*> creatures; std::map<unsigned, GameObject*> objects;
    uint32 GetInstanceId() const { return 42; }
    const auto& GetPlayers() const { return players; }
    Creature* GetCreature(unsigned id) { return creatures.count(id) ? creatures[id] : nullptr; }
    GameObject* GetGameObject(unsigned id) { return objects.count(id) ? objects[id] : nullptr; }
};
struct ScriptedInstance {
    std::map<unsigned,unsigned> m_npcEntryGuidStore;
    Map* instance; unsigned saves = 0; std::map<unsigned, unsigned> doorUses; bool orbDisabled = false;
    explicit ScriptedInstance(Map* map) : instance(map) {}
    Creature* GetSingleCreatureFromStorage(unsigned id) const { return instance->GetCreature(id); }
    void DoUseDoorOrButton(unsigned id) { ++doorUses[id]; }
    void DoToggleGameObjectFlags(unsigned, unsigned, bool value) { orbDisabled = value; }
    void DoOrSimulateScriptTextForThisInstance(int, unsigned) {}
    void SaveToDB() { ++saves; }
};
void DoScriptText(int, Creature*) {}
unsigned urand(unsigned low, unsigned) { return low; }
std::mt19937* GetRandomGenerator() { static std::mt19937 rng(7); return &rng; }
struct Log {
    std::vector<std::string> lines;
    void outString(const char* format, ...) {
        char line[256]; va_list args; va_start(args, format);
        vsnprintf(line, sizeof(line), format, args); va_end(args); lines.emplace_back(line);
    }
} sLog;
#define OUT_SAVE_INST_DATA ((void)0)
#define OUT_SAVE_INST_DATA_COMPLETE ((void)0)
__HEADER__
void instance_blackwing_lair::CleanupNefarianStage(bool) {}
__METHODS__

struct Fixture {
    Map map, otherMap;
    WorldSession session, secondSession, botSession;
    Player human, second, bot;
    Creature boss, orb, defender;
    GameObject egg;
    instance_blackwing_lair raid;
    Fixture() : raid(&map) {
        sLog.lines.clear();
        human.map = second.map = bot.map = &map;
        human.session = &session; second.session = &secondSession; bot.session = &botSession;
        session.player = &human; secondSession.player = &second; botSession.player = &bot;
        botSession.socket = false;
        map.players = {{&human}, {&bot}};
        // A non-playerbot build has no socketless bot sessions.
#if !defined(BUILD_DEPRECATED_PLAYERBOT) && !defined(ENABLE_PLAYERBOTS)
        map.players = {{&human}};
#endif
        map.creatures[NPC_RAZORGORE] = &boss;
        map.creatures[NPC_BLACKWING_ORB_TRIGGER] = &orb;
        map.creatures[1] = &defender;
        map.objects[2] = &egg;
        raid.m_lDefendersGuids = {1}; raid.m_lDragonEggsGuids = {2}; raid.m_lUsedEggsGuids = {2};
        raid.m_uiBlackwingDefCount = 1; raid.m_uiDragonspawnCount = 1;
        // Native generators may be unloaded; their GUID slots remain valid.
        raid.m_vGeneratorGuids = {100, 101, 102, 103};
    }
    void start(uint32 phase = IN_PROGRESS) { raid.SetData(TYPE_RAZORGORE, IN_PROGRESS); if(phase!=IN_PROGRESS)raid.SetData(TYPE_RAZORGORE, phase); }
    void disconnect() { session.state = WORLD_SESSION_STATE_OFFLINE; session.socket = false; }
    void reconnect() { session.state = WORLD_SESSION_STATE_READY; session.socket = true; }
};

int main() {
    // Human capture is synchronous with encounter start, before any instance tick.
    {
        Fixture f; assert(!f.raid.m_bRazorgoreHumanAttempt); f.human.controlling = true; f.start();
        assert(f.raid.m_bRazorgoreHumanAttempt && f.raid.IsEncounterInProgress());
        f.disconnect(); f.raid.Update(59999);
        assert(f.raid.GetData(TYPE_RAZORGORE) == IN_PROGRESS && f.boss.releases == 0);
        assert(sLog.lines.empty());
        f.raid.Update(1);
        assert(f.raid.GetData(TYPE_RAZORGORE) == FAIL && !f.raid.IsEncounterInProgress());
        assert(f.raid.m_bIsMainGateOpen && f.raid.orbDisabled);
        assert(f.boss.releases == 1 && f.boss.resetCasts == 1 && f.boss.despawns == 1);
        assert(f.orb.ai.evades == 1 && f.defender.despawns == 1);
        assert(f.raid.m_lDefendersGuids.empty() && f.raid.m_lUsedEggsGuids.empty());
        assert(f.raid.m_uiBlackwingDefCount == 0 && f.raid.m_uiDragonspawnCount == 0);
        assert(f.raid.m_uiResetTimer == 30000 && !f.raid.m_bRazorgoreHumanAttempt);
        assert(sLog.lines.size() == 2);
        assert(sLog.lines[0] == "BWL_RAZORGORE_RECOVERY instance=42 phase=1 reason=no_connected_living_human grace_ms=60000");
        f.raid.Update(29999); assert(f.boss.respawns == 0 && f.egg.respawns == 0);
        f.raid.Update(1); assert(f.boss.respawns == 1 && f.egg.respawns == 1);
        f.raid.Update(120000); assert(f.boss.releases == 1 && f.boss.resetCasts == 1);
        assert(sLog.lines.size() == 2);
    }
    // Reconnection, or another real participant, restarts the entire grace.
    {
        Fixture f; f.start(); f.disconnect(); f.raid.Update(59000);
        f.reconnect(); f.raid.Update(1); assert(f.raid.m_uiRazorgoreNoHumanTimer == 0);
        f.disconnect(); f.raid.Update(59000); assert(f.boss.releases == 0);
        f.map.players.push_back({&f.second}); f.raid.Update(1);
        assert(f.raid.m_uiRazorgoreNoHumanTimer == 0);
        f.raid.Update(120000); assert(f.boss.releases == 0);
        f.secondSession.state = WORLD_SESSION_STATE_OFFLINE;
        f.raid.Update(60000); assert(f.boss.releases == 1);
    }
    // Second human already present keeps the attempt alive through controller loss.
    {
        Fixture f; f.map.players.push_back({&f.second}); f.start(); f.disconnect();
        f.raid.Update(600000); assert(f.boss.releases == 0 && f.raid.m_uiRazorgoreNoHumanTimer == 0);
    }
    // Automated-only attempts are unchanged, but a later human visit arms recovery.
    {
        Fixture f; f.map.players.erase(f.map.players.begin()); f.start();
        f.raid.Update(600000); assert(!f.raid.m_bRazorgoreHumanAttempt && f.boss.releases == 0);
        assert(sLog.lines.empty());
        f.map.players.push_back({&f.human}); f.raid.Update(1);
        assert(f.raid.m_bRazorgoreHumanAttempt); f.disconnect(); f.raid.Update(60000);
        assert(f.boss.releases == 1);
    }
    // Changing phases, even repeated SPECIAL, cannot postpone abandonment.
    {
        Fixture f; f.start(); f.disconnect(); f.raid.Update(40000);
        f.raid.SetData(TYPE_RAZORGORE, SPECIAL); f.raid.Update(19000);
        f.raid.SetData(TYPE_RAZORGORE, SPECIAL); f.raid.Update(1000);
        assert(f.raid.GetData(TYPE_RAZORGORE) == FAIL && f.boss.releases == 1);
    }
    {
        Fixture f; f.start(SPECIAL); assert(f.raid.m_bRazorgoreHumanAttempt);
        f.disconnect(); f.raid.Update(60000); assert(f.boss.releases == 1);
    }
    // Terminal or reset states erase the historical-human latch and elapsed time.
    for (uint32 state : {NOT_STARTED, FAIL, DONE}) {
        Fixture f; f.start(); f.disconnect(); f.raid.Update(59000);
        f.boss.possessed = false; // ordinary native FAIL already tears down possession
        f.raid.SetData(TYPE_RAZORGORE, state);
        assert(!f.raid.m_bRazorgoreHumanAttempt && f.raid.m_uiRazorgoreNoHumanTimer == 0);
        f.raid.Update(60000); assert(f.boss.releases == (state==FAIL ? 1u : 0u));
        f.raid.SetData(TYPE_RAZORGORE, IN_PROGRESS); f.raid.Update(60000);
        assert(!f.raid.m_bRazorgoreHumanAttempt && f.boss.releases == (state==FAIL ? 1u : 0u));
    }
    // Invalid/transient session and world states never masquerade as a live human.
    for (unsigned invalid = 0; invalid < 10; ++invalid) {
        Fixture f;
        switch (invalid) {
            case 0: f.human.alive = false; break;
            case 1: f.human.gm = true; break;
            case 2: f.human.transferring = true; break;
            case 3: f.human.inWorld = false; break;
            case 4: f.human.map = &f.otherMap; break;
            case 5: f.human.session = nullptr; break;
            case 6: f.session.player = &f.second; break;
            case 7: f.session.state = WORLD_SESSION_STATE_OFFLINE; break;
            case 8: f.session.logout = true; break;
            case 9: f.session.state = 0; break; // loading session
        }
        f.start(); f.raid.Update(600000);
        assert(!f.raid.HasActiveRazorgoreHuman() && !f.raid.m_bRazorgoreHumanAttempt && f.boss.releases == 0);
    }
#if defined(BUILD_DEPRECATED_PLAYERBOT) || defined(ENABLE_PLAYERBOTS)
    {
        Fixture f; f.session.socket = false; f.start(); f.raid.Update(600000);
        assert(!f.raid.m_bRazorgoreHumanAttempt && f.boss.releases == 0);
    }
#endif
    // Losing all living humans after arming starts the timer; fear/possession do not.
    {
        Fixture f; f.start(); f.human.feared = true; f.human.controlling = true;
        f.raid.Update(120000); assert(f.raid.m_uiRazorgoreNoHumanTimer == 0);
        f.human.alive = false; f.raid.Update(60000); assert(f.boss.releases == 1);
    }
    {
        Fixture f; f.start(); f.human.transferring = true; f.raid.Update(10000);
        f.human.transferring = false; f.raid.Update(1);
        assert(f.raid.m_uiRazorgoreNoHumanTimer == 0 && f.boss.releases == 0);
    }
    // Missing/unloaded boss does not prevent the native state/door cleanup.
    {
        Fixture f; f.start(); f.map.creatures.erase(NPC_RAZORGORE); f.disconnect(); f.raid.Update(60000);
        assert(f.raid.GetData(TYPE_RAZORGORE) == FAIL && f.raid.m_bIsMainGateOpen);
        assert(f.raid.m_uiResetTimer == 30000 && f.defender.despawns == 1);
    }
    // An unrelated active encounter still controls the entrance lock normally.
    {
        Fixture f; f.start(); f.raid.SetData(TYPE_FIREMAW, IN_PROGRESS); f.disconnect(); f.raid.Update(60000);
        assert(f.raid.GetData(TYPE_RAZORGORE) == FAIL && f.raid.IsEncounterInProgress());
        assert(!f.raid.m_bIsMainGateOpen);
    }

    // Real wave startup, cooldown re-entry, late summons, repeated failure and
    // stale eggs cannot leave a reset room with an active wave timer.
    {
        Fixture f; Creature grethok, generator, late;
        grethok.entry=NPC_GRETHOK_CONTROLLER;
        f.raid.m_vGeneratorGuids={100,101,102,103};
        for(unsigned id:{100u,101u,102u,103u})f.map.creatures[id]=&generator;
        f.raid.OnCreatureEnterCombat(&grethok);
        assert(f.raid.m_uiDefenseTimer==40000);
        f.raid.Update(39999);assert(generator.casts==0);
        f.raid.Update(2);assert(generator.casts==4&&f.raid.m_uiDefenseTimer==15000);
        f.raid.Update(15001);assert(generator.casts==8);
        f.raid.SetData(TYPE_RAZORGORE,FAIL);
        assert(generator.interrupts==4&&!f.raid.m_uiDefenseTimer);
        f.raid.Update(1000);f.raid.SetData(TYPE_RAZORGORE,FAIL);
        assert(f.raid.m_uiResetTimer==29000&&f.boss.releases==1);
        f.raid.OnCreatureEnterCombat(&grethok);f.raid.SetData(TYPE_RAZORGORE,IN_PROGRESS);
        assert(f.raid.GetData(TYPE_RAZORGORE)==FAIL&&!f.raid.m_uiDefenseTimer);
        late.temporary=true;late.entry=NPC_BLACKWING_MAGE;late.guid=50;
        f.raid.OnCreatureCreate(&late);assert(late.despawns==1&&f.raid.m_lDefendersGuids.empty());
        f.raid.SetData64(DATA_DRAGON_EGG,2);assert(f.raid.m_lUsedEggsGuids.empty());
        f.raid.Update(29000);f.raid.Update(60000);
        assert(generator.casts==8&&f.egg.respawns==1&&f.boss.respawns==1);
        f.raid.OnCreatureEnterCombat(&grethok);assert(f.raid.m_uiDefenseTimer==40000);
        late.alive=true;late.despawned=false;f.raid.OnCreatureCreate(&late);
        assert(f.raid.m_uiBlackwingDefCount==1&&f.raid.m_uiRazorgoreWaveSpawns==1);
        f.raid.OnCreatureDeath(&late);f.raid.OnCreatureDeath(&late);
        assert(f.raid.m_uiBlackwingDefCount==0&&f.raid.m_uiRazorgoreWaveDeaths==1);
        GameObject otherEgg;f.map.objects[3]=&otherEgg;f.raid.m_lDragonEggsGuids.push_back(3);
        f.raid.SetData64(DATA_DRAGON_EGG,999);assert(f.raid.m_lUsedEggsGuids.empty());
        f.raid.SetData64(DATA_DRAGON_EGG,2);f.raid.SetData64(DATA_DRAGON_EGG,2);
        assert(f.raid.m_lUsedEggsGuids.size()==1&&f.raid.GetData(TYPE_RAZORGORE)==IN_PROGRESS);
        f.raid.SetData64(DATA_DRAGON_EGG,3);
        assert(f.raid.GetData(TYPE_RAZORGORE)==SPECIAL&&!f.raid.m_uiDefenseTimer);
        f.raid.OnCreatureEnterCombat(&grethok);f.raid.SetData(TYPE_RAZORGORE,IN_PROGRESS);
        assert(f.raid.GetData(TYPE_RAZORGORE)==SPECIAL);
        f.raid.SetData(TYPE_RAZORGORE,DONE);f.raid.SetData(TYPE_RAZORGORE,FAIL);
        assert(f.raid.GetData(TYPE_RAZORGORE)==DONE&&!f.raid.m_uiResetTimer);
    }
    std::cout << "PASS: actual Classic Razorgore human/session classification, both phases, 60s grace, native FAIL teardown and 30s reset\n";
}
'''.replace('__HEADER__', native_header).replace('__METHODS__', methods).replace('__STATES__', states)

compiler = os.environ.get('CXX') or ('cl' if shutil.which('cl') else 'c++')
for mode in ('ENABLE_PLAYERBOTS', 'BUILD_DEPRECATED_PLAYERBOT', 'NO_PLAYERBOTS'):
    with tempfile.TemporaryDirectory(prefix='razorgore-abandonment-') as folder:
        directory = Path(folder)
        (directory / 'test.cpp').write_text(code)
        defines = [] if mode == 'NO_PLAYERBOTS' else [mode]
        if Path(compiler).stem.lower() == 'cl':
            command = [compiler, '/nologo', '/std:c++17', '/EHsc', *('/D' + d for d in defines), 'test.cpp', '/Fe:test.exe']
            executable = directory / 'test.exe'
        else:
            command = [compiler, '-std=c++17', *('-D' + d for d in defines), 'test.cpp', '-o', 'test']
            executable = directory / 'test'
        print(mode, flush=True)
        subprocess.run(command, cwd=directory, check=True)
        subprocess.run([str(executable)], cwd=directory, check=True)
