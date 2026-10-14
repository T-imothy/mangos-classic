"""Execute native Fallen Sky Lords marker admission and personal credit."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(sys.argv[1]);s=(root/'src/game/AI/ScriptDevAI/scripts/world/av_quest_objectives.cpp').read_text(encoding='utf-8')
body=s.split('namespace\n{',1)[1].rsplit('\n}\nvoid AddSC_',1)[0]
code=r'''
#include <cassert>
#include <map>
using uint32=unsigned;using Team=unsigned;
enum{HORDE=67,ALLIANCE=469,QUEST_STATUS_INCOMPLETE=3,BATTLEGROUND_AV=1,STATUS_IN_PROGRESS=3};constexpr float INTERACTION_DISTANCE=5;
struct Map{};
struct Unit{bool player=false,world=true,alive=true;Map*map=nullptr;unsigned instance=1,mapId=30;bool IsPlayer(){return player;}bool IsInWorld(){return world;}bool IsAlive(){return alive;}unsigned GetMapId(){return mapId;}Map*GetMap(){return map;}unsigned GetObjectGuid(){return 1;}};
struct BattleGround{unsigned type=1,status=3;Map*map=nullptr;std::map<unsigned,unsigned>members{{1,0}};unsigned GetTypeId(){return type;}unsigned GetStatus(){return status;}Map*GetBgMap(){return map;}auto&GetPlayers(){return members;}};
struct Player:Unit{bool loading=false,los=true;float distance=0;unsigned team=HORDE,status=3,credits=0,expectedQuest=7302;BattleGround*bg=nullptr;std::map<unsigned,unsigned>progress;
 Player(){player=true;}bool IsBeingTeleported(){return loading;}bool IsInMap(Unit*o){return o&&map==o->map&&instance==o->instance&&mapId==o->mapId;}
 unsigned GetQuestStatus(unsigned q){return q==expectedQuest?status:0;}unsigned GetBGTeam(){return team;}bool IsWithinDistInMap(Unit*o,float d){return IsInMap(o)&&distance<=d;}bool IsWithinLOSInMap(Unit*){return los;}
 BattleGround*GetBattleGround(){return bg;}unsigned GetReqKillOrCastCurrentCount(unsigned q,int entry){assert(q==expectedQuest);return progress[entry];}
 void KilledMonsterCredit(unsigned entry,unsigned){++progress[entry];++credits;}};
struct Creature:Unit{unsigned entry=14026;unsigned GetEntry(){return entry;}};
struct Scripted_NoMovementAI{Creature*m_creature;explicit Scripted_NoMovementAI(Creature*c):m_creature(c){}virtual~Scripted_NoMovementAI(){}virtual void Reset(){}virtual void UpdateAI(unsigned){}virtual void MoveInLineOfSight(Unit*){}};
__BODY__
int main(){Map map;BattleGround bg;bg.map=&map;Player p;p.map=&map;p.bg=&bg;Creature marker;marker.map=&map;npc_av_sky_lord_markerAI ai(&marker);
 for(unsigned entry=14026;entry<=14031;++entry){marker.entry=entry;p.team=entry<=14028?HORDE:ALLIANCE;p.expectedQuest=entry<=14028?7302:7301;
  auto before=p.credits;ai.MoveInLineOfSight(&p);assert(p.credits==before+1);ai.MoveInLineOfSight(&p);assert(p.credits==before+1);}
 p.progress.clear();p.credits=0;marker.entry=14026;p.team=HORDE;p.expectedQuest=7302;
 auto refuse=[&](){ai.MoveInLineOfSight(&p);assert(p.credits==0);};
 p.loading=true;refuse();p.loading=false;p.world=false;refuse();p.world=true;p.alive=false;refuse();p.alive=true;
 p.distance=5.1f;refuse();p.distance=0;p.los=false;refuse();p.los=true;p.instance=2;refuse();p.instance=1;
 p.status=0;refuse();p.status=3;p.team=ALLIANCE;refuse();p.team=HORDE;
 bg.status=0;refuse();bg.status=3;bg.members.clear();refuse();bg.members[1]=0;
 Map other;bg.map=&other;refuse();bg.map=&map;p.bg=nullptr;refuse();p.bg=&bg;
 marker.world=false;refuse();marker.world=true;marker.alive=false;refuse();marker.alive=true;marker.entry=14032;refuse();marker.entry=14026;
 Unit pet;ai.MoveInLineOfSight(&pet);ai.MoveInLineOfSight(nullptr);assert(p.credits==0);
 p.distance=5;ai.MoveInLineOfSight(&p);assert(p.credits==1);
}
'''.replace('__BODY__',body)
with tempfile.TemporaryDirectory(prefix='av-discovery-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'],cwd=p,check=True)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
assert 'AddSC_av_quest_objectives();' in (root/'src/game/AI/ScriptDevAI/system/ScriptLoader.cpp').read_text(encoding='utf-8')
print('PASS native discovery credit for six markers/both factions, range/LOS, no duplicates, wrong quest/team/instance/member/loading rejection')
