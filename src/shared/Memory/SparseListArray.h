#ifndef MANTECH_SPARSE_LIST_ARRAY_H
#define MANTECH_SPARSE_LIST_ARRAY_H
#include "Memory/MemoryLedger.h"
#include <array>
#include <atomic>
#include <list>
#include <memory>
#include <cassert>

namespace ManTech
{
// Unused types do not require a list sentinel. Exposed references and end
// iterators remain valid until owner destruction, even across empty/nonempty
// transitions. Only publication is synchronized; list mutation still follows
// the owning Unit's existing thread rules.
template<class T, std::size_t N>
class SparseListArray
{
    using List = std::list<T>;
    mutable std::array<std::atomic<List*>, N> buckets{};
public:
    SparseListArray() = default;
    SparseListArray(SparseListArray const&) = delete;
    SparseListArray& operator=(SparseListArray const&) = delete;
    ~SparseListArray()
    {
        for (auto const& bucket : buckets)
            if (auto list = bucket.load(std::memory_order_relaxed))
            {
                delete list;
                MemoryLedger::Remove(MemoryKind::AuraBuckets, sizeof(List));
            }
    }
    // Internal non-escaping read. Use Stable when returning a reference to a
    // caller that could retain it across later aura additions.
    List const& operator[](std::size_t index) const
    {
        assert(index < N);
        static List const empty;
        auto list = buckets[index].load(std::memory_order_acquire);
        return list ? *list : empty;
    }
    List const& Stable(std::size_t index) const
    {
        assert(index < N);
        auto list = buckets[index].load(std::memory_order_acquire);
        if (!list)
        {
            auto candidate = std::make_unique<List>();
            if (buckets[index].compare_exchange_strong(list, candidate.get(), std::memory_order_acq_rel))
            {
                list = candidate.release();
                MemoryLedger::Add(MemoryKind::AuraBuckets, sizeof(List));
            }
        }
        return *list;
    }
    List& Mutable(std::size_t index)
    {
        return const_cast<List&>(Stable(index));
    }
};
}
#endif
