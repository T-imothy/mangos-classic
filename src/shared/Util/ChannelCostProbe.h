#ifndef MANTECH_CHANNEL_COST_PROBE_H
#define MANTECH_CHANNEL_COST_PROBE_H
#include <chrono>
#include <cstdint>
#ifdef _WIN32
#include <windows.h>
#else
#include <time.h>
#endif
namespace ManTech {
struct ThreadCpuSample { std::uint64_t microseconds = 0, cycles = 0; };
inline ThreadCpuSample ReadThreadCpu() {
    ThreadCpuSample result;
#ifdef _WIN32
    FILETIME created, exited, kernel, user;
    if (GetThreadTimes(GetCurrentThread(), &created, &exited, &kernel, &user)) {
        auto ticks = [](FILETIME t) { return (std::uint64_t(t.dwHighDateTime) << 32) | t.dwLowDateTime; };
        result.microseconds = (ticks(kernel) + ticks(user)) / 10;
    }
    ULONG64 cycles = 0;
    if (QueryThreadCycleTime(GetCurrentThread(), &cycles)) result.cycles = cycles;
#else
    timespec value{};
    if (clock_gettime(CLOCK_THREAD_CPUTIME_ID, &value) == 0)
        result.microseconds = std::uint64_t(value.tv_sec) * 1000000 + value.tv_nsec / 1000;
#endif
    return result;
}
inline ThreadCpuSample CpuDelta(ThreadCpuSample end, ThreadCpuSample begin) {
    return {end.microseconds >= begin.microseconds ? end.microseconds - begin.microseconds : 0,
        end.cycles >= begin.cycles ? end.cycles - begin.cycles : 0};
}
// Diagnostic wall/CPU time. Thread-local counters avoid adding a shared lock
// to the broadcast path; Map::Update reads a delta on its own worker thread.
struct ChannelCostSample {
    std::uint64_t microseconds = 0, calls = 0, recipients = 0;
    std::uint64_t cpuMicroseconds = 0;
};
inline thread_local ChannelCostSample channelCost;
struct IdleBotCostSample {
    ChannelCostSample chat;
    std::uint64_t elapsedUs = 0;
    ThreadCpuSample cpu;
};
class ChannelCostScope {
    std::chrono::steady_clock::time_point started = std::chrono::steady_clock::now();
    ThreadCpuSample cpuStarted = ReadThreadCpu();
    std::uint64_t recipients;
public:
    explicit ChannelCostScope(std::uint64_t count) : recipients(count) {}
    ~ChannelCostScope() {
        channelCost.cpuMicroseconds += CpuDelta(ReadThreadCpu(), cpuStarted).microseconds;
        channelCost.microseconds += std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - started).count();
        ++channelCost.calls;
        channelCost.recipients += recipients;
    }
};
}
#endif
