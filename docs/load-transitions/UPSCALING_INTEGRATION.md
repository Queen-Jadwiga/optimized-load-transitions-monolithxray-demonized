# Native upscaling integration

Branch: `experimental/pr614-upscaling-oct11`.

Sources:

- Load-only integration: `7f5936cd6bb6923f3686fe213db3edfbe5fe8f1c` (documentation
  successor of compiled source `6b791e720fc1e7ad415c8aaf5638722b4e936ac3`).
- brodrigz/xray-monolith native-upscaling 0.5, tag `1.0.1`, commit
  `854dd2795203f8bd8992cb5a0c9646b57804652e`.
- Common engine baseline: `871e2491228a64f0d5e257c7a7e0255feb841ac8`.

Two textual conflicts were reconciled: retain renderer startup measurement while
initializing upscaler targets inside the measured constructor, and retain fluid
startup measurement while using the upscaler scene dimensions. Device creation
changes merged with PR #614's existing device flags. NGX/FSR initialization stays
in target/device creation; it is not moved onto loading workers. The imported
renderer invalidates temporal history on loading/menu paths and separates scope
frames. This integration additionally invalidates both upscaler histories in
the owner-thread level_BeginAsyncLoad hook: cached map returns and skipped
precache world renders must not reuse history from the previous level.
Settings changes trigger target recreation and the existing static-cache
release path. These source observations are not a concurrency or runtime proof.

The original temporal, sampler, sharpening, PDA-depth, backend and UI tests are
retained. The Lua test runner accepts the built engine's Release/Release-AVX Lua
library configuration. CI runs the PPL lifecycle tests, temporal contract and UI
tests, plus D3D11 WARP sampler/CAS/PDA-depth tests. Hardware NGX evaluation requires
an RTX machine and is not claimed from hosted CI. WARP FSR and hardware backend
tests remain available in tools/dlss; they are not part of the initial CI gate.

Local Python metric tests and the portable temporal contract test pass. The
combined FOMOD packs successfully and all installer source paths are checked.
Windows compilation, software-renderer tests and in-game checks are pending.

Packaging includes original licenses/credits and a SHA256-pinned NVIDIA release
runtime downloaded from its official repository. Runtime DLLs are not committed.
No upstream pull request is opened. No runtime or performance claim is made.

See [COMBINED_TEST.md](COMBINED_TEST.md) for installation and initial tests.
