# First in-game test

Use the [verified build run](BUILD_2026-10-16.md) for the exact candidate commit. The artifact named
`unverified-mt-DX11-AVX` is a compile artifact, not a stable release or a measured
speedup. It targets Windows x64 MT, DX11 with AVX. Other renderers are unverified.

Test with copies of saves and the same October 11 engine gamedata dependencies.
Keep the same MO2/game profile, installed gameplay mods and graphics settings. Preserve the original executable so returning to the baseline
is a file replacement. Do not combine candidate engine components with arbitrary
components from another build. The `License.txt` must accompany redistribution.

Extract `_build/_game/bin_dbg/AnomalyDX11AVX.exe` from the binary artifact ZIP.
Back up the existing `bin/AnomalyDX11AVX.exe`, then copy the candidate into its
place. Keep the matching PDB for crash analysis.

1. Launch using the same MO2/game profile and the candidate executable. Load a
   familiar save and reach actual player control.
2. Check textures, lighting, HUD, sound, NPCs and basic movement. Reload that save.
3. Transition to a neighboring map, then return. Check that collision, static
   objects, visuals and controls remain correct after the cached return.
4. Return to the menu and exit. Keep the full log, including any crash tail.

No stopwatch timing is needed for this first compatibility check. The new engine
logs startup and load-session phases automatically. Send the log and describe
anything visibly wrong. The engine-ready metric excludes time spent waiting for
user input, but it is not a measurement of the precise displayed loading-screen
frame. Launcher delay before the executable starts is outside that metric.

If this passes, use the paired scenarios in [VALIDATION.md](VALIDATION.md) to
measure performance and test longer transition loops, memory growth, failure
handling and device resets. A simple smoke test does not establish those cases.

This integration does not add transition damage protection. The reported gap
between confirmation and the loading screen remains a separate issue to fix and
verify.
