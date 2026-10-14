"""Actual corpse race condition, parameter admission and target swap handling."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(sys.argv[1]);s=(root/'src/game/Globals/Conditions.cpp').read_text(encoding='utf-8');h=(root/'src/game/Globals/Conditions.h').read_text(encoding='utf-8')
def block(text,marker):
 start=text.index(marker);opening=text.index('{',start);depth=0
 for end in range(opening,len(text)):
  depth+=(text[end]=='{')-(text[end]=='}')
  if not depth:return text[start:end+1]
 raise AssertionError(marker)
race=block(s,'case CONDITION_RACE_CLASS:');race=race[race.index('{')+1:-1]
code=r'''
#include <cassert>
#include <utility>
using uint8=unsigned char;using uint32=unsigned;
#define DEBUG_LOG(...) ((void)0)
enum{CONDITION_FLAG_SWAP_TARGETS=2,CONDITION_FLAG_REVERSE_RESULT=1};using ConditionSource=int;
struct Log{void outErrorDb(const char*,...){}}sLog;const char*conditionSourceToStr[]={"loot"};
struct Guid{const char*c_str()const{return "test";}};struct Map{unsigned GetId()const{return 30;}};
struct WorldObject{unsigned kind=0;bool IsPlayer()const{return kind==1;}bool IsUnit()const{return kind==1||kind==3;}bool IsCorpse()const{return kind==2;}
 bool IsCreature()const{return kind==3;}bool IsGameObject()const{return kind==4;}Guid GetGuidStr()const{return {};}};
struct Unit:WorldObject{unsigned race=1,cls=2;unsigned getRaceMask()const{return race;}unsigned getClassMask()const{return cls;}};
struct Corpse:WorldObject{unsigned race=4;mutable unsigned reads=0;Corpse(){kind=2;}unsigned getRace()const{return race?3:0;}unsigned getRaceMask()const{assert(race);++reads;return race;}};
struct ConditionEntry{unsigned m_entry=9000403,m_condition=14,m_flags=2,m_value1=4,m_value2=0;
 bool CheckParamRequirements(WorldObject const*,Map const*,WorldObject const*)const;bool Meets(WorldObject const*,Map const*,WorldObject const*,ConditionSource)const;
 bool Evaluate(WorldObject const*target,Map const*map,WorldObject const*source,ConditionSource conditionSourceType)const{__RACE__}};
__REQUIREMENTS__
__ARRAY__
uint8 const*ConditionTargets=&ConditionTargetsInternal[3];
__CHECK__
__MEETS__
int main(){Map map;Unit looter;looter.kind=1;Corpse corpse;ConditionEntry c;
 assert(c.Meets(&looter,&map,&corpse,0)&&corpse.reads==1); // swapped source: dead dwarf, human recipient
 corpse.race=1;assert(!c.Meets(&looter,&map,&corpse,0));corpse.race=4;c.m_value2=2;assert(!c.Meets(&looter,&map,&corpse,0)); // corpse has no persisted class
 c.m_value2=0;corpse.race=0;auto reads=corpse.reads;assert(!c.Meets(&looter,&map,&corpse,0)&&reads==corpse.reads); // no shift from malformed race
 c.m_flags=0;c.m_value1=1;c.m_value2=2;assert(c.Meets(&looter,&map,nullptr,0));c.m_value2=4;assert(!c.Meets(&looter,&map,nullptr,0));
 c.m_value2=0;WorldObject go;go.kind=4;assert(!c.Meets(&go,&map,nullptr,0)&&!c.Meets(nullptr,&map,nullptr,0));
 c.m_flags=CONDITION_FLAG_REVERSE_RESULT;c.m_value1=4;assert(c.Meets(&looter,&map,nullptr,0));
 Unit creature;creature.kind=3;creature.race=4;c.m_flags=0;assert(c.Meets(&creature,&map,nullptr,0)); // original creature behavior
}
'''
for token,value in {
 '__RACE__':race,'__REQUIREMENTS__':block(h,'enum ConditionRequirement')+';',
 '__ARRAY__':block(s,'uint8 const ConditionTargetsInternal[]')+';',
 '__CHECK__':block(s,'bool ConditionEntry::CheckParamRequirements'),
 '__MEETS__':block(s,'bool ConditionEntry::Meets('),
}.items():code=code.replace(token,value)
with tempfile.TemporaryDirectory(prefix='corpse-race-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'],cwd=p,check=True)
 subprocess.run([str(p/'test.exe')],cwd=p,check=True)
print('PASS native corpse race bytes, source swap, no class/invalid-race assumption, original unit masks and parameter rejection')
