# CMOS Inverter Applications: A Functional Knowledge Map

Razavi's five-part series uses the CMOS inverter as a logic element, a transconductor, a feedback amplifier and a clock-driven charge source. This map organizes the reviewed articles by function. All **48 original PDF pages** were read and visually inspected. The linked notes contain independent derivations and reproducible ideal-model checks; they do not reproduce a PDK, extracted layout or silicon experiment. Marker progress is recorded separately in the [sixth-batch verification record](sources/razavi-sixth-batch-verification.md).

## Sources and operating conditions

| ID | Article / original PDF | Issue | PDF / printed pages | DOI |
|---|---|---|---|---|
| P1 | [Fifty Applications of the CMOS Inverter—Part 1](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2024.pdf) | Summer 2024 | 8 / 7–14 | [10.1109/MSSC.2024.3419528](https://doi.org/10.1109/MSSC.2024.3419528) |
| P2 | [Part 2](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2024.pdf) | Fall 2024 | 9 / 12–20 | [10.1109/MSSC.2024.3473737](https://doi.org/10.1109/MSSC.2024.3473737) |
| P3 | [Part 3](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2025.pdf) | Winter 2025 | 10 / 12–20, 159 | [10.1109/MSSC.2024.3498732](https://doi.org/10.1109/MSSC.2024.3498732) |
| P4 | [Part 4](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_2_2025.pdf) | Spring 2025 | 11 / 8–18 | [10.1109/MSSC.2025.3561955](https://doi.org/10.1109/MSSC.2025.3561955) |
| P5 | [Part 5](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2025.pdf) | Summer 2025 | 10 / 9–17, 28 | [10.1109/MSSC.2025.3581644](https://doi.org/10.1109/MSSC.2025.3581644) |

All are by Behzad Razavi in *IEEE Solid-State Circuits Magazine*. Unless an example explicitly overrides them, source simulations use 28-nm CMOS, slow–slow, 0.95 V and 75 °C; P1/P2 specify nominal 30-nm length and estimated layout capacitances. Longer devices, the 0.25-V charge pump and 0.6-V PUF are explicit exceptions. These source conditions do not define the parameters of the project's illustrative models.

P1 p. 14 includes an unrelated Editor's Note. P3 p. 159 includes unrelated lecture news. P5 p. 28 includes another column's continuation and an Editor's Note before the target references. Those sections are retained in raw files and excluded from the research notes. Article bibliographies identify further original work; their inclusion does not imply those papers were separately read.

## Choose the circuit function first

| Knowledge note | Source sections covered | Design question |
|---|---|---|
| [Analog Front Ends](CMOS-Inverter-Analog-Front-Ends.md) | P1 LNA, self-bias, active inductor, CTLE, TIA; P3 stacked/wideband amplifiers; P4 CTLE, gyrator, active-feedback LNA, linearized transconductor; P5 op amp, high-gain TIA, polyphase filter, translational virtual ground, active mixer | What establishes bias, impedance, gain, noise and stability? |
| [Clock and Timing Circuits](CMOS-Inverter-Clock-and-Timing-Circuits.md) | P1 tapered buffer/duty correction; P2 ring/differential/quadrature/CCO/DCO/crystal oscillators, burst CDR, feedforward/quadrature dividers, PI; P3 peaked buffer, TDC/DTC; P4 phase splitting/alignment; P5 duty loop | What changes crossing time, phase, resolution and jitter? |
| [Memory and Comparators](CMOS-Inverter-Memory-and-Comparators.md) | P1 transmission-gate/tristate/SR/dynamic latches and SRAM; P4 PUF, offset-canceled and programmable-threshold comparators | How is a state stored, disturbed, resolved or deliberately randomized? |
| [Drivers and Power Circuits](CMOS-Inverter-Drivers-and-Power-Circuits.md) | P3 SST, PAM4 and analog FFE; P4 Class-D; P5 back-terminated PAM4 and bidirectional hybrid | What impedance, energy and cancellation does the load require? |
| [Charge-Domain Circuits](CMOS-Inverter-Charge-Domain-Circuits.md) | P3 voltage multiplier/charge steering; P5 autozeroed discrete-time integrator | Where does charge come from, and where is it retained between phases? |
| [Floating Inverter Amplifier](Floating-Inverter-Amplifier.md) | P3 FIA, reset, common-mode constraint and dynamic gain | What determines the gain at the sampling instant? |

The title's “fifty applications” counts related implementations and variants. This map covers every topical section of all five articles; it does not invent an item numbering absent from the sources. Existing [phase interpolator](Phase-Interpolator-Design.md), [CDR](Clock-and-Data-Recovery.md), [TIA](Transimpedance-Amplifier-Design.md) and [CTLE](Continuous-Time-Linear-Equalizer.md) notes supply related models with their own topology definitions.

## Four distinctions that prevent misuse

1. **Bias versus signal gain:** an inverter amplifies near its trip point, not over its complete rail-to-rail characteristic. Feedback, reset capacitors or common-mode control must establish that region.
2. **A frozen model versus an entire cycle:** $g_mr_o$, an endpoint dynamic gain and a closed-loop capacitor ratio are different quantities. A ring amplifier with a dead zone also requires a different model from a continuously biased three-stage op amp. The existing [Ring Amplifier](Ring-Amplifier.md) note's numerical claims were not revalidated by this series review.
3. **Single-ended versus differential ports:** an impedance measured between two outputs can differ by a factor of two from its odd-mode half-circuit value. Define the current and voltage before using a gyrator, driver or tank equation.
4. **A target versus a demonstrated result:** a divider frequency sweep does not establish arbitrary-data BER; a displayed eye does not establish RMS jitter; a small-signal noise result does not establish large-blocker linearity or terminal-voltage reliability.

Independent models, their parameters and the source discrepancies are preserved in [the verification record](sources/razavi-sixth-batch-verification.md). Run `python code/razavi_sixth_batch_analysis.py` to regenerate the three project plots. Conversion is auxiliary evidence: a successful OCR run alone never changes a research entry to reviewed.
