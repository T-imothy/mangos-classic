"""Execute actual native quest credit/objective and level admission bodies."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(sys.argv[1]);source=(root/'src/game/Entities/Player.cpp').read_text(encoding='utf-8')
def block(text,marker):
 start=text.index(marker);opening=text.index('{',start);depth=0
 for end in range(opening,len(text)):
  depth+=(text[end]=='{')-(text[end]=='}')
  if not depth:return text[start:end+1]
 raise AssertionError(marker)
methods='\n'.join(block(source,x) for x in ('void Player::KilledMonsterCredit(','bool Player::HasQuestForGO(','bool Player::SatisfyQuestLevel('))
code=r'''
#include <cassert>
#include <map>
using uint32=unsigned;using int32=int;using ObjectGuid=unsigned;
enum{MAX_QUEST_LOG_SIZE=2,QUEST_OBJECTIVES_COUNT=4,QUEST_STATUS_INCOMPLETE=3,QUEST_STATUS_COMPLETE=1,QUEST_NEW=0,QUEST_CHANGED=1,QUEST_SPECIAL_FLAG_KILL_OR_CAST=32,INVALIDREASON_DONT_HAVE_REQ=1};
struct Quest{bool raid=false;unsigned min=10,max=19;int ReqCreatureOrGOId[4]={100,-200,0,0};unsigned ReqCreatureOrGOCount[4]={1,1,0,0},ReqSpell[4]={};
 bool IsAllowedInRaid()const{return raid;}bool HasSpecialFlag(unsigned)const{return true;}unsigned GetMinLevel()const{return min;}unsigned GetMaxLevel()const{return max;}};
struct Manager{Quest q;const Quest*GetQuestTemplate(unsigned id){return id==1?&q:nullptr;}}sObjectMgr;
struct QuestStatusData{unsigned m_status=QUEST_STATUS_INCOMPLETE,uState=QUEST_NEW,m_creatureOrGOcount[4]={};};using QuestStatusMap=std::map<unsigned,QuestStatusData>;
struct Group{bool raid=true;bool IsRaidGroup(){return raid;}};
struct Player{Group group;bool grouped=true,bg=true;unsigned level=10,notices=0,completions=0;QuestStatusMap mQuestStatus{{1,{}}};
 Group*GetGroup()const{return grouped?const_cast<Group*>(&group):nullptr;}bool InBattleGround()const{return bg;}
 unsigned GetQuestSlotQuestId(unsigned slot)const{return slot==0?1:0;}unsigned GetLevel()const{return level;}
 void SendQuestUpdateAddCreatureOrGo(const Quest*,unsigned,int,unsigned){++notices;}
 bool CanCompleteQuest(unsigned){return mQuestStatus[1].m_creatureOrGOcount[0]>=1&&mQuestStatus[1].m_creatureOrGOcount[1]>=1;}
 void CompleteQuest(unsigned){++completions;mQuestStatus[1].m_status=QUEST_STATUS_COMPLETE;}
 void SendCanTakeQuestResponse(unsigned)const{}
 void KilledMonsterCredit(unsigned,unsigned);bool HasQuestForGO(int)const;bool SatisfyQuestLevel(const Quest*,bool)const;};
__METHODS__
int main(){Player p;auto&status=p.mQuestStatus[1];
 for(unsigned level:{10u,19u,20u,29u,30u,39u,40u,49u,50u,59u,60u}){
  sObjectMgr.q.min=level==60?60:(level/10)*10;sObjectMgr.q.max=level==60?60:sObjectMgr.q.min+9;p.level=level;
  assert(p.SatisfyQuestLevel(&sObjectMgr.q,false));p.level=sObjectMgr.q.min-1;assert(!p.SatisfyQuestLevel(&sObjectMgr.q,false));
  p.level=sObjectMgr.q.max+1;assert(!p.SatisfyQuestLevel(&sObjectMgr.q,false));}
 p.bg=false;p.KilledMonsterCredit(100,1);assert(status.m_creatureOrGOcount[0]==0&&!p.HasQuestForGO(200)); // outdoor raid restriction retained
 p.bg=true;assert(p.HasQuestForGO(200));p.KilledMonsterCredit(100,1);assert(status.m_creatureOrGOcount[0]==1&&p.notices==1);
 p.KilledMonsterCredit(100,1);assert(status.m_creatureOrGOcount[0]==1&&p.notices==1); // cap, repeated combat event
 status.m_creatureOrGOcount[1]=1;assert(!p.HasQuestForGO(200));p.KilledMonsterCredit(100,1);assert(p.completions==1);
 status={};p.bg=false;p.grouped=false;p.KilledMonsterCredit(100,1);assert(status.m_creatureOrGOcount[0]==1); // solo unchanged
 status={};p.grouped=true;sObjectMgr.q.raid=true;p.KilledMonsterCredit(100,1);assert(status.m_creatureOrGOcount[0]==1); // native raid quest unchanged
 status.m_status=QUEST_STATUS_COMPLETE;assert(!p.HasQuestForGO(200));
}
'''.replace('__METHODS__',methods)
with tempfile.TemporaryDirectory(prefix='pvp-quest-credit-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'],cwd=p,check=True)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
print('PASS native BG raid quest kill/objective credit, repeated-event caps, outdoor/solo/raid preservation and every level boundary')
