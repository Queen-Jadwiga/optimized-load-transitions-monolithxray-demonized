# Optimized Load & Transitions for Demonized Modded EXE - Monolith X-ray Engine

Experimental engine work for faster startup, save loading, and level transitions in S.T.A.L.K.E.R. Anomaly/GAMMA. The goal is to preserve installed gameplay mods, save compatibility, and ordered Lua/object lifecycle behavior.

**Current status: source baseline and initial PR review. No improved executable has been built or benchmarked by this project.**

This repository starts from themrdemonized's October 11, 2026 MT branch. It retains the engine source, history, original license, and third-party notices. The unmodified upstream README is preserved at [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md).

## Source branches

| Branch | Purpose |
|---|---|
| `main` | October 11 MT source plus project documentation and benchmark tooling; engine behavior unchanged |
| `upstream/oct11-mt` | Exact upstream MT baseline `871e2491228a64f0d5e257c7a7e0255feb841ac8` |
| `reference/pr-614` | Unmodified PR #614 head `8b3d9be9935f7f0aa2a315678977882a03cb64de`, credited to qkff99 |

The original PR is [MT/R4: parallel level loading and faster startup](https://github.com/themrdemonized/xray-monolith/pull/614). Its code is not merged into `main`: a three-way integration with the pinned MT baseline conflicts in nine files. Preservation on a reference branch is not compatibility certification.

Read the [initial review](docs/load-transitions/PR614_REVIEW.md), [source provenance](docs/load-transitions/SOURCES.json), and [validation plan](docs/load-transitions/VALIDATION.md).

## Approach

1. Retain complete attribution and pin the compared revisions.
2. Separate load-session measurement, startup/VFS changes, native preparation, caching, and precache rendering into reviewable changes.
3. Keep Lua, object spawning, and renderer publication on their required threads.
4. Verify failure, cancellation, shutdown, device reset, and cache invalidation before distributing a candidate.
5. Benchmark complete engine-ready time separately from partial phase timings and manual user wait.

Initial targets are Windows x64 MT DX11 and DX11-AVX. No compatibility claim is made for other renderers. There is no release to install yet.

## Benchmark tooling

With Python 3.10 or newer:

```sh
python tools/summarize_loading.py baseline=baseline.log candidate=candidate.log
python -m unittest discover -s tests -v
```

The CSV reports medians, ranges, and counts, grouped by build and scenario. It never sums overlapping phase measurements or mixes the legacy partial load metric with full engine-ready timing. It does not upload logs.

The manual Windows workflow builds the selected source ref as a **compile check** and stores artifacts; success does not establish runtime compatibility or a speedup. The inherited upstream release workflow is restricted to its original branch and is not the project release process.

## Credits and terms

Engine foundation: GSC Game World and the upstream X-Ray/Anomaly/Monolith contributors. Monolith maintenance: [themrdemonized](https://github.com/themrdemonized/xray-monolith). PR #614 implementation: [qkff99](https://github.com/qkff99/xray-monolith), with AI assistance disclosed by its author.

[License.txt](License.txt) and existing third-party licenses remain in force. Engine redistribution is noncommercial under the upstream terms. This project is independent and is not an official Demonized release.
