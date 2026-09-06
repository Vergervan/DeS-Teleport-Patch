# ABANDONED — independent Noclip cave. Playtest failed; do not ship.
# Knowledge is in archive/reverse_notes.md (Abandoned Noclip).
# Generate leftover YAML: python assemble_noclip.py → imported_patch_noclip.yml

def D(op, a, b, imm):
    return ((op & 0x3F) << 26) | ((a & 0x1F) << 21) | ((b & 0x1F) << 16) | (imm & 0xFFFF)


def X(rs, ra, rb, xo, rc=0):
    return (31 << 26) | ((rs & 0x1F) << 21) | ((ra & 0x1F) << 16) | ((rb & 0x1F) << 11) | ((xo & 0x3FF) << 1) | rc


def A(frt, fra, frb, frc, xo, rc=0):
    return (63 << 26) | ((frt & 0x1F) << 21) | ((fra & 0x1F) << 16) | ((frb & 0x1F) << 11) | ((frc & 0x1F) << 6) | ((xo & 0x1F) << 1) | rc


def addi(rd, ra, i):
    return D(14, rd, ra, i)


def addis(rd, ra, i):
    return D(15, rd, ra, i)


def li(rd, i):
    return addi(rd, 0, i)


def lis(rd, i):
    return addis(rd, 0, i)


def lwz(rd, i, ra):
    return D(32, rd, ra, i)


def stw(rs, i, ra):
    return D(36, rs, ra, i)


def lbz(rd, i, ra):
    return D(34, rd, ra, i)


def stb(rs, i, ra):
    return D(38, rs, ra, i)


def lhz(rd, i, ra):
    return D(40, rd, ra, i)


def lfs(fr, i, ra):
    return D(48, fr, ra, i)


def stfs(fr, i, ra):
    return D(52, fr, ra, i)


def stdu(rs, imm, ra):
    return (62 << 26) | (rs << 21) | (ra << 16) | (((imm >> 2) & 0x3FFF) << 2) | 1


def std_i(rs, imm, ra):
    return (62 << 26) | (rs << 21) | (ra << 16) | (((imm >> 2) & 0x3FFF) << 2) | 0


def ld_i(rd, imm, ra):
    return (58 << 26) | (rd << 21) | (ra << 16) | (((imm >> 2) & 0x3FFF) << 2) | 0


def cmpwi(cr, ra, imm):
    return (11 << 26) | (cr << 23) | (ra << 16) | (imm & 0xFFFF)


def andi_(ra, rs, ui):
    return D(28, rs, ra, ui)


def xori(ra, rs, ui):
    return D(26, rs, ra, ui)


def or_(ra, rs, rb):
    return X(rs, ra, rb, 444)


def mr(rd, rs):
    return or_(rd, rs, rs)


def nor(ra, rs, rb):
    return X(rs, ra, rb, 124)


def mflr(rd):
    return (31 << 26) | (rd << 21) | (8 << 16) | (339 << 1)


def mtlr(rs):
    return (31 << 26) | (rs << 21) | (8 << 16) | (467 << 1)


def lvx(vd, ra, rb):
    return (31 << 26) | (vd << 21) | (ra << 16) | (rb << 11) | (103 << 1)


def stvx(vs, ra, rb):
    return (31 << 26) | (vs << 21) | (ra << 16) | (rb << 11) | (231 << 1)


def fsubs(fd, fa, fb):
    return A(fd, fa, fb, 0, 20)


def fadds(fd, fa, fb):
    return A(fd, fa, fb, 0, 21)


def fmuls(fd, fa, fc):
    return A(fd, fa, 0, fc, 25)


def fmadds(fd, fa, fc, fb):
    return A(fd, fa, fb, fc, 29)


def b_off(delta, lk=0):
    return (18 << 26) | (delta & 0x03FFFFFC) | lk


def bc_off(bo, bi, delta):
    return (16 << 26) | (bo << 21) | (bi << 16) | (delta & 0xFFFC)


def cmplwi(cr, ra, ui):
    return (10 << 26) | (cr << 23) | (ra << 16) | (ui & 0xFFFF)


def cmplw(cr, ra, rb):
    return (31 << 26) | (cr << 23) | (ra << 16) | (rb << 11) | (32 << 1)


assert hex(nor(3, 3, 3)) == "0x7c6318f8"
assert hex(andi_(3, 3, 0x300)) == "0x70630300"
assert hex(stdu(1, -0xA0, 1)) == "0xf821ff61"
assert hex(lwz(9, -0x788C, 2)) == "0x81228774"

# 0x222538 is a live method of the FreeCam class — stealing it crashes on load.
# 0x207880 is the second of two identical 0x280-byte methods (vtable 0x192A608).
# Do not redirect that vtable; pad-poll is the only intended entry.
BASE = 0x207880
CAVE_END = 0x207B00
raw = []  # (kind, payload) kind=word or ('b', lab, lk) or ('beq', cr, lab) or ('bne', cr, lab) or ('label', name)

def W(x):
    raw.append(("w", x & 0xFFFFFFFF))


def L(name):
    raw.append(("L", name))


def BR(lab, lk=0):
    raw.append(("b", lab, lk))


def BEQ(cr, lab):
    raw.append(("beq", cr, lab))


def BNE(cr, lab):
    raw.append(("bne", cr, lab))


def BGE(cr, lab):
    raw.append(("bge", cr, lab))


def BLT(cr, lab):
    raw.append(("blt", cr, lab))


# --- cave ---
# Virtual calls to this slot must still run the identical twin at 0x207600.
W(mflr(12))
W(addis(0, 12, -0x14))
W(cmpwi(7, 0, 0x51FC))
BEQ(7, "body")
W(mtlr(12))
BR("Twin")
L("body")
W(stdu(1, -0x100, 1))
W(std_i(12, 0x110, 1))
W(stw(3, 0x94, 1))  # pad
W(cmpwi(7, 3, 0))
BEQ(7, "epi")
W(lwz(11, 4, 3))  # inner
W(cmpwi(7, 11, 0))
BEQ(7, "epi")
W(lhz(10, 0x12E, 11))
W(nor(9, 10, 10))  # not
W(andi_(9, 9, 0x0300))  # cr0: L3+R3 held if eq
W(stw(11, 0x90, 1))
W(stw(10, 0x6C, 1))  # buttons
W(lwz(8, 0x34, 31))  # cam_mgr
W(cmpwi(7, 8, 0))
BEQ(7, "epi")
W(stw(8, 0x98, 1))
W(lbz(7, 0x201, 8))  # enabled magic 0x4E
W(lbz(6, 0x200, 8))  # hold
BNE(0, "combo_up")  # not holding L3+R3
W(cmpwi(7, 6, 0))
BNE(7, "skip_tog")  # already held
W(li(6, 1))
W(stb(6, 0x200, 8))
W(cmpwi(7, 7, 0x4E))
BEQ(7, "turn_off")
W(li(7, 0x4E))
W(stb(7, 0x201, 8))
BR("skip_tog")
L("turn_off")
W(li(7, 0))
W(stb(7, 0x201, 8))
BR("epi")
L("combo_up")
W(li(6, 0))
W(stb(6, 0x200, 8))
L("skip_tog")
W(lwz(8, 0x98, 1))
W(lbz(7, 0x201, 8))
W(cmpwi(7, 7, 0x4E))
BNE(7, "epi")

# player
W(lwz(9, -0x788C, 2))
W(lwz(9, -0x7FFC, 9))
W(lwz(3, 0, 9))
W(cmpwi(7, 3, 0))
BEQ(7, "epi")
W(lwz(4, 0x204, 3))
W(cmpwi(7, 4, 0))
BNE(7, "have_pl")
W(lwz(4, 0x1BC, 3))
L("have_pl")
W(cmpwi(7, 4, 0))
BEQ(7, "epi")
W(stw(4, 0x9C, 1))
W(lwz(3, 0x20, 4))
W(cmpwi(7, 3, 0))
BEQ(7, "epi")
W(stw(3, 0xA0, 1))  # ChrCtrl

# GetPos
W(addi(3, 1, 0x80))
W(lwz(4, 0x9C, 1))
BR("GetPos", 1)
W(0x60000000)
W(li(0, 0x80))
W(lvx(2, 1, 0))

# Left stick: DbgCam 1B6E90/1B6DA8 (inner+0x60/0x64). StickX/Y at
# 1B4DE0/1B4E18 are the right stick — idle during normal gameplay.
W(lwz(3, 0x94, 1))
W(stw(3, 0x64, 1))
W(addi(3, 1, 0x60))
BR("StickX", 1)
W(0x60000000)
W(stfs(1, 0x70, 1))
W(addi(3, 1, 0x60))
BR("StickY", 1)
W(stfs(1, 0x74, 1))
W(lwz(10, 0x6C, 1))
W(lis(9, 0x4000))
W(andi_(0, 10, 0x0020))  # R1
BEQ(0, "no_fast")
W(lis(9, 0x4100))
L("no_fast")
W(andi_(0, 10, 0x0010))  # L1
BEQ(0, "no_slow")
W(lis(9, 0x3F00))
L("no_slow")
W(stw(9, 0x78, 1))
W(lfs(2, 0x78, 1))

# vertical R2=+1 L2=-1
W(li(9, 0))
W(andi_(0, 10, 0x0080))
BEQ(0, "no_up")
W(lis(9, 0x3F80))
L("no_up")
W(andi_(0, 10, 0x0040))
BEQ(0, "no_dn")
W(lis(9, 0xBF80))
L("no_dn")
W(stw(9, 0x7C, 1))
W(lfs(3, 0x7C, 1))
W(fmuls(3, 3, 2))

# gameplay camera [cam_mgr+0x204] (same object teleport uses)
W(lwz(8, 0x98, 1))
W(lwz(12, 0x204, 8))
W(cmpwi(7, 12, 0))
BEQ(7, "world")

W(lfs(4, 0x10, 12))  # right.x
W(lfs(5, 0x18, 12))  # right.z
W(lfs(6, 0x30, 12))  # fwd.x
W(lfs(7, 0x38, 12))  # fwd.z
W(lfs(8, 0x70, 1))
W(lfs(9, 0x74, 1))
W(fmuls(8, 8, 2))
W(fmuls(9, 9, 2))
W(fmuls(10, 8, 4))
W(fmadds(10, 9, 6, 10))  # dx
W(fmuls(11, 8, 5))
W(fmadds(11, 9, 7, 11))  # dz
# face camera look: yaw slot = fwd.x (character was locked to old +0xD0)
W(li(5, 0))
W(stw(5, 0xB0, 1))
W(stw(5, 0xB8, 1))
W(stw(5, 0xBC, 1))
W(stfs(6, 0xB4, 1))
BR("addpos")

L("world")
W(lfs(8, 0x70, 1))
W(lfs(9, 0x74, 1))
W(fmuls(10, 8, 2))
W(fmuls(11, 9, 2))
W(lwz(3, 0xA0, 1))
W(li(0, 0xD0))
W(lvx(3, 3, 0))
W(li(0, 0xB0))
W(stvx(3, 1, 0))

L("addpos")
W(li(0, 0x80))
W(stvx(2, 1, 0))
W(lfs(0, 0x80, 1))
W(lfs(1, 0x84, 1))
W(lfs(13, 0x88, 1))
W(fadds(0, 0, 10))
W(fadds(1, 1, 3))
W(fadds(13, 13, 11))
W(stfs(0, 0x80, 1))
W(stfs(1, 0x84, 1))
W(stfs(13, 0x88, 1))
W(lvx(2, 1, 0))

# SetTransform: pos v2, angles from 0xB0
W(lwz(3, 0xA0, 1))
W(li(0, 0xB0))
W(lvx(3, 1, 0))
BR("SetTransform", 1)
W(0x60000000)
# Live GetPos matrix *(ChrCtrl+0x10)+0x10 — physics reads this, not only +0xC0
W(lwz(3, 0xA0, 1))
W(lwz(11, 0x10, 3))
W(cmpwi(7, 11, 0))
BEQ(7, "no_live")
W(li(0, 0x10))
W(stvx(2, 11, 0))
L("no_live")
# Zero ChrCtrl motion state (next to SetTransform in the ELF)
W(lwz(3, 0xA0, 1))
BR("ClearMotion", 1)
W(lwz(3, 0x9C, 1))
BR("RefreshChr", 1)

L("epi")
W(lwz(3, 0x94, 1))
W(ld_i(0, 0x110, 1))
W(mtlr(0))
W(addi(1, 1, 0x100))
W(0x4E800020)

# resolve
labs = {}
pc = BASE
for kind, *rest in raw:
    if kind == "L":
        labs[rest[0]] = pc
    else:
        pc += 4

ext = {
    "Twin": 0x207600,
    "GetPos": 0x273030,
    "StickX": 0x1B6E90,  # left stick X (DbgCam); 1B4DE0 is right stick
    "StickY": 0x1B6DA8,  # left stick Y
    "SetTransform": 0x2E85E0,
    "ClearMotion": 0x2E8610,
    "RefreshChr": 0x26FFF0,
}

out = []
pc = BASE
for kind, *rest in raw:
    if kind == "L":
        continue
    if kind == "w":
        w = rest[0]
    elif kind == "b":
        lab, lk = rest
        dest = ext[lab] if lab in ext else labs[lab]
        w = b_off((dest - pc) & 0x03FFFFFC, lk)
    elif kind == "beq":
        cr, lab = rest
        dest = labs[lab]
        w = bc_off(12, cr * 4 + 2, (dest - pc) & 0xFFFC)
    elif kind == "bne":
        cr, lab = rest
        dest = labs[lab]
        w = bc_off(4, cr * 4 + 2, (dest - pc) & 0xFFFC)
    elif kind == "bge":
        cr, lab = rest
        dest = labs[lab]
        w = bc_off(4, cr * 4 + 0, (dest - pc) & 0xFFFC)
    elif kind == "blt":
        cr, lab = rest
        dest = labs[lab]
        w = bc_off(12, cr * 4 + 0, (dest - pc) & 0xFFFC)
    else:
        raise SystemExit(kind)
    out.append((pc, w))
    pc += 4

assert pc <= CAVE_END, hex(pc)
hook = 0x1451F8
bl_hook = b_off((BASE - hook) & 0x03FFFFFC, 1)

lines = []
lines.append("    - [ be32, 0x%08x, 0x%08x ] # bl noclip cave (after GetPadDevice)" % (hook, bl_hook))
for a, w in out:
    lines.append("    - [ be32, 0x%08x, 0x%08x ]" % (a, w))
body = "\n".join(lines)
yaml = """Version: 1.2

# ABANDONED — Independent Noclip (BLES00932 01.00). Playtest failed; not shipping.
# Independent Noclip for Demon's Souls BLES00932 01.00
# Cave 0x207880 (0x280). Virtual calls to this slot are forwarded to the
# identical twin at 0x207600 so load still runs the original method.
# Hook is the nop at 0x1451F8, after GetPadDevice / stock FreeCam return.
# Does not write FreeCam cave 0x220320, 0x222538, or call DbgCamControls.
#
# L3+R3       toggle noclip (edge). Do not also enable Teleport (same combo).
# Left stick  move, camera-relative (DbgCam 1B6E90/1B6DA8, not right-stick 1B4DE0)
# L2 / R2     down / up
# L1 / R1     slower / faster
# Each tick: SetTransform + live pos + ClearMotion + RefreshChr (teleport sync).
#
# Stock Enable FreeCam can stay on. Do not enable CamStream.
# BLES00932 01.00 only.

Anchors:
  BLES00932_Noclip: &BLES00932_Noclip
%s

PPU-5446a2645880eefa75f7e374abd6b7818511e2ef:
  "Enable Noclip":
    Games:
      "Demon's Souls":
        BLES00932: [ 01.00 ]
    Author: "Vergervan"
    Notes: "L3+R3 toggles player noclip/fly. Left stick moves relative to the gameplay camera, L2/R2 down/up, L1/R1 slow/fast. Independent of Enable FreeCam. Do not also enable Enable FreeCam + Teleport (same combo)."
    Patch Version: 1.0
    Patch:
      - [ load, *BLES00932_Noclip ]
""" % body

out_path = "C:/Users/Vergervan/Desktop/des/imported_patch_noclip.yml"
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(yaml)
print("# size", hex(pc - BASE), "end", hex(pc))
print("HOOK", hex(bl_hook))
print("wrote", out_path)
