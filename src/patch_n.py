#!/usr/bin/env python3
"""
patch_n.py -> patch a bitstream to a different truth table of any
input width N, using a fuse_map.json from scan_n.py.

Usage:
    python3 patch_n.py <source.bin> <fuse_map.json> --truth 01111111 --out <patched_NAME.bin>

    - truth is a binary string, one bit per address in the same order as
    the addresses in fuse_map.json (000,001,010,011,100,101,110,111 for N=3,
    or 00,01,10,11 for N=2, etc.) -> length must be 2^N.
"""

import sys
import json
import argparse
import itertools

def load_fuse_map(path):
    with open(path) as f:
        d = json.load(f)
    return d["fuse_map"], d["n_inputs"]

def pick_normal_locations(fuse_map, addr_key):
    return [h for h in fuse_map[addr_key] if h["polarity"] == "normal"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_bin")
    ap.add_argument("fuse_map_json")
    ap.add_argument("--truth", required=True,
                     help="binary string, one bit per address, length 2^N, e.g. 01111111 for 3-input OR")
    ap.add_argument("--out", default="patched.bin")
    args = ap.parse_args()

    fuse_map, n_inputs = load_fuse_map(args.fuse_map_json)
    expected_len = 2 ** n_inputs
    if len(args.truth) != expected_len:
        print(f"[error] --truth must be {expected_len} chars long for this {n_inputs}-input fuse map "
              f"(got {len(args.truth)})")
        sys.exit(1)

    addr_keys = ["".join(bits) for bits in itertools.product("01", repeat=n_inputs)]
    target_map = dict(zip(addr_keys, [int(c) for c in args.truth]))

    with open(args.source_bin, "rb") as f:
        data = bytearray(f.read())

    total_flips = 0
    for addr_key, want_bit in target_map.items():
        locs = pick_normal_locations(fuse_map, addr_key)
        if not locs:
            print(f"[warn] no known fuse location for address {addr_key}, skipping")
            continue
        for loc in locs:
            off, bitpos = loc["offset"], loc["bit"]
            before = data[off]
            if want_bit:
                data[off] |= (1 << bitpos)
            else:
                data[off] &= ~(1 << bitpos)
            after = data[off]
            if before != after:
                total_flips += 1
                print(f"  addr={addr_key} offset={off} bit={bitpos}: {before:#04x} -> {after:#04x}")

    with open(args.out, "wb") as f:
        f.write(data)

    print(f"\n{total_flips} bits changed. Wrote {args.out}")
    print("Flash this file directly")

if __name__ == "__main__":
    main()