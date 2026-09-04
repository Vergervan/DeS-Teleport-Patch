# FreeCam + Teleport (Demon's Souls)

RPCS3 PPU patch **1.0**: hold **L3 + R3** to teleport the player to the **current camera** (normal gameplay or FreeCam). Does **not** include FreeCam code. Enable stock **Enable FreeCam** first.

Playtested on **BLES00932 01.00** and **BLUS30443 01.00**. Asia still uses inferred `bl` encodings (likely crash on teleport). Japanese **BCJS30022** is not included (no FreeCam cave upstream).

| Serial | Version | Status |
| --- | --- | --- |
| BLES00932 | 01.00 | tested |
| BLUS30443 | 01.00 | tested |
| BCAS20071 | 01.04 | untested (EU `bl` encodings) |
| BLUD80018 | 01.01 | untested (same overlay as US) |

## Install

Release file: `imported_patch.yml` (**Teleport to FreeCam** overlay only).

1. If `RPCS3/patches/imported_patch.yml` does **not** exist, copy this file there.
2. If that file **already exists**, do **not** replace it. Merge: keep one `Version: 1.2` at the top, paste the `Anchors:` blocks and each `PPU-...` `"Teleport to FreeCam"` patch next to any existing patches for that hash.
3. Manage Game Patches → enable stock **Enable FreeCam** **and** **Teleport to FreeCam**. Disable **Enable FreeCam + Teleport** if an old combined patch is still listed.

Do **not** enable this patch without stock Enable FreeCam.

## Controls

| Combo | Action |
| --- | --- |
| Tap **Cross**, then **L3** | Cycle FreeCam modes (stock Enable FreeCam) |
| **L2** / **R2** | Camera down / up |
| **L1** / **R1** | Slower / faster |
| **L3 + R3** | Player to current camera (once per press; works on foot, not only while flying) |

Facing is kept. Physics stays valid.

## Credits

- **horkrux** — stock Enable FreeCam in RPCS3 (required; not in this file)
- **Meowmaritus** — original DS1 freecam approach
- **Vergervan** — teleport overlay, pad map, this package

---

## For developers / agents

Technical notes for anyone extending this patch. Do not put this back into the YAML as line comments.

### Files

- `imported_patch.yml` — shipping patch (**Teleport to FreeCam** overlay only). Same overlay that worked with stock Enable FreeCam.
- `archive/FreeCam_Teleport.yml` — dual-patch snapshot (combined + overlay-only)
- `archive/Enable_FreeCam_Teleport.yml` — combined-only snapshot
- `archive/FreeCam_Teleport_configurable.yml` — combo dropdown (testing 1.9)

YAML file format version at the top must stay `Version: 1.2`. If merging into an existing `imported_patch.yml`, do not add a second `Version` key.

Enable stock **Enable FreeCam** and **Teleport to FreeCam**. Never enable overlay-only alone.

### PPU hashes and caves

FreeCam source: official `patch.yml`. Teleport is overlaid after the FreeCam epilogue, in the gap before a live constructor.

| Serial | Ver | PPU hash | Hook | Cave | Slide from EU | Status |
| --- | --- | --- | --- | --- | --- | --- |
| BLES00932 | 01.00 | `PPU-5446a2645880eefa75f7e374abd6b7818511e2ef` | `0x001451F4` | `0x00220320` | — | tested |
| BLUS30443 | 01.00 | `PPU-83681f6110d33442329073b72b8dc88a2f677172` | `0x0014422C` | `0x0021F498` | −0xE88 | tested |
| BCAS20071 | 01.04 | `PPU-9403fe1678487def5d7f3c380b4c4fb275035378` | `0x00142304` | `0x0021D570` | −0x2DB0 | untested |
| BLUD80018 | 01.01 | `PPU-f965a746d844cd0c572a7e8731b5b3b7a81f7bdd` | same as US | same as US | same as US | untested |
| BCJS30022 | 01.04 | `PPU-68544b29e92609ccb2710f485ae7708e4cb35df1` | — | no FreeCam cave | cannot port | — |

`GetPadDeviceForIdx` `bl` encoding is identical in all three caves: `0x4bfa5639` (code slide). `DbgCamControls` encodings differ: EU `0x4bf0be2d`, US/AS `0x4bf0bced`.

**Do not reuse EU `SetTransform` / `RefreshChr` `bl` encodings on other regions.** Functions do not all slide by the cave delta (−0xE88). ChrInsMan GOT is the same TOC offset (`lwz r9, -0x788C(r2)` → `0x81228774`) on US (confirmed in WarpDmy).

| | SetTransform | RefreshChr (post-warp, PlayerIns in r3) |
| --- | --- | --- |
| EU | `0x2E85E0`  bl `0x480c8081` | `0x26FFF0`  bl `0x4804fa85` |
| US | `0x2E7808`  bl `0x480c8131` | `0x26F148`  bl `0x4804fa65` |
| demo | same `bl` as US (not playtested) | same as US |
| Asia | still EU `bl` encodings — likely crash | unknown |

US WarpDmy (`sub_428248` at `0x428248`): `lwz r30, -0x788C(r2)` / player `+0x1BC` / `SetTransform` on `player+0x20` / then `bl sub_26F148`. Copying EU `bl` `0x480c8081` jumped to `0x2E7758` (not a function) → crash on teleport. Fixed by retargeting the two `bl`s; FreeCam cave and ChrInsMan GOT were already correct.

### US layout (BLUS30443)

Same cave offsets as EU. Analyze **`EBOOT.elf.i64`**.

```
pad poll  0x0014422C ──bl──►  cave 0x0021F498
                              │
                              ├─ FreeCam (horkrux)  … 0x0021F624
                              │
                              └─ teleport           0x0021F628 … 0x0021F714
                                   SetTransform 0x2E7808
                                   refresh     0x26F148

0x0021F718+  LIVE constructor — do not patch (cave+0x280)
```

GetPadDevice `0x1C4AE0`. DbgCamControls `0x12B2F8`.

### EU layout (BLES00932)

Analyze **`EBOOT.elf.i64`**, not encrypted `EBOOT.BIN`. PPC64 BE, TOC **`0x19B5270`**, image base `0x0`.

```
pad poll  0x001451F4 ──bl──►  cave 0x00220320
                              │
                              ├─ FreeCam (horkrux)  … 0x002204AC
                              │    inner = *(GetPadDevice(0)+4)
                              │    Cross+L3 TAP:  inner+0x120 bit 0x200
                              │                   AND inner+0x11E == 0xA
                              │    cam_mgr = [game_obj+0x34]
                              │    camera  = [cam_mgr+0x204]
                              │    pos     = camera+0x40
                              │
                              └─ teleport           cave+0x190 … cave+0x27C
                                   EU: 0x002204B0 … 0x0022059C
                                   hold: (~inner+0x12E & 0x0300) == 0
                                   edge flag:  [cam_mgr+0x1F8]
                                   player:     ChrInsMan+0x204 else +0x1BC
                                   ChrCtrl:    player+0x20
                                   SetTransform 0x2E85E0  (pos v2, keep ang v3)
                                   refresh     0x26FFF0  (same as WarpDmy)

0x002205A0+  LIVE constructor — do not patch
```

Caller at the hook keeps `r31` = game object, `r30` = GOT, `r2` = TOC.

Cave offsets (same on every region):

| Offset | What |
| --- | --- |
| `+0x00` … `+0x18C` | FreeCam (horkrux). Overlay starts by replacing `+0x17C` (`lwz r3, 0x94(r1)`) with `b teleport` (`0x48000014`) |
| `+0x190` … `+0x27C` | Teleport. Last safe byte is `+0x27C` (`blr`) |
| `+0x280` | Live constructor. On EU this is `0x002205A0` (`stw r27, 0x1D0(r15)` …). Patching it makes analog/walk stick left |

Do **not** use `r0` as an `extrdi` dest (PPC `r0` is special; analog sticks left). Epilogue must return the pad pointer in `r3` (`lwz r3, 0x94(r1)`).

### Teleport combo (L3+R3)

```
lhz  r3, 0x12E(r11)     # 0xa06b012e
not  r3, r3             # 0x7c6318f8  (nor r3,r3,r3)
andi. r3, r3, 0x0300    # 0x70630300  MASK L3|R3
bne  cr0, clear_flag    # 0x408200a4
```

`(~pad & MASK)==0` means all required bits are held; extra buttons are ignored. Do not offer L3+Cross — it collides with FreeCam.

Configurable archive writes the `andi.` word from Patch Manager (`long_enum`). Default value `0x70630300`. Other masks on `+0x12E`: L3+Triangle `0x0101`, L3+Circle `0x0102`, R3 `0x0200`, L1+R1 `0x0030`, Triangle+Circle `0x0003`.

### Pad map (hold, big-endian)

Copied into `inner+0x110…+0x12E`. This is **not** CELL_PAD from `pad_types.h`. Tap ≠ hold; L1/R1 and d-pad also pulse extra columns.

Best digital word for new combos: **`inner+0x12E`**

| Mask | Button |
| --- | --- |
| `0001` | Triangle |
| `0002` | Circle |
| `0004` | Square |
| `0008` | Cross |
| `0010` | L1 |
| `0020` | R1 |
| `0040` | L2 |
| `0080` | R2 |
| `0100` | L3 |
| `0200` | R3 |
| `0400` | Select (one frame, then idle) |

Also:

- `+0x11A`: L3=`0001`, R3=`0002`, Select pulse=`0004` → L3+R3 is `0003`
- `+0x11C` hold: Triangle=`0040`, Square=`0080`, Cross=`0100`
- Start: only `+0x12A == 0400` (not in `+0x12E`)
- D-pad stable in `+0x128`: U=`0010` D=`0020` L=`0040` R=`0080`
- Idle analog `+0x116 = 0040` — ignore
- `+0x124` XOR `0800` flicker — do not bind
- FreeCam’s `+0x11E == 000A` is a **tap pulse** (hold is `0008`). The `+0x120` bit `0200` is **Cross**, not L3.

Watch `inner+0x110` in RPCS3 Memory Viewer (runtime address changes each boot). PINE `pine_read32` returns correct BE PPC words; `pine_read_range` dumps LE-swapped groups.

### Hard rules

1. Never patch past **cave+0x27C**.
2. Never use `r0` as a rotate/`extrdi` destination.
3. Always return pad in `r3` from `0x94(r1)`.
4. Keep stock FreeCam bytes intact except the `b teleport` overlay at cave+0x17C.
5. Overlay-only **requires** stock Enable FreeCam. Never enable it alone.
