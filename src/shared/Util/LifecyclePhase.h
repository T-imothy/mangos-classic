#ifndef MANTECH_LIFECYCLE_PHASE_H
#define MANTECH_LIFECYCLE_PHASE_H
#include "Log/Log.h"
#include <chrono>
#ifdef _WIN32
#include <windows.h>
#endif

// Used only around coarse startup/shutdown operations, never in update loops.
class LifecyclePhase
{
    struct Snapshot
    {
        unsigned long long cpuMs=0, readBytes=0, writeBytes=0, reads=0, writes=0, availableMb=0;
        bool valid=false;
    };
    static Snapshot Capture()
    {
        Snapshot s;
#ifdef _WIN32
        FILETIME created{}, exited{}, kernel{}, user{};
        IO_COUNTERS io{}; MEMORYSTATUSEX mem{}; mem.dwLength=sizeof(mem);
        if (GetProcessTimes(GetCurrentProcess(), &created, &exited, &kernel, &user) &&
            GetProcessIoCounters(GetCurrentProcess(), &io) && GlobalMemoryStatusEx(&mem))
        {
            auto ticks=[](FILETIME t) { return (static_cast<unsigned long long>(t.dwHighDateTime)<<32)|t.dwLowDateTime; };
            s.cpuMs=(ticks(kernel)+ticks(user))/10000;
            s.readBytes=io.ReadTransferCount; s.writeBytes=io.WriteTransferCount;
            s.reads=io.ReadOperationCount; s.writes=io.WriteOperationCount;
            s.availableMb=mem.ullAvailPhys/(1024*1024); s.valid=true;
        }
#endif
        return s;
    }
    const char* name;
    std::chrono::steady_clock::time_point started;
    Snapshot before;
public:
    explicit LifecyclePhase(const char* label):name(label),started(std::chrono::steady_clock::now()),before(Capture())
    { sLog.outString("LIFECYCLE_PHASE begin=%s",name); }
    ~LifecyclePhase()
    {
        auto after=Capture();
        const bool valid=before.valid && after.valid;
        if (!valid) after=before;
        const auto ms=std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-started).count();
        sLog.outString("LIFECYCLE_PHASE end=%s wall_ms=%llu counters_valid=%u cpu_ms=%llu process_read_bytes=%llu process_write_bytes=%llu process_reads=%llu process_writes=%llu available_mb_before=%llu available_mb_after=%llu",
            name,static_cast<unsigned long long>(ms),valid?1u:0u,
            after.cpuMs-before.cpuMs,after.readBytes-before.readBytes,after.writeBytes-before.writeBytes,
            after.reads-before.reads,after.writes-before.writes,before.availableMb,after.availableMb);
    }
};
#endif
