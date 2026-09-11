#!/usr/bin/env python3
"""
Hard Coded version -> check diff.py for same general purpose variant

Hand-flip fuse bits in a working .bin to change its logic function
without regenerating via GoConfig. Proves write-capability, not just read.

Edit SRC_FILE, OUT_FILE, and FLIP_OFFSETS below to match your latest
diff.py scan output (offsets differ per IO plan / build).
"""

SRC_FILE = "FPGA_bitstream_MCU_AND.bin"
OUT_FILE = "FPGA_bitstream_MCU_AND_to_OR_handflip.bin"

# From your latest scan: offsets for input (0,1) and (1,0), each with its bitpos.
# AND=0 at these addresses, OR=1 at these addresses -> we flip 0->1.
FLIP_OFFSETS = [
    # (offset, bitpos)  -- input (a=0,b=1)
    (6249,2),(6253,2),(6285,3),(6289,3),
    (6425,2),(6429,2),(6461,3),(6465,3),
    (6601,2),(6605,2),(6637,3),(6641,3),
    (6777,2),(6781,2),(6813,3),(6817,3),
    # input (a=1,b=0)
    (6337,2),(6341,2),(6373,3),(6377,3),
    (6513,2),(6517,2),(6549,3),(6553,3),
    (6689,2),(6693,2),(6725,3),(6729,3),
    (6865,2),(6869,2),(6901,3),(6905,3),
]

def main():
    with open(SRC_FILE, "rb") as f:
        data = bytearray(f.read())

    for off, bitpos in FLIP_OFFSETS:
        before = data[off]
        data[off] |= (1 << bitpos)   # force bit to 1 (0->1, no-op if already 1)
        after = data[off]
        print(f"offset {off} bit{bitpos}: {before:#04x} -> {after:#04x}")

    with open(OUT_FILE, "wb") as f:
        f.write(data)
    print(f"\nWrote {OUT_FILE}")

if __name__ == "__main__":
    main()