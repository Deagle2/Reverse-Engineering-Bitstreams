#!/usr/bin/env python3
"""  bitstream bit-level diff + truth-table correlation tool.

Expects files named FPGA_bitstream_MCU_<NAME>.bin in that dir.
Edit GATES dictionary below to match whichever gates you've actually built.

"""

import sys
import os

# name -> truth table as dict{(a,b): out},
#  Currently supports only 1 bit inputs - 2-input Combinational Gates
GATES = {
    "AND":       {(0,0):0, (0,1):0, (1,0):0, (1,1):1},
    "OR":        {(0,0):0, (0,1):1, (1,0):1, (1,1):1},
    "NAND":      {(0,0):1, (0,1):1, (1,0):1, (1,1):0},
    "NOR":       {(0,0):1, (0,1):0, (1,0):0, (1,1):0},
    "XOR":       {(0,0):0, (0,1):1, (1,0):1, (1,1):0},
    "XNOR":      {(0,0):1, (0,1):0, (1,0):0, (1,1):1},
    "ANDNOT_AB": {(0,0):0, (0,1):0, (1,0):1, (1,1):0},  # a & ~b
    "ANDNOT_BA": {(0,0):0, (0,1):1, (1,0):0, (1,1):0},  # ~a & b
}

# Open read binary, return as a bytes object
def load(path):
    with open(path, "rb") as f:
        return f.read()

def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    data = {}
    for name in GATES:
        p = os.path.join(d, f"FPGA_bitstream_MCU_{name}.bin")
        if not os.path.exists(p):
            print(f"[skip] missing {p}")
            continue
        data[name] = load(p)

    names = list(data.keys())
    if len(names) < 2:
        print("Need minimum 2 gate files present.")
        return

    length = len(data[names[0]])
    for n in names:
        if len(data[n]) != length:
            print(f"[WARN] size mismatch: {n} = {len(data[n])} bytes vs {length}")

#####################################################################################
    # bit-level scan: for each byte offset, for each bit position 0-7,
    # collect which gates have that bit set
    print(f"Scanning {length} bytes x 8 bits across {len(names)} gates: {names}\n")

    candidate_bits = []  # (offset, bitpos, {name: bitval})

    for off in range(length):
        byte_vals = {n: data[n][off] for n in names}
        if len(set(byte_vals.values())) == 1:
            continue  # identical across all gates at this byte, skip
        for bitpos in range(8):
            bits = {n: (byte_vals[n] >> bitpos) & 1 for n in names}
            if len(set(bits.values())) > 1:  # this bit toggles across gates
                candidate_bits.append((off, bitpos, bits))

    print(f"Found {len(candidate_bits)} (offset,bit) positions that toggle across gate set.\n")

    # correlate each candidate bit against each of the 4 truth-table input cases
    input_cases = [(0,0), (0,1), (1,0), (1,1)]
    matches_by_case = {ic: [] for ic in input_cases}

    for off, bitpos, bits in candidate_bits:
        for ic in input_cases:
            expected = {n: GATES[n][ic] for n in names}
            if bits == expected:
                matches_by_case[ic].append((off, bitpos))
            # also check inverted correlation (in case fuse polarity is flipped)
            inv_expected = {n: 1 - GATES[n][ic] for n in names}
            if bits == inv_expected:
                matches_by_case[ic].append((off, bitpos, "INVERTED"))
        # Results
    print("=== Candidate fuse bit(s) per truth-table input case (a,b) ===")
    for ic, hits in matches_by_case.items():
        print(f"\ninput (a={ic[0]}, b={ic[1]}):")
        if not hits:
            print("  none found")
        for h in hits:
            print(" ", h)

    # dump raw candidate bits too 
    print("\n=== Raw candidate bit list (offset, bitpos, {gate:bitval}) ===")
    for off, bitpos, bits in candidate_bits:
        print(off, bitpos, bits)

if __name__ == "__main__":
    main()