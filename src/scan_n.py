#!/usr/bin/env python3
"""
scan_n.py   

Gate truth tables are loaded from an external JSON config

Config file format (gates_config.json):
{
  "AND3": {"000":0,"001":0,"010":0,"011":0,"100":0,"101":0,"110":0,"111":1},
  "OR3":  {"000":0,"001":1,"010":1,"011":1,"100":1,"101":1,"110":1,"111":1},
  ...
}
Keys are N-character binary strings (address), values are 0/1 (output).
All entries must have the same key length (= N).

Usage:
    python3 scan_n.py <bitstream_dir> <gates_config.json> [--out fuse_map.json]

Bitstream files must be named FPGA_bitstream_MCU_<NAME>.bin 
"""

import sys
import os
import json
import argparse
import itertools

def load_gate_config(path):
    with open(path) as f:
        cfg = json.load(f)
    n_values = {len(k) for tbl in cfg.values() for k in tbl}
    if len(n_values) != 1:
        print(f"[error] inconsistent address key lengths in config: {n_values}")
        sys.exit(1)
    n = n_values.pop()
    return cfg, n

def load_bitstreams(directory, gate_names):
    data = {}
    for name in gate_names:
        path = os.path.join(directory, f"FPGA_bitstream_MCU_{name}.bin")
        if os.path.exists(path):
            with open(path, "rb") as f:
                data[name] = f.read()
        else:
            print(f"[skip] missing {path}")
    return data

def scan(data):
    names = list(data.keys())
    length = min(len(v) for v in data.values())
    for n in names:
        if len(data[n]) != length:
            print(f"[warn] size mismatch: {n} = {len(data[n])} bytes (using min length {length})")

    candidates = []
    for off in range(length):
        byte_vals = {n: data[n][off] for n in names}
        if len(set(byte_vals.values())) == 1:
            continue
        for bitpos in range(8):
            bits = {n: (byte_vals[n] >> bitpos) & 1 for n in names}
            if len(set(bits.values())) > 1:
                candidates.append((off, bitpos, bits))
    return candidates, names

def correlate(candidates, names, cfg, n_inputs):
    addr_keys = ["".join(bits) for bits in itertools.product("01", repeat=n_inputs)]
    fuse_map = {addr: [] for addr in addr_keys}

    for off, bitpos, bits in candidates:
        for addr in addr_keys:
            expected = {n: cfg[n][addr] for n in names}
            if bits == expected:
                fuse_map[addr].append({"offset": off, "bit": bitpos, "polarity": "normal", "values": bits})
            inv_expected = {n: 1 - expected[n] for n in names}
            if bits == inv_expected:
                fuse_map[addr].append({"offset": off, "bit": bitpos, "polarity": "inverted", "values": bits})
    return fuse_map

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bitstream_dir")
    ap.add_argument("gates_config")
    ap.add_argument("--out", default="fuse_map.json")
    ap.add_argument("--dump-address", default=None)
    args = ap.parse_args()

    cfg, n_inputs = load_gate_config(args.gates_config)
    print(f"Loaded config for {len(cfg)} gates, {n_inputs}-input functions "
          f"({2**n_inputs} addresses).")

    data = load_bitstreams(args.bitstream_dir, cfg.keys())
    if len(data) < 2:
        print("Need at least 2 gate .bin files present.")
        sys.exit(1)

    candidates, names = scan(data)
    print(f"Scanned {len(data)} bitstreams ({names}), {len(candidates)} candidate toggling bits found.")

    fuse_map = correlate(candidates, names, cfg, n_inputs)
    for addr, hits in sorted(fuse_map.items()):
        print(f"  input={addr}: {len(hits)} matching fuse locations")

    save_map = {
        addr: [{"offset": h["offset"], "bit": h["bit"], "polarity": h["polarity"]} for h in hits]
        for addr, hits in fuse_map.items()
    }
    with open(args.out, "w") as f:
        json.dump({"n_inputs": n_inputs, "gates_used": names, "fuse_map": save_map}, f, indent=2)
    print(f"\nWrote fuse map to {args.out}")

    if args.dump_address:
        print(f"\n=== Raw hits for address {args.dump_address} ===")
        for h in fuse_map.get(args.dump_address, []):
            print(f"  offset={h['offset']} bit={h['bit']} polarity={h['polarity']} values={h['values']}")

if __name__ == "__main__":
    main()