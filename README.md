# Reverse-Engineering-Bitstreams
Reverse Engineering Renesas ForgeFPGA bitstreams using differential fuzzing

- Gray-box analysis and hardware-verified patching of the fuse map used by Renesas' Go Configure Software Hub to program the SLG47910 (Shrike Lite board, 1K-LUT Forge FPGA)
- The LUT truth-table field was located purely by differential analysis across known bitstreams, then confirmed by manually patching a bitstream to implement a different logic function and verifying correct behavior on the FPGA.
- Combinational 2/3-Input gates and sequential flip flops were tested

## Disclaimer

This project is still under development. 

## Results

**TL;DR**
Manually flipped fuse bits inside compiled bitstream files without usage of Go Configure Software Hub (ForgeFPGA Toolchain), after the initial build  and the FPGA correctly implemented a different logic function each time. Verified on hardware via LED output across all 4 input combinations.

**2-input functions** (4 addresses, set-only / clear-only / mixed patches,
all verified):
<details>
<summary> 2-input Gate Tables [Click Here]</summary>

**AND → OR** (set-only)
| a | b | expected OR | measured |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 1 |
| 1 | 0 | 1 | 1 |
| 1 | 1 | 1 | 1 |

**NAND → NOR** (clear-only)
| a | b | expected NOR | measured |
|---|---|---|---|
| 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 0 |
| 1 | 0 | 0 | 0 |
| 1 | 1 | 0 | 0 |

**XOR → AND** (mixed: clear at 2 addresses, set at 1)
| a | b | expected AND | measured |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 0 |
| 1 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 |

</details> 

| Patch | Bit direction | Result |
|---|---|---|
| AND -> OR | set-only (0->1) | exact OR truth table |
| NAND -> NOR | clear-only (1->0) | exact NOR truth table |
| XOR -> AND | mixed (set + clear) | exact AND truth table |



**3-input functions** (8 addresses, extendended the method to a wider LUT
input count, verified):

| Patch | Result |
|---|---|
| AND3 -> OR3 | exact OR3 truth table |
| AND3 -> XNOR3 | exact XNOR3 truth table |

## Hardware / Toolchain

| Component | Detail |
|---|---|
| Target FPGA | Renesas Forge FPGA SLG47910 (Rev BB), 1120 LUTs |
| Dev board | Vicharak Shrike Lite (dual-core RP2040 MCU + FPGA) — [board docs](https://docs.zephyrproject.org) |
| Toolchain | Renesas GoConfig Software Hub (bitstream generation) | 
| Scripting | Python, Micropython, bash|

## Methodology (Short Ver.)

- The core technique is **differential analysis/fuzzing**, across known functions such as `Combinational Gates` and `Flip Flops`
- Several tiny modules are built, are pin-for-pin identical and differ only in the actual function.
1. Compile the modules -> Synthesize -> IO Planning -> Generate Bitstream via Go-Configure Software hub
2. Repeat for every variation/gate/circuit
3. Diff the binary file bitstreams
4. Bits that change consistently across many such pairs encode the actual logic; everything else is noise (such as routing artifacts or unrelated PnR states).

### Full writeup  Soon&trade; ;)

## Findings

- Bitstream was an **unencrypted NVM/SRAM fuse map** (no security fuse set in this project), straightforward for differtial-based analysis. 
- **Fuse offset and bit position are not fixed globally** -- they shift based on IO pin assignment.
- Demonstrated **arbitrary write access**: hand-patched fuse bits directly in the compiled `.bin`, **bypassing GoConfig entirely post-generation**, and the chip executed the new logic correctly on the first flash, every time.
- **Sequential elements: partially mapped**. Clock-edge polarity
(posedge vs negedge) resolved to a single clean fuse bit, cross-validated
across two independent comparisons. Reset polarity (active-high vs
active-low) did not resolve to a single fuse bit



# FloorPlan
![floorplan](/assets/asym5floor.png)

Floorplan example for 3-input function `ASYM5.v` 
See more `/GoConfigure/ffpga/src`


  **IO Planning**
* **Inputs:**
    * `a`  $\rightarrow$ `GPIO4_IN` --(2)
    * `b` $\rightarrow$ `GPIO5_IN` --(1)
    * `c` $\rightarrow$ `GPIO3_IN` --(3)
* **Outputs:**
    * `led`  $\rightarrow$ `GPIO16_OUT` (Data) --(4)
    * `led_oe`  $\rightarrow$ `GPIO16_OE` (Output Enable) --(4)



### References

1. [Go Configure Software Hub](https://www.renesas.com/en/document/mat/go-configure-software-hub-user-guide?r=1572736)
2. [SLG47910 Datasheet](https://www.renesas.com/en/document/dst/slg47910-datasheet?srsltid=AfmBOoqI0tQzS0ZP8XkVIxNAi7YjWlqPVxMkdJybMs8P2cc7ZRjvYXGn)
3. [Shrike-Lite Docs](https://docs.zephyrproject.org)

# License

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

### Author: A script kiddie :D