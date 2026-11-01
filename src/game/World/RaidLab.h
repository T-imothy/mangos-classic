#pragma once
#ifdef MANTECH_RAID_LAB
#include "Common.h"
#include <string>
class Map;
class Unit;
class Player;
namespace RaidLab {
bool Enabled();
bool AllowedMap(uint32 map);
bool Begin(Player* leader, uint32 boss, std::string const& scenario, bool controlled);
bool PrepareLeader(Player* leader);
void End(Map* map, std::string const& result);
void EndLeader(uint64 leader, std::string const& result);
void StopAll();
void Event(Unit* unit, char const* event, uint64 value = 0, uint64 other = 0);
void Instance(Map* map, uint32 type, uint32 value);
void Count(Unit* unit, char const* action, uint32 id, uint32 result = 0, uint64 target = 0);
void Impact(Unit* source, Unit* target, char const* kind, uint32 spell, uint32 amount, uint32 healthBefore, int32 effective);
void PreparationCombat(Unit* unit, Unit* enemy);
void BodyPull(Unit* enemy, Unit* target, float radius);
void Snapshot(Map* map);
void RouteRejected(Unit* unit, float ax,float ay,float az,float bx,float by,float bz,float hx,float hy,float hz,float radius);
void DestinationRejected(Unit* unit, uint32 reason, float x,float y,float z,float originalZ,uint32 pathSize=0,float endX=0,float endY=0,float endZ=0);
void Cast(Unit* caster, uint32 spell, uint64 target, char const* stage, bool ok = true);
void CancelStack(Unit* caster, uint32 spell, uint64 target, uint32 elapsed);
bool Controlled(Player* player);
bool BossDied(Map* map, uint64 guid);
bool BossResetObserved(Map* map, uint64 guid);
bool BindNativeBoss(Unit* boss);
}
#define RAID_LAB_PHASE(unit, field, value) do { (field) = (value); RaidLab::Event((unit), "phase:" #field, uint64(field)); } while (false)
#else
#define RAID_LAB_PHASE(unit, field, value) do { (field) = (value); } while (false)
#endif
