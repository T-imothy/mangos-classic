"""Execute actual dual-spec lifecycle/save bodies through bot-to-human takeover."""
from pathlib import Path
import subprocess,sys,tempfile

root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
source=(root/'src/modules/dualspec/src/DualspecModule.cpp').read_text()
def function(signature):
    start=source.index(signature); brace=source.index('{',start); end=brace+1; depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}'); end+=1
    return source[start:end]

fixture=r'''
#include <map>
#include <array>
#include <memory>
#include <string>
#include <vector>
#include <cstdio>
#include <cassert>
#include <iostream>
#define MANGOS_ASSERT(x) assert(x)
using uint8=unsigned char;using uint32=unsigned;
enum {ACTIONBUTTON_NEW,ACTIONBUTTON_CHANGED,ACTIONBUTTON_DELETED,ACTIONBUTTON_UNCHANGED};
struct ActionButton {int uState;unsigned action,type;unsigned GetAction(){return action;}unsigned GetType(){return type;}};
using ActionButtonList=std::map<uint8,ActionButton>;
struct Guid {uint32 id;uint32 GetCounter()const{return id;}};
struct Player {uint32 id=7;bool human=true;bool alwaysOnline=true;bool isRealPlayer()const{return human;}Guid GetObjectGuid()const{return {id};}};
// Always-online eligibility deliberately disagrees with the human socket.
struct RandomMgr {bool IsFreeBot(uint32){return true;}} sRandomPlayerbotMgr;
struct Field {uint8 value;uint8 GetUInt8(){return value;}};
struct Result {Field fields[2];Field* Fetch(){return fields;}bool NextRow(){return false;}};
struct Database {
 std::map<uint32,std::array<uint8,2>> saved{{7,{2,1}}};std::vector<std::string> sql;unsigned queries=0;
 std::unique_ptr<Result> PQuery(const char*,uint32 id){++queries;auto it=saved.find(id);if(it==saved.end())return {};auto r=std::make_unique<Result>();r->fields[0].value=it->second[0];r->fields[1].value=it->second[1];return r;}
 template<class...T>void PExecute(const char* f,T...args){char b[2048];std::snprintf(b,sizeof(b),f,args...);sql.push_back(b);}
} CharacterDatabase;
struct Config {bool enabled=true;};
struct Status {uint8 specCount,activeSpec;};
struct DualspecModule {
 Config config;std::map<uint32,Status>playersStatus;std::map<uint32,std::map<uint32,int>>playersTalents;std::map<uint32,std::array<std::string,2>>playersSpecNames;
 unsigned talentLoads=0,nameLoads=0,talentSaves=0,nameSaves=0;
 Config*GetConfig(){return &config;}
 bool EnsurePlayerData(Player*);void LoadPlayerSpec(uint32);uint8 GetPlayerActiveSpec(uint32)const;uint8 GetPlayerSpecCount(uint32)const;
 void OnPreLoadFromDB(Player*);void OnLoadFromDB(Player*);void OnSaveToDB(Player*);void OnLogOut(Player*);void OnCharacterCreated(Player*);
 bool OnSaveActionButtons(Player*,ActionButtonList&);void SavePlayerSpec(uint32);
 void LoadPlayerTalents(Player*p){assert(playersStatus.count(p->id));++talentLoads;playersTalents[p->id][42]=77;}
 void LoadPlayerSpecNames(Player*p){assert(playersStatus.count(p->id));++nameLoads;playersSpecNames[p->id]={{"first","second"}};}
 void SavePlayerTalents(uint32 id){assert(playersTalents.count(id));++talentSaves;}
 void SavePlayerSpecNames(Player*p){assert(playersSpecNames.count(p->id));++nameSaves;}
};
__METHODS__
int main(){
 Player p;DualspecModule m;
 // A human on the always-online list must preload the saved active spec.
 m.OnPreLoadFromDB(&p);assert(CharacterDatabase.queries==1 && m.GetPlayerActiveSpec(7)==1);
 m.OnLoadFromDB(&p);assert(m.talentLoads==1 && m.nameLoads==1);
 m.playersTalents[7][42]=99;m.playersSpecNames[7][1]="dirty name";
 auto queries=CharacterDatabase.queries;
 m.OnLoadFromDB(&p);assert(CharacterDatabase.queries==queries && m.talentLoads==1 && m.nameLoads==1);
 assert(m.playersTalents[7][42]==99 && m.playersSpecNames[7][1]=="dirty name");
 m.OnSaveToDB(&p);assert(m.talentSaves==1 && m.nameSaves==1);
 assert(CharacterDatabase.sql.back().find("`active_spec` = '1'")!=std::string::npos);
 ActionButtonList buttons{{1,{ACTIONBUTTON_NEW,100,0}}};
 assert(m.OnSaveActionButtons(&p,buttons));assert(buttons[1].uState==ACTIONBUTTON_UNCHANGED);
 assert(CharacterDatabase.sql.back().find("`spec` = '1'")!=std::string::npos);
 // Destruction after socket detach must remove data even if disabled meanwhile.
 p.human=false;m.config.enabled=false;m.OnLogOut(&p);
 assert(m.playersStatus.empty() && m.playersTalents.empty() && m.playersSpecNames.empty());
 m.OnLogOut(nullptr);
 // Exact incident: bot DB login, then a client takes over without DB callbacks.
 DualspecModule takeover;CharacterDatabase.sql.clear();queries=CharacterDatabase.queries;
 takeover.OnPreLoadFromDB(&p);takeover.OnLoadFromDB(&p);
 assert(takeover.playersStatus.empty() && CharacterDatabase.queries==queries);
 assert(!takeover.OnSaveActionButtons(&p,buttons));takeover.OnSaveToDB(&p);
 assert(CharacterDatabase.sql.empty() && CharacterDatabase.queries==queries);
 p.human=true;buttons[1].uState=ACTIONBUTTON_CHANGED;
 assert(takeover.OnSaveActionButtons(&p,buttons));
 assert(takeover.GetPlayerActiveSpec(7)==1 && CharacterDatabase.queries==queries+1);
 assert(takeover.talentLoads==1 && takeover.nameLoads==1);
 assert(CharacterDatabase.sql.back().find("`spec` = '1'")!=std::string::npos);
 takeover.OnSaveToDB(&p);assert(takeover.talentSaves==1 && takeover.nameSaves==1);
 queries=CharacterDatabase.queries;takeover.OnSaveToDB(&p);
 assert(CharacterDatabase.queries==queries && takeover.talentLoads==1);
 // Ordinary reconnect keeps the current in-memory spec and dirty maps.
 takeover.playersStatus[7].activeSpec=0;takeover.playersTalents[7][42]=123;
 p.human=false;p.human=true;assert(takeover.EnsurePlayerData(&p));
 assert(takeover.GetPlayerActiveSpec(7)==0 && takeover.playersTalents[7][42]==123 && CharacterDatabase.queries==queries);
 // Saving can be the first operation after takeover, even with no action changes.
 DualspecModule saveFirst;saveFirst.OnSaveToDB(&p);assert(saveFirst.GetPlayerActiveSpec(7)==1);
 assert(saveFirst.talentSaves==1 && saveFirst.nameSaves==1);
 // Disabled/null calls do not query, mutate bars or invent a spec.
 DualspecModule disabled;disabled.config.enabled=false;queries=CharacterDatabase.queries;auto sqlCount=CharacterDatabase.sql.size();
 disabled.OnPreLoadFromDB(&p);disabled.OnLoadFromDB(&p);disabled.OnSaveToDB(&p);
 assert(!disabled.OnSaveActionButtons(&p,buttons));assert(!disabled.EnsurePlayerData(nullptr));
 assert(CharacterDatabase.queries==queries && CharacterDatabase.sql.size()==sqlCount && disabled.playersStatus.empty());
 disabled.config.enabled=true;disabled.OnPreLoadFromDB(nullptr);disabled.OnLoadFromDB(nullptr);disabled.OnSaveToDB(nullptr);
 assert(!disabled.OnSaveActionButtons(nullptr,buttons));
 // Only a genuinely new metadata row receives the existing default spec.
 Player fresh;fresh.id=8;DualspecModule newCharacter;newCharacter.OnLoadFromDB(&fresh);
 assert(newCharacter.GetPlayerActiveSpec(8)==0 && newCharacter.GetPlayerSpecCount(8)==1);
 assert(CharacterDatabase.sql.back().find("INSERT INTO `custom_dualspec_characters`")!=std::string::npos);
 queries=CharacterDatabase.queries;assert(newCharacter.EnsurePlayerData(&fresh));assert(queries==CharacterDatabase.queries);
 // Character creation remains the native initialization path and needs no query.
 Player created;created.id=9;DualspecModule creation;creation.OnCharacterCreated(&created);
 assert(creation.GetPlayerActiveSpec(9)==0 && creation.playersTalents.count(9) && creation.playersSpecNames.count(9));
 assert(CharacterDatabase.queries==queries);
 std::cout<<"PASS: actual lifecycle bodies preserve saved spec, bot takeover, dirty caches, action mirroring and socket-detached cleanup\n";
}
'''
signatures=['bool DualspecModule::EnsurePlayerData(', 'void DualspecModule::LoadPlayerSpec(',
 'uint8 DualspecModule::GetPlayerActiveSpec(', 'uint8 DualspecModule::GetPlayerSpecCount(',
 'void DualspecModule::OnPreLoadFromDB(', 'void DualspecModule::OnLoadFromDB(',
 'void DualspecModule::OnSaveToDB(', 'void DualspecModule::OnLogOut(',
 'void DualspecModule::OnCharacterCreated(', 'bool DualspecModule::OnSaveActionButtons(',
 'void DualspecModule::SavePlayerSpec(']
methods='\n'.join(function(s) for s in signatures)
with tempfile.TemporaryDirectory(prefix='mantech-dualspec-lifecycle-') as directory:
    path=Path(directory);cpp=path/'probe.cpp';exe=path/'probe.exe'
    cpp.write_text(fixture.replace('__METHODS__',methods))
    define='MANGOSBOT_ZERO' if root.name=='classic' else 'MANGOSBOT_ONE'
    run=subprocess.run(['cl','/nologo','/std:c++17','/EHsc','/DENABLE_PLAYERBOTS','/D'+define,str(cpp),'/Fe:'+str(exe)],cwd=path,capture_output=True,text=True)
    assert run.returncode==0,run.stdout+run.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True)
    assert run.returncode==0,run.stdout+run.stderr
    print(root.name+': '+run.stdout.strip())
