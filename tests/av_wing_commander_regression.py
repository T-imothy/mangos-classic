"""Execute actual commander gossip, discovery, route and lifecycle handlers."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(sys.argv[1]);s=(root/'src/game/AI/ScriptDevAI/scripts/world/av_wing_commanders.cpp').read_text(encoding='utf-8')
body=s.split('namespace\n{',1)[1].rsplit('\n}\nvoid AddSC_',1)[0]
code=r'''
#include <cassert>
#include <map>
#include <vector>
#include <cmath>
using uint32=unsigned;using Team=unsigned;using MovementGeneratorType=unsigned;
enum{HORDE=67,ALLIANCE=469,QUEST_STATUS_INCOMPLETE=3,BATTLEGROUND_AV=1,STATUS_IN_PROGRESS=3,PATH_FROM_WAYPOINT_PATH=4,FORCED_MOVEMENT_RUN=2,UNIT_NPC_FLAGS=0,UNIT_NPC_FLAG_NONE=0,UNIT_NPC_FLAG_GOSSIP=1,UNIT_NPC_FLAG_QUESTGIVER=2,UNIT_STAND_STATE_STAND=0,EXTERNAL_WAYPOINT_MOVE=100,EXTERNAL_WAYPOINT_MOVE_START=101,ACTION_T_CAST=11,ORDER_EVADE=1,IDLE_MOTION_TYPE=0,GOSSIP_ICON_CHAT=0,GOSSIP_SENDER_MAIN=1,GOSSIP_ACTION_INFO_DEF=100};constexpr float INTERACTION_DISTANCE=5;
struct Position{float x=0,y=0,z=0,o=0;};struct Map{};
struct Unit{bool player=false,world=true,alive=true;uint32 mapId=30,instance=1;Map*map=nullptr;Position pos;
 bool IsPlayer(){return player;}bool IsInWorld(){return world;}bool IsAlive(){return alive;}uint32 GetMapId(){return mapId;}Map*GetMap(){return map;}uint32 GetObjectGuid(){return 1;} };
struct BattleGround{unsigned type=1,status=3;Map*map=nullptr;std::map<uint32,uint32>members{{1,0}};unsigned GetTypeId(){return type;}unsigned GetStatus(){return status;}Map*GetBgMap(){return map;}auto&GetPlayers(){return members;}};
struct Creature;
struct Player:Unit{bool loading=false,los=true;uint32 team=HORDE,quest=7302,status=3,credits=0,options=0,menus=0,closes=0;BattleGround*bg=nullptr;std::map<uint32,uint32>progress;
 Player(){player=true;}bool IsBeingTeleported(){return loading;}bool IsInMap(Unit*o){return o&&map==o->map&&instance==o->instance&&mapId==o->mapId;}
 uint32 GetBGTeam(){return team;}bool IsWithinDistInMap(Unit*o,float d){return IsInMap(o)&&std::sqrt(std::pow(pos.x-o->pos.x,2)+std::pow(pos.y-o->pos.y,2)+std::pow(pos.z-o->pos.z,2))<=d;}
 bool IsWithinLOSInMap(Unit*){return los;}BattleGround*GetBattleGround(){return bg;}uint32 GetQuestStatus(uint32 id){return id==quest?status:0;}
 uint32 GetReqKillOrCastCurrentCount(uint32 id,uint32 marker){assert(id==quest);return progress[marker];}void KilledMonsterCredit(uint32 marker,uint32){++credits;++progress[marker];}
 void PrepareQuestMenu(uint32){++menus;}void ADD_GOSSIP_ITEM(uint32,const char*,uint32,uint32){++options;}void SEND_GOSSIP_MENU(uint32,uint32){}uint32 GetGossipTextId(Creature*){return 1;}void CLOSE_GOSSIP_MENU(){++closes;}};
struct Motion{uint32 launches=0,seeks=0,idles=0,clears=0,path=0,next=0;void Clear(bool,bool){++clears;}void MoveWaypoint(uint32 p,uint32,uint32,uint32,uint32){path=p;++launches;}bool SetNextWaypoint(uint32 p){next=p;++seeks;return true;}void MoveIdle(){++idles;}};
struct CreatureAI{virtual~CreatureAI(){};};
struct Creature:Unit{uint32 entry=13179,flags=3,movement=1,removed=0,stand=1;bool combat=false;Position home;Motion motion;CreatureAI*brain=nullptr;
 uint32 GetEntry(){return entry;}uint32 GetGUIDLow(){return entry;}Position GetRespawnPosition(){return home;}uint32 GetDefaultMovementType(){return movement;}
 uint32 GetUInt32Value(uint32){return flags;}void SetUInt32Value(uint32,uint32 v){flags=v;}void SetWalk(bool){}Motion*GetMotionMaster(){return &motion;}bool IsInCombat(){return combat;}
 void SetStandState(uint32 v){stand=v;}void RemoveAurasDueToSpell(uint32 id){removed=id;}void SetRespawnCoord(float x,float y,float z,float o){home={x,y,z,o};}
 float GetOrientation(){return pos.o;}void SetDefaultMovementType(uint32 v){movement=v;}CreatureAI*AI(){return brain;}};
struct WaypointNode{float x=0,y=0,z=0;};using WaypointPath=std::map<uint32,WaypointNode>;
struct WaypointManager{std::map<uint32,WaypointPath>paths;WaypointPath*GetPathFromOrigin(uint32,uint32,uint32 id,uint32){return paths.count(id)?&paths[id]:nullptr;}}sWaypointMgr;
struct CreatureEventAI_Action{uint32 type=11;struct{uint32 spellId=0;}cast;};
struct CreatureEventAI:CreatureAI{Creature*m_creature;uint32 ticks=0,sights=0,moves=0,homes=0,actions=0,respawns=0,deaths=0,order=0;explicit CreatureEventAI(Creature*c):m_creature(c){}
 virtual uint32 GetCurrentWaypointPath()const{return 0;}virtual void MoveInLineOfSight(Unit*){++sights;}virtual void MovementInform(uint32,uint32){++moves;}
 virtual void JustReachedHome(){++homes;}virtual bool ProcessAction(CreatureEventAI_Action const&,uint32,uint32,Unit*,Unit*,Unit*){++actions;return true;}
 virtual void UpdateAI(uint32){++ticks;}uint32 GetAIOrder(){return order;}virtual void JustRespawned(){++respawns;}virtual void JustDied(Unit*){++deaths;} };
__BODY__
void LoadRoutes(){for(auto const&d:commanders)for(uint32 p=1;p<=d.lastPoint;++p)sWaypointMgr.paths[d.path][p]={float(p),0,0};}
int main(){LoadRoutes();Map map;BattleGround bg;bg.map=&map;
 for(auto const&d:commanders){Player p;p.bg=&bg;p.map=&map;p.team=d.team;p.quest=d.quest;Creature c;c.map=&map;c.entry=d.entry;c.home={-700,-300,70,1};c.pos=c.home;p.pos=c.pos;
  npc_av_wing_commanderAI ai(&c);c.brain=&ai;
  // Actual NPC discovery works at its native floor, independent of a marker 22 yards above it.
  ai.MoveInLineOfSight(&p);assert(p.credits==1&&p.progress[d.marker]==1&&ai.sights==1);ai.MoveInLineOfSight(&p);assert(p.credits==1);
  assert(GossipHello_av_wing_commander(&p,&c)&&p.options==1&&p.menus==1);
  GossipSelect_av_wing_commander(&p,&c,99,GOSSIP_ACTION_INFO_DEF+1);assert(!ai.returning);
  GossipSelect_av_wing_commander(&p,&c,GOSSIP_SENDER_MAIN,GOSSIP_ACTION_INFO_DEF+1);assert(ai.returning&&c.flags==0&&c.motion.path==d.path&&c.motion.launches==1&&c.motion.next==1);
  assert(!ai.Rescue(&p)&&c.motion.launches==1);assert(!GossipHello_av_wing_commander(&p,&c));
  ai.MovementInform(EXTERNAL_WAYPOINT_MOVE_START,1);ai.MovementInform(EXTERNAL_WAYPOINT_MOVE,2);assert(ai.nextPoint==1); // no false progress
  ai.MovementInform(EXTERNAL_WAYPOINT_MOVE,1);assert(ai.nextPoint==2&&c.home.x==1);
  c.combat=true;ai.JustReachedHome();ai.UpdateAI(100);assert(c.motion.launches==1&&ai.ticks==1);c.combat=false;
  ai.UpdateAI(100);assert(c.motion.launches==2&&c.motion.next==2&&!ai.resumePending); // combat reset resumes without starting over
  CreatureEventAI_Action action;action.cast.spellId=12345;ai.ProcessAction(action,0,0,nullptr,nullptr,nullptr);assert(ai.actions==1);
  action.cast.spellId=16380;ai.ProcessAction(action,0,0,nullptr,nullptr,nullptr);assert(ai.actions==(d.entry==13437?1:2));
  for(uint32 point=2;point<=d.lastPoint;++point)ai.MovementInform(EXTERNAL_WAYPOINT_MOVE,point);
  assert(ai.finishPending&&ai.returning&&c.motion.idles==0);ai.order=ORDER_EVADE;ai.UpdateAI(100);assert(!ai.arrived);ai.order=0;
  ai.UpdateAI(100);assert(ai.arrived&&!ai.returning&&c.motion.idles==1&&c.flags==2&&c.movement==IDLE_MOTION_TYPE&&c.home.x==d.lastPoint);
  p.progress.clear();p.credits=0;ai.MoveInLineOfSight(&p);assert(p.credits==0);assert(!ai.Rescue(&p)); // no discovery/rescue replay at base
  ai.JustDied(nullptr);assert(c.home.x==-700&&c.home.z==70&&c.movement==1&&ai.deaths==1);c.alive=true;ai.JustRespawned();assert(!ai.arrived&&!ai.returning&&c.flags==3&&ai.respawns==1);
 }
 Creature c;c.map=&map;Player p;p.map=&map;p.bg=&bg;c.entry=13179;npc_av_wing_commanderAI ai(&c);c.brain=&ai;
 auto refuse=[&](){assert(!ai.Rescue(&p)&&!ai.returning&&c.motion.launches==0&&p.credits==0);};
 p.loading=true;refuse();p.loading=false;p.alive=false;refuse();p.alive=true;p.world=false;refuse();p.world=true;
 p.pos.z=22;refuse();p.pos.z=0;p.los=false;refuse();p.los=true;p.instance=2;refuse();p.instance=1;p.team=ALLIANCE;refuse();p.team=HORDE;
 bg.members.clear();refuse();bg.members[1]=0;bg.status=0;refuse();bg.status=3;Map other;bg.map=&other;refuse();bg.map=&map;
 c.combat=true;refuse();c.combat=false;c.alive=false;refuse();c.alive=true;
 auto saved=sWaypointMgr.paths[ai.data->path];sWaypointMgr.paths[ai.data->path].erase(10);refuse();sWaypointMgr.paths[ai.data->path]=saved;
 assert(ai.Rescue(&p));c.alive=false;ai.UpdateAI(100);assert(!ai.arrived);ai.JustDied(nullptr);ai.JustRespawned();assert(!ai.returning&&c.flags==3);
 assert(CommanderData(99999)==nullptr);
}
'''.replace('__BODY__',body)
with tempfile.TemporaryDirectory(prefix='av-commanders-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'],cwd=p,check=True)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
assert 'AddSC_av_wing_commanders();' in (root/'src/game/AI/ScriptDevAI/system/ScriptLoader.cpp').read_text(encoding='utf-8')
print('PASS actual six-commander discovery/gossip, active instance/faction/range/LOS, duplicate clicks, missing paths, combat resume/checkpoints, safe arrival, native combat and death/respawn')
