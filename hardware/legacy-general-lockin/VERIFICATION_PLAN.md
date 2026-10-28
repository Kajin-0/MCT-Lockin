# Release-gate Verification Plan (Rev A -> Release Candidate)

The following are engineering acceptance criteria, not tests already passed.

| Gate | Verification method | Quantitative or binary acceptance |
|---|---|---|
| Schematic/ERC | KiCad graphical review + ERC | Zero unexplained errors; all labels/pins/gain jumper logic confirmed |
| Device/footprint | Datasheets + pin-1 drawings + KiCad 3D | 100% connector, U1 and clamp polarities verified |
| MCU integration | STM32CubeMX + official Nucleo pinout | PA ADC/timer mapping fixed; no pin conflict; reference output clock measured |
| ADC input safety | Worst-case SPICE/DC bench, with rails on/off | ADC pin voltage/injection within all ST absolute max and operating limits |
| Power | 5-V USB min/max; rail-noise spectrum, plug/unplug test | U1 rails and common-mode valid, no latch-up; measured rail and input-referred spurs |
| AFE stability | SPICE AC/transient + scope | Phase margin >= 45 deg target; no sustained oscillation; settles after gain changes |
| Frequency response | 1, 10, 100, 1k, 10k, 50k, 100k Hz sweeps | After calibration, provisional magnitude error <= 2% at all points; phase error <= 2 deg after calibrating with a coherent source |
| Input sensitivity | Calibrated 1uV RMS from 50-ohm source; 10s duration | RMS amplitude SNR >= 5 at all six frequency checkpoints; report 95th-percentile error |
| Shorted input | BNC short + 10 s at each checkpoint | False-tone RMS < 0.2uV (tentative); repeat across USB hosts |
| Anti-alias interference | Add out-of-band 150kHz–1MHz interfering tones | Determine maximum tolerable interferer; revise filter if it aliases above sensitivity criterion |
| Reference input | Digital reference at 1Hz and 100kHz, phase steps, burst and missing edges | Lock acquisition/holdover defined, no silent invalid outputs |
| Internal reference | Timer output with 10k-ohm load | Logic high/low meets target input of the intended load; no 50-ohm termination |
| Coherence | 100kHz reference & signal over 10s, varying phase | Stable I/Q, no systematic alias/mixer spur, no DMA overrun |
| PCB power/ground | Layout review, plane continuity, decoupling near U1 | No digital reference return through analog input ground path |
| ESD/abuse | Risk assessment, current limit and ESD qualification if needed | All specified operational and fault ratings documented |
| Thermal | Bench soak at 10–40 C, optional 0–50 C | Input-referred noise/gain drift within empirically derived calibration budget |
| Production files | KiCad DRC, footprint/BOM reconciliation | Zero unwaived violations; Gerbers/drills visual inspected |

**Gates that are currently completed:** (a) initial topology defined, (b) key datasheet/availability screen, (c) arithmetic noise/sampling estimates, (d) KiCad-text parenthesis and explicit net-connectivity static checks. Nothing in this list is equivalent to an ERC pass, validated schematic, functional prototype or fabrication approval.
