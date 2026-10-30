#include "RaidLab.h"
#ifdef MANTECH_RAID_LAB
#include "Config/Config.h"
#include "Maps/Map.h"
#include "Maps/InstanceData.h"
#include "Entities/Player.h"
#include "Entities/Creature.h"
#include "Entities/GameObject.h"
#include "Entities/DynamicObject.h"
#include "Grids/GridNotifiers.h"
#include "Grids/GridNotifiersImpl.h"
#include "Grids/CellImpl.h"
#include <set>
#include "Spells/Spell.h"
#include "Spells/SpellAuras.h"
#include "playerbot/PlayerbotAI.h"
#include <fstream>
#include <map>
#include <memory>
#include <mutex>
#include <sstream>
#include <chrono>
#include <tuple>
namespace RaidLab {
namespace {
std::recursive_mutex guard;
uint64 Clock() { return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
std::string Quote(std::string const& text) { std::ostringstream o; o << '"'; for(unsigned char c:text) { if(c=='"'||c=='\\')o << '\\' << c; else if(c>=32)o << c; else o << ' '; } o << '"'; return o.str(); }
using CountKey = std::tuple<uint64,uint32,std::string,uint32,uint32,uint64>;
struct CountBucket { uint64 first=0,last=0,count=0; };
struct Attempt { std::map<CountKey,CountBucket> counts; std::ofstream file; uint64 start=0,last=0,leader=0,seq=0,bytes=0; uint32 boss=0; uint64 target=0; bool bossDied=false,controlled=false,limited=false; std::string id; };
std::map<std::pair<uint32,uint32>,std::unique_ptr<Attempt>> attempts;
Attempt* Find(Map* map) { if(!map)return nullptr; auto i=attempts.find({map->GetId(),map->GetInstanceId()}); return i==attempts.end()?nullptr:i->second.get(); }
void Write(Attempt& a, std::string const& fields) {
 if(a.limited)return;
 std::ostringstream s; s << "{\"attempt\":" << Quote(a.id) << ",\"seq\":" << ++a.seq << ",\"ms\":" << Clock()-a.start << ',' << fields << "}\n";
 std::string row=s.str(); a.bytes+=row.size();
 if(a.bytes>256ull*1024*1024) {a.file << "{\"type\":\"truncated\",\"reason\":\"256MiB_limit\"}\n";a.file.flush();a.limited=true;return;}
 a.file << row;
}
void FlushCounts(Attempt& a) {
 for(auto const& item:a.counts) {
  auto const& k=item.first;auto const& b=item.second;
  Write(a,"\"type\":\"ai_attempts\",\"guid\":"+std::to_string(std::get<0>(k))+",\"entry\":"+std::to_string(std::get<1>(k))+",\"action\":"+Quote(std::get<2>(k))+",\"id\":"+std::to_string(std::get<3>(k))+",\"result\":"+std::to_string(std::get<4>(k))+",\"target\":"+std::to_string(std::get<5>(k))+",\"count\":"+std::to_string(b.count)+",\"first_ms\":"+std::to_string(b.first)+",\"last_ms\":"+std::to_string(b.last));
 }
 a.counts.clear();
}
void State(Attempt& a, Unit* u) {
 std::ostringstream s; s << "\"type\":\"unit\",\"guid\":" << u->GetObjectGuid().GetRawValue() << ",\"entry\":" << u->GetEntry() << ",\"player\":" << (u->GetTypeId()==TYPEID_PLAYER) << ",\"alive\":" << u->IsAlive() << ",\"combat\":" << u->IsInCombat() << ",\"evade\":" << u->GetCombatManager().IsInEvadeMode() << ",\"hp\":" << u->GetHealth() << ",\"max_hp\":" << u->GetMaxHealth() << ",\"x\":" << u->GetPositionX() << ",\"y\":" << u->GetPositionY() << ",\"z\":" << u->GetPositionZ() << ",\"o\":" << u->GetOrientation() << ",\"moving\":" << u->IsMoving() << ",\"flags\":" << u->GetUInt32Value(UNIT_FIELD_FLAGS) << ",\"victim\":" << (u->GetVictim()?u->GetVictim()->GetObjectGuid().GetRawValue():0) << ",\"auras\":[";
 bool first=true; for(auto const& aura:u->GetSpellAuraHolderMap()) {if(!first)s<<',';first=false;s<<'['<<aura.first<<','<<aura.second->GetStackAmount()<<']';}s<<']';
 if(u->GetTypeId()==TYPEID_PLAYER) {auto ai=static_cast<Player*>(u)->GetPlayerbotAI(); if(ai) s << ",\"action\":" << Quote(ai->GetLastExecutedActionName(ai->GetState())) << ",\"decision\":" << Quote(ai->GetLastActionDecision(ai->GetState())) << ",\"tank\":" << ai->IsTank(static_cast<Player*>(u)) << ",\"healer\":" << ai->IsHeal(static_cast<Player*>(u));}
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
 a->id=std::to_string(a->start)+"-"+std::to_string(key.first)+"-"+std::to_string(key.second);
 a->file.open(sConfig.GetStringDefault("LogsDir")+"/raid-"+a->id+".jsonl");if(!a->file)return false;
 Write(*a,"\"type\":\"begin\",\"map\":"+std::to_string(key.first)+",\"instance\":"+std::to_string(key.second)+",\"boss\":"+std::to_string(boss)+",\"leader\":"+std::to_string(a->leader)+",\"controlled\":"+(controlled?"true":"false")+",\"scenario\":"+Quote(name));a->file.flush();attempts[key]=std::move(a);return true;
}
void End(Map* map,std::string const& result) {std::lock_guard<std::recursive_mutex> lock(guard);if(auto a=Find(map)){FlushCounts(*a);Write(*a,"\"type\":\"end\",\"result\":"+Quote(result));a->file.flush();attempts.erase({map->GetId(),map->GetInstanceId()});}}
void EndLeader(uint64 leader, std::string const& result) {
 std::lock_guard<std::recursive_mutex> lock(guard);
 for(auto i=attempts.begin();i!=attempts.end();) {
  if(i->second->leader!=leader){++i;continue;}
  FlushCounts(*i->second);Write(*i->second,"\"type\":\"end\",\"result\":"+Quote(result));i=attempts.erase(i);
 }
}
void StopAll() {
 std::lock_guard<std::recursive_mutex> lock(guard);
 for(auto& entry:attempts) {FlushCounts(*entry.second);Write(*entry.second,"\"type\":\"end\",\"result\":\"ABORT: local server shutdown\"");}
 attempts.clear();
}
void Event(Unit* u, char const* event, uint64 value, uint64 other) {
 if(!Enabled()||!u||!u->IsInWorld()||!AllowedMap(u->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(u->GetMap())) {
 if(u->GetObjectGuid().GetRawValue()==a->target && std::string(event)=="death_state" && value==JUST_DIED) a->bossDied=true;
 Write(*a,"\"type\":\"event\",\"event\":"+Quote(event)+",\"guid\":"+std::to_string(u->GetObjectGuid().GetRawValue())+",\"entry\":"+std::to_string(u->GetEntry())+",\"value\":"+std::to_string(value)+",\"other\":"+std::to_string(other));
 }
}
bool BossDied(Map* map,uint64 guid) {std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(map);return a&&a->target==guid&&a->bossDied;}
void Count(Unit* u, char const* action, uint32 id, uint32 result, uint64 target) {
 if(!Enabled()||!u||!u->IsInWorld()||!AllowedMap(u->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(u->GetMap())) {
  if(a->counts.size()>=4096) {FlushCounts(*a);Write(*a,"\"type\":\"coverage_gap\",\"reason\":\"AI count bucket overflow\"");}
  auto& b=a->counts[{u->GetObjectGuid().GetRawValue(),u->GetEntry(),action,id,result,target}];
  auto now=Clock()-a->start;if(!b.count)b.first=now;b.last=now;++b.count;
 }
}
void Instance(Map* map, uint32 type, uint32 value) {
 if(!Enabled()||!map||!AllowedMap(map->GetId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(map))Write(*a,"\"type\":\"instance_set_data\",\"key\":"+std::to_string(type)+",\"value\":"+std::to_string(value));
}
void Impact(Unit* source, Unit* target, char const* kind, uint32 spell, uint32 amount, uint32 healthBefore, int32 effective) {
 if(!Enabled()||!target||!target->IsInWorld()||!AllowedMap(target->GetMapId()))return;
 std::lock_guard<std::recursive_mutex> lock(guard);
 if(auto a=Find(target->GetMap())) {
  Write(*a,"\"type\":\"impact\",\"kind\":"+Quote(kind)+",\"source\":"+std::to_string(source?source->GetObjectGuid().GetRawValue():0)+",\"source_entry\":"+std::to_string(source?source->GetEntry():0)+",\"target\":"+std::to_string(target->GetObjectGuid().GetRawValue())+",\"target_entry\":"+std::to_string(target->GetEntry())+",\"spell\":"+std::to_string(spell)+",\"amount\":"+std::to_string(amount)+",\"hp_before\":"+std::to_string(healthBefore)+",\"effective\":"+std::to_string(effective));
 }
}
bool Controlled(Player* p) {if(!Enabled()||!p||!p->IsInWorld())return false;std::lock_guard<std::recursive_mutex> lock(guard);auto a=Find(p->GetMap());return a&&a->controlled&&a->leader==p->GetObjectGuid().GetRawValue();}
void Cast(Unit* u,uint32 spell,uint64 target,char const* stage,bool ok) {if(!Enabled()||!u||!u->IsInWorld()||!AllowedMap(u->GetMapId()))return;std::lock_guard<std::recursive_mutex> lock(guard);if(auto a=Find(u->GetMap()))Write(*a,"\"type\":\"cast\",\"caster\":"+std::to_string(u->GetObjectGuid().GetRawValue())+",\"entry\":"+std::to_string(u->GetEntry())+",\"spell\":"+std::to_string(spell)+",\"target\":"+std::to_string(target)+",\"stage\":"+Quote(stage)+",\"ok\":"+(ok?"true":"false"));}
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
 auto& store=map->GetObjectsStore();for(auto i=store.begin<Creature>();i!=store.end<Creature>();++i)if(auto c=i->second)if(c->GetEntry()==a->boss||c->IsInCombat())State(*a,c);
 // Native hazard objects, sampled without asking bot planners to recompute.
 // Trap diameter is its trigger footprint, not necessarily its damage radius.
 WorldObjectList objects;
 struct HazardCheck {
  Player* focus;
  WorldObject const& GetFocusObject()const{return *focus;}
  bool operator()(WorldObject* o)const{return o&&o->IsInWorld()&&(o->GetTypeId()==TYPEID_GAMEOBJECT||o->GetTypeId()==TYPEID_DYNAMICOBJECT);}
 };
 for(auto const& ref:map->GetPlayers())if(auto p=ref.getSource())if(p->IsInWorld()) {
  HazardCheck check{p};MaNGOS::WorldObjectListSearcher<HazardCheck> searcher(objects,check);Cell::VisitAllObjects(p,searcher,60.0f);
 }
 std::set<uint64> seen;
 for(auto object:objects) {
  if(!seen.insert(object->GetObjectGuid().GetRawValue()).second)continue;
  if(object->GetTypeId()==TYPEID_GAMEOBJECT) {
   auto g=static_cast<GameObject*>(object);
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
