#ifndef MANTECH_ALLOCATION_PROFILE_H
#define MANTECH_ALLOCATION_PROFILE_H
#include <cstddef>
namespace ManTech {
// Diagnostic hooks are registered before main only in an opt-in profile build.
inline void (*allocationProfileStart)(unsigned) = nullptr;
inline void (*allocationProfileWrite)() = nullptr;
inline void (*allocationProfileStop)() = nullptr;
inline std::size_t (*allocationProfileCapacity)() = nullptr;
inline std::size_t AllocationProfileCapacity(){return allocationProfileCapacity?allocationProfileCapacity():0;}
inline void StopAllocationProfile(){if(allocationProfileStop)allocationProfileStop();}
inline void StartAllocationProfile(unsigned mask=1023) { if (allocationProfileStart) allocationProfileStart(mask); }
inline void WriteAllocationProfile() { if (allocationProfileWrite) allocationProfileWrite(); }
}
#endif
