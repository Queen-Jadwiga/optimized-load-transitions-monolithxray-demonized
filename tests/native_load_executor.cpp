// Standalone Windows/PPL tests of the actual engine executor header.
#define NOMINMAX
#include <cstdint>
#include <memory>
#include <future>
#include <iostream>
#include <stdexcept>
#include <chrono>
using u8 = std::uint8_t;
using u32 = std::uint32_t;
using u64 = std::uint64_t;
template<class T> using xalloc = std::allocator<T>;
#define IC inline
#include "../src/xrCore/_noncopyable.h"
#include "../src/xrCore/_thread_types.h"

static void require(bool value, const char* message)
{
    if (!value) throw std::runtime_error(message);
}

static void nested_batches()
{
    auto& executor = NativeLoadExecutor::Instance();
    const auto generation = executor.BeginGeneration();
    auto parents = executor.BeginBatch(generation);
    std::atomic_uint completed{0};
    // More parents than scheduler workers: nested waits must help their own batch.
    for (u32 i = 0; i < executor.WorkerLimit() + 2; ++i)
        require(executor.Submit(parents, NativeLoadPriority::Geometry, [&] {
            auto children = executor.BeginBatch(generation);
            for (u32 j = 0; j < 4; ++j)
                require(executor.Submit(children, NativeLoadPriority::Geometry,
                    [&] { ++completed; }), "child rejected");
            executor.Wait(children);
        }), "parent rejected");
    executor.Wait(parents);
    require(completed == (executor.WorkerLimit() + 2) * 4, "nested work lost");
    require(!executor.Submit(parents, NativeLoadPriority::Geometry, [] {}),
        "closed batch accepted work");
    executor.FinalizeGeneration(generation);
    require(executor.CurrentGeneration() == 0, "finalized generation retained");
}

static void failure_and_recovery()
{
    auto& executor = NativeLoadExecutor::Instance();
    const auto generation = executor.BeginGeneration();
    auto batch = executor.BeginBatch(generation);
    require(executor.Submit(batch, NativeLoadPriority::Spawn,
        [] { throw std::runtime_error("expected worker failure"); }), "failure task rejected");
    bool batch_failed = false;
    try { executor.Wait(batch); } catch (const std::runtime_error&) { batch_failed = true; }
    require(batch_failed, "worker exception lost by batch wait");
    bool generation_failed = false;
    try { executor.FinalizeGeneration(generation); }
    catch (const std::runtime_error&) { generation_failed = true; }
    require(generation_failed, "worker exception lost by finalization");
    require(executor.CurrentGeneration() == 0, "failed generation retained");
    nested_batches();
}

static void cancellation_joins_active_work()
{
    using namespace std::chrono_literals;
    auto& executor = NativeLoadExecutor::Instance();
    const auto generation = executor.BeginGeneration();
    auto batch = executor.BeginBatch(generation);
    std::promise<void> started;
    std::promise<void> release;
    auto gate = release.get_future().share();
    std::atomic_bool finished{false};
    require(executor.Submit(batch, NativeLoadPriority::Spawn, [&] {
        started.set_value();
        gate.wait();
        finished = true;
    }), "active task rejected");
    require(started.get_future().wait_for(10s) == std::future_status::ready,
        "worker did not start");
    auto cancel = std::async(std::launch::async, [&] { executor.CancelGeneration(generation); });
    const auto deadline = std::chrono::steady_clock::now() + 10s;
    while (executor.IsCurrent(generation) && std::chrono::steady_clock::now() < deadline)
        std::this_thread::yield();
    const bool marked_cancelled = !executor.IsCurrent(generation);
    const bool returned_early = cancel.wait_for(0s) == std::future_status::ready;
    // Release captures before any assertion can unwind their scope.
    release.set_value();
    cancel.get();
    require(marked_cancelled, "cancellation did not start");
    require(!returned_early, "cancellation returned while captures were in use");
    require(finished, "active task not joined");
    require(!executor.Submit(batch, NativeLoadPriority::Spawn, [] {}),
        "cancelled batch accepted work");
    require(!executor.BeginBatch(generation).Valid(), "stale generation accepted batch");
}

static void replacement_drains_previous_generation()
{
    auto& executor = NativeLoadExecutor::Instance();
    auto old_generation = executor.BeginGeneration();
    auto old_batch = executor.BeginBatch(old_generation);
    std::atomic_uint handled{0};
    for (u32 i = 0; i < 100; ++i)
        require(executor.Submit(old_batch, NativeLoadPriority::Speculative,
            [&] { ++handled; }, [&] { ++handled; }), "old task rejected");
    const auto generation = executor.BeginGeneration();
    require(handled == 100, "replacement lost execution/cancellation completion");
    require(!executor.IsCurrent(old_generation), "old generation still current");
    require(!executor.Submit(old_batch, NativeLoadPriority::Spawn, [] {}),
        "replacement accepted stale work");
    executor.FinalizeGeneration(generation);
}

int main()
{
    try
    {
        nested_batches();
        failure_and_recovery();
        cancellation_joins_active_work();
        replacement_drains_previous_generation();
        std::cout << "PASS: nested batches, failure/recovery, cancellation joins, replacement\n";
    }
    catch (const std::exception& e)
    {
        std::cerr << "FAIL: " << e.what() << '\n';
        return 1;
    }
}
