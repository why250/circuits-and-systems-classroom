# Razavi Analog Mind: Fourth-Batch Verification

Review date: **2026-10-05**. This batch covers three millimeter-wave articles and **21 original PDF pages**. The PDFs, extracted text, original-page previews and Marker artifacts stay under gitignored `reference/razavi/`. The [source manifest](razavi-analog-mind.json) preserves stable URLs, DOI, issue metadata, original hashes and separate research/conversion status.

## Review coverage and article boundaries

| Source | PDF / printed pages | Reviewed scope | Authored note |
|---|---|---|---|
| VCO, Summer 2022 | PDF 1–7 / printed 6–12 | Full article, original pages, tank conventions, tuning/switch connections, noise, mirror changes and references | [Millimeter-Wave VCO Design](../Millimeter-Wave-VCO-Design.md) |
| Divider, Fall 2022 | PDF 1–6 / printed 6–10, 16 | Full article, original pages, FF polarity/state, modular feedback, clocked-inverter paths, sizing, timing, noise and power | [Millimeter-Wave Frequency Divider](../Millimeter-Wave-Frequency-Divider.md) |
| Synthesizer, Spring 2023 | PDF 1–8 / printed 6–13 | Full article, original pages, reused topology differences, filter/PFD/CP, loop equations, scaling, spectra, noise and jitter | [Millimeter-Wave Frequency Synthesizer](../Millimeter-Wave-Frequency-Synthesizer.md) |

The mailing-address advertisement on the VCO's last page is excluded. Divider printed p. 16 is shared with Shop Talk; only the Analog Mind continuation and its references enter the research. Synthesizer's website pp. 7–17 citation conflicts with the original pp. 6–13. Licensing/footer overlays in the synthesizer PDF are preexisting source artifacts. Historical papers and textbooks appearing in these bibliographies were not separately read and are not claimed as reviewed sources.

## Marker conversion review

All three sources converted successfully with **Marker 1.10.2**, CUDA, batch size 1, all pages, page separators and no LLM service. The retry exited zero. Original hashes match the acquisition manifest and conversion records. The initial sandboxed attempt failed because the external model-cache manifest could not be read, causing redundant downloads and destination collisions. Reusing the existing cache with the required access completed conversion; external model files/packages were not deleted or patched. Both logs remain local.

| Source | Zero-based page separators | Markdown image links | Metadata / links |
|---|---|---:|---|
| VCO | 0–6, complete | 13 | Seven page-stat entries; JSON parses; all image links resolve |
| Divider | 0–5, complete | 12 | Six page-stat entries; JSON parses; all image links resolve |
| Synthesizer | 0–7, complete | 22 | Eight page-stat entries; JSON parses; all image links resolve |

Converted text was reviewed around the major equations, phase labels, device dimensions and shared-page boundaries. Representative extracted images were visually checked: VCO Fig. 8 (differential switch), divider Fig. 4 (clocked-inverter stacks), synthesizer Fig. 5 (filter and pump). They preserve useful connections and dimensions. This is a review of critical material, not certification of every converted character.

| Source | Actual conversion observations / treatment |
|---|---|
| VCO | Eqs. (1)–(3) and (4)/(6) are readable, but Eq. (5) reads $1/O$ rather than $1/Q$. Fig. 6's branch is replaced by an incomplete `\\begin{array}` fragment, rather than a usable circuit image. Last-page mirror dimensions flatten into corrupted nm/m fragments; original Fig. 11 and prose govern. The 30-µm switch-length prose, thermal values and capacitance-loss discrepancy are source issues preserved by conversion. The mailing advertisement remains as an image. |
| Divider | Weighted divide-ratio expression is readable. Several complementary $CK$ labels and latch primes disappear in prose. Clock power $fCV_{DD}^2$ becomes displaced superscript text; later inverter/node labels corrupt. Fig. 4's image preserves the complementary clock bars and stack order. Shared printed p. 16 retains unrelated Shop Talk prose and references before the Analog Mind continuation; only the latter is used. |
| Synthesizer | Eq. (3) loses the square on $(1+2\\zeta^2)$ inside the inner radical; Eqs. (4)/(5)/(7) and pump Eqs. (11)–(14) are readable. Eqs. (8)–(10) preserve independently identified source inconsistencies, rather than introducing them. The first-page frequency-range dash is lost, $f_{REF}$ becomes $f_{RFF}$, and Fig. 1 is flattened to text. $f_{BW}$ becomes $f_{RW}$ in several places, and callout/column order is disjoint with some duplicated text. Extracted Fig. 5 preserves the pump dimensions and filter connections. Prose 27-fF / Fig. 19 26-fF discrepancy is in the original. |

Raw conversions remain intact and separate from the authored notes. All research conclusions use original-page checks and independent derivations where appropriate.

## Original-source anchors and treatment

| Source locator | Material checked | Project treatment |
|---|---|---|
| VCO p. 6, Fig. 1, Eqs. (1)–(2) | Cross-coupling, tank loss, thermal approximation, swing, reference/division assumptions | Explicit half-tank/differential conventions; current fundamental; source 200-MHz/$N=300$ discrepancy |
| VCO pp. 7–8, Table 1, Figs. 2–4 | EMX inductance/Q, swing/PN, MOS varactors, ripple and control noise | Source EM results distinct from models; ASD/SSB definitions and numerical discrepancies retained |
| VCO pp. 9–10, Eq. (3), Figs. 5–8 | Capacitance-weighted loss, switch resistance, parasitic/off capacitance, differential switch | Independent branch KCL, code overlap, total-versus-fixed capacitance arithmetic and 30-nm label |
| VCO pp. 11–12, Figs. 9–12 | Negative bottom-plate swings, pull-ups, mirror ratio/sizes/current, final PN | Explicit bias paths, AM-to-PM charge illustration; no universal lower-current noise benefit |
| Divider pp. 6–7, Figs. 1–3 | True/complemented FF states, returned modulus control, weighted static bits | Boolean cycles and $N=2^n+\sum2^{j-1}B_j$; nine/eight-stage configuration distinction |
| Divider pp. 7–9, Figs. 4–8 | Clocked-inverter stacking, sense/store phases, width sweeps, sharing and NAND latch | Explicit PMOS/NMOS paths, internal node, clock polarity requirements; ambiguous Fig. 8 clock labels not converted into an invented netlist |
| Divider pp. 9–10, Figs. 9–12 | 60-GHz schematic module, 30-GHz buffers/power, heterogeneous stages | Isolated latch speed distinct from chain/layout speed; clock-buffer load and code-update qualifications |
| Divider pp. 10, 16, Fig. 13; p. 9, Fig. 10 | Divide-by-575 sequence, retention, transition kinks and output/input-referred PN | 30-GHz output 52.174 MHz; timing validity, noiseless phase division and approximately 4-dB source penalty |
| Synthesizer pp. 6–7, Figs. 1–4, Eqs. (1)–(8) | Targets, reused VCO, NOR PFD, exact filter, damping/natural frequency and open-loop expression | Device/reference differences; derive KCL and $K_{pd}=I_p/(2\pi)$; record Eq. (8) prefactor inconsistency |
| Synthesizer p. 8, Figs. 5–7 | Pump implementation, constant-dynamics scaling, simulation cost | Preserve $I_p,C\downarrow$/$R\uparrow$ transform; step-count arithmetic separated from adaptive solver behavior |
| Synthesizer pp. 9–10, Figs. 8–14, Eqs. (9)–(10) | Accelerated loop, PSD scaling, modular divider, noise-injection method and lock | Derive exact averaged scaling, correct bandwidth/PSD dimensions, retain fixed parasitics and pulse-width limits |
| Synthesizer pp. 11–12, Figs. 15–22, Eqs. (11)–(14) | Spur/skew compensation, response/noise shaping, reset-duty pump noise and jitter integral | Peak/rms and SSB/one-sided conventions; duty-aware pump scaling versus reference scaling |
| Synthesizer p. 13, Fig. 23 | $N=16,32,64$ outcomes, PN plateaus and jitter extrapolation | Source table retained; no direct $N=300$ validation or measured jitter guarantee |

## Independent discrepancies and qualifications

No formal publisher erratum for these three articles was established in this batch. The following are independently checked discrepancies or model qualifications, not publisher-issued corrections. Original PDFs and raw conversions are preserved.

1. **Reference configurations:** VCO 200 MHz/$N=300$ implies 60 GHz; at 30 GHz the ratio is 150. Divider 50 MHz needs 560–640, while synthesizer 100 MHz needs 280–320. A nine-stage 512–1023 divider cannot directly supply the latter range.
2. **VCO equation values:** Source thermal algebra gives −110.87 dB at 1 MHz for its stated 350-K/2-mA/Q32/30-GHz parameters. Source prose quotes −112 and −114 dBc/Hz; side normalization is not fully stated. A consistently defined SSB −110-dBc/Hz target permits 2.354-nV/√Hz one-sided control ASD at $K_f=1.9$ GHz/V; the quoted 4.4-nV/√Hz number is not reproduced from those exact definitions.
3. **Tank loss arithmetic:** Fixed/varactor ratio 20 and Q32/Q20 give a 7.08% Q reduction, rather than approximately 9%. A 470-fF fixed plus 140-fF Q32 bank gives total Q26.027; using total 610 fF as fixed capacitance before adding 140 fF gives approximately Q27, explaining the different source estimate. Switch-length prose says 30 µm where Fig. 7 labels 30 nm.
4. **AM-to-PM and current:** The final tail/reference reduction improves a source upconversion mechanism; the ideal thermal equation alone predicts a different current tradeoff. The 1.33-mW core/reference subtotal omits buffers and additional controls.
5. **Divider coverage:** A61/B105-GHz isolated divide-by-two results do not establish complete MMD/layout speed. Source Fig. 13's 30 GHz divided by 575 is 52.174 MHz; 50-MHz locked feedback at that ratio would require 28.75 GHz. Power of the clock buffers is substantial relative to the module core.
6. **Reused VCO:** Synthesizer Fig. 2 changes core/varactor/bottom-switch sizes, still draws an ideal tail and omits pull-ups while reusing prior noise curves. Do not claim identical final configurations or saved decks.
7. **PLL normalization:** Source Eq. (8) uses $2\pi I_p$ for open-loop gain where its Eq. (4)/(5) and pulse-charge averaging require $I_p/(2\pi)$. This is a $4\pi^2$ loop-gain discrepancy. The project defines $L$ as open-loop and $H=L/(1+L)$ as normalized closed-loop reference response.
8. **Bandwidth and PSD:** Source Eqs. (9)–(10) use $f_{REF}$ in the bandwidth-scaling context, and Eq. (10) squares $S_{REF}$. Independent derivations use loop bandwidth and PSD to the first power. Source reference-response bandwidth, oscillator-noise shaping and unity gain are distinct.
9. **Reset-duty noise scaling:** Fixed $T_{res}$ makes pump duty $T_{res}f_{ref}$ increase with acceleration. Pump plateau decreases by $K$ and broadly integrated white variance stays constant, while fixed white reference PSD gives variance $1/K$. Lumping these into one fixed input PSD does not establish a universal $\sqrt K$ jitter law. At doubled $N$/halved reference, Eq. (11)'s fixed-reset pump plateau increases 3 dB, not the p. 13 expectation of 6 dB.
10. **PSD side convention:** Starting from one-sided $4k_BTg_m$, source Eq. (12) gives a one-sided phase density; translating to SSB introduces a factor 1/2. Eq. (14) separately doubles the plotted integral. Retain this convention ambiguity; do not assert an unexplained simulation measurement error.
11. **Numerical reporting:** Source 500-ns/5-ps arithmetic is 100,000 nominal steps, not 500,000. At $N=16$, $C_2$ is 27 fF in prose versus 26 fF in Fig. 19. The 100-mVpp control disturbance includes carrier feedthrough and is not entirely reference ripple.
12. **Target margin:** Scaled simulated jitter and source extrapolations do not directly validate an unscaled $N=300$ loop, full noise budget or post-layout result. Fixed integration limits, pulse folding, flicker and physical parasitics must be checked explicitly.

## Independent analytical verification

Run from the repository root, or use the script's absolute path:

```powershell
python code/razavi_fourth_batch_analysis.py
```

The script uses NumPy/Matplotlib and locates outputs relative to itself. It checks switched-branch admittance against node KCL, nonlinear-capacitor fundamental against charge integration, simple divide-by-2/3 Boolean periods and all arithmetic codes, complete-filter impedance against two-node KCL, second-order response, third-order stable roots, and both loop-scaling identities. Independent numerical integration distinguishes fixed-white-reference and reset-duty pump scaling.

| Model / conditions | Independent result |
|---|---:|
| VCO, 53-pH half tank, Q32, 30 GHz | $R_p=319.688$ Ω |
| Ideal fully steered 2-mA swing | 0.81408 Vpp single ended |
| Ideal per-side total C, 28 / 32 GHz | 609.605 / 466.729 fF |
| Source thermal algebra, 350 K, 1-MHz offset | −110.867 dB |
| Varactor-loaded Q, fixed/varactor 20, Q32/Q20 | 29.7345 |
| Tank Q, fixed470/bank140 fF, both Q32 losses | 26.0267; 1.7946-dB $Q^{-2}$ penalty |
| 140-fF branch Ron for Q32 at 30 GHz | 1.184 Ω |
| Illustrative single-ended / differential-switch off C | 70 / 46.6667 fF per half |
| Divider Boolean period, MC0 / MC1 | 2 / 3 input cycles |
| Nine-stage arithmetic range | 512–1023, all 512 static codes |
| 30 GHz / 575 | 52.1739 MHz |
| Clock-buffer effective C from 0.92 mW | 33.9797 fF |
| Illustrative sharing, $C_Q=4$ fF, $C_N=2$ fF, 0 / 0.95 V | 0.316667 V |
| Retention example, 4 fF, 300-mV droop, 10 ns | 120-nA maximum constant leakage |
| PLL second-order natural frequency / damping | 2.40356 MHz / 0.998544 |
| Second-order / complete-filter reference bandwidth | 5.96108 / 6.53829 MHz |
| Complete loop unity frequency / phase margin | 4.75620 MHz / 68.6264° |
| Complete filter extra pole | 37.7909 MHz |
| Source rough reference-plus-VCO jitter estimate | 34.8691 fs |
| $K=37.5$ ideal reference / pump variance ratios | 0.0266667 / 1 |
| Source $\sqrt K$ jitter projections at N8/16/32/64 | 251.073 / 203.516 / 183.712 / 194.856 fs |
| −50-dBc sinusoidal ripple budget, 100 MHz, 2.08 GHz/V | 0.304065 mV peak |

The scaling integrals deliberately use a broad illustrative mathematical range (100 Hz–100 GHz, then scaled limits). They verify an ideal identity and are not a physical averaged-loop validity claim across that range, a replication of source jitter, or a check of its fixed 10-kHz–1-GHz target. All three generated plots were visually inspected. Final checks passed for all 22 PDF hashes / 156 page counts, 13 reviewed / 9 pending entries, conversion checksums/page statistics/image links, authored local links/math delimiters, Python syntax and whitespace. Analytical checks do not validate transistor noise, EM Q, clocked timing, layout parasitics or terminal stress; concrete implementation test plans are retained in each note.
