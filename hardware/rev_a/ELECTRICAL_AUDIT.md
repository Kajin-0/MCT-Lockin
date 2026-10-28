# Rev A native KiCad capture — electrical audit / blockers

Date: 2026-10-28. **STATUS: UNVERIFIED CAPTURE; NO FABRICATION APPROVAL.**

## Deliverable
`hardware/rev_a/MCT_LIA_Mini_RevA_capture.kicad_sch` is a native KiCad schematic file with 49 *provisional* self-contained component symbols and 146 individually labeled physical pins based on `hardware/mct-reva/PIN_NET_CONNECTIONS.csv`. Every pin is mapped by a corresponding local net label. The symbols are deliberately generic pin-map audit boxes, **not vendor-approved graphical symbols**. Their pins are passive for mechanical capture and therefore **ERC cannot establish circuit electrical correctness until symbol types are assigned**. A KiCad netlist export must be diffed against the source-of-truth pin CSV. The netlist must NOT be used for PCB manufacture without symbol/footprint audit.

## Major findings / corrections required (highest priority first)
1. **Bias safety absent**: J2 assumes an externally validated current-limited 0–3 V supply; on-board 50 mA hardware protection is NOT implemented. Do not attach cooled MCT detectors.
2. **Bipolar op amp DC saturation**: OPA1612 input bias flowing through the provisional 47 kΩ return resistor may yield mV-scale offset; multiplied by ~201x can saturate the gain stage. Calculate worst-case input bias and offset at temperature and replace topology/return resistance as needed. Validate stability, bias current return, noise and recovery.
3. **Anti-alias attenuation is inadequate**: 48 kSPS ADC means 24 kHz Nyquist; ~32/34 kHz analog poles do not adequately reject aliases. Quantitatively select a suitable multi-pole analog response while keeping 10 kHz amplitude/phase calibrated.
4. **ADC drive and clocking**: PCM1804 differential input is asymmetrically driven. Confirm acceptable VCOM loading, peak range, charge/settling behavior, ADC reference, digital high-pass, 12.288 MHz clock, master/slave mode, I2S wiring and clock-domain tolerance from manufacturer datasheets.
5. **Power rails absent**: external +5 V, −5 V, ADC +5 V and 3.3 V; no startup sequencing, rail filtering or USB ground topology finalized. EMI from clock/reference switching can produce coherent spurs.
6. **I/O protection absent**: detector input and digital reference require ESD/miswire protections with demonstrated noise and leakage effects; thermally safe detector power limits are per-device.
7. **No actual STM32 header mapping, validated oscillator footprint or real shielded-connector footprints**. Current Kelvin pins are generic header candidates.
8. **No electrical sign-off**: no SPICE, no KiCad ERC/DRC, no bench measurements. Previous ~1.64–2.23 nV/√Hz figures are only optimistic nominal 1 kHz calculations excluding bias and excess noise.

## Required reproducibility checks
- Open capture with KiCad eeschema: verify parse and all 49 components, 146 pins and net labels. If parser rejects capture, repair generator syntax, do not silently discard connections.
- Replace provisional symbols with library-exact OPA1612, PCM1804, oscillator, connector and other symbols; confirm **physical pin number matches each CSV row**.
- `kicad-cli sch erc hardware/rev_a/MCT_LIA_Mini_RevA_capture.kicad_sch -o erc_report.txt` (after exact symbol conversion); correct issues.
- `kicad-cli sch export netlist hardware/rev_a/MCT_LIA_Mini_RevA_capture.kicad_sch -o audited.net`; compare all ref/pin/net tuples to `hardware/mct-reva/PIN_NET_CONNECTIONS.csv`.
- SPICE noise, DC worst-case, overload/recovery, transfer/phase, sampling aliases and regulator-noise simulations BEFORE designing PCB.
- Next step is **electrically correct revised schematic**, NOT PCB layout.

## Environment
The connected Ubuntu 25.10 VPS was online on 2026-10-28, but `kicad-cli` was absent. The remote terminal denied package-install commands. KiCad parser/ERC execution was **not performed**. Install KiCad (prefer matching recent stable major version) using authorized VPS administration or reproduce in CI. No successful ERC, DRC or electrical simulation is claimed.
