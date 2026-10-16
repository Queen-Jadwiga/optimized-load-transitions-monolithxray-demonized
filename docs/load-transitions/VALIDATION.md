# Build and runtime comparison protocol

## Reproducible source

Use the pinned upstream MT baseline and a separately named candidate commit. Record configuration, compiler/toolset, binary hashes and relevant console settings. Keep the same GAMMA/MO2 profile, installed mods, saves, driver, renderer and graphics settings. Avoid changing the mod list between the paired runs.

Build the same Windows x64 DX11 or DX11-AVX configuration for both revisions. The experimental branch runs a Windows compile workflow; inspect the latest run and exact commit before treating compilation as verified. It includes standalone tests against the actual PPL executor header for nested batches, failure recovery, cancellation joins, and generation replacement. These do not test D3D ownership or prove game compatibility. The local development environment is Linux and cannot validate the Windows engine binary. Preserve PDBs for crashes. Include upstream notices with any distributed binaries.

## Performance scenarios

Test startup to menu, first menu save load, same-map reload, transition to an unvisited map, and return to a visited map separately. Take at least three paired warm-cache runs per scenario and report median and range. Record cold-start runs separately with a clear definition of cold; restarting the process does not clear the OS filesystem cache. Never present the legacy partial `total loading time` result as the full player's wait.

Record transition confirmation to the first loading-screen frame; loading-screen start to engine ready; and readiness to actual player control separately. Human waiting at the key prompt must not inflate engine work time. Existing Lua diagnostics can explain sequential costs but do not measure the exact displayed frame. Native phase times can overlap; do not add them into a false total.

Use `tools/summarize_loading.py` to group supported logged metrics. It reports sample counts so one-off runs are visible. A successful compile or a lower partial metric is not a release gate by itself.

## Compatibility and stress cases

Exercise repeated out-and-back transitions, reload after death, main-menu return, new game, cancelled/failed loads, quit during work, and device reset/settings changes. Check missing-file and resource failure handling, background sound prefetch, cache hit/miss correctness, and shader/texture consistency. Compare object IDs, spawn/event order, save restoration, NPC and actor state, and callback counts. Do not parallelize Lua or net_Spawn as a shortcut.

Monitor process committed memory, RAM and dedicated/shared GPU memory across many maps. Confirm eviction and worker/resource cleanup. A process-local cache must not reuse stale data after relevant changes. Check visual temporal effects and first-frame responsiveness when reducing warmup rendering.

For transition protection, test acceptance, rejection, failure, save/load and recovery. Protection must not persist into ordinary gameplay or leak into saved state. Avoid merely restoring health after a fatal hit. Confirm that any pause/protection mechanism cannot prevent the transition request from being processed.

## Release evidence

An experimental binary needs a coherent Windows build, runtime smoke tests and explicit remaining limitations. A public speedup claim needs paired measurements of the relevant end-to-end scenario. Preserve credit for PR #614 and upstream changes; submit upstream-ready changes as reviewable patches when validated.
