#ifndef MANTECH_CHANNEL_COST_PROBE_H
#define MANTECH_CHANNEL_COST_PROBE_H
#include <chrono>
#include <cstdint>
namespace ManTech {
// Diagnostic wall time only. Thread-local counters avoid adding a shared lock
// to the broadcast path; Map::Update reads a delta on its own worker thread.
struct ChannelCostSample {
    std::uint64_t microseconds = 0, calls = 0, recipients = 0;
};
inline thread_local ChannelCostSample channelCost;
struct IdleBotCostSample {
    ChannelCostSample chat;
    std::uint64_t elapsedUs = 0;
};
class ChannelCostScope {
    std::chrono::steady_clock::time_point started = std::chrono::steady_clock::now();
    std::uint64_t recipients;
public:
    explicit ChannelCostScope(std::uint64_t count) : recipients(count) {}
    ~ChannelCostScope() {
        channelCost.microseconds += std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - started).count();
        ++channelCost.calls;
        channelCost.recipients += recipients;
    }
};
}
#endif
