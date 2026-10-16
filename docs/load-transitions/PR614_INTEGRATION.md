# Experimental October 11 integration

Branch: `experimental/pr614-oct11`. Main remains the unmodified engine baseline.

Merged qkff99 PR #614 at `8b3d9be9935f7f0aa2a315678977882a03cb64de`
into MT baseline `871e2491228a64f0d5e257c7a7e0255feb841ac8`.
Original authorship and merge ancestry are retained.

## Conflict resolutions

- Keep the PR lifetime-owning texture queue and deferred texture references.
- Preserve October 11 asynchronous evicted-texture reloads through that queue;
  remove the obsolete global task-group declaration.
- Preserve `_FindTexture`, shader-bus texture aliases and shader defines.
- Keep parallel THM reads, deterministic game/level merge, then October 11 LTX
  fallbacks. THM metadata retains precedence over either source of LTX metadata.
- Preserve October 11 collision array publication and reader closure on the
  loading thread; only tree construction runs in the background. Wait for any
  previous tree job before replacing arrays. Do not reuse the PR reader-capturing
  worker, which conflicts with the newer lifetime fix.
- Retain RenderDoc initialization alongside new startup timing output.

## Additional compatibility corrections

- Preserve the full collision model status when swapping cached models. The
  newer baseline uses three integer states; the PR's Boolean temporary would
  collapse a failed/building state into initialized.
- Match non-creating texture lookups to the PR's level-qualified texture keys,
  and retain an owning reference while UI code reads texture dimensions. Read
  the atomic load state rather than the legacy packed flag.

## Verification

The three Python log-analysis tests pass locally. The Windows workflow additionally
tests actual executor lifecycle behavior with PPL: nested batches, exception
propagation/recovery, cancellation joining active captures, and stale-generation
rejection/replacement. Windows executor tests passed on commit `ec0f2798d9a972a83f93c08d50a0d430fd3d57e3`
([run 2](https://github.com/Queen-Jadwiga/optimized-load-transitions-monolithxray-demonized/actions/runs/38966012260)).
The first full build caught a private queue method accessed by the new reload
path; its declaration is now public. Full compilation and runtime validation
remain pending. No measured performance improvement is claimed. The PR
is a large experimental change: integration does not establish thread safety.

Automatic builds of this experimental branch target DX11-AVX, with compile logs,
symbols and executable hashes retained for 14 days. Manual DX11 builds are also
available. Build artifacts remain runtime-unverified until tested in game.
