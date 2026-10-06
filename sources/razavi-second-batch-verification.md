# Analog Mind: Second-Batch Source Verification

Review date: **2026-10-05**. This batch covers four building blocks and **26 original PDF pages**. Original PDFs, extracted text, rendered pages and raw Marker output remain under gitignored `reference/razavi/`. Stable URLs, DOI, hashes and review state are in the [source manifest](razavi-analog-mind.json). Source simulations, independently evaluated models and implementation validation are separate evidence categories.

## Review coverage

| Source | PDF / printed pages | Reviewed scope | Authored note |
|---|---|---|---|
| Low-voltage bandgap, Summer 2021 | PDF 1–8 / printed 6–12, 16 | Full article, all original page previews, circuit connections, equations, plots, startup and references | [Low-Voltage Bandgap Reference](../Low-Voltage-Bandgap-Reference.md) |
| LDO, Spring 2022 | PDF 1–5 / printed 7–10, 17 | Full article, all original page previews, pass/feedback polarity, oscillator budget, compensation and transients | [LDO Regulator Design](../LDO-Regulator-Design.md) |
| TIA, Winter 2023 | PDF 1–5 / printed 7–10, final number unconfirmed | Full article, all original page previews, PMOS pair, feedback model, noise integration and failed specifications | [Transimpedance Amplifier Design](../Transimpedance-Amplifier-Design.md) |
| Biquad, Winter 2024 | PDF 1–8 / printed 6–13 | Full article, all original page previews, crossed differential feedback, finite-gain/noise equations and complete filter | [Tow–Thomas Biquadratic Filter](../Tow-Thomas-Biquadratic-Filter.md) |

Bandgap p. 16 and LDO p. 17 are shared continuation pages: unrelated Circuit Intuitions/equalizer and quantum-electronics material is excluded from the notes. The TIA last-page printed number remains `null` in the manifest; the website's pp. 7–11 is not sufficient to confirm a missing printed number.

## Marker conversion review

All four PDFs converted successfully with **Marker 1.10.2**, inference batch size 1, all pages, page separators enabled and no LLM service. The installed Python/CUDA environment and model cache were reused; no package or cache deletion was performed. Conversion records retain input SHA256, and all four originals still match both those records and the acquisition manifest.

Zero-based separators are complete: 0–7, 0–4, 0–4 and 0–7 respectively. All 22, 9, 17 and 22 generated Markdown image references resolve locally, and each metadata file parses. Representative extracted circuit images were visually checked: bandgap Fig. 2, LDO Fig. 5, TIA Fig. 8 and biquad Fig. 5. This auxiliary review covers boundaries, important expressions and representative image connectivity, not certification of every OCR character.

| Source | Observed conversion defects / treatment |
|---|---|
| Bandgap | Eq. (1) changes $V_{BE}$ subscripts into `RF`; Eq. (4) replaces the distinct $R_1,R_3$ denominators with `P_T`. Eq. (6) and offset Eq. (7) remain usable after original-page checks. Later text flattens resistor ratios, units and device dimensions. The shared final page includes an unrelated article and its bibliography before the Analog Mind continuation; isolate the continuation explicitly. Fig. 2 is a usable extracted image. |
| LDO | Fig. 2 becomes a truncated LaTeX array instead of a usable circuit image. Use original p. 8 for connectivity and feedback polarity. The important 50-MHz/V sensitivity, 32-nV budget and ripple expressions are readable. Compensation prose misreads $g_{m0}$ as `q_m0` and µA units as `A n`; Fig. 5's extracted image preserves its resistor/capacitor values. Fig. 9's caption corrupts the supply subscript. Shared p. 17 retains unrelated quantum text/references. |
| TIA | Fig. 8 is usable and identifies the topology variants. The p. 10 RMS parenthesis drops the `m` in 1.34 mV, producing 1.34 V, while nearby Eq. (11) retains mV. Use original p. 10 and $\sqrt{1.8\times10^{-6}}$ to check units. Converted text preserves the source's inconsistent $(1000+1000)/(1+3.9)=200$ claim; conversion does not correct source arithmetic. Final-page caption/figure material does not establish a printed page number. |
| Biquad | Eq. (15) changes denominator $b$ into `h`; Eq. (18) preserves the source's 0.25 coefficient discrepancy. Later text corrupts decimals/µA/kΩ and changes the final compression swing $1.8V_{pp}$ into $1.8V_{DD}$. Last-page figures are reordered in Markdown relative to the printed layout; use captions and original page anchors. Extracted Fig. 5 preserves crossed feedback. |

Raw converted Markdown is preserved, not silently repaired or used as the authored knowledge note.

## Checked source anchors and project treatment

| Source locator | Checked material | Treatment |
|---|---|---|
| Bandgap pp. 6–8, Fig. 2, Eqs. (1)–(8) | PNP terminals, PMOS gates/drains, resistor branches, area/current ratios, offset | KCL derivation, $n=16$, summed-current example, separate slope/output trim |
| Bandgap pp. 9–10, Figs. 7–11, Eqs. (9)–(14) | Preliminary PTAT PSRR, amplifier supply tracking, gain assumptions | Do not carry preliminary $R_1/R_L\simeq0.14$ into final resistor choice |
| Bandgap pp. 10–12, Figs. 12–18 | Mirror channel-length error, regulated cascode, output curve, passive filter and noise | Separate drift/absolute error; independently solve loaded two-node filter |
| Bandgap pp. 12, 16, Figs. 19–20 | Startup threshold, pull-down path, 900-ns and 1-ms ramps | Multi-ramp/initial-state verification plan |
| LDO p. 7, Eqs. (1)–(2), Fig. 1 | 50-MHz/V VCO sensitivity, noise budget, ripple and input power | Explicit PSD/SSB convention, supply sensitivity versus tuning gain, power balance |
| LDO p. 8, Figs. 2–3, Eq. (3) | PMOS feedback polarity, divider, 0.5-pF load and amplifier gain | Independent supply/reference/load KCL with direct amplifier feedthrough |
| LDO pp. 9–10, Figs. 4–8, Eq. (4) | Uncompensated/compensated loop, 500 Ω/1 pF, noise and PSRR | Source-only stability data; qualified compensation/load sweep |
| LDO pp. 10, 17, Figs. 9–10 | 10-ns supply and 1-ns load ramps, approximately 2-ns recovery | Charge-balance bound distinguished from actual nonlinear response |
| TIA pp. 7–8, Eqs. (1)–(9), Figs. 1–7 | BER/current budget, capacitance, common-gate noise, long runs | Gaussian/ENBW calculation and independent NRZ/droop extensions |
| TIA pp. 9–10, Figs. 8–13, Eqs. (10)–(11) | PMOS pair, unloaded gain model, bias, noise units, detector input | Explicit connections, exact DC KCL, gain-definition discrepancy |
| TIA PDF p. 5, Figs. 14–16 | 17-GHz bandwidth, 224-Ω input, 2-mA current, noise and limitations | Preserve failure to meet gain/data-rate targets after parasitics |
| Biquad pp. 6–8, Figs. 1–5, Eqs. (1)–(9) | Application noise factor, crossed feedback, frequency/Q, bandwidth rule | Independent state equations, linear noise-factor budget, rule assumptions |
| Biquad p. 9, Eqs. (10)–(20), Figs. 6–8 | Finite-gain polynomial, noise weights, finite output resistance | Source approximation versus exact KCL; numerical noise correction; RHP zero |
| Biquad pp. 10–12, Figs. 9–17, Eqs. (21)–(22) | In-situ gain, integrated noise, cascade bandwidth, component scaling | Q-dependent cascade and loading/noise/headroom tradeoffs |
| Biquad pp. 12–13, Figs. 18–21 | Compression, high-band error/peaking, feedforward and switch resistance | Keep unmet rejection targets; programmable-bank/PVT test plan |

## Corrections and qualifications

1. **Bandgap current and accuracy:** $64/4=16$ is the area ratio. The early 35-µA PTAT current is not the final summed current. The final graph around 0.5133–0.5151 V can have low temperature drift without meeting exact 0.500-V accuracy.
2. **Bandgap filter:** The unbuffered two-capacitor network has loading-dependent poles. It cannot be modeled as two isolated identical RC filters without a buffer or a different topology.
3. **LDO noise conventions:** The original uses $K_{VCO}=2\pi\times50$ MHz/V. Its algebra reproduces 32.18 nV/√Hz; declared one-sided voltage PSD with $\mathcal L=S_{\phi,1}/2$ gives 45.51 nV/√Hz. The source does not state a side convention, so record the difference as convention-dependent rather than a confirmed source typo. Real $K_{DD}$ and PLL filtering need separate extraction.
4. **LDO power:** At 1.2→1 V and 5 mA, input power is 6 mW, load power 5 mW and pass loss 1 mW before quiescent current. The source's phrase “provided to the load” uses the input voltage in its multiplication.
5. **TIA gain arithmetic:** $(R_F+R_o)/(1+A)$ gives 408.16 Ω for 1 kΩ, 1 kΩ and 3.9, not 200 Ω. The source's 200 Ω / 800 Ω simulations are internally consistent with feedback KCL and loaded voltage gain near four. Unloaded $A\simeq9$ produces those values if $R_o=1$ kΩ; do not conflate loaded and unloaded gain.
6. **TIA spectral/noise normalization:** Ideal rectangular NRZ gives 77.37% power within half the bit rate versus the source's approximate 75%. Its first-order noise normalization is not a flat-spectrum measurement. Original preliminary integration is 100 MHz–100 GHz and RMS is 1.34 mV.
7. **Biquad cascade bandwidth:** The source's 0.802 factor is valid for two identical $Q=1/\sqrt2$ sections. Two identical $Q=1$ sections give 0.90150 times single-section bandwidth. Identical second-order Butterworth sections are not a fourth-order Butterworth filter.
8. **Biquad finite gain:** Source Eq. (13), under its stated $A_0\gg1$ assumption, contains $(A_0+1)^2R_1R_2$ as the last constant term. Exact KCL for the stated crossed-feedback, constant-gain/zero-output-resistance model contains $A_0^2R_1R_2$. At $A_0=10$ the difference is material. Preserve the source approximation and state the independently derived model; neither replaces a transistor model.
9. **Biquad noise substitution:** Source Eq. (17) gives $(R_1/R_2)^2=0.0625$ for 500 Ω/2 kΩ, whereas original Eq. (18) prints 0.25. The first coefficient 2.25 is consistent. The resistor-noise example also uses approximately 300 K, whereas source transistor simulation temperature is 348.15 K.
10. **Unmet source specs:** The final TIA remains below 1 kΩ and warns against claiming 40-Gb/s operation after layout. The complete filter's 24/48-dB rejection remains below 25/50 dB, and high-band response is 88 rather than 80 MHz. These limitations are retained.

These observations concern the acquired copies; no publisher errata or independent measurement was checked. Historical references listed inside the articles are not presented as independently read sources.

**Dated supplement, 2026-10-05, after the third-batch review:** Equalizer Part Two's “Corrections to Previous Articles” (printed p. 12) supplies a formal correction to bandgap Fig. 9: connect $M_c,M_d$ gates to $M_a,M_b$ drains, respectively. The authored bandgap note now includes this correction and source reference. The statement above describes the evidence available at the original second-batch review, before this later article was read. See the [third-batch record](razavi-third-batch-verification.md); the core temperature/filter calculations are unchanged.

## Independent analytical verification

Run from any directory:

```powershell
python code/razavi_second_batch_analysis.py
```

The script uses NumPy and Matplotlib; no PDK/SPICE/silicon data. It compares derived transfer functions with separately implemented node or state equations, integrates the declared spectral models and generates four figures.

| Model / check | Independently calculated result |
|---|---|
| Bandgap linear-$V_{BE}$ KCL, 25 °C | 93.310 µA, 0.513204 V; cancellation ratio 6.27817 |
| Offset gain / 1.7-mV offset | 3.17308 / 5.39423 mV |
| Loaded passive filter poles | 11.0531 / 75.7587 MHz |
| LDO noise budget | 32.1823 / 45.5127 nV/√Hz for the two declared conventions |
| LDO ripple / illustrative efficiency | 40-mV peak / 80.128% at $I_Q=200$ µA |
| Isolated-capacitor current mismatch | 1-ps uncompensated delay for 10 mV, 0.5 pF, 5 mA |
| TIA DC KCL at unloaded A=3.9 | 408.163 Ω input, −591.837 Ω transimpedance |
| Gaussian receiver / first-order 20-GHz ENBW | 1.77696-µA RMS limit / 10.0254-pA/√Hz white ASD |
| NRZ spectrum, ±0.5 / ±0.7 bit rate | 77.3695% / 87.7640% |
| Source preliminary/final noise normalization | 9.70755 / 8.72162 pA/√Hz |
| AC-coupling droop, 100 bits, 40 Gb/s, 1% | Minimum time constant 248.748 ns |
| Biquad source approximation, A=10 | $f_n=10.5844$ MHz, $Q=0.688512$, $f_{3dB}=10.2988$ MHz |
| Biquad exact KCL, same constants | $f_n=9.73950$ MHz, $Q=0.633549$, $f_{3dB}=8.62399$ MHz |
| Cascade bandwidth ratios | 0.802243 at $Q=1/\sqrt2$; 0.901504 at Q=1 |
| Biquad opamp noise weights | 2.25 / 0.0625 |

All four generated figures were visually inspected; overlapping logarithmic labels in the cascade plot were corrected and the final plot re-inspected. Local links, JSON, image references, source checksums and script execution were checked. Remaining implementation tests are specified in each note; no startup yield, loop-margin simulation, actual BER, post-layout filter response or measured noise is claimed.
