"""Native stationary-boss root survives a temporary root aura's removal."""
from pathlib import Path
import os,shutil,subprocess,sys,tempfile
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
boss_path='src/game/AI/ScriptDevAI/scripts/eastern_kingdoms/molten_core/boss_ragnaros.cpp'
boss=(root/boss_path).read_text()
if '--before' in sys.argv:boss=subprocess.check_output(['git','-C',str(root),'show','HEAD:'+boss_path],text=True)
def block(text,marker):
 start=text.index(marker);begin=text.index('{',start);depth=0
 for end in range(begin,len(text)):
  depth+=(text[end]=='{')-(text[end]=='}')
  if not depth:return text[start:end+1].replace(' override','')
unit=block((root/'src/game/Entities/Unit.cpp').read_text(),'void Unit::SetImmobilizedState(').replace('Unit::','')
ai=(root/'src/game/AI/BaseAI/UnitAI.cpp').read_text()
stationary=block(ai,'void UnitAI::SetAIImmobilizedState(').replace('UnitAI::','').replace('bool combatOnly)','bool combatOnly = false)')
clear=block(ai,'void UnitAI::ClearCombatOnlyRoot(').replace('UnitAI::','')
reset=block(boss,'void Reset(')
code=r'''
#include <cassert>
#include <vector>
#include <iostream>
using uint32=unsigned;
enum {UNIT_STAT_ROOT=0x10,UNIT_STAT_STUNNED=0x40000,UNIT_STAT_LOGOUT_TIMER=0x80000,UNIT_STAT_AI_ROOT=0x20000000};
enum {PHASE_EMERGED=1,EMOTE_STATE_STAND,SPELL_RAGNA_SUBMERGE,SPELL_SUBMERGE_EFFECT,SPELL_MELT_WEAPON,SPELL_ELEMENTAL_FIRE,CAST_TRIGGERED=1,CAST_AURA_NOT_PRESENT=2};
#define RAID_LAB_PHASE(actor,value,next) (value=next)
struct Unit {
 unsigned state=0;bool clientRoot=false;
 void addUnitState(unsigned v){state|=v;}void clearUnitState(unsigned v){state&=~v;}
 bool IsClientControlled(){return false;}void StopMoving(){}void SendMoveRoot(bool v){clientRoot=v;}
 bool IsImmobilizedState(){return state&(UNIT_STAT_ROOT|UNIT_STAT_STUNNED|UNIT_STAT_LOGOUT_TIMER|UNIT_STAT_AI_ROOT);}
 void SetIgnoreRangedTargets(bool){}void HandleEmote(unsigned){}void RemoveAurasDueToSpell(unsigned){}
 __UNIT__
};
struct CombatAI {
 Unit*m_unit;bool m_combatOnlyRoot=false;
 CombatAI(Unit*u):m_unit(u){}void Reset(){}
 __STATIONARY__
 __CLEAR__
};
struct Rag:CombatAI {
 Unit*m_creature;unsigned m_uiAddCount=0,m_phase=0;int m_rangeCheckState=0;
 bool m_sonsSummoned=false,m_bHasYelledMagmaBurst=false,m_bHasSubmergedOnce=false;
 std::vector<unsigned>m_sons,m_spawns;
 Rag(Unit*u):CombatAI(u),m_creature(u){}
 void DoCastSpellIfCan(void*,unsigned,unsigned){}void DespawnGuids(std::vector<unsigned>&v){v.clear();}
 __RESET__
};
int main(){
 Unit boss;Rag rag(&boss);rag.Reset();assert(boss.IsImmobilizedState());
 // The native aura path applies a root, then removes its own root. The
 // encounter's stationary state must survive that independent lifecycle.
 boss.SetImmobilizedState(true,false,false);
 boss.SetImmobilizedState(false,false,false);
 assert(boss.IsImmobilizedState()&&boss.clientRoot&&(boss.state&UNIT_STAT_AI_ROOT));
 rag.ClearCombatOnlyRoot();assert(boss.IsImmobilizedState());
 for(int n=0;n<3;++n){rag.Reset();boss.SetImmobilizedState(true,false,false);boss.SetImmobilizedState(false,false,false);assert(boss.IsImmobilizedState());}
 // Ordinary units still unroot; temporary AI roots still clean up normally.
 Unit ordinary;ordinary.SetImmobilizedState(true,false,false);ordinary.SetImmobilizedState(false,false,false);assert(!ordinary.IsImmobilizedState()&&!ordinary.clientRoot);
 Unit temporary;CombatAI control(&temporary);control.SetAIImmobilizedState(true,true);control.ClearCombatOnlyRoot();assert(!temporary.IsImmobilizedState());
 std::cout<<"PASS: Ragnaros native stationary state survives temporary roots and resets; ordinary root removal is unchanged\n";
}
'''.replace('__UNIT__',unit.replace('bool stun, bool logout','bool stun = false, bool logout = false')).replace('__STATIONARY__',stationary).replace('__CLEAR__',clear).replace('__RESET__',reset)
with tempfile.TemporaryDirectory(prefix='ragnaros-root-') as folder:
 d=Path(folder);(d/'test.cpp').write_text(code)
 compiler=os.environ.get('CXX') or ('cl' if shutil.which('cl') else 'c++')
 if Path(compiler).stem.lower()=='cl':cmd=[compiler,'/nologo','/std:c++17','/EHsc','test.cpp','/Fe:test.exe'];exe=d/'test.exe'
 else:cmd=[compiler,'-std=c++17','test.cpp','-o','test'];exe=d/'test'
 subprocess.run(cmd,cwd=d,check=True);subprocess.run([str(exe)],cwd=d,check=True)
