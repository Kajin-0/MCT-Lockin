# MCT-LIA Mini | Rev A — pin-level netlist / capture handoff

**Design intent:** inexpensive, low-noise lock-in for 10–200 ohm HgCdTe photoconductors at 77–200 K. Target 100 Hz–10 kHz, input-referred electronics noise <=3 nV/sqrt(Hz) at 1 kHz (design target, NOT a measured specification), USB / Python I/Q via STM32G474 development carrier.

**Status (October 27, 2026):** PIN-LEVEL NETLIST DRAFT. No EDA/ERC/PCB/thermal/reliability/safety sign-off. The **bias supply and bipolar +/-5V op-amp supply are deliberately EXTERNAL for bring-up**. Do NOT connect an unprotected detector to the prototype.

## Files
- `MCT_LIA_Mini_RevA.net`: KiCad-style s-expression netlist draft (component-level + pin connections). This **is not** a KiCad `.kicad_sch` schematic and cannot replace schematic ERC. The output format was not tested in KiCad.
- `PIN_NET_CONNECTIONS.csv`: complete auditable ref/pin/net matrix; useful as schematic capture authoritative mapping.
- `NET_SUMMARY.csv`: net-by-net membership.
- `COMPONENTS.csv`: preliminary BOM with PCB footprint candidates, unverified footprints clearly marked.
- `MCT_LIA_Mini_RevA.json`: machine-readable single source-of-truth map.
- `noise_estimate.py`: repeatable first-order noise calculation, no detector excess / bias noise included.
- `build_netlist.py`: deterministic netlist generator.
- `VALIDATION.md`: risk register, milestones, pin-level checklist.

## Architecture

```text
     CURRENT-LIMITED LOW-NOISE EXTERNAL BIAS   (NOT IMPLEMENTED ON THIS BOARD)
                |        +--------+-----------------
                +-- J2 --| J1: FORCE+ / FORCE-    |-- MCT (outside board)
                         | J1: SENSE+ / SENSE-    |
                         +----------+--------------
                                    |
                              22R + 4.7uF
                                    |
                         OPA1612A non-inverting
                      feedback: 1k / 20R = 51x
                      jumper 6.65R => ~201x
                                    |
                              RC pole ~32kHz
                                    |
                              10uF high pass
                                    |
                         OPA1612B inverting
                           output @ VCOM=2.5V
                      feedback RC pole ~34kHz
                                    |
                        PCM1804 differential L input
                         L+ tied to VCOM via 47R
                         L- driven via 47R
                                    |
                          48kHz 24b I2S (master)
                                    |
                         J5 --> STM32 carrier + USB
```

OSC: 12.288 MHz 3.3V oscillator U3 -> PCM1804 SCKI at 256 fs for 48 kSPS. In master mode PCM1804 provides I2S BCK/LRCK and DATA to MCU in slave receive mode. Must validate actual STM32 pin alternate functions, DMA and clock-domain synchronization.

### Bias / detector connector
J1 is a nominal 4-conductor *Kelvin* interface with separate detector-force and sense wires. Short FORCE+ to SENSE+ and FORCE- to SENSE- **only at the detector**; do NOT short these pairs together in the pcb. The sense minus lead is grounded at the analog star through R2=0R, whereas force minus directly returns the externally supplied bias. Real Kelvin cable and contact details are unresolved.

J2 connects an **external laboratory bias source**. It MUST be rated/limited to **0–3 V and <=50 mA** and must comply with detector power constraints. There is **no on-board 50 mA limit** in this netlist. A low-noise bias system is not optional for final product; adding it comes next with verified startup/fault behavior and sufficiently low current-noise density.

### Gain and frequency
- `SW1` gain jumper **open** => G = 1 + 1000/20 = **51.0x**.
- `SW1` **closed** => G = 1 + 1000/(20 || 6.65) = **~201.4x**.
- Input high-pass from `C1=4.7uF`, `R3=47k`: nominal f_c ~0.72 Hz (capacitor effective value must be confirmed).
- ADC-driver high-pass `C3=10uF`, `R8=10k`: nominal f_c ~1.59 Hz.
- Anti-alias first pole `R7=330R`, `C2=15nF`: ~32.2 kHz (nonideal loading/active feedback effects require simulation).
- ADC driver feedback `R9=10k`, `C4=470pF`: ~33.9 kHz; response across 100 Hz–10 kHz needs software amplitude/phase calibration.
- **ADC analog interface is single-sided into a differential ADC** (VCOML on VINL+, actively-driven VINL-). Expect poorer rejection than fully symmetric differential drive. This choice is intentional to keep it to ONE dual op-amp.
- PCM1804 right channel connected to VCOMR on both inputs as diagnostic quiet channel, not a detector input.

### External power
The **J5 interface is electrical/logical only**, not an actual NUCLEO-G474RE pin mapping. It requests AVDD_P5 = +5 V, AVEE_N5 = -5 V, AVDD_ADC5 = +5 V analog ADC, D3V3 = +3.3 V, and AGND / DGND joined via one 0-ohm link (`R14`). Power-supply generation, start-up sequencing, 5V ADC/reference noise, analog return current / shielding are **NOT included**.

### Reference
The external input is 0-3.3 V TTL only, no overvoltage protection yet. The internal reference is a 3.3 V logic output with a 100R series resistor and is intended for >=10k-ohm loads; it is NOT a 50-ohm pulse generator.

## Nominal 1kHz noise model
`noise_estimate.py` models typical TI OPA1612 1.1 nV/sqrt(Hz) voltage and 1.7 pA/sqrt(Hz) current noise, Johnson noise, 22-ohm input series resistor, feedback resistors, second op-amp and PCM1804 111 dB typical SNR approximated as uniform broadband noise. At 200-ohm detector at 200K, **2.23 nV/sqrt(Hz predicted combined noise** at low gain 51x), but this explicitly *excludes* bias current noise, G-R/1/f detector noise, pickup, ADC quantization effects, noise-gain peaking, the temperature dependence of components and any coupling from digital MCLK/reference output. Do not advertise as measured. Noise may be worse at 100 Hz.

## Official source datasheets / control mappings
- TI OPA1612 SOIC-8 pins: https://www.ti.com/lit/ds/symlink/opa1612.pdf , pin 1 OUT A, 2 -IN A, 3 +IN A, 4 V-, 5 +IN B, 6 -IN B, 7 OUT B, 8 V+.
- TI PCM1804 SSOP-28: https://www.ti.com/lit/ds/symlink/pcm1804.pdf , pin table and master mode control pages 2, 4, 19, 21, 27, 30. Here OSR[2:0]=011 (256fs at single rate), FMT[1:0]=01 (I2S), S/M=0 master, BYPAS=0 high-pass enabled, RST programmable.
- Abracon ASEM1 12.288MHz XO candidate: https://www.digikey.com/en/products/detail/abracon-llc/ASEM1-12-288MHZ-L/29264030 . Physical pins 1=OE, 2=GND, 3=OUT, 4=VDD; verify part suffix and footprint.
- Official KiCad netlist guidance: https://docs.kicad.org/master/en/eeschema/eeschema.html (preferred path is schematic capture then Update PCB from Schematic).

## Known blockers BEFORE prototype assembly
1. Select and validate real ADC and oscillator footprints, selected jumper and shielded cables. J3/J4 are **2-pin header placeholders**, not actual BNC footprints.
2. Transfer pin map into a native `.kicad_sch` and run KiCad ERC; this `.net` has only undergone local structural validation.
3. Engineer an actual quiet supply of +5 V/-5 V/ADC +5 V/+3.3 V, isolation/ground strategy and current-limited startup.
4. Validate OPA1612 first stage DC bias current at G~201, input overload, AC-input voltage limits, ADC analog input drive and anti-alias attenuation.
5. Design detector bias source and prove independent 3V/50mA hardware safety limits, including shorted/open detector and cold/warm startup.
6. Add input ESD and reference I/O protection; current circuit does not contain a qualified protection network.
7. Prototype test input-referred spectral density at 100 Hz/1 kHz/10 kHz, with bias ON and 10/50/200 ohm sources, calibrate phase/gain and report actual measured uncertainty.

**This is a capture handoff, not a board-order package.**
