#!/usr/bin/env python3
"""Marvell Kirkwood BootROM NAND Reed-Solomon ECC (4-bit, 10 bytes / 512 B).

Port of OpenOCD src/flash/nand/ecc_kw.c (GPL-2.0-or-later, Marvell /
L. Buytenhek / N. Pitre). For 2048-byte pages the 4 x 10 ECC bytes go to
OOB bytes 24..63, the rest of the OOB stays 0xff.

  kwrs.py check <raw dump>             verify against data+OOB pages
  kwrs.py encode <in.bin> <out.raw>    data -> data+OOB pages (2112 B each)
"""
import sys

PAGE, OOB = 2048, 64
MODPOLY = 0x409

gf_exp = [0] * 2046
gf_log = [0] * 1024
p = 1
for i in range(1023):
    gf_exp[i] = gf_exp[i + 1023] = p
    gf_log[p] = i
    p <<= 1
    if p & 0x400:
        p ^= MODPOLY

GEN = (0x21c, 0x181, 0x18e, 0x25f, 0x197, 0x193, 0x237, 0x024)


def ecc_kw(data):
    r = [data[504 + k] for k in range(8)]          # r0..r7
    for i in range(503, -9, -1):
        d = data[i] if i >= 0 else 0
        r7 = r[7]
        if r7:
            t = gf_log[r7]
            r = [d ^ gf_exp[t + GEN[7]]] + \
                [r[k - 1] ^ gf_exp[t + GEN[7 - k]] for k in range(1, 8)]
        else:
            r = [d] + r[:7]
    r0, r1, r2, r3, r4, r5, r6, r7 = r
    return bytes(x & 0xff for x in (
        r0, (r0 >> 8) | (r1 << 2), (r1 >> 6) | (r2 << 4), (r2 >> 4) | (r3 << 6),
        r3 >> 2, r4, (r4 >> 8) | (r5 << 2), (r5 >> 6) | (r6 << 4),
        (r6 >> 4) | (r7 << 6), r7 >> 2))


def page_oob(data):
    ecc = b"".join(ecc_kw(data[i:i + 512]) for i in range(0, PAGE, 512))
    return b"\xff" * 24 + ecc


def check(path):
    d = open(path, "rb").read()
    n = len(d) // (PAGE + OOB)
    rs_ok = rs_bad = blank = other = 0
    bad_pages = []
    for i in range(n):
        pg = d[i * 2112:i * 2112 + PAGE]
        oob = d[i * 2112 + PAGE:(i + 1) * 2112]
        if pg == b"\xff" * PAGE and oob == b"\xff" * OOB:
            blank += 1
        elif oob[24:] == page_oob(pg)[24:]:
            rs_ok += 1
        elif oob[24:40] == b"\xff" * 16:            # Hamming page (OOB 40-63)
            other += 1
        else:
            rs_bad += 1
            bad_pages.append(i)
    print("pages %d: RS match %d, RS mismatch %d, blank %d, other (Hamming) %d"
          % (n, rs_ok, rs_bad, blank, other))
    if bad_pages:
        print("first mismatching pages:", bad_pages[:10])


def encode(src, dst):
    d = open(src, "rb").read()
    d += b"\xff" * (-len(d) % PAGE)
    out = bytearray()
    for i in range(0, len(d), PAGE):
        pg = d[i:i + PAGE]
        out += pg + page_oob(pg)
    open(dst, "wb").write(out)
    print("%s: %d pages (%d bytes) -> %s" % (src, len(d) // PAGE, len(out), dst))


if __name__ == "__main__":
    if sys.argv[1] == "check":
        check(sys.argv[2])
    elif sys.argv[1] == "encode":
        encode(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
