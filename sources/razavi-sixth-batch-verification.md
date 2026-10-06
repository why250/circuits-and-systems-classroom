# Razavi Analog Mind: Sixth-Batch Verification

Reviewed 2026-10-05. This batch covers all five parts of **Fifty Applications of the CMOS Inverter**, with 48 original PDF pages. Complete extracted source text was read and all original pages were visually inspected, including shared continuation pages. The functional notes reorganize the material and add independent derivations; they are not copies of the converted articles. No PDK, SPICE/PSS/Pnoise, EM, post-layout or silicon validation was performed.

## Sources, coverage and outputs

| ID / original source | Issue / DOI | One-based PDF pages | Printed pages | Research |
|---|---|---|---|---|
| P1 / [BR_SSCM_3_2024.pdf](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2024.pdf) | Summer 2024 / [10.1109/MSSC.2024.3419528](https://doi.org/10.1109/MSSC.2024.3419528) | 1–8 | 7–14 | Full reading and original-page review |
| P2 / [BR_SSCM_4_2024.pdf](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2024.pdf) | Fall 2024 / [10.1109/MSSC.2024.3473737](https://doi.org/10.1109/MSSC.2024.3473737) | 1–9 | 12–20 | Full reading and original-page review |
| P3 / [BR_SSCM_1_2025.pdf](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2025.pdf) | Winter 2025 / [10.1109/MSSC.2024.3498732](https://doi.org/10.1109/MSSC.2024.3498732) | 1–10 | 12–20, 159 | Full reading and original-page review |
| P4 / [BR_SSCM_2_2025.pdf](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_2_2025.pdf) | Spring 2025 / [10.1109/MSSC.2025.3561955](https://doi.org/10.1109/MSSC.2025.3561955) | 1–11 | 8–18 | Full reading and original-page review |
| P5 / [BR_SSCM_3_2025.pdf](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2025.pdf) | Summer 2025 / [10.1109/MSSC.2025.3581644](https://doi.org/10.1109/MSSC.2025.3581644) | 1–10 | 9–17, 28 | Full reading and original-page review |

The [source manifest](razavi-analog-mind.json) retains original URLs, website citations and acquisition hashes. The [functional map](../CMOS-Inverter-Applications.md) connects all five articles to these outputs:

- [Analog Front Ends](../CMOS-Inverter-Analog-Front-Ends.md): feedback/noise, impedance, current reuse, CTLE/gyrator, op amp/TIA, linearized transconductance, polyphase and translated RF processing.
- [Clock and Timing Circuits](../CMOS-Inverter-Clock-and-Timing-Circuits.md): buffer, oscillator/control, crystal, burst recovery, division, phase conditioning, duty correction and TDC/DTC.
- [Memory and Comparators](../CMOS-Inverter-Memory-and-Comparators.md): state storage, SRAM disturbance, PUF, autozero regeneration and programmed thresholds.
- [Drivers and Power Circuits](../CMOS-Inverter-Drivers-and-Power-Circuits.md): SST, loaded PAM4, analog FFE, hybrid and Class-D.
- [Charge-Domain Circuits](../CMOS-Inverter-Charge-Domain-Circuits.md): packet transfer, doubler, charge steering and retained-state switched-capacitor integration.
- Revised [Floating Inverter Amplifier](../Floating-Inverter-Amplifier.md): dynamic endpoint gain, weighted common-mode charge, reservoir energy and sampled noise. Unsupported static-gain/process/performance rules from the prior note were removed.

P1 p. 14 includes an Editor's Note continuation. P3 p. 159 includes unrelated lecture news and its Fig. 1. P5 p. 28 includes another column's continuation and an Editor's Note as well as the target bibliography. Those materials remain in the raw source/conversion but are excluded from the knowledge notes. Article bibliography entries are further references, not separately read papers. No formal publisher erratum for this series was established in this batch.

## Original-page locators

Printed pages below are distinct from zero-based Marker page indices. The ranges together cover all 48 pages.

| Source / printed pages | Figures / equations | Checked content and model boundary |
|---|---|---|
| P1 pp. 7–8 | Figs. 1–3; Eqs. (1)–(4) | Inverter origin, tapered buffer, external first-gate power boundary, static latch phase connections and divider test |
| P1 pp. 9–10 | Figs. 4–8; Eqs. (5)–(6) | Tristate/SR/dynamic latches, bitline read disturbance, LNA feedback and finite output resistance |
| P1 p. 11 | Figs. 9–10; Eqs. (7)–(9) | Noise factor assumptions, source arithmetic, source gain/NF, AC bias and tank loading |
| P1 pp. 12–14 | Figs. 11–14; Eq. (10) | Crossing shift, capacitor-loaded feedback impedance, active-inductor CTLE, TIA gain/noise normalization and shared-page boundaries |
| P2 pp. 12–13 | Figs. 1–3; Eq. (1) | Device current/noise bias, ring frequency, capacitance/stage/area scaling, tuning and power normalization |
| P2 pp. 14–16 | Figs. 4–8 | Differential/quadrature loop connections, static latch alternatives, CCO bypass/reference path and disabled DCO loading |
| P2 pp. 16–17 | Figs. 9–10; Eq. (2) | Crystal-port current/voltage definitions, negative series resistance, motional/shunt branches and startup |
| P2 pp. 17–18 | Figs. 11–12 | Reset/restart burst CDR, long-run frequency error and NAND propagation symmetry |
| P2 pp. 18–20 | Figs. 13–16 | X-to-Y feedforward bypass, upper/lower divider bounds, clocked quadrature stages and PI output complement/code law |
| P3 pp. 12–13 | Figs. 1–3; Eqs. (1)–(2) | Sample/transfer clocks, boosted complementary gates, 0.25-V exception, startup and twice-per-cycle sharing |
| P3 pp. 13–14 | Figs. 4–5 | NMOS/complementary charge steering, floating-rail reset, common-mode equivalent, FIA gain/time/energy |
| P3 pp. 14–16 | Figs. 6–8 | Stacked amplifier coupling, noise averaging, negative Miller connections, CML/SST matching and power |
| P3 pp. 16–18 | Figs. 9–13 | Driver eyes, binary weighting/loading, peaked-buffer inductor endpoints and per-leg load, Vernier arbiter timing |
| P3 pp. 18–20, 159 | Figs. 14–17 and continuation | TDC/DTC signed range, capacitor code limitations, impulse versus symbol response, FFE coefficients, late continuation and bibliography |
| P4 pp. 8–9 | Figs. 1–3 | Printed supply typo, PUF ambiguity arithmetic, stage bias, source histogram and 0.6-V override |
| P4 p. 10 | Figs. 4–5 | Autozero trip offsets, swapped input steps, cross-coupling capacitors, bypass and false-seed growth |
| P4 pp. 10–12 | Figs. 6–9; Eqs. (1)–(9) | CTLE bridge KCL; differential/half-port gyrator definitions, between-node negative resistance and inductance slope |
| P4 pp. 12–14 | Figs. 10–15; Eq. (10) | T-gate versus inverting path, same-phase joining endpoints, phase alignment and mixer-loaded feedback LNA |
| P4 pp. 14–16 | Figs. 16–18 | Degenerated inverter threshold polarity/nonuniformity, H-bridge, PWM and LC topology |
| P4 pp. 16–18 | Figs. 19–22; Eqs. (11)–(12) | Two-leg output waveform and power, harmonic scope, finite replica-loop gain and transconductor scaling |
| P5 pp. 9–10 | Figs. 1–4; Eqs. (1)–(3) | Three-stage signs, series Miller branch, feedforward zeros, source phase convention and distinct TIA compensation endpoints |
| P5 pp. 11–12 | Figs. 5–8; Eq. (4) | Colored TIA noise, starved-output duty sign, intervening/final inversions, sensed pump polarity and driven output impedance |
| P5 pp. 13–14 | Figs. 9–12 | PAM4 eye; SC-integrator switches, floating C2 plate during sample/autozero, retained charge, C3 bias and polyphase ports |
| P5 pp. 15–16 | Figs. 13–16; Eqs. (5)–(6) | Actual overshoot label, 25%-duty hold timing, translated input impedance, inverter/mixer bias and switching path |
| P5 pp. 17, 28 | Figs. 17–19 and references | DSB NF, resistor/replica cancellation, final transmission gate, residual glitches and unrelated-column boundaries |

P5 Fig. 10 was additionally examined at a larger scale. C2's left plate floats during CK1 while its output-connected right plate moves; this preserves charge, rather than preserving output voltage. The source operation is an autozeroed inverter integrator, distinct from the P3 floating-reservoir amplifier.

## Source discrepancies and independent qualifications

1. **P1 LNA substitution:** $G_m=44$ mS and $r_o=90$ Ω give $1+G_mr_o=4.96$, rather than the printed denominator 9. At $R_F=500$ Ω, $R_{in}=118.95$ Ω rather than about 66 Ω; exactly 50 Ω requires $R_F=158$ Ω rather than 370 Ω. A denominator of 9 would require about 88.9 mS. This does not identify which simulated parameter or reported number is incorrect.
2. **Feedback/noise assumptions:** source NF expressions omit feedback-resistor noise and assume large gain. Exact signal/noise KCL uses the same finite-gain matrix, with correlated terminal injection for resistor noise. There is no universal 3-dB lower bound for all inverter feedback LNAs, nor a universal process gamma. P1 active-inductor high/low plateaus are approximate; the explicit retained-branch model gives $Z_{in}=[1+R_F(g_o+sC)]/(G_m+g_o+sC)$ before input capacitance.
3. **Noise versus bandwidth:** P1 TIA reports 25-GHz bandwidth but uses 18 GHz in the single-pole normalization. P5's 35-pA/√Hz value is formed from integrated colored output noise. Input PSD requires division by $|Z_t(f)|^2$; a white-equivalent density instead requires a defined ENBW and DC gain squared. A density is not integrated RMS noise.
4. **Clock-buffer power/jitter:** P1's geometric sum includes the externally driven first input capacitance. Implemented widths 1:3:9 are not the exact zero-parasitic e-optimum. Peak-to-peak jitter divided by six is a record-dependent source estimate, not a statistical identity.
5. **CCO filtering:** P2 derives a pole proportional to $MC_Lf_0/C_1$ but asks for a large $C_L$ to lower it. Larger bypass $C_1$ lowers that pole at fixed other parameters. The actual incremental node resistance also includes frequency sensitivity and current-source output resistance.
6. **Crystal startup:** printed motional values give about 24.316-MHz series and 24.351-MHz unloaded parallel resonance, rather than exact 25 MHz. The calculated negative active series resistance is about −4.053 kΩ at 25 MHz. It cannot be directly canceled against the source's approximately $2\times10^{11}$-Ω parallel-equivalent crystal resistance. Compare total admittance at the candidate frequency with consistent port definitions.
7. **Oscillator/divider interpretation:** a plain even-inverter loop can latch. Coupled quadrature modes require strength/startup checks; source “latch-up” here is static latching, not an established parasitic SCR event. The feedforward divider has both low/high valid bounds. Restarting burst recovery does not continuously correct frequency during long runs.
8. **Current-reuse noise and bandwidth:** equal independent stacked amplifier noise averages to half the variance; common noise remains. Negative Miller cancellation uses frequency-dependent complex gain, and requires differential/common-mode stability checks. A resonantly peaked clock buffer must be compared at equal swing/load/power boundaries.
9. **SST/PAM4/FFE:** a full-swing held matched 0.95-V differential SST bridge draws 4.5125 mW, exceeding the source's about 4-mW total including predriver; actual swing/nonlinear impedance and budget definitions need reconciliation. PAM4 weights require channel conductance. 112-Gb/s PAM4 is 56 Gbaud. The FFE impulse graph is not automatically the NRZ decision pulse response; source 17-ps nominal delay is approximate relative to the actual 17.857-ps UI.
10. **TDC/DTC range:** ±3 periods at 7 GHz means ±428.571 ps. At 1.4-ps resolution, 307 magnitude intervals or 613 contiguous signed intervals are needed. The source's 430-ps “full scale” and 306 stages lack an explicit sign/rounding architecture. DTC code increments do not directly equal the ratio of total node capacitances because baseline parasitics remain.
11. **FIA gain and energy:** source reservoir/load ratio 20 does not establish gain 20 or 40. Endpoint gain follows the time-varying state equation. Reservoir charge is integrated through-current, not only differential output charge. The source's 160 µW/100 MHz means 1.6 pJ/cycle; complete zero-to-0.95-V recharge of 4 pF would have a different 3.61-pJ boundary. $kT/g_m$ is a density, not sampled variance.
12. **PUF source arithmetic:** the P4 intro prints $V_{DD}=95$ V; the series uses 0.95 V, with a 0.6-V PUF example. Its $A=200,V_{DD}\approx1$-V ambiguity threshold should be 2.5 mV instead of 0.5 mV. At a zero-mean 10-mV standard deviation, ideal ambiguous probability is 19.74%. A fixed per-die value is not fresh entropy or a security proof.
13. **Regeneration and gyrator conventions:** P4 comparator's 20-ps gap is an operating example. Desired and spurious seeds grow on different schedules. The gyrator's local odd-mode cross-coupled conductance is distinct from a between-node resistance; Eqs. (8)–(9) leave a half/differential-port conversion implicit. The note defines its convention rather than mixing factor-of-two formulas.
14. **Class-D differential voltage:** P4 prose says 750 mVpp differential, but Fig. 19(b) shows two approximately 750-mVpp complementary legs. A 1.5-Vpp differential sinusoid gives 35.156 mW into 8 Ω, consistent with the reported 35 mW; 750 mVpp differential would give 8.789 mW. A −64-dBc third harmonic is not −100-dB total distortion.
15. **Compensation and source TIA poles:** P5 names $C_B$ in its stage-2 RHP-zero expression; the actual Miller branch gives $G_{m2}/C_M$ at zero series resistance. Source TIA local compensation connects input x to A, not A to B as in the op amp. Statements that the A pole rises and A/B poles remain unchanged cannot serve as one consistent pole derivation.
16. **Duty-loop sign:** higher control narrows the starved stage's high duty, contrary to P5 prose. Intervening/final inversions make the sensed E high duty increase with control. With charging during E low, $C\dot V_c=I_U(1-D_E)-I_DD_E$ restores for positive $dD_E/dV_c$. Current mismatch shifts the locked duty away from 50%.
17. **SC integrator memory:** C2 charge persists while its left plate floats. Define $u=-Q_{C2}/C_F$; then $v_{new}=(u+rv_{in})/[1+(1+r)/A]$. For the same prior settled gain, $u=(1+1/A)v_{old}$. Substituting the reset output for the memory loses the state. C3/gate capacitance, injection and finite settling require additional phase equations.
18. **Translation, overshoot and hybrid labels:** P5's printed hold inequality $R_LC_L\gg1/(4T_{LO})$ is dimensionally wrong; use $R_LC_L\gg T_{LO}/4$. Its Fig. 13 overshooting signal is X, although prose says Y. The final hybrid T-gate is Fig. 18(d), although prose again cites (c). Rails crossing, plotted cancellation and DSB NF require their actual terminal, bandwidth and noise conventions.

These are checked source expressions and independent model qualifications, not claimed publisher corrections or reproductions of source simulations.

## Marker conversion review

Marker 1.10.2 reused the installed CUDA models/cache, with all pages, page separators, batch size 4, `OMP_NUM_THREADS=4` and no LLM service. No external package/cache files were changed. P1–P5 completed and their complete Markdown was read; page separators, image links, page-stat counts and input SHA256 were checked. All five conversions are reviewed with defects, separately from the original-page research.

| Conversion | Zero-based page separators | Resolved image links | Page-stat entries | Checksum / review |
|---|---|---:|---:|---|
| P1 | 0–7 | 14 | 8 | Matches original; reviewed with defects |
| P2 | 0–8 | 16 | 9 | Matches original; reviewed with defects |
| P3 | 0–9 | 18 | 10 | Matches original; reviewed with defects |
| P4 | 0–10 | 23 | 11 | Matches original; reviewed with defects |
| P5 | 0–9 | 22 | 10 | Matches original; reviewed with defects |

P1's Fig. 3 is flattened into text rather than a usable extracted image. Device $g_m$ becomes `a_m`/`q_m`, microampere units and clock overbars disappear, active-inductor division is lost in prose, and equation numbering is incomplete. Extracted Figs. 8 and 12 were inspected: they preserve feedback endpoints, current/voltage-noise model and output shunt capacitance. The wrong LNA denominator and TIA bandwidth are in the source, rather than introduced by OCR.

P2 Eq. (1) and crystal-port Eq. (2) are readable, but the CCO noise comparison expands into a long repeated malformed logarithm; crystal resonance expressions, ohm units, division signs and complementary data labels flatten or disappear. The raw caption changes current $I_D$ to $I_0$. Extracted Figs. 9 and 13 were inspected: the crystal spans A/B with shunt capacitors, and the feedforward inverter joins X to Y. Raw formula text cannot substitute for those connections.

P3 Eqs. (1)–(2) preserve the core sharing relation, but surrounding prose misidentifies output C_Y as C_X and the clock CK as C_X. Tau/startup, SST current/power, noise square roots and many ratios flatten into italic fragments. One Vernier explanation is reduced to an incomplete sentence. Bibliography anchors point to the start of unrelated lecture news on the shared final page. Extracted Figs. 2 and 4 were inspected; boosted cross-connections, reset paths, reservoir placement and grounded output loads are retained. Fig. 4 is classified as a Picture but is a usable circuit image. The unrelated lecture image is retained in raw output.

P4 preserves the original 95-V typo and ambiguity arithmetic. Eq. (7)'s $G_{m1}G_{m2}$ becomes repeated `G_rel`; indices in CTLE Eq. (4), sigma, inequalities and units are distorted. Pull quotes interrupt and repeat LNA paragraphs. Extracted Figs. 4, 6, 8 and 19 were inspected: autozero/bypass phases, CTLE capacitor bridge, gyrator internal capacitance/cross-coupling and the two leg-voltage traces remain visible. The source swing contradiction and gyrator convention issue are distinct from these OCR defects.

P5 preserves the original Miller-zero capacitance, duty-sign and N-path dimensional discrepancies. OCR additionally changes the grouping in output-driver Eq. (4), loses square-root noise units and LO complements, and corrupts pp swing labels. Figure 10 retains the isolated left plate of C2, but nearby prose alone does not define that memory. The Fig. 17 anchor is attached near its caption while hybrid links can land there. Bibliography citations to `#page-9-0` and `#page-9-2` point into the unrelated DLL continuation and references, rather than the Analog Mind bibliography. One generated DOI link contains the reference number instead of a DOI. The target references are duplicated on the shared page. Extracted Figs. 1, 6, 10 and 18 were inspected: Miller endpoints, sensed duty polarity, the floating C2 plate and final T-gate replica are preserved. Raw unrelated DLL/Editor material is excluded from research.

Conversion review concerns complete reading, critical formulas and representative images, not certification of every OCR character or internal anchor. Raw files are preserved under gitignored `reference/razavi/marker/`.

## Independent analytical verification

```powershell
python code/razavi_sixth_batch_analysis.py
```

The [script](../code/razavi_sixth_batch_analysis.py) locates project outputs from its own path. It independently solves feedback-LNA signal/noise KCL, capacitor-bridge CTLE KCL, the compensation network versus a four-state capacitor model, and Pierce port KCL. Further checks compare packet sharing with its recurrence, retained C2 charge with the integrator coefficients, dynamic gain with an integrated endpoint, white-current sampled noise with the constant-coefficient covariance solution, and correlated noise averaging. PAM4 loading, SST resistor dissipation, Class-D voltage arithmetic, FFE convolution, phase-alignment KCL, timing/range calculations and duty-loop sign are checked separately.

| Model / stated condition | Result |
|---|---:|
| LNA, 44 mS / 90 Ω / 500 Ω | 118.9516-Ω input; 158-Ω feedback for 50-Ω input |
| CTLE illustration, G=(1,3,8,2) mS, C=25 fF | 1.41471-GHz zero, 7.63944-GHz pole, 14.6479-dB boost |
| Pierce, 10 mS, 10-pF/10-pF, 25 MHz | −4.05285-kΩ active series resistance |
| Crystal, 12.6 mH / 3.4 fF / 1.2 pF | 24.31618-MHz series; 24.35061-MHz unloaded parallel |
| Doubler, 100-fF flying / 2-pF output / 100 MHz | 100-ns RC envelope; 102.4797-ns exact envelope; 50-kΩ SSL resistance |
| FIA illustrative decaying gm, 0.2-pF load, 2 ns | 1.80369 endpoint magnitude, versus frozen ratio 10 |
| Sampled white noise, Si=4e−24 A²/Hz, g=0.1 mS, CL=0.2 pF, T=2 ns | 4.32332e−8 V² |
| SC integrator, r=1 and A=8 | State retention 0.9; input coefficient 0.8 |
| Source FIA 160 µW / 100 MHz | 1.6 pJ/cycle |
| PUF ideal 1 V / gain 200 / sigma 10 mV | 2.5-mV bound; 19.7413% ambiguous |
| SST / compared CML at 0.95 V, 50 Ω | 4.5125 / 18.05 mW under the defined ideal power boundaries |
| Loaded single-ended PAM4 / VDD | 0, 1/6, 1/3, 1/2 |
| Class-D, 8 Ω, 750 mVpp differential / each leg | 8.78906 / 35.15625 mW |
| Full-rail two-load buffer, 100 fF per leg, 56 GHz, 0.95 V | 10.108 mW |
| TDC, ±3 periods at 7 GHz / 1.4 ps | 857.143-ps signed span; 307 magnitude or 613 signed intervals |
| DTC, 430 ps / 0.35 ps | 1,229 increments |
| Static duty correction, 180 mV / 10-ps, 0.95-V edge | 3.78947 ps |
| Duty loop illustration, 50-µA currents, 0.5 pF, sensitivity magnitude 0.2/V | 4e7 s−1 restoring rate |
| Phase joining, r=50 Ω, RE=20 Ω | 1/6 local equal-slope skew |
| N-path, 5.1-GHz LO quarter period | 49.0196 ps |
| Gyrator slope, 380 nΩ/Hz | 60.4789 nH in the inductance-dominated approximation |

All three generated plots were visually inspected; the Vernier span/mismatch panel uses separately labeled axes to retain the small error scale. Numerical examples are independent ideal/illustrative models, not recreated transistor waveforms or process characterization. The notes give concrete implementation tests for the omitted physical effects.

At sixth-batch completion, all 22 original SHA256 values remained unchanged; 20 reviewed articles covered 145 PDF pages, and two pending articles covered 11. Authored local links, math delimiters, whitespace and Python syntax passed. The [seventh batch](razavi-seventh-batch-verification.md) subsequently completed the final two articles.
