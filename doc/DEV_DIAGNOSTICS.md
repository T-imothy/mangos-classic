# DEV runtime diagnostics

Build with MANTECH_DEV_DIAGNOSTICS=ON on Windows. It defaults OFF and must stay
OFF for production builds. MANTECH_PROFILE_ALLOCATIONS=ON provides on-demand
allocation capture; Memory.SampleAllocations stays 0, so allocation sampling is
not enabled during ordinary DEV running. These options do not limit realm RAM,
entity populations, map loading, simulation cadence or gameplay caches.

Timing scopes record exact call counts and sampled inclusive durations. Detailed
operations sample every 32 invocations per thread; world/map/worker scopes record
each invocation. Per-thread atomic storage avoids shared hot-path locks. Labels
are evaluated only for sampled invocations. CPU clocks are recorded for major
world/map/worker scopes; small scopes record wall time only. Windows thread CPU
time has coarse resolution and cannot identify every wait reason.

A background observer publishes logs/DevDiagnostics-latest.json and bounded
history every 10 seconds. Fixed histogram buckets report percentile upper bounds.
Counters are cumulative, concurrent observations; viewers use differences for
window rates. Inclusive scopes and parallel workers must not be added together
as world elapsed time. Timeline lanes retain map/instance context across worker
handoffs and include map queue and barrier waits.

Write one command to logs/DevDiagnostics.control:

- capture N: an instrumented-scope timeline lasting 1–30 seconds.
- memory N: sample new C++ allocations for 1–60 seconds, then stop new samples
  and symbolize a retained-allocation snapshot on the observer thread.
- enabled 0 / enabled 1: disable / enable timing instrumentation at runtime.

Timing buffers, label tables and trace rings have fixed capacities; overflow
counts are visible. Overflow drops diagnostic observations, never gameplay work.
Four trace files and eight allocation TSV files are rotated. History uses two
bounded files. The fixed diagnostic capacity is exposed separately in memory
output, including allocation tables. These capacities are NOT a server RAM cap.

Memory output includes process private bytes/working set, committed private,
image and mapped address ranges, reserved address space, entity counts and the
existing partial subsystem ledger. Ledger categories can overlap and are not
subtracted into a misleading "leak" remainder. Growth with growing entity/cache
counts differs from growth with stable counts. Allocation captures exclude
pre-existing allocations, arbitrary malloc calls and external DLL heaps. The
free-side Bloom filter skips definitely untracked pointers; sampled frees remain
tracked after capture ends. Dropped allocations/sites are reported in every TSV.

Instrumented timelines are NOT sampled CPU call stacks. Native Windows CPU stack
tracing is a separate capability; this host currently rejects WPR's profiling
privilege. Do not change machine policy or pretend an ETW capture succeeded.

Native tests cover bucket boundaries/percentiles, counts, concurrent snapshots,
stable fixed capacity, trace overflow, publication, and allocation/free tracking
across a stopped capture. Runtime validation must also measure enabled/disabled
overhead at equal population. Diagnostic data identifies candidates for changes;
it does not itself prove a leak or certify a gameplay rewrite.
