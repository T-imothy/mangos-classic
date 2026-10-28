"""Exercise the production script dispatcher when delayed participants vanish."""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(sys.argv[1]).resolve()
s=(root/'src/game/DBScripts/ScriptMgr.cpp').read_text()
start=s.index('bool ScriptAction::HandleScriptStep()');opening=s.index('{',start);depth=0
for i in range(opening,len(s)):
 depth+=(s[i]=='{')-(s[i]=='}')
 if not depth:body=s[start:i+1];break
code=r'''
#include <cassert>
#include <vector>
#include <tuple>
#include <utility>
#define DETAIL_FILTER_LOG(...)
enum {SCRIPT_COMMAND_TERMINATE_SCRIPT=31,SCRIPT_FLAG_BUDDY_BY_GUID=16,TYPEMASK_WORLDOBJECT=1,TYPEMASK_ITEM=2};
struct Object {virtual ~Object()=default;bool isType(int n){return n==TYPEMASK_WORLDOBJECT;}};
struct WorldObject:Object{};
struct Info {int command=31,data_flags=0;};
struct ScriptAction {
 Info info;Info* m_script=&info;int m_sourceGuid=1,m_targetGuid=2;
 WorldObject source,target,buddy;bool sourceExists=false,targetExists=false;unsigned searches=0,executions=0;bool commandResult=false;
 bool GetScriptCommandObject(int guid,bool,Object*& o){o=guid==1?(sourceExists?&source:nullptr):(targetExists?&target:nullptr);return true;}
 std::pair<bool,bool> GetScriptProcessTargets(WorldObject*,WorldObject*,std::vector<WorldObject*>&sources,std::vector<WorldObject*>&){++searches;if(info.data_flags&16)sources.push_back(&buddy);return {true,false};}
 bool ExecuteDbscriptCommand(WorldObject*,WorldObject*,Object*,bool){++executions;return commandResult;}
 bool HandleScriptStep();
};
'''+body+r'''
int main(){
 ScriptAction vanished;assert(vanished.HandleScriptStep());assert(vanished.searches==0&&vanished.executions==0);
 ScriptAction live;live.sourceExists=true;assert(!live.HandleScriptStep());assert(live.searches==1&&live.executions==1);
 ScriptAction target;target.targetExists=true;assert(!target.HandleScriptStep());assert(target.searches==1);
 ScriptAction explicitBuddy;explicitBuddy.info.data_flags=16;assert(!explicitBuddy.HandleScriptStep());assert(explicitBuddy.searches==1&&explicitBuddy.executions==1);
 ScriptAction regular;regular.info.command=15;assert(!regular.HandleScriptStep());assert(regular.searches==1);
 ScriptAction terminate;terminate.sourceExists=true;terminate.commandResult=true;assert(terminate.HandleScriptStep());assert(terminate.executions==1);
}
'''
with tempfile.TemporaryDirectory(prefix='script-guard-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/EHsc','/std:c++17',str(p/'test.cpp'),'/Fe:'+str(p/'test.exe'),'/Fo:'+str(p/'test.obj')],check=True)
 subprocess.run([str(p/'test.exe')],check=True)
print('PASS: vanished participants terminate; live participants, GUID buddies and ordinary steps preserved')
