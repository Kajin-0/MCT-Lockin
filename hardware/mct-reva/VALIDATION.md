# MCT-LIA Mini Rev A — release gates

## Completed in this artifact
- [x] Pin-number mapping audited against TI datasheet: OPA1612 dual SOIC-8.
- [x] Pin-number mapping audited against TI datasheet: PCM1804 28-pin SSOP.
- [x] 48kHz I2S master/12.288MHz system clock control combination checked against TI PCM1804 Table 1 / Table 5.
- [x] Machine validation: unique reference designators, unique physical pins per component, each named net has at least two mapped pins.
- [x] Python numerical noise-model execution (nominal assumptions).

## Not completed and required
- [ ] Reconstruct and open `.kicad_sch` in KiCad, run ERC and independently inspect all local symbols.
- [ ] Validate netlist import in installed KiCad and footprint libraries.
- [ ] Assign actual STM32G474 alternate function pins for slave I2S and reset/capture/timer outputs.
- [ ] Verify oscillator land pattern/pad 1 convention and output control; crystal vs CMOS clock drive.
- [ ] Verify ADC VCOM maximum load and input impedance with this asymmetric single-sided drive; TI Figure 44 is reference for balanced analog driver.
- [ ] SPICE: transfer function, resistor tolerances, OPA1612 stability and noise @ 100Hz,1kHz,10kHz; test both jumper states, C effective bias dependence.
- [ ] Verify OPA1612 47k bias-resistor input DC offsets at 201x gain (input bias and 0.5mV specified max offset).
- [ ] Specify 0..3V detector bias with <=50mA independent analog hardware limit, proof across 10..200R and open/short, required supply compliance.
- [ ] Prove bias-source current noise small: at 200 ohms <=5pA/sqrt(Hz produces <=1nV/sqrt(Hz), if current source coupling is direct.
- [ ] Select low-noise +/-5V analog supplies and filtered ADC rails with power sequencing.
- [ ] Define ESD, accidental miswire, safe insert/remove and detector connector arrangement.
- [ ] Physical PCB EMI/ground return design; electrical noise measurement with REF OUT toggling at all frequencies.
- [ ] Real ADC firmware, synchronized I/Q demod test, 48kHz frame clock handling, calibrate phase.
- [ ] Validate 100Hz–10kHz amplitude flatness and calibrated phase, test near -0.75dB first-order 10kHz analog filter loss.
- [ ] Verify noise floor <=3nV/sqrt(Hz with detector and bias noise distinguished, at 1kHz, two gains.

## Stop conditions
No PCB manufacturing or detector connection until the first five blocker categories (schematic/footprints, safety bias, supplies, protection, amplifier stability) have been resolved, simulated where appropriate, and prototypes inspected.
