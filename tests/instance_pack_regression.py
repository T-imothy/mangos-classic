"""Compile the real packing method; check save/reference identity and replay."""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(sys.argv[1]).resolve()
def block(s,marker):
 start=s.index(marker);opening=s.index('{',start);depth=0
 for i in range(opening,len(s)):
  depth+=(s[i]=='{')-(s[i]=='}')
  if not depth:return s[start:i+1]
body=block((root/'src/game/Maps/MapPersistentStateMgr.cpp').read_text(),'void MapPersistentStateManager::PackInstances() const')
trap=block((root/'src/game/Spells/SpellEffects.cpp').read_text(),'switch (lockType)')
wrath=root.name=='wotlk'
code=r'''
#include <cassert>
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <memory>
using uint32=uint32_t;
struct Field {uint32 value;uint32 GetUInt32(){return value;}};
struct Result {std::vector<Field> rows;size_t cursor=0;Field* Fetch(){return &rows[cursor];}bool NextRow(){return ++cursor<rows.size();}};
struct DB {
 std::map<std::string,std::map<uint32,uint32>> tables;
 bool transaction=false;
 std::shared_ptr<Result> Query(const char*) {auto r=std::make_shared<Result>();for(auto p:tables["instance"])r->rows.push_back({p.first});return r->rows.empty()?nullptr:r;}
 void BeginTransaction(){assert(!transaction);transaction=true;}
 void PExecute(const char* sql,uint32 to,uint32 from){
  assert(transaction);std::string text=sql;auto name=text.substr(7,text.find(' ',7)-7);
  auto &t=tables.at(name);assert(t.count(from));assert(!t.count(to));
  auto identity=t.at(from);t.erase(from);t.emplace(to,identity);
 }
 void CommitTransaction(){assert(transaction);transaction=false;}
} CharacterDatabase;
struct BarGoLink {BarGoLink(size_t){}void step(){}};
struct Log {template<class...T>void outString(T...){} } sLog;
struct MapPersistentStateManager {void PackInstances()const;};
enum {LOCKTYPE_NONE,LOCKTYPE_DISARM_TRAP,LOCKTYPE_OPEN_ATTACKING,LOCKTYPE_OPEN,LOCKTYPE_OPEN_TINKERING,GO_ACTIVATED};
struct GO {bool activated=false;void SetLootState(int){activated=true;}unsigned GetEntry(){return 180583;}};
struct SpellInfo {unsigned Id=6477;};
struct ErrorLog {template<class...T>void outError(T...){} } trapLog;
void openTrap(int lockType,GO* gameObjTarget){SpellInfo info;auto m_spellInfo=&info;
'''
code+=trap.replace('sLog.','trapLog.')+'}\n'+body
code+=r'''
int main(){MapPersistentStateManager mgr;
 for(unsigned mask=0;mask<256;++mask){CharacterDatabase.tables.clear();
  for(auto name: {"instance","creature_respawn","gameobject_respawn","corpse","character_instance","group_instance"}){
   auto &t=CharacterDatabase.tables[name];for(unsigned i=1;i<=8;++i)if(mask&(1u<<(i-1)))t[i]=100+i;
  }
  auto before=CharacterDatabase.tables.at("instance");mgr.PackInstances();
  std::map<uint32,uint32> expected;unsigned next=WRATH?2:1;
  for(auto row:before){if(WRATH&&row.first==1)expected[1]=row.second;else expected[next++]=row.second;}
  for(auto &table:CharacterDatabase.tables)assert(table.second==expected);
  mgr.PackInstances();for(auto &table:CharacterDatabase.tables)assert(table.second==expected);
 }
 for(int kind:{LOCKTYPE_NONE,LOCKTYPE_DISARM_TRAP,LOCKTYPE_OPEN_ATTACKING,LOCKTYPE_OPEN_TINKERING}){GO go;openTrap(kind,&go);assert(go.activated);}
 GO invalid;openTrap(99,&invalid);assert(!invalid.activated);
}
'''
with tempfile.TemporaryDirectory(prefix='instance-pack-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(code)
 subprocess.run(['cl','/nologo','/EHsc','/std:c++17','/DWRATH='+str(int(wrath)),str(p/'test.cpp'),'/Fe:'+str(p/'test.exe'),'/Fo:'+str(p/'test.obj')],check=True)
 subprocess.run([str(p/'test.exe')],check=True)
print('PASS: 256 save layouts, six reference tables, repeated packing, reserved slot and trap opening')
