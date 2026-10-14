"""Compile actual native Geddon patrol activation, with saves/waypoints unchanged."""
from pathlib import Path
import subprocess,tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'playerbots/tests'))
from behavior_regression import block
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
native=R/'src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core'
source=(native/'molten_core.cpp').read_text()
methods='\n'.join(block(source,key) for key in ('void instance_molten_core::EnsureGeddonPatrol(', 'void instance_molten_core::OnPlayerEnter(', 'void instance_molten_core::OnCreatureCreate('))
death=block((native/'boss_baron_geddon.cpp').read_text(),'void JustDied(')
code=r"""
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include <map>
#include <vector>
using uint32=unsigned;
enum{TYPE_GEDDON=5,DONE=3,SPECIAL=4,NPC_GEDDON=12056,NPC_GARR=12057,NPC_SULFURON=12098,NPC_MAJORDOMO=12018,PATH_FROM_ENTRY=1};
struct Unit{};struct Player{};struct Creature{unsigned entry=NPC_GEDDON;bool alive=true,active=false;unsigned GetEntry(){return entry;}unsigned GetObjectGuid(){return 1;}bool IsAlive(){return alive;}void SetActiveObjectState(bool v){active=v;}};
struct Node{float x,y,z;};using WaypointPath=std::map<unsigned,Node>;
struct Waypoints{WaypointPath path;bool missing=false;const WaypointPath*GetPathFromOrigin(unsigned e,unsigned,unsigned,unsigned p){assert(e==NPC_GEDDON&&p==PATH_FROM_ENTRY);return missing?nullptr:&path;}}sWaypointMgr;
unsigned errors=0;void script_error_log(const char*,unsigned){++errors;}
struct Map{unsigned loads=0;std::vector<std::pair<float,float>>points;unsigned GetInstanceId(){return 17;}void ForceLoadGrid(float x,float y){++loads;points.push_back({x,y});}};
struct instance_molten_core{Map*instance;bool m_geddonPatrolLoaded=false;unsigned state=0,majordomoCalls=0;std::map<unsigned,unsigned>m_npcEntryGuidStore;
 unsigned GetData(unsigned){return state;}void SetData(unsigned t,unsigned s){assert(t==TYPE_GEDDON);state=s;}void DoSpawnMajordomoIfCan(bool p){assert(p);++majordomoCalls;}
 void EnsureGeddonPatrol();void OnPlayerEnter(Player*);void OnCreatureCreate(Creature*);};
struct BossBase{virtual void JustDied(Unit*){}};
struct Boss:BossBase{Creature*m_creature;instance_molten_core*m_instance;Boss(Creature*c,instance_molten_core*i):m_creature(c),m_instance(i){}
__DEATH__
};
__METHODS__
int main(){Map map;instance_molten_core mc{&map};sWaypointMgr.path={{1,{1,2,3}},{2,{4,5,6}}};mc.OnPlayerEnter(nullptr);assert(map.loads==2&&mc.majordomoCalls==1);mc.OnPlayerEnter(nullptr);assert(map.loads==2&&mc.majordomoCalls==2);
 Creature boss;mc.OnCreatureCreate(&boss);assert(boss.active&&mc.m_npcEntryGuidStore.count(NPC_GEDDON));Boss ai{&boss,&mc};ai.JustDied(nullptr);assert(!boss.active&&mc.state==DONE);
 for(unsigned state:{unsigned(DONE),unsigned(SPECIAL)}){mc.state=state;mc.m_geddonPatrolLoaded=false;mc.EnsureGeddonPatrol();assert(!mc.m_geddonPatrolLoaded&&map.loads==2);}
 mc.state=0;sWaypointMgr.missing=true;mc.EnsureGeddonPatrol();mc.EnsureGeddonPatrol();assert(errors==1&&map.loads==2);sWaypointMgr.missing=false;
 for(unsigned size:{0u,1u,65u}){mc.m_geddonPatrolLoaded=false;sWaypointMgr.path.clear();for(unsigned i=0;i<size;++i)sWaypointMgr.path[i]={1,2,3};unsigned before=errors;mc.EnsureGeddonPatrol();mc.EnsureGeddonPatrol();assert(errors==before+1&&map.loads==2);}
 sWaypointMgr.path={{1,{1,2,3}},{2,{4,5,std::numeric_limits<float>::quiet_NaN()}}};mc.m_geddonPatrolLoaded=false;mc.EnsureGeddonPatrol();assert(map.loads==2);
 boss.alive=false;mc.OnCreatureCreate(&boss);assert(!boss.active);Creature other;other.entry=NPC_GARR;mc.OnCreatureCreate(&other);assert(!other.active&&mc.m_npcEntryGuidStore.count(NPC_GARR));
 std::cout<<"PASS: native bounded patrol preloading, one activation, death/save guards, missing paths and unchanged Majordomo entry\n";
}
""".replace('__METHODS__',methods).replace('__DEATH__',death)
with tempfile.TemporaryDirectory(prefix='geddon-patrol-') as d:
 p=Path(d);(p/'test.cpp').write_text(code)
 r=subprocess.run(['cl','/nologo','/EHsc','/std:c++17','test.cpp','/Fe:test.exe'],cwd=p,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
assert 'm_geddonPatrolLoaded = false;' in block(source,'void instance_molten_core::Initialize(')
assert 'Respawn' not in block(source,'void instance_molten_core::EnsureGeddonPatrol(')
