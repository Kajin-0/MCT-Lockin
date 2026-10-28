# 1 Hz–100 kHz USB Lock-in Amplifier — REV A design start

**Dated:** 2026-10-27 | **Status:** preliminary engineering schematic, NOT fabrication-approved.

This project contains a first-pass, **native KiCad schematic** for the analog input, bias supply, gain selection, ADC anti-alias network, optional 50-ohm input termination, and TTL reference input/output. It connects to an **NUCLEO-G474RE** during engineering validation. Firmware, on-board STM32 MCU/USB, board layout, routing, enclosure, calibrated instrument firmware, assembly, and hardware testing have NOT yet been completed.

## Open files
- `lockin_reva_afe.kicad_sch`: native schematic; all symbols self-contained (custom library symbols embedded).
- `BOM_draft.csv`: preliminary component and footprint inventory; prices on some key ICs sourced separately below.
- `NET_CONNECTIONS.csv`: explicit pin-to-net connectivity to simplify technical review.
- `DESIGN_SPEC.md`: architecture and quantitative electrical budget.
- `VERIFICATION_PLAN.md`: gates to PCB release.
- `noise_budget.py`: repeatable analytical calculations for the performance estimates.
- `build_schematic.py`: generator for the schematic, BOM, and net connectivity.

## Important interpretation of the design
- A **50-ohm source impedance** is **not** the same as a requirement for 50-ohm receiver termination. JP1 is normally OPEN (high-Z), close it only to deliberately terminate with R2=49.9 ohms.
- JP2 and JP3 **must not both be closed**. Both open = gain ~1; JP3 closed = gain ~11; JP2 closed = gain ~101. These are *manual prototype jumper selections*, not electronically programmable gains.
- Input is **AC coupled**; does not measure DC. The 10-uF/1-Mohm high-pass is nominally ~0.0159 Hz (effective capacitance must be measured).
- Single-ended signal BNC is ground-referenced. External reference BNC accepts **0–3.3 V digital square wave** only; analog sinusoidal reference is a deferred option.
- Internal reference BNC delivers MCU logic through 100-ohm series resistance; **use loads >= 10 kohms**, never use as a 50-ohm output driver.
- The AFE uses OPA1656 powered from filtered USB5V. ADC input is limited to the 3.3-V rail; candidate external Schottky clamps and limiting resistance are included **but must be verified** for safe injection into the ADC/rail, especially when rails are off.
- NUCLEO header J2 is an **electrical 6-pin abstraction**; no verified physical Nucleo-mating pin map. In the first board revision, map named signals to the actual NUCLEO headers using its official board schematic and STM32CubeMX.
- The BNC footprint is provisional and **must not** be released for fabrication without a specific connector MPN, pinout, and 3D/mechanical check.
- The schematic has passed syntax-parentheses and net-label-connection *static checks only*, **not** KiCad open/ERC, simulation, DRC or functional validation: KiCad binaries were unavailable in this execution environment.

## Price/availability evidence (queried 2026-10-27; all mutable)
- OPA1656IDR: DigiKey ~$2.99 each, listed in stock: https://www.digikey.com/en/products/detail/texas-instruments/OPA1656IDR/10715414
- NUCLEO-G474RE (engineering carrier, includes MCU and debug/USB-serial): DigiKey ~$20.13, listed in stock: https://www.digikey.com/en/products/detail/stmicroelectronics/NUCLEO-G474RE/10231585
- STM32G474RET6 bare chip: DigiKey ~$10.00 but **out of stock**: https://www.digikey.com/en/products/detail/stmicroelectronics/STM32G474RET6/10326780
- ADS8860IDGSR 16-bit 1 MSPS ADC optional upgrade: DigiKey ~$19.43 and **out of stock**: https://www.digikey.com/en/products/detail/texas-instruments/ADS8860IDGSR/4571636
- BAT54WS-G3-18 Schottky clamp: DigiKey ~$0.46 per diode, listed in stock: https://www.digikey.com/en/products/detail/vishay-general-semiconductor-diodes-division/BAT54WS-G3-18/4826908
- Unpriced resistors, capacitors, connectors, PCB fabrication, shipping, taxes and the Nucleo-to-daughterboard wiring remain to be sourced. No verified all-in BOM cost is claimed.

## Recommended next engineering step
Open `lockin_reva_afe.kicad_sch` in KiCad. Finalize connector MPNs and Nucleo header pin mapping; run ERC; inspect all junctions and protection polarities; perform transient/noise and ADC-drive simulation. Obtain a first analog board layout *only after* these checks.
