# AGENTS.md — Full project context and agent handoff
Last authored: 2026-10-27. Repository: https://github.com/Kajin-0/MCT-Lockin


## 2026-10-28 milestone: native KiCad capture generated (not ERC-verified)
- New `hardware/rev_a/MCT_LIA_Mini_RevA_capture.kicad_sch`: self-contained, native KiCad schematic capture with 49 generic symbol boxes and all 146 source pin-to-net mappings. Treat as a **pin-mapping handoff**, not electrically qualified design. Generic symbols have passive pins; replace with vendor-exact symbols and correct pin electrical types before trusting ERC.
- New `hardware/rev_a/ELECTRICAL_AUDIT.md`: explicit critical issues and command-level verification protocol. **Read it before making any layout or bias circuitry changes.**
- Main technical risks: OPA1612 input bias x 47 kΩ return x ~201 gain may saturate; inadequate ADC Nyquist anti-alias for 48 kSPS; provisional asymmetrically driven PCM1804 input/VCOM; no onboard protected bias or power supply; unqualified I/O protection/footprints or STM32 carrier mapping.
- On 2026-10-28 connected Ubuntu VPS was online, but `kicad-cli` not installed and remote terminal rejected installation commands. **No KiCad ERC, DRC, official netlist export, SPICE, or bench proof has been run.** Prefer authorized KiCad installation or CI before advancing.
- Next agent: first independently open/parse the native schematic, run netlist export and pin tuple diff, replace generic symbol capture with exact manufacturer library symbols, then resolve analog issues. Do not order a board or connect a detector.

## Agent startup protocol (mandatory)
1. Read this file completely, then README.md, hardware/mct-reva/README.md and hardware/mct-reva/VALIDATION.md.
2. Inspect source-of-truth `hardware/mct-reva/MCT_LIA_Mini_RevA.json`, `build_netlist.py`, `PIN_NET_CONNECTIONS.csv`, and `MCT_LIA_Mini_RevA.net`. Do not infer full connectivity from prose.
3. Run `python3 validate.py`, `python3 noise_estimate.py` and re-generate the netlist. Compare generated outputs against checked-in artifacts.
4. Review any newer git commits/PRs or project notes; this file captures the original design discussion, not future changes.
5. Report current status, verified claims, unverified assumptions, and the next blocking gate **before** proposing fabrication.

## Owner’s product vision
Build an exceptionally cost-effective, genuinely useful, small laboratory lock-in amplifier for MCT *photoconductors*. Spend scarce hardware budget on noise, bias, protection, grounding, filtering, connectors, shielding, and calibration. Use AI-developed firmware/Python software for advanced analysis, frequency sweeps, reporting, USB control, noise PSD, and calibration. **Bang-for-buck, simplicity, and dependable measurements over feature proliferation.** No touchscreen, integrated TEC controller, needless MHz bandwidth, multiple expensive analog modes or general-purpose commercial-instrument imitation. A target prototype parts/PCB/enclosure cost of **$100–150** is aspirational and **not validated** by a full BOM.

## Chronological conversation decisions (important)
1. Initially explored a *general-purpose* 1 Hz–100 kHz, 1 µV RMS, 50 Ω **source impedance** USB lock-in: STM32G474, OPA1656 and optional external ADC. That early KiCad schematic lives in `hardware/legacy-general-lockin/`. It is **not** the MCT architecture. Avoid confusing 50 Ω source resistance with 50 Ω mandatory input termination.
2. Owner proposed a *specialized* instrument for low-resistance MCT photoconductors. Detector **resistance** clarified as **10–200 Ω**; it is **NOT a request for 10–200 Ω instrument input impedance**. Use high-impedance voltage sensing to avoid loading the detector.
3. MCT testing frequency 100 Hz–10 kHz, single-digit nV/√Hz target. Intended typical detector operating temperature **77 K**, sometimes thermoelectrically cooled to **~200 K**.
4. User stated usual detector bias **0.5–3 V OR up to 50 mA**. Treat 3 V and 50 mA as simultaneous **absolute instrument ceilings**, with actual device-specific allowed bias/power **lower**. Do not hard-code 50 mA for all detectors. Desirable controlled 0–3 V range with OFF and hardware overcurrent protection.
5. We considered both constant-current voltage sensing and constant-voltage current sensing. Owner prioritized **simple hardware**, so the first prototype is **ONE voltage-sensing front end**; alternate specialized current-mode/precision-bias modes are deferred or handled externally.
6. Considered OPA1612 input preamp (TI typical ~1.1 nV/√Hz at 1 kHz) + PCM1804 audio ADC (24-bit, up to 192 kSPS; typical 111 dB SNR) + STM32G474 firmware. Current netlist uses 51× and ~201× gains, not the earlier draft’s nominal 50×/200×.
7. First deliverable was the **pin-level Rev A netlist**, generator, BOM, validation/README, not a tested schematic, routed PCB, firmware, or assembled device.
8. Project has been moved to this dedicated GitHub repository with `AGENTS.md` for continuity across assistants/agents.

## Frozen technical design targets (NOT measured claims)
| Item | Target |
|---|---|
| Application | 10–200 Ω HgCdTe/MCT photoconductors |
| Operating T | ~77–200 K detector temperature; analog PCB at ambient |
| Modulation / lock-in band | 100 Hz–10 kHz |
| Electronics input noise | ≤3 nV/√Hz at 1 kHz target, ≤4 nV/√Hz at 100 Hz target |
| Detector bias | 0–3 V and ≤50 mA; hardware limits; device-specific power ceiling |
| Lock-in DSP | Dual-phase I/Q, reported X/Y/R/phase, configurable time constants |
| External reference | 0–3.3 V TTL concept; add ESD/miswire protection |
| Internal reference | 3.3 V TTL square-wave, high-impedance load (NOT 50 Ω driver) |
| ADC | PCM1804 proposed 48 kSPS, 12.288 MHz MCLK, I²S, master configuration |
| MCU | STM32G474 development board initially; final pin map and firmware not implemented |
| Validation | Calibrated gain/phase + input-referred noise WITH energized bias |
| Cost | $100–150 aspiration; not a procurement quote |

## Files and sources of truth
- `hardware/mct-reva/MCT_LIA_Mini_RevA.json`: programmatic components/pins/nets map. Treat as **draft source data**.
- `hardware/mct-reva/build_netlist.py`: generates `.net` and diagnostic CSVs from JSON.
- `hardware/mct-reva/MCT_LIA_Mini_RevA.net`: **KiCad-style s-expression exported/netlist concept**, not native `.kicad_sch`; not verified with KiCad.
- `hardware/mct-reva/PIN_NET_CONNECTIONS.csv`, `NET_SUMMARY.csv`, `COMPONENTS.csv`: auditable mapping/BOM candidates; no accepted placement or pin-1 check.
- `hardware/mct-reva/noise_estimate.py`: first-order **nominal** white-noise model; not a simulation or laboratory measurement.
- `hardware/mct-reva/validate.py`: structural checks, not ERC.
- `hardware/mct-reva/README.md` + `VALIDATION.md`: detailed Rev A decisions/blockers.
- `hardware/legacy-general-lockin/`: historical general-purpose design concept. Keep isolated.

## Rev A signal chain and hazards
- Kelvin-style MCT FORCE and SENSE connector, external CURRENT-LIMITED detector bias, AC-coupled low-noise OPA1612A gain stage, RC low-pass (~32 kHz), second OPA1612B ADC driver, single-sided drive to PCM1804 differential inputs, 48 kSPS I²S, USB MCU.
- External +5 V, −5 V, ADC +5 V and +3.3 V supply rails are assumed. An onboard protected bias source, supply design, physical MCU headers and firmware are NOT included.
- 12.288 MHz oscillator candidate clock requires confirmed part/footprint, timing, logic levels; PCM1804 control bits and ADC pin mapping require datasheet/EDA review. ADC nominal 24 bits is NOT 24 ENOB.
- The single-ended drive to differential PCM1804 sacrifices some common-mode rejection; verify PCM1804 VCOM loading and anti-alias behavior near 10 kHz and Nyquist at 24 kHz.
- Gain-setting input-bias current, ~47 kΩ bias resistance, offset voltages, headroom, recovery from overload, and low-frequency noise MUST be simulated. The OPA1612 is bipolar-input: input bias currents can generate problematic DC offsets at gain ~201×.
- Kelvin 4-wire concept does not automatically provide current measurement or eliminate pickup.
- External TTL reference and detector input lack verified ESD/miswire protection; digital 3.3 V reference toggling can coherently contaminate nV measurements. Shielding and return-current control are central.
- **Never connect a valuable cooled MCT detector until bias source, protection, failure states, isolation, polarity, maximum dissipation and startup behavior are validated.**

## Noise metrology and accuracy
- A 10–200 Ω equilibrium resistance at 77 K contributes ~0.21–0.92 nV/√Hz Johnson noise; at 200 K ~0.33–1.49 nV/√Hz. The detector may have MUCH HIGHER flicker, generation-recombination, dark-current and bias-dependent noise.
- The existing Python noise model previously estimated combined electronics+detector thermal noise ~1.64–2.23 nV/√Hz at 1 kHz (by configuration). This result EXCLUDES detector excess and **bias source** current noise, EMI/coherent pickup, ground loops, ADC nonlinearities, and practical analog filter effects. Treat as optimistic preliminary budget, not a verified specification.
- With 200 Ω detector, bias-current noise 5 pA/√Hz causes 1 nV/√Hz detector voltage noise. A quiet bias source is a make-or-break condition. Low-noise current source output compliance/impedance must be evaluated.
- Test room-temperature dummy resistors 10, 50, 200 Ω and actual cooled test fixture; compare input-referred output noise with bias OFF/ON and digital reference toggling. Record PSD estimator ENBW, window, averaging and confidence intervals; distinguish random noise from coherent spurs. Reference frequency sweep endpoints 100 Hz, 1 kHz, 10 kHz.
- Derive amplitude/phase transfer response, integrated noise vs time constant, detector responsivity calibration when optical power is independently measured. Do not claim NEP/D* without calibrated optical modulation, device area and properly measured detector noise.
- Nominal goals proposed: calibrated gain error ≤2% and phase error ≤3° under specified test conditions. They remain proposed and require specified amplitude/temperature/bias conditions.

## Must-pass engineering gates (priority order)
1. **Audit netlist and datasheets independently**: missing/unconnected nets, supply pins, ADC modes, jumper states; native KiCad schematic and ERC; pin-to-footprint verification. Resolve faults instead of blindly preserving generator outputs.
2. **Noise/SPICE analyses**: OPA1612 input-bias/47k resistor DC offset, both gain settings, bandwidth 100 Hz–10 kHz, output headroom, ADC antialias (24 kHz Nyquist), VCOM buffer/input compliance, 100 Hz 1/f effects and amplifier stability.
3. **Bias/safety**: design/validate quiet 0–3 V, ≤50 mA bias supply with hard current limit, safe turn-on/turn-off, open/short/misconnection, per-device thermal power constraints. Evaluate fixed-voltage bias+resistor vs regulated source with quantitative bias-noise budget.
4. **Power & physical I/O**: shielded connectors and enclosure, filtered quiet analog rails with supply start-up sequencing; isolate digital return currents, no 50 Ω internal TTL driver claim.
5. **Firmware**: lock-in DSP at ADC rate, precise clock domain, coherent reference tracking, amplitude/phase calibration, safe configuration, USB command protocol and Python integration.
6. **Prototype PCB**: KiCad DRC, 4-layer vs 2-layer EMI/cost comparison, footprints, fab drawings, assembly BOM and design reviews.
7. **Bench acceptance**: source/detector resistors, bias ON/OFF, 100 Hz/1kHz/10kHz, amplitude/phase calibration, noise floor and real detector tests before any performance advertising.

## Engineering collaboration rules
- Prefer minimal bill of materials and modular external preamps, but do **not** reduce safety or measurement quality to save pennies.
- No speculative measured claims, invented vendor prices/stock or fabricated validation results. Record date and evidence.
- Do not confuse generic 1 µV resolution in a long lock-in integration with **1 nV/√Hz** input noise density.
- Keep design outputs reproducible and clearly mark **calculated / simulated / hardware measured** separately.
- Avoid big redesigns/feature additions without quantitative benefit and owner agreement.
- Commit self-contained sources; run local tests, list commands and outcomes, update this handoff with material decisions.
- For independent agents: write down discoveries and blockers in this file or a linked design decision record; no reliance on chat-memory alone.

## Reference materials
Official datasheets:
- OPA1612: https://www.ti.com/lit/ds/symlink/opa1612.pdf
- PCM1804: https://www.ti.com/lit/ds/symlink/pcm1804.pdf
- STM32G474 family: https://www.st.com/en/microcontrollers-microprocessors/stm32g4-series.html
- KiCad documentation: https://docs.kicad.org/
The precise origin of candidate pricing is noted in the historical docs. Prices/stock are not live proof.

## Immediate next task for a new agent
**Read active `hardware/mct-reva/` artifacts and perform an independent connectivity + electrical audit; then create an actual KiCad schematic with successful ERC and a demonstrated small-signal/noise SPICE model before laying out a board.** Do not fabricate this draft.
