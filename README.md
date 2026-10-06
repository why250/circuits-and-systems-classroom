# Circuits & Systems Classroom

An interactive classroom and knowledge base for analog and mixed-signal circuits and systems, spanning amplifiers, data converters, PLLs, noise, feedback, and signal analysis.

## Interactive illustrations

The `web/` folder holds **Circuits & Systems Classroom**, published at
<https://circuits-and-systems.tokenzhang.com>. It combines selected interactive lessons on data converters and PLLs with
an external Bode-plot tool. The [ADCToolbox](https://github.com/Arcadia-1/ADCToolbox) reference manual remains at
<https://adctoolbox.tokenzhang.com/doc/>. See [`web/README.md`](web/README.md) for development and deployment.

## Contents

### Razavi's Analog Mind Collection

[Series index and source status](Razavi-Analog-Mind-Index.md) covers the complete 22-article, 156-PDF-page Analog Mind snapshot (2020–2026). All articles have full-text and original-page review, organized into functional notes with independent derivations and reproducible analytical checks. All 22 Marker conversions were reviewed with recorded defects. [Source manifest](sources/razavi-analog-mind.json) records URLs, DOI, issue metadata, hashes, and per-article progress. Topic research also extends beyond the articles; physical implementation validation remains separate.

### Millimeter-Wave Oscillators and Frequency Synthesis

#### [Millimeter-Wave VCO Design](Millimeter-Wave-VCO-Design.md)
Cross-coupled tank startup and swing, half-circuit inductance, continuous/coarse tuning, switch loss and off-capacitance, flicker upconversion and control-noise/spur budgets.

#### [Millimeter-Wave Frequency Divider](Millimeter-Wave-Frequency-Divider.md)
Modular divide-by-2/3 state and programming relations, explicit clocked CMOS paths, speed/loading tradeoffs, charge sharing, retention, phase noise and clock-buffer power.

#### [Millimeter-Wave Frequency Synthesizer](Millimeter-Wave-Frequency-Synthesizer.md)
Charge-pump loop and exact passive-filter KCL, bandwidth and stability, consistent phase-noise integration, simulation scaling with reset-duty-dependent pump noise, and source jitter extrapolation limits.

### Sampling Phase and Clock Recovery

#### [Phase Interpolator Design](Phase-Interpolator-Design.md)
Inverter/resistor summation, finite feedback gain, quadrature phasors, exact ideal predistortion, fine-branch code ordering, quadrant transitions, input-clock correlation and timing-noise budgets.

#### [Clock and Data Recovery](Clock-and-Data-Recovery.md)
Alexander sample alignment, explicit CML/XOR connections, transition-dependent gain, separately derived voltage-filter and current/RC loop models, relative jitter and long-run holdover.

### Broadband I/O and Wireline Equalization

#### [Broadband I/O and T-Coil Design](Broadband-IO-and-T-Coil-Design.md)
Explicit coupled-inductor topology, corrected transfer polynomials, broadband matching, excitation-dependent all-pass/low-pass responses, pad loading and transient limitations. Includes the author's later formal erratum.

#### [Continuous-Time Linear Equalizer](Continuous-Time-Linear-Equalizer.md)
Reconstructed copper-channel ladder, differential bridge KCL, gain/boost tradeoff, pole placement, output peaking, resistor noise and programmable capacitance. Separates ideal equations from loaded source results.

#### [Decision-Feedback Equalizer and CML Latch](Decision-Feedback-Equalizer-and-CML-Latch.md)
Signed symbol cancellation, NRZ tap extraction, feedback timing, explicit CML latch connections and overdrive recovery. Distinguishes offset yield, static noise BER, finite data checks and feedback error propagation.

### References, Regulators and Analog Signal Processing

#### [Low-Voltage Bandgap Reference](Low-Voltage-Bandgap-Reference.md)
Current-mode CTAT/PTAT reference with explicit connections, temperature/offset derivations, resistor-ratio trim, regulated mirrors, loaded output filtering and startup verification. Separates temperature drift from absolute accuracy.

#### [LDO Regulator Design](LDO-Regulator-Design.md)
PMOS regulator feedback, supply and load transfer, oscillator noise/spur budgets with explicit PSD conventions, dropout, compensation, transient charge balance and efficiency.

#### [Transimpedance Amplifier Design](Transimpedance-Amplifier-Design.md)
Optical-receiver TIA topology, loaded/unloaded gain, finite-bandwidth feedback, BER and noise integration, NRZ spectra and long-run droop. Records source arithmetic inconsistencies and unmet gain/data-rate targets.

#### [Tow–Thomas Biquadratic Filter](Tow-Thomas-Biquadratic-Filter.md)
Differential state equations, Q-dependent cascade bandwidth, source approximations versus exact finite-gain KCL, noise budgets, common-mode/loading constraints and switched-capacitor programming.

### CMOS Inverter Applications

#### [CMOS Inverter Applications: Functional Map](CMOS-Inverter-Applications.md)
All five articles organized by circuit function, with source conditions, page boundaries and model assumptions.

- [Analog Front Ends](CMOS-Inverter-Analog-Front-Ends.md): feedback impedance/noise, CTLE/gyrator, stacked amplification, compensation, TIA and RF translation.
- [Clock and Timing Circuits](CMOS-Inverter-Clock-and-Timing-Circuits.md): buffers, oscillators, crystal startup, division, phase/duty correction and time converters.
- [Memory and Comparators](CMOS-Inverter-Memory-and-Comparators.md): static/dynamic storage, SRAM disturbance, PUF ambiguity and autozero regeneration.
- [Drivers and Power Circuits](CMOS-Inverter-Drivers-and-Power-Circuits.md): matched SST/PAM4, analog FFE, hybrid cancellation and Class-D power.
- [Charge-Domain Circuits](CMOS-Inverter-Charge-Domain-Circuits.md): clock-delivered charge, doubler startup and retained-charge SC integration.

### Basic Amplifier Topologies

#### [Reviewing AI-Assisted Analog Circuit Analysis and Design](AI-Assisted-Analog-Design-Review.md)
Both historical AI experiment articles reorganized into a circuit-review method: terminal identification, bias constraints, impedance/feedback, independent states, observation time and parameter trends. Includes source qualifications, independently checked equations and reproducible analytical models.

#### `Single-Transistor-Amplifier-Configurations.md`
Reference guide for the three fundamental MOSFET amplifier topologies (Common Source, Common Gate, Common Drain). Includes voltage gain, input/output impedance analysis, and typical applications for each configuration.

#### `5T-Differential-Amplifier-Analysis.md`
Complete mathematical analysis of 5-transistor differential amplifiers including differential/common-mode gains, CMRR, PSRR, noise analysis (thermal and flicker), frequency response (poles, zeros, transfer function), and pole-zero doublet settling time analysis.

#### `Miller-Compensated-Two-Stage-Amplifier.md`
Classical two-stage operational amplifier with Miller compensation. Comprehensive reference covering DC gain equations, dominant/non-dominant poles, RHP zero analysis, GBW calculations, phase margin design, slew rate, settling time, noise analysis, CMRR/PSRR, and complete design procedure with sizing equations.

### Dynamic and Advanced Amplifiers

#### `Ring-Amplifier.md`
Ring amplifier (Ringamp) topology using dynamically stabilized inverter stages. Covers working principle, dead-zone design, bandwidth/power equations, dead-zone degeneration (DZD), multi-stage configurations, and state-of-the-art pipelined ADC applications.

#### [Floating Inverter Amplifier](Floating-Inverter-Amplifier.md)
Floating-rail charge constraints, time-varying endpoint gain, reservoir droop/energy and sampled-noise kernels. Replaces unsupported static-gain and process-performance rules with reviewed-source analysis.

#### `Floating-Charge-Transfer-Amplifier.md`
Floating Charge Transfer (FCT) amplifier with complementary common-gate topology and cross-coupled capacitor biasing (C³B). Covers charge conservation equations, PVT-robust gain, filter-embedded Pipe-SAR ADC architecture achieving 172 dB Schreier FoM.

### Noise Reduction Techniques

#### `kTC-Noise-Cancellation.md`
Thermal noise cancellation achieving up to 70% noise power reduction using auxiliary capacitors. Includes basic cancellation, presampling techniques (>5× sampling rate improvement), design equations, capacitor sizing, and applications in high-resolution SAR ADCs and ΔΣ modulators.

#### `Correlated-Double-Sampling.md`
Correlated Double Sampling (CDS) for removing offset, reset noise, and 1/f noise. Covers frequency response, noise shaping, reset noise cancellation, switched-capacitor implementation, Correlated Multiple Sampling (CMS), and comparison with other techniques.

#### `Correlated-Level-Shifting.md`
Correlated Level Shifting (CLS) for gain enhancement achieving effective gain A² from opamp with gain A. Enables >60 dB performance from 30 dB opamps. Includes sequential CLS (SCLS), noise analysis, pipelined SAR ADC applications, and look-ahead CLS techniques.

### Sampling and Data Conversion

#### `Bootstrapped-Sampling-Switch.md`
Functional and source-grounded analysis of bootstrapped sampling: phase operation, charge conservation, body effect, parasitics, noise, ADC budgets, incremental driver design, coherent FFT, stress and buffer demands. Includes original-page checks, analytical examples and plots, and a PDK verification plan.

#### `Current-Integration-Sampling.md`
Current integration sampling for converting current signals to voltage. Covers fundamental equations, integrating ADC architectures (dual-slope, incremental ΔΣ, multi-slope), photodiode integrators, noise analysis (kT/C, shot noise), jitter performance comparison with voltage sampling, and design equations.

### Analysis and Calculations

#### `Z-Transform-for-Analog-Designers.md`
Discrete-time design intuition from delays and explicit state equations: FIR filtering, CDS covariance, leaky/delaying integrators, signal/noise transfer functions, in-band noise, and qualified unit-circle stability. Includes original-page checks and independently calculated figures.

#### `StrongARM-Comparator-Design.md`
StrongARM topology, mismatch/yield, local regeneration, metastability, probability-based noise, reset, kickback and energy. Connects Razavi's design study to independent models and a PDK verification plan, and records a dimensional correction to the source's time-constant prose.

#### `Amplifier-Bandwidth-Calculations.md`
Comprehensive guide to amplifier bandwidth theory including gain-bandwidth product (GBW) fundamentals, closed-loop bandwidth calculations, gain-bandwidth tradeoffs, and multi-stage bandwidth analysis with visual comparisons.

#### `Phase-Noise-Calculations.md`
Bidirectional conversion formulas between phase noise and amplitude noise, including definitions, step-by-step derivations, direct formulas, and worked examples for high-speed applications.

#### `Comparator-Noise-Calculation.md`
Statistical analysis of comparator decision noise using Gaussian distributions, including offset-aware extraction, finite-trial uncertainty, probability illustrations and explicitly defined energy/delay comparison metrics.

#### `Capacitance-AC-Simulation.md`
Practical method for extracting capacitance values from AC simulation results using current-frequency relationships. Includes derivation from I = jωCV, formulas for imaginary current component analysis, and ready-to-use Virtuoso Calculator expressions for automated capacitance extraction.

### Source Degeneration Analysis

#### `Degenerated-Resistor-Noise.md`
Complete noise analysis comparing non-degenerated vs source-degenerated resistor configurations. Covers transistor and resistor noise contributions, output current/voltage noise PSD derivations, frequency-dependent behavior, noise ratio calculations, and numerical examples showing noise contribution breakdown for different γ and gₘRₛ values.

#### `Degenerated-Resistor-Current-Noise.md`
Focused current noise analysis for source-degenerated circuits. Derives output current noise PSD for both cases, includes sanity checks for limiting cases (Rₛ→0 and gₘRₛ≫1), and provides simplified noise ratio formulas for design calculations.

#### `Degenerated-Resistor-Charging-Time.md`
Charging time comparison between RC charging and constant-current source degeneration. Includes time-to-Vdd/2 derivations, equivalence conditions for matched speed, design tables mapping gₘ/Rₛ/Rₗ values, effective transconductance calculations, and output resistance boosting analysis.

## Directories

### `skills/analog-circuit-research/`
Reusable circuit research workflow for building technical notes with explicit topology, assumptions, derivations, sources, and validation status. Includes optional PDF/Marker ingestion, original-page checks, and separate source/conversion/research progress; topic research can extend beyond the initial papers. Project conventions and source-ingestion guidance are kept in separate references. Example invocation: `Use $analog-circuit-research to research a bootstrapped sampling switch and write a technical note.`

### `code/`
Python scripts for generating figures and visualizations.

### `figures/`
Generated plots and images referenced in the documentation.

### `reference/`
Local reference materials including LaTeX source documents and papers.
