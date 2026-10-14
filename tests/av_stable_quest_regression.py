"""Execute actual AV stable NPC tame/follow/delivery and lifecycle handlers."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(sys.argv[1]);s=(root/'src/game/AI/ScriptDevAI/scripts/world/av_stable_quests.cpp').read_text(encoding='utf-8')
body=s.split('namespace\n{',1)[1].rsplit('\n}\nvoid AddSC_',1)[0]
code=r'''
#include <cassert>
#include <map>
#include <list>
#include <cmath>
using uint32=unsigned;constexpr float M_PI_F=3.1415926535f;
enum{QUEST_STATUS_INCOMPLETE=3,BATTLEGROUND_AV=1,STATUS_IN_PROGRESS=3,HORDE=67,ALLIANCE=469,FOLLOW_MOTION_TYPE=7};
struct ObjectGuid{unsigned id=0;bool IsEmpty()const{return !id;}void Clear(){id=0;}bool operator!=(ObjectGuid o)const{return id!=o.id;}bool operator==(ObjectGuid o)const{return id==o.id;}bool operator<(ObjectGuid o)const{return id<o.id;}};
struct Player;struct Creature;struct Map{std::map<ObjectGuid,Player*>players;Player*GetPlayer(ObjectGuid g){return players.count(g)?players[g]:nullptr;}};
struct WorldObject{unsigned map=30,instance=7;bool world=true,alive=true;float distance=0;Map*mapObject=nullptr;ObjectGuid guid{1};
 bool IsInWorld(){return world;}bool IsAlive(){return alive;}bool IsInMap(WorldObject*o){return o&&map==o->map&&instance==o->instance;}
 unsigned GetMapId(){return map;}Map*GetMap(){return mapObject;}ObjectGuid GetObjectGuid(){return guid;}bool IsWithinDistInMap(WorldObject*o,float d){return IsInMap(o)&&std::fabs(distance-o->distance)<=d;}};
struct Unit:WorldObject{bool player=false;unsigned faction=1214;bool IsPlayer(){return player;}unsigned GetFaction(){return faction;}};
struct BattleGround{Map*mapObject=nullptr;Map*GetBgMap(){return mapObject;}unsigned type=1,status=3;std::map<ObjectGuid,unsigned>members{{{1},67}};unsigned GetTypeId(){return type;}unsigned GetStatus(){return status;}auto&GetPlayers(){return members;}};
struct Player:Unit{bool loading=false;unsigned status=3,team=67,credits=0,menus=0;BattleGround*bg=nullptr;Player(){player=true;faction=67;}
 bool IsBeingTeleported(){return loading;}unsigned GetQuestStatus(unsigned){return status;}BattleGround*GetBattleGround(){return bg;}unsigned GetBGTeam(){return team;}
 void AreaExploredOrEventHappens(unsigned){++credits;status=1;}void PrepareQuestMenu(ObjectGuid){++menus;}unsigned GetGossipTextId(Creature*){return 0;}void SEND_GOSSIP_MENU(unsigned,ObjectGuid){} };
struct Motion{unsigned type=0,moves=0;void MoveFollow(Player*,float,float){++moves;type=7;}unsigned GetCurrentMovementGeneratorType(){return type;}void MoveIdle(){type=0;}};
struct SpellEntry{unsigned Id=21794;};struct CreatureAI{Creature*m_creature;explicit CreatureAI(Creature*c):m_creature(c){}virtual~CreatureAI(){}virtual void JustRespawned(){}virtual void SpellHit(Unit*,const SpellEntry*){}virtual void UpdateAI(unsigned){} };
struct Creature:Unit{unsigned entry=10981,aura=21794,despawns=0;ObjectGuid auraOwner{1};bool charmed=false,combat=false,los=true;Motion motion;CreatureAI*brain=nullptr;
 unsigned GetEntry(){return entry;}bool HasCharmer(){return charmed;}void*GetSpellAuraHolder(unsigned id,ObjectGuid caster){return id==aura&&caster==auraOwner?this:nullptr;}
 void CombatStop(bool){combat=false;}void DeleteThreatList(){}void setFaction(unsigned f){faction=f;}Motion*GetMotionMaster(){return &motion;}bool IsInCombat(){return combat;}
 void RemoveAurasDueToSpell(unsigned){aura=0;}bool IsWithinLOSInMap(Creature*){return los;}void ForcedDespawn(unsigned){++despawns;}CreatureAI*AI(){return brain;}};
struct CreatureEventAI:CreatureAI{unsigned legacyHits=0,legacyTicks=0,evades=0,respawns=0;using CreatureAI::CreatureAI;
 void SpellHit(Unit*,const SpellEntry*)override{++legacyHits;}void UpdateAI(unsigned)override{++legacyTicks;}void EnterEvadeMode(){++evades;}
 void JustRespawned()override{++respawns;} };
using CreatureList=std::list<Creature*>;Creature*nearby=nullptr;
void GetCreatureListWithEntryInGrid(CreatureList&out,Creature*,unsigned entry,float){if(nearby&&nearby->entry==entry)out.push_back(nearby);}
__BODY__
int main(){Map map;BattleGround bg;bg.mapObject=&map;Player p,other;p.bg=other.bg=&bg;p.mapObject=other.mapObject=&map;other.guid={2};map.players[p.guid]=&p;
 Creature beast,stable;beast.mapObject=stable.mapObject=&map;stable.entry=13616;beast.distance=0;stable.distance=1;
 av_stable_beastAI ai(&beast);beast.brain=&ai;SpellEntry spell;
 p.loading=true;ai.SpellHit(&p,&spell);assert(ai.owner.IsEmpty());p.loading=false;
 beast.aura=0;ai.SpellHit(&p,&spell);assert(ai.owner.IsEmpty());beast.aura=21794;
 ai.SpellHit(&p,&spell);assert(ai.owner==p.guid&&beast.motion.moves==1&&beast.faction==p.faction);
 ai.SpellHit(&p,&spell);assert(beast.motion.moves==1);ai.SpellHit(&other,&spell);assert(ai.owner==p.guid); // route stable and no theft
 assert(!ai.Deliver(&other,&stable));stable.entry=13617;assert(!ai.Deliver(&p,&stable));stable.entry=13616;
 beast.distance=10;assert(!ai.Deliver(&p,&stable));beast.distance=0;beast.los=false;assert(!ai.Deliver(&p,&stable));beast.los=true;
 beast.combat=true;assert(!ai.Deliver(&p,&stable));beast.combat=false;nearby=&beast;
 assert(!GossipHello_av_stable_master(&p,&stable)&&p.credits==1&&beast.despawns==1&&p.menus==0); // native gossip is preserved
 assert(!ai.Deliver(&p,&stable)&&p.credits==1); // event only once; native turn-in/reward is still separate
 ai.JustRespawned();assert(ai.owner.IsEmpty()&&!ai.delivered&&beast.faction==ai.originalFaction);p.status=3;
 ai.SpellHit(&p,&spell);beast.aura=0;assert(!ai.Deliver(&p,&stable));ai.UpdateAI(500);assert(ai.owner.IsEmpty());beast.aura=21794;
 ai.SpellHit(&p,&spell);p.loading=true;ai.UpdateAI(500);assert(ai.owner.IsEmpty()&&ai.evades==2);p.loading=false;
 ai.SpellHit(&p,&spell);p.status=0;ai.UpdateAI(500);assert(ai.owner.IsEmpty());p.status=3;beast.aura=21794;
 ai.SpellHit(&p,&spell);p.instance=8;ai.UpdateAI(500);assert(ai.owner.IsEmpty());p.instance=7;
 ai.UpdateAI(500);assert(ai.legacyTicks>0&&ai.legacyHits>0); // original EventAI behavior remains delegated
 beast.entry=10990;beast.aura=21866;spell.Id=21866;p.team=469;stable.entry=13617;
 ai.SpellHit(&p,&spell);assert(ai.owner==p.guid&&ai.QuestId()==7027);assert(ai.Deliver(&p,&stable)&&p.credits==2);
}
'''.replace('__BODY__',body)
with tempfile.TemporaryDirectory(prefix='av-stable-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'],cwd=p,check=True)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
assert 'AddSC_av_stable_quests();' in (root/'src/game/AI/ScriptDevAI/system/ScriptLoader.cpp').read_text(encoding='utf-8')
print('PASS actual native spell/aura ownership, both factions, taming/follow/delivery, no theft or duplicate credit, transfer/cancel/respawn and wild EventAI preservation')
