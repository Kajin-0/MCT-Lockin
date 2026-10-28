# MCT-Lockin · MCT-LIA Mini

A **low-cost, low-noise USB digital lock-in amplifier for HgCdTe (MCT) photoconductor testing**. Hardware should be deliberately simple and cost-effective; advanced functions belong in reproducible Python/firmware software.

> **STATUS: EARLY CONCEPT / PIN-LEVEL NETLIST DRAFT. NOT FABRICATION-READY.** No demonstrated noise floor, calibrated accuracy, completed PCB, qualified protection, KiCad ERC, or tested firmware. **Do not connect an expensive detector to this design.**

## Project goals

| Parameter | Engineering target (not achieved) |
|---|---|
| Detector | HgCdTe (MCT) photoconductors, nominal 10–200 Ω |
| Detector temperature | 77 K typical; thermoelectrically cooled devices around 200 K |
| Measurement band | 100 Hz–10 kHz |
| Electronics input-referred noise | ≤3 nV/√Hz at 1 kHz; ≤4 nV/√Hz at 100 Hz (targets) |
| Detector bias | 0–3 V, ≤50 mA **with physical hardware limit** |
| Measurement | Dual-phase X/Y/R/phase; noise spectrum; calibrated sweeps |
| Interface | USB / Python |
| Form factor | Small metal enclosure, no screen or unnecessary controls |
| Cost | $100–150 prototype aspiration; **no verified BOM quotation** |

## Source layout

- [AGENTS.md](AGENTS.md): **start here** for full project history, decisions, open issues, safety, and handoff.
- [hardware/mct-reva/](hardware/mct-reva/): pin-level netlist, component inventory, scripts and calculations for the **active MCT design**.
- [hardware/legacy-general-lockin/](hardware/legacy-general-lockin/): earlier 1 Hz–100 kHz general-purpose lock-in *concept*. **Archive only; not active MCT hardware**.

## Current Rev A concept

- MCT detector with separate FORCE+/FORCE− and SENSE+/SENSE− leads (detector connections not qualified).
- External professionally current-limited, verified quiet detector bias **for initial experiments**.
- OPA1612A low-noise noninverting gain nominal 51× or 201× (jumper controlled).
- OPA1612B conditioning and nominal 2.5 V ADC common-mode interface.
- PCM1804 24-bit stereo audio ADC, proposed 48 kSPS with 12.288 MHz oscillator.
- STM32G474 development board performs I/Q DSP, TTL reference and USB communication.
- External ±5 V / analog +5 V supplies required by the netlist; power circuitry not designed.

**Netlist ≠ schematic ≠ verified PCB.** The generated `.net` has not been imported/tested in KiCad. No tested board design exists.

## Development

```bash
cd hardware/mct-reva
python3 validate.py
python3 noise_estimate.py
python3 build_netlist.py
```

The scripts are intended to validate structural assumptions, not actual electrical correctness. KiCad schematic capture, ERC, simulation, footprint verification and prototype bench testing are still required.

See [AGENTS.md](AGENTS.md) before making any changes. Keep uncertainty explicit, and never claim a calculated noise floor is measured performance.

## Device safety

Do not power a detector without verified voltage/current limits, startup protection, thermal dissipation constraints, cable polarity and input fault handling. A nominal 3 V / 50 mA envelope is **not a universal safe detector operating point**, especially at 77 K.
