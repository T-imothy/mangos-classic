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
void End(Map* map, std::string const& result);
void EndLeader(uint64 leader, std::string const& result);
void StopAll();
void Event(Unit* unit, char const* event, uint64 value = 0, uint64 other = 0);
void Instance(Map* map, uint32 type, uint32 value);
void Count(Unit* unit, char const* action, uint32 id, uint32 result = 0, uint64 target = 0);
void Impact(Unit* source, Unit* target, char const* kind, uint32 spell, uint32 amount, uint32 healthBefore, int32 effective);
void Snapshot(Map* map);
void Cast(Unit* caster, uint32 spell, uint64 target, char const* stage, bool ok = true);
bool Controlled(Player* player);
bool BossDied(Map* map, uint64 guid);
}
#define RAID_LAB_PHASE(unit, field, value) do { (field) = (value); RaidLab::Event((unit), "phase:" #field, uint64(field)); } while (false)
#else
#define RAID_LAB_PHASE(unit, field, value) do { (field) = (value); } while (false)
#endif
