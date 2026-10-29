"""Execute Classic's actual forced-speed sender/ACK handler and mover lifecycle."""
from pathlib import Path
import argparse, subprocess, tempfile

parser=argparse.ArgumentParser();parser.add_argument('--core',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args();root=args.core
def block(source,marker):
    start=source.index(marker);opening=source.index('{',start);depth=1;i=opening+1
    while depth:
        if source[i]=='{':depth+=1
        elif source[i]=='}':depth-=1
        i+=1
    return source[start:i]
source=(root/'src/game/MotionGenerators/MovementHandler.cpp').read_text()
methods='\n'.join(block(source,m) for m in ('void WorldSession::NotifyMovementControllerChanged(', 'void WorldSession::RetireSpeedOrder(', 'void WorldSession::SendForcedSpeedChange(', 'void WorldSession::LogIgnoredSpeedAck(', 'void WorldSession::HandleForceSpeedChangeAckOpcodes('))
player=(root/'src/game/Entities/Player.cpp').read_text();session=(root/'src/game/Server/WorldSession.cpp').read_text()
methods+='\n'+block(player,'void Player::SetMover(')+'\n'+block(session,'void WorldSession::SetPlayer(')
unit=(root/'src/game/Entities/Unit.cpp').read_text()
sender=block(unit,'void Unit::SetSpeedRate(')
assert 'player->GetSession()->SendForcedSpeedChange(this, mtype)' in sender
assert 'm_forced_speed_changes' not in sender
header=(root/'src/game/Server/WorldSession.h').read_text()
record=block(header,'struct ForcedSpeedOrder')+';'
native=(root/'src/game/Anticheat/module/Movement/movement.cpp').read_text()
native_methods='\n'.join(block(native,m) for m in ('void Movement::OrderSent(', 'void Movement::OrderAck(', 'void Movement::OrderAckIfPending(', 'void Movement::CheckExpiredOrders('))
code=r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <deque>
#include <iostream>
#include <limits>
#include <map>
#include <string>
#include <vector>
using uint16=uint16_t;using uint32=uint32_t;using int32=int32_t;
enum UnitMoveType{MOVE_WALK,MOVE_RUN,MOVE_RUN_BACK,MOVE_SWIM,MOVE_SWIM_BACK,MOVE_TURN_RATE,MAX_MOVE_TYPE};
enum {CMSG_FORCE_WALK_SPEED_CHANGE_ACK=200,CMSG_FORCE_RUN_SPEED_CHANGE_ACK,CMSG_FORCE_RUN_BACK_SPEED_CHANGE_ACK,CMSG_FORCE_SWIM_SPEED_CHANGE_ACK,CMSG_FORCE_SWIM_BACK_SPEED_CHANGE_ACK,CMSG_FORCE_TURN_RATE_CHANGE_ACK};
using SpeedOpcodePair=std::array<uint16,3>;
const SpeedOpcodePair SetSpeed2Opc_table[MAX_MOVE_TYPE]={{{100,300,400}},{{101,301,401}},{{102,302,402}},{{103,303,403}},{{104,304,404}},{{105,305,405}}};
struct ObjectGuid{uint32 value=0;ObjectGuid()=default;ObjectGuid(uint32 v):value(v){}bool operator==(ObjectGuid r)const{return value==r.value;}bool operator!=(ObjectGuid r)const{return value!=r.value;}std::string GetString()const{return std::to_string(value);}ObjectGuid WriteAsPacked()const{return *this;}};
struct MovementInfo{bool valid=true;float position=7;};
struct WorldPacket{uint16 opcode;ObjectGuid guid;uint32 counter=0;MovementInfo movement;float speed=0;WorldPacket(uint16 op,unsigned=0):opcode(op){}uint16 GetOpcode()const{return opcode;}char const* GetOpcodeName(){return "ack";}
 WorldPacket& operator>>(ObjectGuid& v){v=guid;return *this;}WorldPacket& operator>>(uint32& v){v=counter;return *this;}WorldPacket& operator>>(MovementInfo& v){v=movement;return *this;}WorldPacket& operator>>(float& v){v=speed;return *this;}
 WorldPacket& operator<<(ObjectGuid v){guid=v;return *this;}WorldPacket& operator<<(uint32 v){counter=v;return *this;}WorldPacket& operator<<(const MovementInfo& v){movement=v;return *this;}WorldPacket& operator<<(float v){speed=v;return *this;}};
struct Player;struct WorldSession;
struct Unit{virtual ~Unit()=default;ObjectGuid guid;Player* controller=nullptr;bool controlled=true,transport=false;float position=0;unsigned broadcasts=0;std::array<float,MAX_MOVE_TYPE> speeds{{2.5f,7,2.25f,2.361111f,2.5f,3.14f}};
 virtual bool IsPlayer(){return false;}ObjectGuid GetObjectGuid()const{return guid;}ObjectGuid GetPackGUID(){return guid;}std::string GetGuidStr()const{return guid.GetString();}Player* GetControllingPlayer(){return controller;}bool IsClientControlled(){return controlled;}float GetSpeed(UnitMoveType t){return speeds[t];}void* GetTransport(){return transport?this:nullptr;}void SendMessageToAllWhoSeeMeMove(WorldPacket&,ObjectGuid){++broadcasts;}};
struct Player:Unit{WorldSession* session=nullptr;Unit* m_mover=this;bool IsPlayer()override{return true;}WorldSession* GetSession(){return session;}Unit* GetMover(){return m_mover;}bool IsSelfMover(){return m_mover==this;}char const* GetName(){return "fixture";}void SetMover(Unit*);};
struct Logger{unsigned errors=0,infos=0,kicks=0;std::string last;template<class... A>void outError(char const* format,A...){++errors;last=format;if(last.find("SpeedAck kick")!=std::string::npos)++kicks;}template<class... A>void outString(char const* format,A...){++infos;last=format;}template<class... A>void outDebug(char const*,A...){}}sLog;
namespace WorldTimer{static uint32 now=1;uint32 getMSTime(){return now;}}
char const* LookupOpcodeName(uint16){return "opcode";}
constexpr unsigned CHEAT_TYPE_BAD_ORDER_ACK=1;
struct Config{bool enabled=true;bool IsEnabled(unsigned){return enabled;}}sAnticheatConfig;
struct Recorder{unsigned badAck=0;template<class... A>void RecordCheatInternal(unsigned,char const*,A...){++badAck;}};
struct PendingOrder{uint16 opcode;uint32 counter,time;};
struct History{uint16 opcode;uint32 time;};
struct NameHolder{char const* GetName(){return "fixture";}};
struct Movement{std::deque<PendingOrder> _orders;std::vector<History> _orderHistory,_ackHistory;NameHolder name;NameHolder* _me=&name;Recorder record;Recorder* _anticheat=&record;
 static uint16 GetOrderResponse(uint16 opcode){return opcode+100;}
 void OrderSent(uint16,uint32);void OrderAck(uint16,uint32);void OrderAckIfPending(uint16,uint32);void CheckExpiredOrders(uint32);
};
__NATIVE_METHODS__
struct Anticheat{Movement movement;std::deque<PendingOrder>& orders=movement._orders;unsigned ackCalls=0,speedChecks=0,resets=0;unsigned& badAck=movement.record.badAck;bool allowSpeed=true;
 void OrderSent(uint16 opcode,uint32 counter){movement.OrderSent(opcode,counter);}
 void OrderAck(uint16 opcode,uint32 counter){++ackCalls;movement.OrderAck(opcode,counter);}
 void OrderAckIfPending(uint16 opcode,uint32 counter){++ackCalls;movement.OrderAckIfPending(opcode,counter);}
 bool SpeedChangeAck(MovementInfo&,WorldPacket&,float){++speedChecks;return allowSpeed;}void NewPlayer(){orders.clear();++resets;}};
#define DEBUG_LOG(...) do{}while(0)
struct WorldSession{Player* _player=nullptr;unsigned m_GUIDLow=0;Anticheat anti;Anticheat* m_anticheat=&anti;uint32 m_orderCounter=0,m_speedControlGeneration=0,m_nextSpeedAckDiagnostic=0;unsigned kicks=0,movementChecks=0;Player* lastPlayerMover=nullptr;std::vector<WorldPacket> sent;bool socket=true;bool HasClientSocket(){return socket;}
 __RECORD__
 static constexpr size_t MAX_TRACKED_SPEED_ORDERS=128;
 std::map<uint32,ForcedSpeedOrder> m_pendingSpeedOrders,m_recentSpeedOrders;std::deque<uint32> m_pendingSpeedOrderSequence,m_recentSpeedOrderSequence;
 uint32 GetOrderCounter(){return m_orderCounter;}void IncrementOrderCounter(){++m_orderCounter;}void NotifyMovementControllerChanged(bool resync=false);Anticheat* GetAnticheat(){return m_anticheat;}unsigned GetAccountId(){return 1;}void SendPacket(WorldPacket const& p){sent.push_back(p);}void KickPlayer(){++kicks;}
 bool ProcessMovementInfo(MovementInfo& info,Unit*mover,Player*plMover,WorldPacket&){++movementChecks;lastPlayerMover=plMover;if(!info.valid)return false;mover->position=info.position;return true;}
 void RetireSpeedOrder(uint32,ForcedSpeedOrder);void SendForcedSpeedChange(Unit*,UnitMoveType);void LogIgnoredSpeedAck(char const*,ObjectGuid,uint32,uint16);void HandleForceSpeedChangeAckOpcodes(WorldPacket&);void SetPlayer(Player*,uint32);
};
__METHODS__
struct Fixture{Player player;Unit dragon;WorldSession session;Fixture(){player.guid=1;dragon.guid=2;player.session=&session;player.controller=&player;dragon.controller=&player;session.SetPlayer(&player,1);dragon.speeds[MOVE_RUN_BACK]=1.8f;dragon.speeds[MOVE_SWIM]=1.888889f;}
 uint32 send(Unit* u,UnitMoveType type=MOVE_RUN_BACK){uint32 counter=session.GetOrderCounter();session.SendForcedSpeedChange(u,type);return counter;}
 void ack(uint32 counter,Unit* u,float speed,UnitMoveType type=MOVE_RUN_BACK,bool valid=true){WorldPacket packet(200+type);packet.guid=u->guid;packet.counter=counter;packet.speed=speed;packet.movement.valid=valid;session.HandleForceSpeedChangeAckOpcodes(packet);}
};
int main(){
 {Fixture f;auto c=f.send(&f.player);f.player.SetMover(&f.dragon);f.ack(c,&f.player,2.25f);assert(f.session.kicks==0&&f.session.movementChecks==0&&f.session.anti.ackCalls==1&&f.dragon.position==0);assert(f.dragon.speeds[MOVE_RUN_BACK]==1.8f);}
 {Fixture f;f.player.SetMover(&f.dragon);auto c=f.send(&f.dragon);f.player.SetMover(nullptr);f.ack(c,&f.dragon,1.8f);assert(f.session.kicks==0&&f.session.movementChecks==0&&f.session.anti.speedChecks==0);}
 {Fixture f;auto c=f.send(&f.player);f.player.SetMover(&f.dragon);f.player.SetMover(&f.player);f.ack(c,&f.player,99);assert(!f.session.kicks&&!f.session.movementChecks);}
 {Fixture f;auto generation=f.session.m_speedControlGeneration;f.player.SetMover(nullptr);f.player.SetMover(&f.player);assert(f.session.m_speedControlGeneration==generation);Player withoutSession;withoutSession.SetMover(&f.dragon);assert(withoutSession.GetMover()==&f.dragon);}
 {Fixture f;f.player.speeds[MOVE_RUN_BACK]=1.8f;auto older=f.send(&f.player);f.player.speeds[MOVE_RUN_BACK]=2.25f;auto latest=f.send(&f.player);f.ack(latest,&f.player,2.25f);f.ack(older,&f.player,99);f.ack(latest,&f.player,99);assert(!f.session.kicks&&f.session.movementChecks==1&&f.session.anti.ackCalls==2&&f.session.anti.badAck==0);assert(f.session.m_pendingSpeedOrders.empty());}
 {Fixture f;auto older=f.send(&f.player);auto latest=f.send(&f.player);f.ack(older,&f.player,99);assert(!f.session.kicks&&!f.session.movementChecks);f.ack(latest,&f.player,2.25f);assert(f.session.movementChecks==1);}
 {Fixture f;f.player.SetMover(&f.dragon);auto count=f.session.sent.size();auto c=f.send(&f.dragon);f.ack(c,&f.dragon,1.2f);assert(f.session.sent.size()==count+2&&!f.session.kicks&&!f.session.movementChecks);assert(f.session.sent.back().speed==1.8f&&f.dragon.speeds[MOVE_RUN_BACK]==1.8f&&f.player.speeds[MOVE_RUN_BACK]==2.25f);f.ack(f.session.sent.back().counter,&f.dragon,1.8f);assert(f.session.movementChecks==1&&f.session.lastPlayerMover==nullptr&&f.session.anti.speedChecks==0);}
 {Fixture f;auto c=f.send(&f.player);unsigned logs=sLog.kicks;f.ack(c,&f.player,3);assert(f.session.kicks==1&&!f.session.movementChecks&&sLog.kicks==logs+1);assert(sLog.last.find("ackGuid=%s")!=std::string::npos&&sLog.last.find("expected=%f received=%f")!=std::string::npos);}
 {Fixture f;auto c=f.send(&f.player);f.ack(c,&f.dragon,1.8f);assert(f.session.anti.ackCalls==0&&f.session.m_pendingSpeedOrders.size()==1&&!f.session.movementChecks);f.ack(c,&f.player,2.25f,MOVE_SWIM);assert(f.session.anti.ackCalls==0);f.ack(c,&f.player,2.25f);assert(f.session.movementChecks==1&&f.session.anti.badAck==0);}
 {Fixture f;f.ack(12345,&f.dragon,999);assert(f.session.anti.badAck==1&&!f.session.kicks&&!f.session.movementChecks);}
 {Fixture f;auto c=f.send(&f.player);f.ack(c,&f.player,std::numeric_limits<float>::quiet_NaN());assert(f.session.kicks==1&&!f.session.movementChecks);}
 {Fixture f;auto c=f.send(&f.player);f.ack(c,&f.player,2.25f,MOVE_RUN_BACK,false);assert(!f.session.kicks&&f.session.movementChecks==1&&f.player.position==0&&f.player.broadcasts==0&&f.session.anti.speedChecks==1);}
 {Fixture f;auto c=f.send(&f.player);f.session.anti.allowSpeed=false;f.ack(c,&f.player,2.25f);assert(!f.session.movementChecks&&f.session.anti.speedChecks==1);}
 {Fixture f;auto c=f.send(&f.player);f.player.speeds[MOVE_RUN_BACK]=1.8f;f.ack(c,&f.player,2.25f);assert(!f.session.kicks&&!f.session.movementChecks);}
 {Fixture f;auto first=f.send(&f.player);for(unsigned i=0;i<128;++i)f.send(&f.player);assert(f.session.m_pendingSpeedOrders.size()==128&&f.session.m_recentSpeedOrders.size()==1);f.ack(first,&f.player,99);f.ack(first,&f.player,99);assert(f.session.anti.ackCalls==1&&!f.session.kicks&&!f.session.movementChecks);for(unsigned i=0;i<300;++i)f.send(&f.player);assert(f.session.m_pendingSpeedOrders.size()==128&&f.session.m_recentSpeedOrders.size()==128&&f.session.m_pendingSpeedOrderSequence.size()==128&&f.session.m_recentSpeedOrderSequence.size()==128);f.ack(first,&f.player,99);assert(!f.session.kicks&&!f.session.movementChecks);}
 {Fixture f;f.session.m_orderCounter=std::numeric_limits<uint32>::max()-3;for(unsigned i=0;i<130;++i)f.send(&f.player);auto c=f.session.sent.back().counter;assert(f.session.m_pendingSpeedOrders.count(c));f.ack(c,&f.player,2.25f);assert(f.session.movementChecks==1&&!f.session.kicks);}
 {Fixture f;f.send(&f.player);auto generation=f.session.m_speedControlGeneration;f.session.SetPlayer(nullptr,0);assert(f.session.m_pendingSpeedOrders.empty()&&f.session.m_recentSpeedOrders.empty()&&f.session.m_pendingSpeedOrderSequence.empty()&&f.session.anti.orders.empty()&&f.session.m_speedControlGeneration!=generation);}
 {Fixture f;WorldTimer::now=1;auto infos=sLog.infos;for(unsigned i=0;i<20;++i)f.ack(1000+i,&f.dragon,99);assert(sLog.infos==infos+1);WorldTimer::now=10002;f.ack(5000,&f.dragon,99);assert(sLog.infos==infos+2);}

 {Fixture f;auto c=f.send(&f.player);WorldTimer::now+=1000;f.session.anti.movement.CheckExpiredOrders(10);assert(f.session.anti.orders.empty());f.ack(c,&f.player,2.25f);assert(!f.session.anti.badAck&&f.session.movementChecks==1);f.ack(999999,&f.player,2.25f);assert(f.session.anti.badAck==1&&f.session.movementChecks==1);}
 {Fixture f;f.session.socket=false;auto c=f.send(&f.player);assert(f.session.sent.size()==1&&f.session.sent.back().counter==c&&f.session.GetOrderCounter()==c+1);assert(f.session.m_pendingSpeedOrders.empty()&&f.session.anti.orders.empty());f.player.SetMover(&f.dragon);assert(f.session.sent.size()==1);}
 {Fixture f;auto c=f.send(&f.player);f.ack(c,&f.player,0);assert(!f.session.kicks&&f.session.sent.size()==2&&!f.session.movementChecks);f.ack(f.session.sent.back().counter,&f.player,2.25f);assert(f.session.movementChecks==1);}
 {Fixture f;f.player.SetMover(&f.dragon);assert(f.session.sent.size()==MAX_MOVE_TYPE);auto first=f.session.sent.back().counter;auto oldGeneration=f.session.m_speedControlGeneration;f.player.SetMover(nullptr);assert(f.session.sent.size()==2*MAX_MOVE_TYPE&&f.session.m_speedControlGeneration!=oldGeneration);f.ack(first,&f.dragon,99,MOVE_TURN_RATE);assert(!f.session.kicks&&!f.session.movementChecks);auto current=f.session.sent.back();f.ack(current.counter,&f.player,current.speed,MOVE_TURN_RATE);assert(f.session.anti.speedChecks==1&&f.session.movementChecks==1&&f.session.lastPlayerMover==&f.player);}
 {Fixture f;f.send(&f.player);auto sent=f.session.sent.size();f.session.SetPlayer(&f.player,1);assert(f.session.m_pendingSpeedOrders.empty()&&f.session.anti.orders.empty()&&f.session.sent.size()==sent);}
 std::cout<<"PASS: Classic actual speed ACK handler, actor/control epoch, native order ownership, reordered/duplicate/late ACKs, correction and enforced current speed\n";
}
'''.replace('__RECORD__',record).replace('__NATIVE_METHODS__',native_methods).replace('__METHODS__',methods)
with tempfile.TemporaryDirectory(prefix='classic-speed-ack-') as folder:
    folder=Path(folder);(folder/'test.cpp').write_text(code)
    subprocess.run(['cl','/nologo','/EHsc','/std:c++17','test.cpp','/Fe:test.exe'],cwd=folder,check=True)
    subprocess.run([str(folder/'test.exe')],cwd=folder,check=True)
