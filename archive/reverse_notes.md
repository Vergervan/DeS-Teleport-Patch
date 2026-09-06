# Reverse notes — Demon's Souls BLES00932 (EU 01.00)

Addresses are PPU VA from `EBOOT.elf` / IDA `EBOOT.elf.i64`. TOC `0x19B5270`.
US (BLUS30443) slides many sites by **−0xE88**; `SetTransform` / `RefreshChr` do **not** — see README.

CamStream (map pieces follow FreeCam) was attempted in `imported_patch_camstream.yml` and is **not shipping**. Origin `+0xB20` is only one input to AREA MAP; fog-gated next map is a different path (`WarpNextStage`). Do not revive the unguarded GetPos hook. Do not steal `0x222538` (live method; crashes on load).

Independent **Noclip** was attempted in `imported_patch_noclip.yml` / `archive/assemble_noclip.py` and is **abandoned, not shipping**. Playtest: toggle did not crash after gravity was removed, but the player still fell, did not translate, and stayed facing one way. Do not revive without a proven Havok `this` and a new playtest. Details below.

---

## Objects (every frame in pad-poll / FreeCam cave)

`r31` at hook `0x1451F4` = **game object**. After `0x145D38` the same function reuses `r31` as **player chr** (`ChrInsMan+0x1BC`). Do not treat them as one pointer.

| Object | How to get (EU) | Fields |
| --- | --- | --- |
| game object | pad-poll `this` (`r3` → `r31`) | `+0x34` cam_mgr, `+0x44` time-stop countdown, `+0x58`/`+0x59` FreeCam flags (nonzero **skips** GetPos/B20), `+0x61` another skip, `+0x68` timer |
| cam_mgr | `[game_obj+0x34]` | `+0x1F8` teleport hold, `+0x1FC` FreeCam mode 0–3, `+0x200`/`+0x201` noclip hold/enabled (magic `0x4E`), `+0x204` camera |
| camera | `[cam_mgr+0x204]` | `+0x40` world position (same as teleport) |
| ChrInsMan | `lwz r9, -0x788C(r2)` → `0x81228774`, then `lwz r9, -0x7FFC(r9)` → `lwz r3, 0(r9)` | `+0x204` else `+0x1BC` = player |
| player / ChrCtrl | `player+0x20` | `SetTransform` target |
| origin singleton | GOT `lwz r30, -0x7B44(r2)` then `-0x7FFC` / `0(r9)` | `+0xB20` stream origin, `+0xB30` flag; `+0xAE0`/`+0xAF0` second origin, `+0xB00` flag |

Pad device: `PadMan::GetPadDeviceForIdx(0)`, inner = `[device+4]`. Hold map is `inner+0x12E` (README).

---

## Functions worth keeping

### Player / camera (used by shipping teleport)

| EU | US | Role |
| --- | --- | --- |
| `0x1C5968` | `0x1C4AE0` | `PadMan::GetPadDeviceForIdx` |
| `0x12C2C0` | `0x12B2F8` | `DbgCamControls` (FreeCam fly) |
| `0x2E85E0` | `0x2E7808` | `SetTransform` — write pos `v2`, keep angles `v3` on `ChrCtrl` |
| `0x26FFF0` | `0x26F148` | `RefreshChr` — post-warp, same call as WarpDmy (`PlayerIns` in `r3`) |
| `0x428248` | (US named) | WarpDmy: player `+0x1BC`, `SetTransform` on `+0x20`, then RefreshChr |

### Position read

| EU | Role |
| --- | --- |
| `0x273030` | GetPos: `dst`, `chr` → copies world pos via `*(chr+0x20)` |
| `0x2E81B8` | Inner: `lvx` from `*(transform+0x10)+0x10` |

### Stream origin (CamStream work)

| EU | Role |
| --- | --- |
| `0x211750` | **Set** origin `singleton+0xB20`, flag `+0xB30`. Only `bl` from `0x146560` |
| `0x2116C0` | **Set** `+0xAE0`/`+0xAF0`, flag `+0xB00`. Only `bl` from `0x146664` |
| `0x211938` | **Get** `+0xB20` into caller buffer. vtable `0x192B0E8`; code caller `0x2D224C` |
| `0x20EDB8` | AREA MAP early-out (`+0xB7A` / `+0xB82`) |
| `0x274A40` | Derived vector (AE0 path and map consumer) |
| `0x2D224C` | Reads B20, then `0x2D1268` / `0x569210` / `0x56B4E8` (piece load-ish) |

AREA MAP MAN vtable around `0x192B7C8` (`0x2324D8` … `0x234D20`, ctor-like `0x233A98`). Writing B20 alone does not load fog-gated next maps.

**Do not steal `0x222538`** (live method of the FreeCam class; crashes on load). Same class of mistake: CamStream redirected vtable `0x192B2C0` → empty `blr` at `0x2248B0` and crashed on load.

### Abandoned Noclip (EU) — do not revive as-is

Goal was an independent fly (L3+R3 toggle, no gravity, left-stick fly, third-person cam stays, map follows the **player**). Not teleport, not FreeCam cave, not `DbgCamControls`. Stock Enable FreeCam OK. **Do not enable with Teleport** (same combo) or CamStream.

**Playtest:** failed. After dropping the gravity call the game ran and the toggle did not crash, but physics still pulled the body down (including while holding fly-up), translation did not move the character, facing stayed locked. Experiment stopped.

#### Hook and cave (these rules are still correct)

Independent hook is the **nop after GetPadDevice**, not the FreeCam site:

```
0x1451F0  li r3, 0
0x1451F4  bl GetPadDevice     ← stock Enable FreeCam owns this
0x1451F8  nop                 ← noclip: bl own cave; preserve/return pad in r3
0x1451FC  stw r3, 0x320(r1)
```

At `0x1451F8`, `r31` is still **game object** (after `0x145D38` the same function reuses `r31` as player chr — do not mix them). Epilogue must `lwz r3, 0x94(r1)`. Hook `bl` encoding EU: `0x480c2689` → cave `0x207880`.

Cave **`0x207880` … `0x207B00`** (`0x280` bytes). Second of two identical methods, vtable `0x192A608`, twin at **`0x207600`**. **Do not redirect that vtable.** Gate at cave start: if LR is not the pad-poll return `0x1451FC`, `mtlr` and `b 0x207600` so virtual calls still run the original twin (bodies identical except relative `bl` encodings, delta `0x280`).

**Do not write** FreeCam cave `0x220320`, constructor at FreeCam cave+`0x280`, or `0x222538`.

Flags (must not collide with teleport / live fields):

| `cam_mgr` | Use |
| --- | --- |
| `+0x1F8` | teleport hold — **leave it** |
| `+0x1FA` | live — **do not use** |
| `+0x1FC` | FreeCam mode 0–3 — **leave it** |
| `+0x200` / `+0x201` | noclip hold / enabled magic `0x4E` |
| `+0x204` | gameplay camera (same as teleport). `[cam_mgr+8]` can be junk non-null — do not prefer it |
| `camera+0x10/20/30/40` | right / up / fwd / world pos |

#### Why SetTransform every frame is not noclip

`SetTransform` `0x2E85E0`: `r3` = ChrCtrl (`player+0x20`), `stvx v2` at `+0xC0` (pos), `stvx v3` at `+0xD0` (angles), `*(u8*)(ChrCtrl+0xB8) = 1`.

`GetPos` `0x273030` does **not** read `+0xC0`. It copies `*(ChrCtrl+0x10)+0x10` via `0x2E81B8`. Pending pose and live Havok pose are different slots.

Teleport sticks because WarpDmy / shipping cave does **`SetTransform` then `RefreshChr` `0x26FFF0`**. `RefreshChr` takes **PlayerIns** in `r3`, loads ChrCtrl from `+0x20`, virtual `vtable+0x1C`. SetTransform alone: Havok snaps the body back the same tick — including when adding +Y. That is why “fly up” still fell.

`ClearMotion` `0x2E8610` (`r3` = ChrCtrl) zeros `+0x1C8`…`+0x1E8`. Last cave also wrote the live GetPos matrix and called `RefreshChr` every frame. **Playtest still failed** — do not assume this loop is enough.

#### Gravity — crash, not a toggle

Event name `SetDisableGravity` at `0x16e42a0`. Binding around `0x18e08ac` (name / UTF-16 name / vtable slot `0x19386A8` / …). Method `0x440430`:

```
lwz r0, 0x50(r3)     # this+0x50 must be the Havok object
cmpwi r0, 0
beq skip
r3 = r0
bl 0x4DED18          # r4 = bool; uses r3+0xC0 / +0xD0 as a list
```

Calling it with **PlayerIns** (RPCS3.log): `VM: Access violation reading location 0xcf`, LR `0x440454`, call `0x20796c → 0x440430 → 0x4DED18`, `r28 = 0x1000000bf`. `PlayerIns+0x50` was a small nonzero integer, not a pointer. **Do not call `0x440430` / `0x4DED18` unguarded from the cave.** The event `this` is some other class (same vtable neighborhood as `GetEventRequest` / `SetDoesUpdateByPhalanx`). Sibling at `0x4403F8` uses the same `+0x50` pattern. Havok type names in the ELF: `hkCharacterProxyCinfo`, `hkpCharacterMotion`. Correct proxy from PlayerIns/ChrCtrl was **not** found.

#### Sticks — DbgCam analog is not one function

DbgCamControls `0x12C2C0` builds a wrapper: `[+0]` = vtable (TOC via `lwz r30, -0x7D00(r2)` then `-0x7F9C(r30)`), `[+4]` = **pad device** (not inner), `[+8]` = 0. Stick helpers only need `[r3+4]` = device, then `[device+4]` = inner. Passing GetPadDevice as `r3` is one deref too few.

| EU | Axis | Inner float (after `inner+0x10`, 4-byte align) |
| --- | --- | --- |
| `0x1B6E90` / `0x1B6DA8` | **Left** X/Y (DbgCam fly, bits on `inner+0x124`) | `+0x60` / `+0x64` |
| `0x1B4DE0` / `0x1B4E18` | **Right** X/Y (`StickY` does `fneg`) | `+0x70` / `+0x74` |
| `0x1B4F08` | L2−R2 analog | `+0x58` vs `+0x5C` |

First cave used right-stick readers during normal gameplay → analog ~0 → character stood still. Digital pad map is `inner+0x110…+0x12E` (README), **not** CELL_PAD. D-pad **`inner+0x128`**: U=`0010` D=`0020` L=`0040` R=`0080`. Hold **`inner+0x12E`**. Idle analog `+0x116 = 0040` is not a button. Do not use `r0` as an `extrdi` dest.

Last cave switched to left-stick readers; playtest still reported no translation. D-pad overlay + guarded `4DED18` **did not fit** in `0x280` together with RefreshChr / ClearMotion / live pos (assembler peaked at cave end `0x207BA0`; shipped leftover size `0x278`).

#### Facing

Teleport copies `lvx` from `ChrCtrl+0xD0` on purpose (keep facing). That 16-byte slot is native angles (likely XYZ euler), **not** the camera 3×4. Copying it every frame locks the model to one heading. Writing camera `fwd.x` into the yaw float was a non-atan2 hack and was not playtested as correct. Camera look is matrix `+0x10/+0x20/+0x30`, pos `+0x40`.

#### Leftover files

`imported_patch_noclip.yml`, `archive/assemble_noclip.py`. Not shipping. Do not copy over `imported_patch.yml` for release.

### Game tick (pad poll)

| EU | Role |
| --- | --- |
| `0x145130` | Large tick; `r3` = game object |
| `0x1451F4` | FreeCam hook (`bl` → cave `0x220320`) |
| `0x1451F8` | leftover noclip hook site (`nop` after GetPadDevice). Abandoned; do not ship a `bl` here |
| `0x146548` | GetPos → `0x211750`. **Skipped** if `game_obj+0x58` or `+0x61` ≠ 0 |
| `0x145D38` | `r31` becomes player chr |

Cave: FreeCam `0x220320`…`+0x18C`, teleport `+0x190`…`+0x27C`. **`+0x280` is a live constructor — never patch.** Do not steal `0x222538`. Abandoned noclip leftover cave was `0x207880` (gate to twin `0x207600`).

---

## Ideas that are actually in reach

Already shipped: **L3+R3 teleport to current camera** (on foot and FreeCam).

Realistic next (same cave, same objects):

1. **Freeze player** — `game_obj+0x44 = 1` is already time-stop; FreeCam mode 1 uses it. A dedicated hold to freeze without cycling cam modes. This is **not** noclip.
2. **Copy camera → player without physics refresh** or **player → camera** (`CharactorCopyPosAng` / `DbgFreeCam` strings exist). Inverse of teleport: snap debug cam back to the player.
3. **Save / load a position slot** — `SetTransform` + `RefreshChr` already proven; store `camera+0x40` or GetPos in unused bytes / a PINE-written scratch.
4. **Alternate teleport combos** — pad map on `inner+0x12E` is fully decoded (README). Do not bind L3+Cross.
5. **Independent cave** (US sketched at `0x2216B0`) — own DbgCam toggle without stealing hork’s epilogue. Pad-poll hook still collides with Enable FreeCam.

Harder / abandoned / probably not worth it:

- **Noclip / player fly** — independent cave was built and playtested; physics still wins, movement/facing did not work. Gravity event `this` is not PlayerIns (`read 0xcf`). See **Abandoned Noclip** above. Do not retry the same loop.
- **CamStream** — B20 is a stream origin, but AREA MAP also uses AE0, chr GetPos, and fog gates. Cave space is gone after teleport. Load-time camera pointers are garbage (non-null).
- **WarpNextStage / fog 1-1→1-2** — different event path, not “move origin”.
- **Event flags / item spawn / I-frames** — strings exist in the ELF; not traced to a safe call from the cave.
