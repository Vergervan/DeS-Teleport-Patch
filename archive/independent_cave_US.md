# Independent cave (US BLUS30443) — cache for later

Found 2026-09-04 in EBOOT.elf.i64. Not used by the shipping patch yet.
Do not sit on horkrux cave 0x21F498 if we want our own body; the pad-poll hook still collides with Enable FreeCam (must disable it).

## Hook (game pad poll, not FreeCam)

- `0x0014422C`  `bl sub_1C4AE0`  GetPadDevice
- GetPadDevice `0x1C4AE0`
- DbgCamControls `0x12B2F8` (game; callers `sub_13C810`, `sub_155B28`)
- Time stop bit used by FreeCam: `game_obj+0x44 = 1`
- Camera object: `cam_mgr = [game_obj+0x34]`, `camera = [cam_mgr+0x204]`, pos `camera+0x40`

## Proposed own cave

- `0x002216B0` — next vtable method after hork ctor `0x21F498`
- Room `0xBD8` until next vtable entry `0x222288`
- Same vtable as hork ctor at `0x192B0A8` (func/TOC pairs)
- Steal like FreeCam: overwrite entry, always `blr` before falling into live ctor body
- Hork cave `0x21F498` only has `0x280` until live `stw r27, 0x1D0(r15)` at `0x21F718`

## L3+R3 idea (not implemented)

First edge: DbgCam + freeze. While on: call DbgCamControls every pad poll.
Second edge: teleport to camera, unfreeze, leave DbgCam.
No Cross+L3 mode cycle.

EU/Asia addresses not taken (need those IDBs).
