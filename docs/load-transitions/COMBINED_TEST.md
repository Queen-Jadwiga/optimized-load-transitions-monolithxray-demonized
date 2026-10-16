# Combined Test 1: loading improvements and native DLSS/FSR

Experimental Windows x64 MT DX11 candidate. It combines our October 11 PR #614
integration with brodrigz/bepis native-upscaling 0.5, source tag `1.0.1` at
`854dd2795203f8bd8992cb5a0c9646b57804652e`. Original implementation and notices
are preserved, including OGSR, NVIDIA, AMD and shader authors. No frame generation.
The FSR 3.1.2 DX11 backend is a community port. Loading work originates from
qkff99 PR #614; Monolith maintenance is by themrdemonized, with engine foundations
by GSC/Anomaly and the upstream contributors.

## Installation

1. Keep copies of your original executable, any existing `nvngx_dlss.dll`,
   saves and graphics configuration. Use the same MO2 profile and gameplay mods.
2. Extract `combined-load-upscaling-test1-DX11-AVX.zip` into the Anomaly root.
   Its `bin` directory contains our combined `AnomalyDX11AVX.exe`, matching PDB
   and the pinned NVIDIA runtime. The other files contain instructions/notices.
3. Install `combined-upscaling-compatibility-test1.zip` as a mod in MO2. This is
   mandatory for the upscaling integration, including its UI. Select your actual
   Atmospherics version and only the optional add-ons you have installed. Put
   it below SSS/Atmospherics/NVG/WearableDevices shader mods so its overrides win.
   Disable any older DLSS/FSR compatibility overrides. Keep the original mods.
4. Requires SSS 23.5 with motion vectors and GAMMA's recommended options. Clear
   the shader cache once through the launcher. Set MSAA and SSS TAA to Off.
5. Launch the candidate through MO2. Under Video > Basic choose Upscaling Off
   for the first load/save/transition test. Then test DLSS Quality, Apply, and
   repeat the same scenario. DLAA or FSR can be tested afterward. Mode/quality
   changes restart the renderer. No special Windows launch argument is needed.

The package does not replace the baseline engine gamedata database. The FOMOD
contains the added scripts, localization and shaders required by this integration.
The existing October 11 engine dependencies and full original shader mods remain
necessary. Turning upscaling Off retains the combined engine and shader patches;
compare against the separate load-only build for a true code-baseline comparison.

## What to check

Check load/reload, transition out and back, controls, camera movement, grass,
smoke/fire, HUD weapons, PDA text/occlusion, scopes, NVGs and gas-mask overlays.
Test returning to menu and exiting. A successful initialization message is not
an active DLSS evaluation: the log must show `[DLSS] ACTIVE` or `[FSR3] ACTIVE`.
A red fallback warning means native/spatial fallback, not successful upscaling.
Send the full log and any visible issue; no stopwatch is needed for this first
compatibility test. The loading phase instrumentation is retained.

DLSS needs an NGX-compatible RTX GPU/driver. FSR needs Direct3D feature level 11.1.
The pinned NVIDIA release runtime is 310.9.1; its SHA256 is recorded in
`PROVENANCE.json`. Only one upscaler runs. Image quality, game performance, HDR10,
mod interactions and GPU memory behavior need in-game validation. CPU/WARP tests
cannot establish RTX DLSS behavior. Transition damage protection is not included.

## Reverting

Disable the combined compatibility mod in MO2, restore your previous executable
and runtime DLL (or remove the added DLL if none existed), restore your graphics
configuration and clear the shader cache. Use the original profile/mod settings.
Keep the matching candidate PDB with crash evidence if reporting a problem.
