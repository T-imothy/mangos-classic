#include "Util/DevDiagnosticsService.h"
#include <iostream>
#include <cstdlib>
#include <vector>
using namespace ManTech::Diag;
void check(bool v){if(!v)std::abort();}
int main(){
    check(Bucket(0)==0&&Bucket(127999)==127&&Bucket(128000)==128&&Bucket(9999999)==255);
    std::array<std::uint64_t,Bins> h{};h[0]=50;h[1]=45;h[200]=4;h[255]=1;
    check(Percentile(h,50)==1000&&Percentile(h,95)==2000&&Percentile(h,99)==Upper(200));
    auto baseline=sizeof(Threads)+sizeof(Labels);check(baseline<32*1024*1024);
    TraceGeneration=1;TraceDeadline=Now()+30000000;
    {MapContext c(70,17);Scope s(Metric::Map);check(Context==((70ULL<<32)|17));}
    check(Context==0);
    auto thread=GetThread();auto before=thread->stats[unsigned(Metric::Path)].samples.load();
    {Scope s(Metric::Path,1,"path example");s.Finish();s.Finish();}
    check(thread->stats[unsigned(Metric::Path)].samples.load()==before+1);
    Enabled=false;{Scope s(Metric::Path,1,"disabled");}Enabled=true;
    check(thread->stats[unsigned(Metric::Path)].samples.load()==before+1);
    std::vector<std::thread> workers;std::atomic<bool> done{false};
    std::thread reader([&]{while(!done){auto snapshot=Snapshot();check(snapshot.find("histogram")!=std::string::npos);}});
    for(unsigned n=0;n<8;++n)workers.emplace_back([]{for(unsigned i=0;i<8192;++i){Scope s(Metric::BotValue,32,"sample value");}});
    for(auto& w:workers)w.join();done=true;reader.join();
    std::uint64_t calls=0,samples=0;for(auto& t:Threads){calls+=t.stats[unsigned(Metric::BotValue)].calls.load();samples+=t.stats[unsigned(Metric::BotValue)].samples.load();}
    check(calls==65536&&samples==2048);
    for(unsigned i=0;i<TraceCapacity+30;++i){Scope s(Metric::Path,1,"ring overflow");}
    check(thread->eventCount.load()>TraceCapacity);
    std::filesystem::create_directories("logs");SaveTrace(1);auto snap=Snapshot();Publish("logs/test.json",snap);
    std::ifstream f("logs/DevDiagnostics-trace-1.json");std::string trace((std::istreambuf_iterator<char>(f)),{});
    check(trace.find("overwritten_records")!=std::string::npos&&trace.find("ring overflow")!=std::string::npos);
    auto start=Now();for(unsigned i=0;i<1000000;++i){Scope s(Metric::BotValue,32,"overhead fixture");}auto on=Now()-start;
    Enabled=false;start=Now();for(unsigned i=0;i<1000000;++i){Scope s(Metric::BotValue,32,"overhead fixture");}auto off=Now()-start;
    std::cout<<"fixed_capacity_bytes="<<baseline<<" scoped_calls=1000000 enabled_us="<<on<<" disabled_us="<<off<<"\n";
    check(Assigned.load()<=MaxThreads);std::cout<<"diagnostic concurrency, counts, histogram, overflow and publication checks passed\n";
}
