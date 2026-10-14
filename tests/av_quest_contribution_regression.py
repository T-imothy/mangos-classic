"""Execute actual AV contribution handler and post-reward native hook."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(sys.argv[1])
def block(text,marker):
 start=text.index(marker);opening=text.index('{',start);depth=0
 for end in range(opening,len(text)):
  depth+=(text[end]=='{')-(text[end]=='}')
  if not depth:return text[start:end+1]
 raise AssertionError(marker)
s=(root/'src/game/BattleGround/BattleGroundAV.cpp').read_text(encoding='utf-8');h=(root/'src/game/BattleGround/BattleGroundAV.h').read_text(encoding='utf-8')
player=(root/'src/game/Entities/Player.cpp').read_text(encoding='utf-8');reward=block(player,'void Player::RewardQuest(')
start=reward.index('    if (IsInWorld() && !IsBeingTeleported() && questGiver')
hook=reward[start:reward.index('\n    if (announce)',start)]
assert reward.index('q_status.m_rewarded = true;')<start
assert reward.count('->HandleQuestComplete(')==1
code=r'''
#include <cassert>
#include <map>
#include <vector>
using uint32=unsigned;using uint8=unsigned char;using Team=unsigned;using PvpTeamIndex=unsigned;using AVNodeIds=unsigned;
enum{ALLIANCE=469,HORDE=67,STATUS_IN_PROGRESS=3,POINT_CONTROLLED=1,BG_AV_NODES_FIRSTAID_STATION=0,BG_AV_NODES_FROSTWOLF_HUT=6,BG_AV_FACTION_ID_STORMPIKE=730,BG_AV_FACTION_ID_FROSTWOLF=729,TYPEID_UNIT=3,BATTLEGROUND_AV=1};
#define DEBUG_LOG(...) ((void)0)
__QUEST_IDS__
struct Player;struct BattleGround{unsigned type=BATTLEGROUND_AV;virtual ~BattleGround(){}unsigned GetTypeId(){return type;}};
struct Creature{unsigned kind=TYPEID_UNIT;bool same=true;unsigned GetTypeId(){return kind;}bool IsInMap(Player*){return same;}};
struct Player{unsigned team=ALLIANCE,guid=1;bool world=true,loading=false;BattleGround*bg=nullptr;void*map=nullptr;void*GetMap(){return map;}
 bool IsInWorld(){return world;}bool IsBeingTeleported(){return loading;}BattleGround*GetBattleGround(){return bg;}
 unsigned GetBGTeam(){return team;}unsigned GetObjectGuid(){return guid;}};
struct Node{unsigned owner=0,state=POINT_CONTROLLED;};
struct BattleGroundAV:BattleGround{unsigned status=STATUS_IN_PROGRESS,m_teamQuestStatus[2][9]={},rep[2]={};Node m_nodes[7];std::map<unsigned,unsigned>members{{1,0}};std::vector<unsigned>populated;
 void*map=nullptr;void*GetBgMap(){return map;}unsigned GetStatus(){return status;}auto&GetPlayers(){return members;}unsigned GetTeamIndexByTeamId(unsigned t){assert(t==ALLIANCE||t==HORDE);return t==ALLIANCE?0:1;}
 void PopulateNode(unsigned node){populated.push_back(node);}void RewardReputationToTeam(unsigned faction,unsigned amount,unsigned team){assert(faction==(team==ALLIANCE?730:729));rep[GetTeamIndexByTeamId(team)]+=amount;}
 void HandleQuestComplete(unsigned,Player*);};
__HANDLER__
struct RewardHook:Player{void Notify(unsigned quest_id,Creature*questGiver){__HOOK__}};
int main(){BattleGroundAV bg;RewardHook p;p.bg=&bg;Creature npc;
 p.Notify(7223,&npc);assert(bg.m_teamQuestStatus[0][0]==20&&bg.rep[0]==1);
 for(unsigned i=1;i<25;++i)p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==500&&bg.populated.size()==7&&bg.populated.back()==6);
 auto count=bg.m_teamQuestStatus[0][0];p.loading=true;p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);p.loading=false;
 p.map=&npc;p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);p.map=nullptr;
 npc.same=false;p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);npc.same=true;
 npc.kind=4;p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);npc.kind=TYPEID_UNIT;
 bg.members.clear();p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);bg.members[1]=0;
 p.Notify(6741,&npc);assert(bg.m_teamQuestStatus[1][0]==0); // wrong faction ID rejected
 bg.HandleQuestComplete(6781,nullptr);bg.status=0;p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);bg.status=STATUS_IN_PROGRESS;
 p.world=false;p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);p.world=true;
 BattleGround other;other.type=2;p.bg=&other;p.Notify(6781,&npc);assert(bg.m_teamQuestStatus[0][0]==count);p.bg=&bg;
 p.Notify(8383,&npc);assert(bg.rep[0]==25); // normal BG mark reward not an AV contribution
 p.Notify(6881,&npc);p.Notify(7386,&npc);assert(bg.m_teamQuestStatus[0][4]==6&&bg.rep[0]==31);
 p.team=HORDE;for(auto&n:bg.m_nodes)n.owner=1;
 for(unsigned i=0;i<25;++i)p.Notify(i?6741:7224,&npc);assert(bg.m_teamQuestStatus[1][0]==500&&bg.rep[1]==25&&bg.populated.size()==14);
 p.Notify(6827,&npc);assert(bg.m_teamQuestStatus[1][3]==1&&bg.m_teamQuestStatus[1][1]==0);
}
'''.replace('__QUEST_IDS__',block(h,'enum AVQuestIds')+';').replace('__HANDLER__',block(s,'void BattleGroundAV::HandleQuestComplete(')).replace('__HOOK__',hook)
with tempfile.TemporaryDirectory(prefix='av-contribution-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'],cwd=p,check=True)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
assert 'm_teamQuestStatus[teamIdx][3] == 30' in s and 'm_teamQuestStatus[teamIdx][5] == 28' in s
print('PASS actual native committed-reward hook, both factions, active instance/membership/loading gates, batches, all seven defender nodes and unrelated rewards')
