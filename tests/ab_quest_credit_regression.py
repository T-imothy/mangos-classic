"""Execute native AB banner and four/five-base quest handlers."""
from pathlib import Path
import re,subprocess,tempfile,sys
root=Path(sys.argv[1])
def block(text,marker):
 start=text.index(marker);opening=text.index('{',start);depth=0
 for end in range(opening,len(text)):
  depth+=(text[end]=='{')-(text[end]=='}')
  if not depth:return text[start:end+1]
 raise AssertionError(marker)
s=(root/'src/game/BattleGround/BattleGroundAB.cpp').read_text(encoding='utf-8');h=(root/'src/game/BattleGround/BattleGroundAB.h').read_text(encoding='utf-8')
enums='\n'.join(block(h,'enum '+name)+';' for name in ('ABNodes','ABNodeType','ABNodeStatus','ABSpells'))
handlers=block(s,'void BattleGroundAB::HandlePlayerClickedOnFlag(')+'\n'+block(s,'void BattleGroundAB::ProcessNodeCapture(')
known={'DEBUG_LOG','STATUS_IN_PROGRESS','TEAM_INDEX_ALLIANCE','TEAM_INDEX_HORDE','TEAM_INVALID','HORDE','ALLIANCE','SCORE_BASES_ASSAULTED','SCORE_BASES_DEFENDED','CHAT_MSG_BG_SYSTEM_ALLIANCE','CHAT_MSG_BG_SYSTEM_HORDE'}
known.update(re.findall(r'\b[A-Z][A-Z0-9_]+\b',enums))
constants=sorted(set(re.findall(r'\b[A-Z][A-Z0-9_]+\b',handlers))-known)
code=r'''
#include <cassert>
#include <map>
#include <vector>
using uint32=unsigned;using uint16=unsigned short;using uint8=unsigned char;using int32=int;using Team=unsigned;using PvpTeamIndex=unsigned;using ChatMsg=unsigned;
enum{STATUS_IN_PROGRESS=3,TEAM_INDEX_ALLIANCE=0,TEAM_INDEX_HORDE=1,TEAM_INVALID=2,HORDE=67,ALLIANCE=469,SCORE_BASES_ASSAULTED=20,SCORE_BASES_DEFENDED=21,CHAT_MSG_BG_SYSTEM_ALLIANCE=30,CHAT_MSG_BG_SYSTEM_HORDE=31};
#define DEBUG_LOG(...) ((void)0)
__ENUMS__
__CONSTANTS__
unsigned abContestedStates[2][5]={},abOccupiedStates[2][5]={},abGraveyardIds[5]={};
struct Variables{std::map<int,int>values;int GetVariable(int id){return values[id];}void SetVariable(int id,int value){values[id]=value;}};
struct Graveyards{void SetGraveYardLinkTeam(unsigned,unsigned,unsigned){}};
struct Data{struct Index{unsigned event1=0;}index;Index GetGameObjectEventIndex(unsigned){return index;}};
struct Map{Variables vars;Graveyards graves;Data data;Variables&GetVariableManager(){return vars;}Graveyards&GetGraveyardManager(){return graves;}Data&GetMapDataContainer(){return data;}};
struct BattleGroundAB;
struct Player{bool world=true,alive=true,loading=false;unsigned team=ALLIANCE,guid=1;Map*map=nullptr;BattleGroundAB*bg=nullptr;std::vector<unsigned>credits;
 bool IsInWorld(){return world;}bool IsAlive(){return alive;}bool IsBeingTeleported(){return loading;}BattleGroundAB*GetBattleGround(){return bg;}Map*GetMap(){return map;}
 unsigned GetTeam(){return team;}unsigned GetObjectGuid(){return guid;}void RemoveAurasWithInterruptFlags(unsigned){}void KilledMonsterCredit(unsigned id){credits.push_back(id);}};
struct GameObject{bool same=true;unsigned GetEntry(){return 180087;}unsigned GetDbGuid(){return 1;}bool IsInMap(Player*){return same;}};
struct BattleGroundAB{unsigned status=3,scores=0;Map map;std::map<unsigned,unsigned>members{{1,0}};ABNodeStatus m_nodeStatus[5]={},m_prevNodeStatus[5]={};unsigned m_nodeTimers[5]={};std::vector<unsigned>spells;
 unsigned GetStatus(){return status;}Map*GetBgMap(){return &map;}auto&GetPlayers(){return members;}unsigned GetTeamIndexByTeamId(unsigned t){return t==ALLIANCE?0:1;}unsigned GetTeamIdByTeamIndex(unsigned t){return t?HORDE:ALLIANCE;}
 unsigned GetOtherTeamIndex(unsigned t){return 1-t;}void UpdatePlayerScore(Player*,unsigned,unsigned){++scores;}void DoUpdateBanner(unsigned,ABNodeStatus,bool){}void DoUpdateNodeWorldstate(unsigned,unsigned){}
 unsigned GetNodeMessageId(unsigned n){return n;}template<class...T>void SendMessage2ToAll(T...){}void PlaySoundToAll(unsigned){}void CastSpellOnTeam(unsigned spell,unsigned){spells.push_back(spell);}
 void HandlePlayerClickedOnFlag(Player*,GameObject*);void ProcessNodeCapture(uint8,PvpTeamIndex);};
__HANDLERS__
int main(){
 for(unsigned team=0;team<2;++team)for(unsigned node=0;node<5;++node){BattleGroundAB bg;Player p;GameObject go;p.bg=&bg;p.map=&bg.map;p.team=team?HORDE:ALLIANCE;bg.map.data.index.event1=node;
  bg.HandlePlayerClickedOnFlag(&p,&go);assert(bg.scores==1&&p.credits.size()==1&&p.credits[0]==15001+node);
  bg.HandlePlayerClickedOnFlag(&p,&go);assert(bg.scores==1&&p.credits.size()==1); // own contested banner is not another assault
  bg.m_nodeStatus[node]=ABNodeStatus(3+team);bg.HandlePlayerClickedOnFlag(&p,&go);assert(p.credits.size()==1);
  bg.m_nodeStatus[node]=ABNodeStatus(3+(1-team));bg.HandlePlayerClickedOnFlag(&p,&go);assert(p.credits.size()==2&&bg.scores==2);
  bg.m_nodeStatus[node]=ABNodeStatus(1+(1-team));bg.m_prevNodeStatus[node]=ABNodeStatus(3+team);bg.HandlePlayerClickedOnFlag(&p,&go);assert(p.credits.size()==3&&bg.scores==3); // admitted reclaim
 }
 BattleGroundAB bg;Player p;GameObject go;p.bg=&bg;p.map=&bg.map;
 auto refused=[&](){bg.HandlePlayerClickedOnFlag(&p,&go);assert(p.credits.empty()&&bg.scores==0);};
 p.loading=true;refused();p.loading=false;p.alive=false;refused();p.alive=true;p.world=false;refused();p.world=true;
 Map other;p.map=&other;refused();p.map=&bg.map;go.same=false;refused();go.same=true;
 bg.members.clear();refused();bg.members[1]=0;bg.status=0;refused();bg.status=3;
 bg.map.data.index.event1=5;refused();bg.map.data.index.event1=0;p.bg=nullptr;refused();p.bg=&bg;
 bg.HandlePlayerClickedOnFlag(nullptr,&go);bg.HandlePlayerClickedOnFlag(&p,nullptr);assert(p.credits.empty());
 bg.map.vars.values[BG_AB_OP_OCCUPIED_BASES_ALLY]=3;bg.ProcessNodeCapture(0,0);assert(bg.spells.size()==1&&bg.spells[0]==BG_AB_SPELL_QUEST_REWARD_4_BASES);
 bg.spells.clear();bg.ProcessNodeCapture(1,0);assert(bg.spells.size()==2&&bg.spells[0]==BG_AB_SPELL_QUEST_REWARD_5_BASES&&bg.spells[1]==BG_AB_SPELL_QUEST_REWARD_4_BASES);
}
'''.replace('__ENUMS__',enums).replace('__CONSTANTS__','enum{'+','.join(f'{name}={100+i}' for i,name in enumerate(constants))+'};').replace('__HANDLERS__',handlers)
with tempfile.TemporaryDirectory(prefix='ab-quest-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'],cwd=p,check=True)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
print('PASS native AB credit for all five nodes and both teams, admitted interactions, own-banner/instance/member/loading rejection and four/five-base quest completion')
