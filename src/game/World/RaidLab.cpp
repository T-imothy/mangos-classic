#include "RaidLab.h"
#ifdef MANTECH_RAID_LAB
#include "Config/Config.h"
#include "Maps/Map.h"
#include "Maps/InstanceData.h"
#include "Entities/Player.h"
#include "Groups/Group.h"
#include "Log/Log.h"
#include "Entities/Item.h"
#include "Entities/Creature.h"
#include "Entities/GameObject.h"
#include "Entities/DynamicObject.h"
#include "Grids/GridNotifiers.h"
#include "Grids/GridNotifiersImpl.h"
#include "Grids/CellImpl.h"
#include <set>
#include "Spells/Spell.h"
#include "Movement/MoveSpline.h"
#include "MotionGenerators/MotionMaster.h"
#include "Spells/SpellAuras.h"
#include "playerbot/PlayerbotAI.h"
#include "playerbot/AiFactory.h"
#include "playerbot/strategy/AiObjectContext.h"
#include <fstream>
#include <map>
#include <memory>
#include <mutex>
#include <sstream>
#ifdef _WIN32
#include <windows.h>
#endif
#include <chrono>
#include <tuple>
namespace RaidLab {
namespace {
std::recursive_mutex guard;
std::map<uint64,std::pair<uint32,uint32>> preparedLeaders;
std::map<uint64,uint32> preparationImpacts;
std::map<uint64,uint32> preparationCombats;
uint64 Clock() { return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
std::string Quote(std::string const& text) { std::ostringstream o; o << '"'; for(unsigned char c:text) { if(c=='"'||c=='\\')o << '\\' << c; else if(c>=32)o << c; else o << ' '; } o << '"'; return o.str(); }
using CountKey = std::tuple<uint64,uint32,std::string,uint32,uint32,uint64>;
struct CountBucket { uint64 first=0,last=0,count=0; };
struct Attempt { std::set<std::pair<uint32,uint32>> cancelStacks; uint32 cancelStackSamples=0,combatTransitions=0,combatTransitionLimit=512; std::set<uint64> profiles; std::map<uint64,uint64> lastRouteRejection; std::map<CountKey,CountBucket> counts; std::ofstream file; uint64 start=0,last=0,leader=0,seq=0,bytes=0,traceLimitBytes=256ull*1024*1024; uint32 boss=0; uint64 target=0,bossEvadeAt=0,bossResetAt=0; bool bossDied=false,controlled=false,limited=false; std::string id; };
void SetObservationBudget(Attempt& a,std::string const& name) {
 const std::string suffix="_leader_progression";
 if(a.controlled && name.find("raidlab_")==0 && name.size()>=suffix.size() &&
    name.compare(name.size()-suffix.size(),suffix.size(),suffix)==0) {
  // Forty actors repeatedly entering combat on a full native trash route
  // exhausted the single-boss budget before reaching the boss.
  a.combatTransitionLimit=4096;a.traceLimitBytes=512ull*1024*1024;
 }
}
void ObserveBossReset(Attempt& a,uint64 guid,std::string const& event,uint64 value,uint64 other,uint64 now) {
 if(!guid || guid!=a.target || a.bossDied)return;
 if(event=="evade_state" && value && !other)a.bossEvadeAt=now;
 // A phase may legitimately call Reset. Require the bound actor's native
 // evade transition immediately before its script reset, never an add's reset.
 if(event=="script:Reset" && a.bossEvadeAt && now>=a.bossEvadeAt && now-a.bossEvadeAt<=1000)
  if(!a.bossResetAt)a.bossResetAt=now;
}
std::map<std::pair<uint32,uint32>,std::unique_ptr<Attempt>> attempts;
Attempt* Find(Map* map) { if(!map)return nullptr; auto i=attempts.find({map->GetId(),map->GetInstanceId()}); return i==attempts.end()?nullptr:i->second.get(); }
void Write(Attempt& a, std::string const& fields) {
 if(a.limited)return;
 std::ostringstream s; s << "{\"attempt\":" << Quote(a.id) << ",\"seq\":" << ++a.seq << ",\"ms\":" << Clock()-a.start << ',' << fields << "}\n";
 std::string row=s.str(); a.bytes+=row.size();
 if(a.bytes>a.traceLimitBytes) {a.file << "{\"type\":\"truncated\",\"reason\":\"" << a.traceLimitBytes/(1024*1024) << "MiB_limit\"}\n";a.file.flush();a.limited=true;return;}
 a.file << row;
}
bool RecordCombatTransition(Attempt& a) {
 if(a.combatTransitions>=a.combatTransitionLimit) {
  if(a.combatTransitions==a.combatTransitionLimit) {
   ++a.combatTransitions;
   Write(a,"\"type\":\"coverage_gap\",\"reason\":\"combat_transition_limit\"");
  }
  return false;
 }
 ++a.combatTransitions;return true;
}
void FlushCounts(Attempt& a) {
 for(auto const& item:a.counts) {
  auto const& k=item.first;auto const& b=item.second;
  Write(a,"\"type\":\"ai_attempts\",\"guid\":"+std::to_string(std::get<0>(k))+",\"entry\":"+std::to_string(std::get<1>(k))+",\"action\":"+Quote(std::get<2>(k))+",\"id\":"+std::to_string(std::get<3>(k))+",\"result\":"+std::to_string(std::get<4>(k))+",\"target\":"+std::to_string(std::get<5>(k))+",\"count\":"+std::to_string(b.count)+",\"first_ms\":"+std::to_string(b.first)+",\"last_ms\":"+std::to_string(b.last));
 }
 a.counts.clear();
}
void State(Attempt& a, Unit* u) {
 std::ostringstream s; s << "\"type\":\"unit\",\"guid\":" << u->GetObjectGuid().GetRawValue() << ",\"entry\":" << u->GetEntry() << ",\"player\":" << (u->GetTypeId()==TYPEID_PLAYER) << ",\"alive\":" << u->IsAlive() << ",\"combat\":" << u->IsInCombat() << ",\"evade\":" << u->GetCombatManager().IsInEvadeMode() << ",\"hp\":" << u->GetHealth() << ",\"max_hp\":" << u->GetMaxHealth() << ",\"x\":" << u->GetPositionX() << ",\"y\":" << u->GetPositionY() << ",\"z\":" << u->GetPositionZ() << ",\"o\":" << u->GetOrientation() << ",\"moving\":" << u->IsMoving() << ",\"flags\":" << u->GetUInt32Value(UNIT_FIELD_FLAGS) << ",\"victim\":" << (u->GetVictim()?u->GetVictim()->GetObjectGuid().GetRawValue():0) << ",\"class\":" << uint32(u->getClass()) << ",\"power_type\":" << uint32(u->GetPowerType()) << ",\"power\":" << u->GetPower(u->GetPowerType()) << ",\"max_power\":" << u->GetMaxPower(u->GetPowerType()) << ",\"auras\":[";
 bool first=true; for(auto const& aura:u->GetSpellAuraHolderMap()) {if(!first)s<<',';first=false;s<<'['<<aura.first<<','<<aura.second->GetStackAmount()<<']';}s<<']';
 s << ",\"created_by_spell\":" << u->GetUInt32Value(UNIT_CREATED_BY_SPELL) << ",\"spawner\":" << u->GetSpawnerGuid().GetRawValue();
 s << ",\"native_state\":"; uint32 stateMask=0; for(unsigned bit=0;bit<32;++bit) if(u->hasUnitState(uint32(1)<<bit)) stateMask|=uint32(1)<<bit; s << stateMask;
 if(u->movespline) {
  const auto dest=u->movespline->FinalDestination();const auto next=u->movespline->CurrentDestination();
  s << ",\"spline_done\":" << u->movespline->Finalized() << ",\"spline_end\":[" << dest.x << ',' << dest.y << ',' << dest.z << "]" << ",\"spline_next\":[" << next.x << ',' << next.y << ',' << next.z << "]" << ",\"motion\":" << u->GetMotionMaster()->GetCurrentMovementGeneratorType();
 }
 if(u->GetTypeId()==TYPEID_PLAYER) {
  auto player=static_cast<Player*>(u);auto ai=player->GetPlayerbotAI();
  if(ai && a.profiles.insert(player->GetObjectGuid().GetRawValue()).second) {
   std::ostringstream profile;
   profile << "\"type\":\"profile\",\"guid\":" << player->GetObjectGuid().GetRawValue()
       << ",\"spec_tab\":" << AiFactory::GetPlayerSpecTab(player)
       << ",\"talent_role\":" << unsigned(AiFactory::GetPlayerRoles(player)) << ",\"combat_strategies\":[";
   bool firstStrategy=true;
   for(auto strategy:ai->GetStrategies(BotState::BOT_STATE_COMBAT)) {
    if(!firstStrategy) profile << ',';firstStrategy=false;profile << Quote(std::string(strategy));
   }
   profile << ']' << ",\"level\":" << player->GetLevel()
       << ",\"armor\":" << player->GetArmor()
       << ",\"mainhand_skill\":" << player->GetWeaponSkillValue(BASE_ATTACK)
       << ",\"mainhand_attack_ms\":" << player->GetAttackTime(BASE_ATTACK)
       << ",\"melee_min\":" << player->GetFloatValue(UNIT_FIELD_MINDAMAGE)
       << ",\"melee_max\":" << player->GetFloatValue(UNIT_FIELD_MAXDAMAGE)
       << ",\"attack_power\":" << player->GetTotalAttackPowerValue(BASE_ATTACK)
       << ",\"resistances\":[";
   for(unsigned school=0;school<MAX_SPELL_SCHOOL;++school) {
    if(school)profile<<',';
    profile<<player->GetResistance(SpellSchools(school));
   }
   profile << ']'
       << ",\"owns_onyxia_cloak\":" << (player->GetItemByEntry(15138)!=nullptr)
       << ",\"equipment\":[";
   for(uint8 slot=EQUIPMENT_SLOT_START;slot<EQUIPMENT_SLOT_END;++slot) {
    if(slot!=EQUIPMENT_SLOT_START)profile<<',';
    const Item* item=player->GetItemByPos(INVENTORY_SLOT_BAG_0,slot);
    profile<<(item?item->GetEntry():0);
   }
   profile << "]";Write(a,profile.str());
  }
  s << ",\"selection\":" << player->GetSelectionGuid().GetRawValue();
  if(ai) s << ",\"action\":" << Quote(ai->GetLastExecutedActionName(ai->GetState())) << ",\"decision\":" << Quote(ai->GetLastActionDecision(ai->GetState())) << ",\"tank\":" << ai->IsTank(player) << ",\"healer\":" << ai->IsHeal(player) << ",\"ranged\":" << ai->IsRanged(player)
      << ",\"current_target\":" << ai->GetAiObjectContext()->GetValue<ObjectGuid>("current target")->Get().GetRawValue();
 }
 Write(a,s.str());
}
}
bool AllowedMap(uint32 id) {return id==409||id==249||id==469||id==533||id==309||id==509||id==531;}
bool Enabled() {
 static bool const allowed=[] { if(!sConfig.GetBoolDefault("RaidLab.Enabled",false)||sConfig.GetStringDefault("BindIP")!="127.0.0.1")return false; for(auto key:{"WorldDatabaseInfo","CharacterDatabaseInfo","LoginDatabaseInfo","LogsDatabaseInfo"}) {auto v=sConfig.GetStringDefault(key);if(v.find("127.0.0.1;13307;")!=0||v.find(";bg_lab_")==std::string::npos)return false;} return true;}();return allowed;
}
bool Begin(Player* leader,uint32 boss,std::string const& name,bool controlled) {
 if(!Enabled()||!leader||!leader->IsInWorld()||!AllowedMap(leader->GetMapId()))return false;
 std::lock_guard<std::recursive_mutex> lock(guard); auto key=std::make_pair(leader->GetMapId(),leader->GetInstanceId());if(attempts.count(key))return false;
 auto a=std::make_unique<Attempt>();a->start=Clock();a->leader=leader->GetObjectGuid().GetRawValue();a->boss=boss;a->controlled=controlled;a->target=leader->GetSelectionGuid().GetRawValue();
 SetObservationBudget(*a,name);
 a->id=std::to_string(a->start)+"-"+std::to_string(key.first)+"-"+std::to_string(key.second);
 a->file.open(sConfig.GetStringDefault("LogsDir")+"/raid-"+a->id+".jsonl");if(!a->file)return false;
 Write(*a,"\"type\":\"begin\",\"map\":"+std::to_string(key.first)+",\"instance\":"+std::to_string(key.second)+",\"boss\":"+std::to_string(boss)+",\"leader\":"+std::to_string(a->leader)+",\"controlled\":"+(controlled?"true":"false")+",\"scenario\":"+Quote(name));a->file.flush();attempts[key]=std::move(a);return true;
}
bool PrepareLeader(Player* leader) {
 if(!Enabled() || !leader || !leader->IsInWorld() || leader->IsBeingTeleported() || !AllowedMap(leader->GetMapId()))return false;
 std::lock_guard<std::recursive_mutex> lock(guard);
 preparedLeaders[leader->GetObjectGuid().GetRawValue()]={leader->GetMapId(),leader->GetInstanceId()};return true;
}
void End(Map* map,std::string const& result) {std::lock_guard<std::recursive_mutex> lock(guard);if(auto a=Find(map)){FlushCounts(*a);Write(*a,"\"type\":\"end\",\"result\":"+Quote(result));a->file.flush();attempts.erase({map->GetId(),map->GetInstanceId()});}}
void EndLeader(uint64 leader, std::string const& result) {
 std::lock_guard<std::recursive_mutex> lock(guard);
 preparedLeaders.erase(leader);
 preparationImpacts.erase(leader);
 preparationCombats.erase(leader);
 for(auto i=attempts.begin();i!=attempts.end();) {
  if(i->second->leader!=leader){++i;continue;}
  FlushCounts(*i->second);Write(*i->second,"\"type\":\"end\",\"result\":"+Quote(result));i=attempts.erase(i);
 }
}
void StopAll() {
 std::lock_guard<std::recursive_mutex> lock(guard);
 for(auto& entry:attempts) {FlushCounts(*entry.second);Write(*entry.second,"\"type\":\"end\",\"result\":\"ABORT: local server shutdown\"");}
 attempts.clear();
 preparedLeaders.clear();
 preparationImpacts.clear();
 preparationCombats.clear();
}
void BodyPull(Unit* enemy,Unit* target,float radius) {
 if(!Enabled() || !enemy || !target || !enemy->IsInWorld() || !target->IsInWorld() ||
    !enemy->IsInMap(target) || !std::isfinite(radius))return;
 std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(enemy->GetMap());if(!a)return;
 // Only the native initial acquisition calls this, never every combat tick.
 std::ostringstream s;s<<"\"type\":\"native_body_pull_detail\",\"enemy\":"<<enemy->GetObjectGuid().GetRawValue()
  <<",\"entry\":"<<enemy->GetEntry()<<",\"target\":"<<target->GetObjectGuid().GetRawValue()<<",\"radius\":"<<radius
  <<",\"enemy_position\":["<<enemy->GetPositionX()<<','<<enemy->GetPositionY()<<','<<enemy->GetPositionZ()
  <<"],\"target_position\":["<<target->GetPositionX()<<','<<target->GetPositionY()<<','<<target->GetPositionZ()<<']';Write(*a,s.str());
 State(*a,enemy);State(*a,target);
}
bool ObserveIdleRaidActor(uint32 map,uint32 boss,uint32 entry) {
 // Only relevant already-loaded patrols or the two add platforms.
 // No new grid loads, planner execution, or changes to native actor state.
 return (map==469 && (boss==11981 || boss==11983 || boss==14601) &&
         (entry==11981 || entry==11983 || entry==14601)) ||
        (map==533 && boss==15928 && (entry==15929 || entry==15930)) ||
        (map==409 && boss==12018 && entry==12101);
}
void RouteRejected(Unit* u,float ax,float ay,float az,float bx,float by,float bz,float hx,float hy,float hz,float radius) {
 if(!u||!u->IsInWorld())return;std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(u->GetMap());if(!a)return;
 const uint64 guid=u->GetObjectGuid().GetRawValue(), now=Clock();auto& last=a->lastRouteRejection[guid];if(last && now-last<1000)return;last=now;
 std::ostringstream s;s << "\"type\":\"route_rejected\",\"guid\":" << guid << ",\"from\":[" << ax << ',' << ay << ',' << az << "],\"to\":[" << bx << ',' << by << ',' << bz << "],\"hazard\":[" << hx << ',' << hy << ',' << hz << "],\"radius\":" << radius;Write(*a,s.str());
}
void DestinationRejected(Unit* u,uint32 reason,float x,float y,float z,float originalZ,uint32 pathSize,float endX,float endY,float endZ) {
 if(!Enabled()||!u||!u->IsInWorld())return;
 std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(u->GetMap());if(!a)return;
 // Share the per-actor geometry diagnostic budget: at most one detailed
 // rejected-route or destination record per second, within the attempt cap.
 const uint64 guid=u->GetObjectGuid().GetRawValue(),now=Clock();auto& last=a->lastRouteRejection[guid];if(last&&now-last<1000)return;last=now;
 float nearby=originalZ;const bool found=std::isfinite(x)&&std::isfinite(y)&&std::isfinite(originalZ)&&u->GetMap()->GetHeightInRange(x,y,nearby,8.0f);
 auto finite=[](float v){return std::isfinite(v)?v:0.0f;};
 std::ostringstream s;s << "\"type\":\"destination_rejected\",\"guid\":" << guid << ",\"reason\":" << reason
  << ",\"from\":[" << u->GetPositionX() << ',' << u->GetPositionY() << ',' << u->GetPositionZ()
  << "],\"to\":[" << finite(x) << ',' << finite(y) << ',' << finite(z) << "],\"original_z\":" << finite(originalZ)
  << ",\"adjusted_z_finite\":" << (std::isfinite(z)?"true":"false") << ",\"nearby_floor_found\":" << (found?"true":"false")
  << ",\"nearby_floor\":" << finite(nearby) << ",\"path_size\":" << pathSize << ",\"path_end\":[" << finite(endX) << ',' << finite(endY) << ',' << finite(endZ) << ']';Write(*a,s.str());
}
void Event(Unit* u, char const* event, uint64 value, uint64 other) {
 if(!Enabled()||!u||!u->IsInWorld()||!AllowedMap(u->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(u->GetMap())) {
 ObserveBossReset(*a,u->GetObjectGuid().GetRawValue(),event,value,other,Clock());
 if(u->GetObjectGuid().GetRawValue()==a->target && std::string(event)=="death_state" && value==JUST_DIED) a->bossDied=true;
 Write(*a,"\"type\":\"event\",\"event\":"+Quote(event)+",\"guid\":"+std::to_string(u->GetObjectGuid().GetRawValue())+",\"entry\":"+std::to_string(u->GetEntry())+",\"value\":"+std::to_string(value)+",\"other\":"+std::to_string(other));
 }
}
bool BossDied(Map* map,uint64 guid) {std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(map);return a&&a->target==guid&&a->bossDied;}
bool BossResetObserved(Map* map,uint64 guid) {std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(map);return a&&guid&&a->target==guid&&!a->bossDied&&a->bossResetAt&&Clock()-a->bossResetAt>=30000;}
bool BindNativeBoss(Unit* boss) {
 if(!Enabled() || !boss || !boss->IsInWorld() || !boss->IsAlive())return false;
 std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(boss->GetMap());
 if(!a || a->target || boss->GetEntry()!=a->boss)return false;
 a->target=boss->GetObjectGuid().GetRawValue();
 Write(*a,"\"type\":\"event\",\"event\":\"native_boss_bound\",\"guid\":"+std::to_string(a->target)+",\"entry\":"+std::to_string(a->boss));
 return true;
}
void Count(Unit* u, char const* action, uint32 id, uint32 result, uint64 target) {
 if(!Enabled()||!u||!u->IsInWorld()||!AllowedMap(u->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(u->GetMap())) {
  // Every bucket is written before clearing; pressure is not lost coverage.
  // Write still emits the explicit truncation marker at the byte limit.
  if(a->counts.size()>=4096) {FlushCounts(*a);Write(*a,"\"type\":\"ai_bucket_flush\",\"reason\":\"4096_bucket_limit\"");}
  auto& b=a->counts[{u->GetObjectGuid().GetRawValue(),u->GetEntry(),action,id,result,target}];
  auto now=Clock()-a->start;if(!b.count)b.first=now;b.last=now;++b.count;
 }
}
void Instance(Map* map, uint32 type, uint32 value) {
 if(!Enabled()||!map||!AllowedMap(map->GetId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(map))Write(*a,"\"type\":\"instance_set_data\",\"key\":"+std::to_string(type)+",\"value\":"+std::to_string(value));
}
void PreparationCombat(Unit* unit,Unit* enemy) {
 if(!Enabled() || !unit || !unit->IsInWorld() || !AllowedMap(unit->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(unit->GetMap())) {
  // Called only on a native noncombat->combat transition, never each AI tick.
  // Snapshot both actors before later threat switches obscure an extra pull.
  if(!RecordCombatTransition(*a))return;
  std::ostringstream s;
  s<<"\"type\":\"combat_enter\",\"guid\":"<<unit->GetObjectGuid().GetRawValue()
   <<",\"entry\":"<<unit->GetEntry()<<",\"enemy\":"<<(enemy?enemy->GetObjectGuid().GetRawValue():0)
   <<",\"enemy_entry\":"<<(enemy?enemy->GetEntry():0)
   <<",\"from\":["<<unit->GetPositionX()<<','<<unit->GetPositionY()<<','<<unit->GetPositionZ()<<']';
  if(enemy)s<<",\"enemy_position\":["<<enemy->GetPositionX()<<','<<enemy->GetPositionY()<<','<<enemy->GetPositionZ()<<']';
  Write(*a,s.str());return;
 }
 for(auto const& prepared:preparedLeaders) {
  if(prepared.second!=std::make_pair(unit->GetMapId(),unit->GetInstanceId()))continue;
  auto& count=preparationCombats[prepared.first];
  if(count>=128)continue;
  ++count;
  sLog.outString("RAID_LAB_PREPARATION_COMBAT: leader=" UI64FMTD " unit=" UI64FMTD " entry=%u enemy=" UI64FMTD " enemyEntry=%u map=%u instance=%u position=%.3f,%.3f,%.3f sample=%u",
    prepared.first,unit->GetObjectGuid().GetRawValue(),unit->GetEntry(),
    enemy?enemy->GetObjectGuid().GetRawValue():0,enemy?enemy->GetEntry():0,unit->GetMapId(),unit->GetInstanceId(),
    unit->GetPositionX(),unit->GetPositionY(),unit->GetPositionZ(),count);
  if(unit->GetTypeId()==TYPEID_PLAYER)
   if(auto ai=static_cast<Player*>(unit)->GetPlayerbotAI()) {
    sLog.outString("RAID_LAB_PREPARATION_COMBAT_AI: unit=" UI64FMTD " action=%s decision=%s nc_action=%s currentTarget=" UI64FMTD,
      unit->GetObjectGuid().GetRawValue(),Quote(ai->GetLastExecutedActionName(ai->GetState())).c_str(),
      Quote(ai->GetLastActionDecision(ai->GetState())).c_str(),Quote(ai->GetLastExecutedActionName(BotState::BOT_STATE_NON_COMBAT)).c_str(),
      ai->GetAiObjectContext()->GetValue<ObjectGuid>("current target")->Get().GetRawValue());
    const ObjectGuid followGuid=ai->GetAiObjectContext()->GetValue<ObjectGuid>("follow target")->Get();
    Unit* follow=ai->GetUnit(followGuid);
    const auto endpoint=unit->movespline?unit->movespline->FinalDestination():G3D::Vector3();
    sLog.outString("RAID_LAB_PREPARATION_FOLLOW: unit=" UI64FMTD " master=" UI64FMTD " target=" UI64FMTD " range=%.3f targetPosition=%.3f,%.3f,%.3f splineEnd=%.3f,%.3f,%.3f motion=%u",
      unit->GetObjectGuid().GetRawValue(),ai->GetMaster()?ai->GetMaster()->GetObjectGuid().GetRawValue():0,
      followGuid.GetRawValue(),ai->GetRange("follow"),follow?follow->GetPositionX():0.0f,follow?follow->GetPositionY():0.0f,follow?follow->GetPositionZ():0.0f,
      endpoint.x,endpoint.y,endpoint.z,uint32(unit->GetMotionMaster()->GetCurrentMovementGeneratorType()));
   }
 }
}
void Impact(Unit* source, Unit* target, char const* kind, uint32 spell, uint32 amount, uint32 healthBefore, int32 effective) {
 if(!Enabled()||!target||!target->IsInWorld()||!AllowedMap(target->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(target->GetMap())) {
  Write(*a,"\"type\":\"impact\",\"kind\":"+Quote(kind)+",\"source\":"+std::to_string(source?source->GetObjectGuid().GetRawValue():0)+",\"source_entry\":"+std::to_string(source?source->GetEntry():0)+",\"target\":"+std::to_string(target->GetObjectGuid().GetRawValue())+",\"target_entry\":"+std::to_string(target->GetEntry())+",\"spell\":"+std::to_string(spell)+",\"amount\":"+std::to_string(amount)+",\"hp_before\":"+std::to_string(healthBefore)+",\"effective\":"+std::to_string(effective));
 } else if(target->GetTypeId()==TYPEID_PLAYER && std::string(kind)=="damage" && amount) {
  Player* player=static_cast<Player*>(target);
  Group* group=player->GetGroup();
  if(!group)return;
  const uint64 leader=group->GetLeaderGuid().GetRawValue();
  auto prepared=preparedLeaders.find(leader);
  if(prepared==preparedLeaders.end() || prepared->second!=std::make_pair(player->GetMapId(),player->GetInstanceId()))return;
  // Local fixture diagnostics before Begin: bounded per prepared raid, with
  // identity and actual source/spell so pre-pull deaths are not guessed.
  auto& count=preparationImpacts[leader];
  if(count>=256)return;
  ++count;
  sLog.outString("RAID_LAB_PREPARATION_DAMAGE: leader=" UI64FMTD " target=" UI64FMTD " map=%u instance=%u source=" UI64FMTD " sourceEntry=%u spell=%u amount=%u hpBefore=%u position=%.3f,%.3f,%.3f sample=%u",
    leader,player->GetObjectGuid().GetRawValue(),player->GetMapId(),player->GetInstanceId(),
    source?source->GetObjectGuid().GetRawValue():0,source?source->GetEntry():0,spell,amount,healthBefore,
    player->GetPositionX(),player->GetPositionY(),player->GetPositionZ(),count);
  if(count<=8)
   if(auto ai=player->GetPlayerbotAI())
    sLog.outString("RAID_LAB_PREPARATION_AI: leader=" UI64FMTD " target=" UI64FMTD " action=%s decision=%s nc_action=%s grind=%u currentTarget=" UI64FMTD,
      leader,player->GetObjectGuid().GetRawValue(),Quote(ai->GetLastExecutedActionName(ai->GetState())).c_str(),
      Quote(ai->GetLastActionDecision(ai->GetState())).c_str(),Quote(ai->GetLastExecutedActionName(BotState::BOT_STATE_NON_COMBAT)).c_str(),
      ai->HasStrategy("grind",BotState::BOT_STATE_NON_COMBAT)?1u:0u,
      ai->GetAiObjectContext()->GetValue<ObjectGuid>("current target")->Get().GetRawValue());
 }
}
bool Controlled(Player* p) {
 if(!Enabled()||!p||!p->IsInWorld())return false;
 std::lock_guard<std::recursive_mutex> lock(guard);
 auto prepared=preparedLeaders.find(p->GetObjectGuid().GetRawValue());
 if(prepared!=preparedLeaders.end() && prepared->second==std::make_pair(p->GetMapId(),p->GetInstanceId()))return true;
 auto a=Find(p->GetMap());return a&&a->controlled&&a->leader==p->GetObjectGuid().GetRawValue();
}
void CancelStack(Unit* u,uint32 spell,uint64 target,uint32 elapsed) {
#ifdef _WIN32
 if(!Enabled()||!u||!u->IsPlayer()||!u->IsInWorld()||!AllowedMap(u->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(u->GetMap());
 // Local diagnostic only: no symbols/IO in the unwind and no unbounded log
 // stream. Resolve these addresses offline with this candidate's exact PDB.
 if(!a||a->limited||a->cancelStacks.size()>=64||a->cancelStackSamples++>=4096)return;
 void* frames[16]{};DWORD hash=0;const auto depth=CaptureStackBackTrace(1,16,frames,&hash);
 if(!depth||!a->cancelStacks.insert({spell,hash}).second)return;
 std::ostringstream s;s<<"\"type\":\"cast_cancel_stack\",\"guid\":"<<u->GetObjectGuid().GetRawValue()
  <<",\"spell\":"<<spell<<",\"target\":"<<target<<",\"elapsed_ms\":"<<elapsed
  <<",\"module_base\":"<<uint64(reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr)))<<",\"frames\":[";
 for(unsigned i=0;i<depth;++i){if(i)s<<',';s<<uint64(reinterpret_cast<uintptr_t>(frames[i]));}
 s<<']';Write(*a,s.str());
#endif
}
void Cast(Unit* u,uint32 spell,uint64 target,char const* stage,bool ok) {
 if(!Enabled()||!u||!u->IsInWorld()||!AllowedMap(u->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(u->GetMap()))Write(*a,"\"type\":\"cast\",\"caster\":"+std::to_string(u->GetObjectGuid().GetRawValue())+
  ",\"entry\":"+std::to_string(u->GetEntry())+",\"spell\":"+std::to_string(spell)+",\"target\":"+std::to_string(target)+
  ",\"stage\":"+Quote(stage)+",\"ok\":"+(ok?"true":"false")+
  ",\"position\":["+std::to_string(u->GetPositionX())+","+std::to_string(u->GetPositionY())+","+std::to_string(u->GetPositionZ())+
  "],\"stopped\":"+(u->IsStopped()?"true":"false")+",\"spline_done\":"+(!u->movespline||u->movespline->Finalized()?"true":"false"));
}
void Snapshot(Map* map) {
 if(!Enabled()||!AllowedMap(map->GetId()))return;std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(map);if(!a||Clock()-a->last<1000)return;a->last=Clock();
 FlushCounts(*a);
 if(Clock()-a->start>1800000){End(map,"ABORT: telemetry watchdog 30 minutes");return;}
 if(a->controlled) {
  bool observerPresent=false;
  for(auto const& ref:map->GetPlayers())if(auto p=ref.getSource())if(p->IsInWorld()&&p->GetObjectGuid().GetRawValue()==a->leader)observerPresent=true;
  if(!observerPresent){End(map,"ABORT: synthetic leader left recorded instance; grid activity no longer representative");return;}
 }
 if(map->GetInstanceData()) { auto state=map->GetInstanceData()->Save();Write(*a,"\"type\":\"instance_state\",\"state\":"+Quote(state?state:"")); }
 for(auto const& ref:map->GetPlayers())if(auto p=ref.getSource())State(*a,p);
 auto& store=map->GetObjectsStore();
 for(auto i=store.begin<Creature>();i!=store.end<Creature>();++i)if(auto c=i->second)if(c->GetEntry()==a->boss||c->IsInCombat()||ObserveIdleRaidActor(map->GetId(),a->boss,c->GetEntry())||(a->boss==15936&&map->GetId()==533&&c->GetEntry()==17293)) {
  State(*a,c);
  if (map->GetId()==533 && a->boss==15936 && c->GetEntry()==17293) {
   const Aura* slow=c->GetAura(29351,EFFECT_INDEX_0);const Aura* fast=c->GetAura(30114,EFFECT_INDEX_0);
   std::ostringstream s;s<<"\"type\":\"heigan_controller\",\"guid\":"<<c->GetObjectGuid().GetRawValue()
       <<",\"slow\":"<<bool(slow)<<",\"slow_ticks\":"<<(slow?slow->GetAuraTicks():0)
       <<",\"fast\":"<<bool(fast)<<",\"fast_ticks\":"<<(fast?fast->GetAuraTicks():0);Write(*a,s.str());
  }
  if(map->GetId()==533 && a->boss==16060 && c->GetEntry()==16060) {
   std::ostringstream s;s<<"\"type\":\"gothik_native_state\",\"state\":"<<(map->GetInstanceData()?map->GetInstanceData()->GetData(7):0)<<",\"threat\":[";
   bool first=true;unsigned count=0;
   for(auto reference:c->getThreatManager().getThreatList())if(reference && count++<64) {
    if(!first)s<<',';first=false;s<<'['<<reference->getUnitGuid().GetRawValue()<<','<<reference->getThreat()<<']';
   }
   s<<']';Write(*a,s.str());
  }
 }
 // Native hazard objects, sampled without asking bot planners to recompute.
 // Trap diameter is its trigger footprint, not necessarily its damage radius.
 WorldObjectList objects;
 struct HazardCheck {
  Player* focus;
  WorldObject const& GetFocusObject()const{return *focus;}
  bool operator()(WorldObject* o)const{return o&&o->IsInWorld()&&(o->GetTypeId()==TYPEID_GAMEOBJECT||o->GetTypeId()==TYPEID_DYNAMICOBJECT||o->GetObjectGuid().IsPet());}
 };
 for(auto const& ref:map->GetPlayers())if(auto p=ref.getSource())if(p->IsInWorld()) {
  HazardCheck check{p};MaNGOS::WorldObjectListSearcher<HazardCheck> searcher(objects,check);Cell::VisitAllObjects(p,searcher,60.0f);
 }
 std::set<uint64> seen;
 for(auto object:objects) {
  if(!seen.insert(object->GetObjectGuid().GetRawValue()).second)continue;
  // Native guardians, including Nightmare Illusions, have pet GUIDs and
  // live outside the creature store. Reuse this bounded nearby-object scan
  // to record their positions/victims as well as their existing impact log.
  if(object->GetObjectGuid().IsPet()) {
   auto pet=static_cast<Unit*>(object);
   if(pet->IsInCombat())State(*a,pet);
   continue;
  }
  if(object->GetTypeId()==TYPEID_GAMEOBJECT) {
   auto g=static_cast<GameObject*>(object);
   if(map->GetId()==533 && a->boss==16060 && g->GetEntry()==181170) {
    std::ostringstream s;s<<"\"type\":\"gothik_gate\",\"guid\":"<<g->GetObjectGuid().GetRawValue()<<",\"state\":"<<unsigned(g->GetGoState())<<",\"spawned\":"<<g->IsSpawned()<<",\"x\":"<<g->GetPositionX()<<",\"y\":"<<g->GetPositionY();Write(*a,s.str());
   }
   if(!g->IsSpawned()||g->GetGoType()!=GAMEOBJECT_TYPE_TRAP)continue;
   std::ostringstream s;s<<"\"type\":\"hazard\",\"object_type\":\"trap\",\"guid\":"<<g->GetObjectGuid().GetRawValue()<<",\"entry\":"<<g->GetEntry()<<",\"spell\":"<<g->GetGOInfo()->trap.spellId<<",\"trigger_diameter\":"<<g->GetGOInfo()->trap.diameter<<",\"x\":"<<g->GetPositionX()<<",\"y\":"<<g->GetPositionY()<<",\"z\":"<<g->GetPositionZ();Write(*a,s.str());
  } else {
   auto d=static_cast<DynamicObject*>(object);
   if(d->GetType()!=DYNAMIC_OBJECT_AREA_SPELL||d->GetDuration()<=0)continue;
   std::ostringstream s;s<<"\"type\":\"hazard\",\"object_type\":\"area_spell\",\"guid\":"<<d->GetObjectGuid().GetRawValue()<<",\"spell\":"<<d->GetSpellId()<<",\"radius\":"<<d->GetRadius()<<",\"remaining_ms\":"<<d->GetDuration()<<",\"x\":"<<d->GetPositionX()<<",\"y\":"<<d->GetPositionY()<<",\"z\":"<<d->GetPositionZ();Write(*a,s.str());
  }
 }
 a->file.flush();
}
}
#endif
