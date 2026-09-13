#include "Memory/SparseListArray.h"
#include "Memory/WriteBudget.h"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <thread>
#include <vector>

#define CHECK(x) do { if (!(x)) { std::cerr << __LINE__ << ": " #x " failed\n"; std::abort(); } } while (false)

int main()
{
    using namespace ManTech;
    const auto before = MemoryLedger::Read(MemoryKind::AuraBuckets);
    {
        SparseListArray<int, 317> first, second;
        for (unsigned i = 0; i < 317; ++i)
            CHECK(first[i].empty());
        CHECK(MemoryLedger::Read(MemoryKind::AuraBuckets).count == before.count);
        auto& list = first.Mutable(42);
        list.push_back(1);
        list.push_back(2);
        auto iterator = list.begin();
        auto end = list.end();
        list.push_back(3);
        list.remove(2);
        CHECK(*iterator == 1 && end == list.end());
        CHECK(second[42].empty());
        list.clear();
        CHECK(end == first[42].end());
        first.Mutable(42).push_back(4);
        CHECK(end == first[42].end());
        CHECK(MemoryLedger::Read(MemoryKind::AuraBuckets).count == before.count + 1);
    }
    CHECK(MemoryLedger::Read(MemoryKind::AuraBuckets).bytes == before.bytes);

    {
        SparseListArray<int,317> owner;
        auto const& emptyReference=owner.Stable(7);
        auto emptyEnd=emptyReference.end();
        CHECK(emptyReference.empty());
        owner.Mutable(7).push_back(9);
        CHECK(emptyReference.front()==9 && emptyReference.end()==emptyEnd);
        std::vector<std::thread> readers;
        for(int i=0;i<8;++i)
            readers.emplace_back([&] {
                for(int n=0;n<1000;++n)
                    CHECK(&owner.Stable(8)==&owner.Stable(8));
            });
        for(auto& reader:readers)reader.join();
        CHECK(MemoryLedger::Read(MemoryKind::AuraBuckets).count==before.count+2);
    }
    CHECK(MemoryLedger::Read(MemoryKind::AuraBuckets).bytes == before.bytes);

    std::shared_ptr<WriteBudget::Token> survivor;
    {
        WriteBudget first, second;
        auto one = first.Acquire(64, 100, 128);
        CHECK(one);
        CHECK(!first.Acquire(37, 100, 128));
        CHECK(!second.Acquire(65, 100, 128));
        survivor = second.Acquire(64, 100, 128);
        CHECK(survivor);
        CHECK(!first.Acquire(std::numeric_limits<std::size_t>::max(), 100, 128));
    }
    CHECK(MemoryLedger::Read(MemoryKind::Network).bytes == 64);
    survivor.reset();
    CHECK(MemoryLedger::Read(MemoryKind::Network).bytes == 0);
    {
        WriteBudget budget;
        std::vector<std::thread> threads;
        for (int i = 0; i < 8; ++i)
            threads.emplace_back([&] {
                for (int j = 0; j < 10000; ++j)
                {
                    auto token = budget.Acquire(64, 256, 256);
                    CHECK(MemoryLedger::Read(MemoryKind::Network).bytes <= 256);
                }
            });
        for (auto& thread : threads)
            thread.join();
    }
    CHECK(MemoryLedger::Read(MemoryKind::Network).count == 0);
    CHECK(MemoryLedger::Read(MemoryKind::Network).bytes == 0);
    std::cout << "Sparse aura lifetime/iterator tests and concurrent write budget tests passed\n";
}
