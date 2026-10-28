# Engineering Specification — Low-cost USB Lock-in Amplifier, Rev 0.1

## 1. User requirements (frozen)
- Signal: single-ended voltage; user-provided nominal source impedance **50 ohms**.
- Frequency: **1 Hz–100 kHz**.
- Smallest useful signal: **1 uV RMS**, with approximately **10 s acquisition**.
- Internal and external reference capability. Internal: **3.3-V square-wave excitation**.
- Host: USB-connected laboratory instrument.
- Principal optimization: **minimum cost**, subject to demonstrable performance.

## 2. Open assumptions (not user-specified)
- Max input signal and dc offset not specified. First revision targets **5 mV RMS at gain 101**, **50 mV RMS at gain 11**, or **500 mV RMS at gain 1** (subject to clipping and external interferences); not an overvoltage rating.
- 5:1 output-amplitude SNR (14 dB) is the provisional threshold for "detect" at 1 uV RMS.
- 50-ohm input impedance is optional and normally disabled to maximize sensitivity; the input is AC coupled and has 1-Mohm bias resistance.
- USB is supplied through the Nucleo on prototype; Nucleo ST-LINK virtual serial port can provide the computer interface. Native USB-C device interface is for later custom-MCU PCB revision.
- Reference input is **0–3.3 V TTL/CMOS** square wave. Analog external-reference conditioning is not included in this schematic; its addition will require comparator/hysteresis/interface design.
- Target sample rate **1 MSPS**, timer-triggered DMA, nominal MCU analog range 0–3.3 V; finalized ADC sampling time depends on input source-network validation.
- The mechanical design, enclosure, and emissions/ESD performance are undefined.

## 3. Proposed electrical topology
J1 BNC -> R1 1k input protection -> C1 10uF AC coupling -> U1A OPA1656 noninverting amplifier at +1.65-V bias -> passive two-pole R7/C2/R8/C3 low-pass -> R9 330 ohms and D1/D2 Schottky clamps -> NUCLEO ADC input.

Gain network: R4=10k feedback and selectable R5=100 ohms to VBIAS (G~101) / R6=1k to VBIAS (G~11) / neither (G~1). These prototype solder jumpers are mutually exclusive. Nominal transfer for an AC component is G=1+R4/Rg.

VBIAS: R13/R14 = 10k/10k split from the 3.3-V MCU rail, low-pass with C6=47uF, buffered by U1B (OPA1656). U1 is powered via ferrite bead FB1 and USB5V bypass capacitors. The 3.3-V Nucleo analog rail, its noise and grounding require bench validation.

Reference: J3 TTL BNC -> R10=1k and external clamp/pulldown -> timer input; MCU timer output -> R12=100 ohms -> J4 TTL BNC, high-impedance load only.

The chosen front-end device is the OPA1656: 53 MHz GBW; 2.9 nV/sqrt(Hz) noise at 10 kHz, 4.3 nV/sqrt(Hz) at 1 kHz, 4.5–36-V supply. Its input common-mode limit is V- to V+ minus ~2.25 V, satisfied by a nominal 1.65-V signal on 5-V supply. Validate worst-case margins. Official source: https://www.ti.com/product/OPA1656

## 4. Basic analog transfer
- High-pass nominal: fc=1/(2*pi*R3*C1)=0.0159 Hz at 10uF, 1Mohm; C1 effective capacitance and leakage must be confirmed.
- Anti-alias filter: R7=R8=47 ohms; C2=C3=10 nF. Because sections are **unbuffered**, the actual two-pole transfer is H(s)=1/[1+s*(R7*C2+R7*C3+R8*C3)+s^2*R7*R8*C2*C3]. For equal R,C this is 1/[1+3sRC+(sRC)^2].
- Estimated AA attenuation at 100 kHz: **-2.09 dB**, phase **-44.14 degrees** (before gain-stage phase shift); at 500 kHz: **-13.23 dB**. This is a weak anti-alias filter and is **not acceptable for strong out-of-band interferers**. Rev A is a cost-oriented proof of concept, not a fully characterized broadband anti-alias front end. Calibration can remove a deterministic passband droop but not aliases.
- Nominal amplifier closed-loop first-order BW at G=101: ~53MHz/101 = 525 kHz, requiring additional phase/gain calibration by frequency. This is an approximation and depends on input/feedback capacitances and stability.

## 5. Noise budget — derived estimates, not measured specifications

Assume T=300K, 1MSPS, internal ADC at 3.3V full-scale. Thermal voltage noise = sqrt(4 k_B T R).
- 50-ohm source: **0.91 nV/sqrt(Hz)**.
- 1k input series resistor R1: **4.07 nV/sqrt(Hz)**.
- OPA1656 voltage noise at 1kHz: **4.3 nV/sqrt(Hz)**; lower-frequency 1/f noise requires measured/datasheet spectrum.
- Rg=100-ohm thermal noise referred to input: ~**1.29 nV/sqrt(Hz)**, approximate for the non-inverting gain configuration.
- R3=1Mohm bias resistor has 128.7nV/sqrt(Hz) open circuit but is heavily shunted by the source through C1 at in-band frequencies; at 1Hz and 10uF, its approximate contribution is ~2.05nV/sqrt(Hz).
- VBIAS residual noise and coupling, amplifier offsets, USB interference, ADC drive transients, quantization nonlinearity and timing jitter require measured or SPICE validation. 5nV/sqrt(Hz) for VBIAS at 1kHz is an **assumed illustrative number**, not a guarantee.

STM32G474 datasheet (ST DS12288 Rev 6) typical ENOB **10.6 bits**, and SINAD **65.6 dB**, at maximum sample speed under specified conditions; not verified at our board configuration. For ideal fullscale sine 3.3/(2sqrt(2)) V RMS and SINAD=65.6dB, equivalent total ADC RMS input error across 0–500kHz is ~0.612mV; if treated as spectrally white that is ~0.866uV/sqrt(Hz) at ADC, or ~8.57nV/sqrt(Hz) input-referred at G=101. SINAD includes distortion, so spectral whiteness and frequency independence are **not established**. Official ST datasheet: https://www.st.com/resource/en/datasheet/stm32g474mb.pdf

Illustrative quadrature noise floor for 10s rectangular coherent averaging:
    ENBW ~ 1/(2*T) = 0.05 Hz
    sigma_Vrms_quadrature ~ e_n * sqrt(ENBW)
If effective input ASD e_n were 12 nV/sqrt(Hz), a quadrature component would have ~2.68nV RMS standard deviation, well below 1uV. This **is not a prediction of actual hardware accuracy**. Deterministic synchronous spurs, power-line coupling, 1/f noise, imperfect clock coherence and accidental sample/reference correlations can dominate by orders of magnitude.

Hardware acceptance for a nominal 1uV RMS sine at specified frequencies, 10s acquisition:
- SNR >= 5 (linear amplitude, input-referred), calibrated.
- Noise/false-tone amplitude at same frequency with a shorted input < 0.2uV RMS in 10s (test statistic & percentile to be specified before characterization).

## 6. Internal vs external ADC
| Dimension | STM32G474 internal ADC | ADS8860 external ADC |
|---|---|---|
| Nominal resolution | 12-bit | 16-bit |
| Nominal speed | up to 4MSPS in specific modes | 1MSPS |
| Vendor specified test characteristic | 10.6 typ ENOB at maximum sample rate | 93 dB typical SNR |
| External IC cost | $0 incremental | ~$19.43 single-unit DigiKey, currently out of stock |
| Reference/ADC driver | existing MCU, validate VDDA and driver | external precision reference and dedicated settling/driver analysis |
| Prototype decision | **SELECTED** | deferred upgrade if objective test failures |

DigiKey listing for STM32G474RET6 $10 single but out of stock, so prototype uses the stocked NUCLEO-G474RE (~$20.13) rather than a new custom MCU board.

## 7. Firmware contract and signal processing
- 1MHz sampling, timer-triggered, DMA double buffer; 1024/2048 sample blocks. Track ADC overruns; prohibit USB prints in ISR.
- Each sample: remove DC estimate; multiply by phase coherent sin(theta), cos(theta); accumulate X and Y in 64-bit int or FPU with bounded quantization error. Use NCO (internal) or digital PLL tracking external timer-captured reference edges. Same capture/reference clock domain as sampling timer or compensated time stamps.
- For a 10s user measurement, use **coherent boxcar integration** and optionally flat-top/controlled windows if frequency resolution and neighboring interferers warrant. At 1Hz require a full 10 seconds (10 cycles nominal); coherent averaging end conditions must be defined for non-integral reference periods.
- Scale X,Y by 2/(N*G*|H(f)|) in peak-voltage convention. Then input V_rms = hypot(X,Y)/sqrt(2), after calibrating input attenuation, analog transfer, ADC volts per count and phase.
- Provide USB protocol messages: CONFIG(freq,ref,gain,window), START, STATUS, RESULT(X,Y,R_rms,phase,actual_frequency,clipping,adc_overruns,calibration_id).
- Detect and flag clipped ADC samples, invalid TTL reference, PLL unlock, saturations, USB/ADC frame loss and low sample counts.

## 8. Manufacturing status
**Not fabrication ready.** A schematic file is supplied, but physical BNC/J2 connectivity, component footprints and pin mapping require confirmation; KiCad ERC is unrun; no PCB layout/Gerbers exist; no SPICE or thermal tests have been performed; no firmware has been validated.
