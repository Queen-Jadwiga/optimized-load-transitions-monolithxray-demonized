# PR #614 initial compatibility review — 2026-10-16

This is the historical pre-integration review. See [PR614_INTEGRATION.md](PR614_INTEGRATION.md) for subsequent experimental work.

## Decision

Preserve the original PR as a reference; do not merge or label it tested on October 11 MT yet. Git's three-way merge reports nine conflicted files. This is a compatibility review and a focused reading of loading/caching/measurement code, not an exhaustive concurrency audit of all 144 changed files.

## Pinned comparison

- Upstream MT: `871e2491228a64f0d5e257c7a7e0255feb841ac8`, October 11, 2026.
- Upstream release tag `2026.10.11`: `c57fe5b9fab4fe0506659db03137c52d2500eb2f`. The release tag and MT head are different commits; do not silently substitute the standard-tag tree for the MT baseline. Matching the date is not proof of a locally installed binary's exact build provenance.
- PR merge base: `3cb176018bc16a8b7911fe42157a15e2b6c520cc`.
- PR head: `8b3d9be9935f7f0aa2a315678977882a03cb64de` (qkff99).
- PR change size against its merge base: 144 files, 9,428 additions, 1,772 deletions.
- Live PR metadata at review time: open, unmerged, `mergeable=false`.

## Confirmed integration conflicts

| File | Integration concern |
|---|---|
| `src/Layers/xrRender/ResourceManager.cpp` | Resource ownership, preparation and current renderer changes |
| `src/Layers/xrRender/ResourceManager.h` | Matching resource APIs and layout |
| `src/Layers/xrRender/TextureDescrManager.cpp` | Texture metadata loading and synchronization |
| `src/Layers/xrRender/TextureDescrManager.h` | Metadata API and lock declarations |
| `src/Layers/xrRender/dxRenderDeviceRender.cpp` | Owner-thread resource publication |
| `src/Layers/xrRenderDX10/dx10SH_Texture.cpp` | Texture load/create behavior |
| `src/Layers/xrRenderPC_R4/r4.cpp` | Renderer startup, cache lifecycle and teardown |
| `src/xrCDB/xr_area.cpp` | Collision-data preparation and ownership |
| `src/xrEngine/x_ray.cpp` | Startup and application/load-session lifecycle |

A clean textual merge of other files would not prove semantic compatibility. Interface changes require a coherent full build; selected patched engine components must not be mixed casually with DLLs from another revision.

## Useful mechanisms in the reference implementation

- Native preparation is grouped by generation/batch, while script and object lifecycle work remains ordered.
- `r4_loader.cpp` separates preparation from owner-thread attachment and includes a process-local static level cache.
- Cache identity includes level-file metadata, creation-related renderer options, detail settings, and an asset generation. This is more than a cache keyed only by map name.
- `EvictLevelCacheUnderPressure` evicts while available system RAM falls below the greater of 2 GiB and 15% of physical RAM. This specific policy uses system RAM, not a demonstrated VRAM budget. A VRAM-specific audit remains necessary; this observation does not establish that the cache is unsafe.
- `LoadSessionTryFinish` waits for readiness and resource generation completion, destroys necessary textures, and emits an engine-ready result and phase data.
- Precache telemetry separates frame movement, rendering, presentation, and waits. The PR description says all logical precache frames remain while world-render calls are reduced. Compatibility of shader warmup, temporal effects, and gameplay callbacks requires runtime verification.

## Initial priorities

1. Bring full-session timing onto the October 11 MT baseline first, including transition request, teardown, resource wait, key-prompt preparation, and input restoration. Keep user input wait separate from engine work.
2. Review VFS/startup optimizations separately from the renderer/cache rewrite.
3. Reconcile the nine conflicts preserving current upstream behavior, then compile the coherent MT target.
4. Audit batch cancellation, generation replacement, worker joins, device reset and shutdown, cache invalidation, and D3D immediate-context ownership before enabling the candidate.
5. Evaluate a cache budget or explicit experimental switches only after measuring memory behavior. Do not claim the existing implementation has no eviction.
6. Investigate transition safety separately. Native `CChangeLevelWnd::OnOk` closes the dialog before sending the transition packet; `Hide` unpauses. The ALife before-change callback is executed later when processing the request. This source ordering does not prove where the complete reported black-screen interval occurs.

## What current measurements establish

A local GAMMA diagnostic run identified around 4.8–5.0 seconds in repeated Lua module/startup work and 2.4–2.8 seconds in first-update callbacks. Final Lua cleanup was about 66–77 ms. These are observations from the existing executable, not performance results of this fork or of PR #614. No user logs, save files, installation paths or personal information are committed here.

The earlier PR author reports improvements in partial native loading metrics, especially new-level transitions, with much smaller warm-save gains and a vanilla warm-save regression. These are author-reported single runs. They are not this project's benchmarks and do not establish the same speedup for the full loading-screen wait.

## Validation state

- Retrieved and pinned both source histories: complete.
- Reproduced three-way conflicts without modifying the engine working tree: complete.
- Read selected startup, readiness, precache and cache lifecycle implementation: complete.
- Python benchmark tooling unit tests: run separately and recorded in project work.
- PR integration, Windows compilation, native runtime tests, independent performance measurements: **not performed**.

No claim is made that a newer AI model has improved the engine. Future claims must identify the actual code change, validation and measured outcome.
