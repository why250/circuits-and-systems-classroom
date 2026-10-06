# Razavi Analog Mind: Fifth-Batch Verification

Review date: **2026-10-05**. This batch covers phase interpolation and clock/data recovery, **11 original PDF pages**. The original PDFs, extracted text, page previews and Marker artifacts stay under gitignored `reference/razavi/`. The [manifest](razavi-analog-mind.json) preserves original hashes, URLs, DOI, metadata and independent research/conversion progress.

## Coverage and source boundaries

| Source | PDF / printed pages | Full reviewed scope | Knowledge note |
|---|---|---|---|
| Phase interpolator, Fall 2023 | PDF 1–5 / printed 6–10 | All original pages, waveform/phase conventions, inverter/resistor paths, feedback, predistortion, fine stack, MUXes, jitter and references | [Phase Interpolator Design](../Phase-Interpolator-Design.md) |
| Clock/data recovery, Summer 2026 | PDF 1–6 / printed 11–15, 116 | All original pages, aligned FF timing, Alexander decisions, CML/XOR terminals, filter and loop equations, VCO/buffer, noise/data tests and references | [Clock and Data Recovery](../Clock-and-Data-Recovery.md) |

PI printed p. 10 is shared with the Editor's Note and a related-article appendix; those sections are excluded. CDR p. 116 is shared with unrelated CEDA/publication news; only the Analog Mind continuation, Fig. 17 and references are included. Preexisting licensing/footer overlays are retained. References listed by these articles were not separately read unless a previously reviewed Analog Mind article is explicitly cited in the authored note. No formal publisher erratum for these two articles was established in this batch.

## Marker conversion review

Both PDFs converted using Marker 1.10.2, CUDA, all pages, page separators and no LLM service. PI used batch size 1; CDR completed with batch size 4 and `OMP_NUM_THREADS=4`. The initial CDR batch-size-1 run was interrupted in its owned session because recognition was too slow; the CDR-only retry exited successfully. The installed models/cache were reused; no external package or model files were patched or deleted. Original-page research and independent analytical checks do not rely on successful OCR.

| Conversion | Zero-based page separators | Resolved image links | Page-stat entries | Input checksum |
|---|---|---:|---:|---|
| PI | 0–4 | 14 | 5 | Matches acquisition record |
| CDR | 0–5 | 27 | 6 | Matches acquisition record |

The PI's Markdown has complete zero-based page separators 0–4, 14 resolved image links and five page-stat entries. Its conversion checksum matches the acquisition record. Eqs. (1)–(3) are readable; the initial ideal average changes one $V_Q$ to $V_O$, several overbars disappear or move, and much of the quarter-period/code arithmetic flattens into italic fragments. Predistortion resistor groups and Ω units become corrupted `X`/superscript text. Four-quadrant prose loses complementary-phase bars, making opposite clock selections appear identical. The original 17.4-ps/4 calculation and peak-to-peak/RMS estimate are source issues, not OCR errors. The shared Editor's Note/appendix is retained in raw conversion and excluded from research.

Extracted PI Figs. 7, 11 and 13 were visually checked. They preserve the feedback connection, shared gate drive of the fine stacked branch, complementary clock labels and two MUX ranks. Raw text alone is insufficient for those connections.

The complete CDR Markdown was read. Eqs. (1)–(3), sample XOR logic and the displayed damping expression are readable; the missing factor 1/2 in damping is present in the original source, not introduced by OCR. Later prose flattens phase ratios and $\Delta\phi$ into italic fragments, loses inequality/infinity symbols and distorts degree-to-picosecond expressions. $R_1$/$C_1$ become `RI`/`CI`, and Ω becomes `X`. Some generated anchors exist but point to the wrong content: reference citations linked to `#page-5-0` land in unrelated CEDA news, the Fig. 13 link to `#page-3-3` lands at the Fig. 12 caption, and the Fig. 17 link to `#page-5-1` lands at “Share What's New.” Textual anchor existence does not establish semantic correctness. The 27 extracted images comprise 17 article figures and 10 unrelated publication images, including logos, a headshot and social icons. Shared-page news remains in the raw conversion and is excluded from research.

Extracted CDR Figs. 5, 7, 9 and 11 were visually checked. They preserve sample alignment and clock labels, the Gm output into the series RC, the distinct single-pole voltage-filter model, and the symmetric XOR device triplets/current truth table. Source filter-model differences and the undrawn $M_7$ width annotation remain visible. Conversion review checks critical material and representative figures, not every OCR character; raw conversions are preserved separately from authored notes.

## Original-source anchors

| Source locator | Checked material | Treatment |
|---|---|---|
| PI p. 6, Figs. 1–2 | Half-rate environment, targets, opposing inverters and separated edges | Separate UI/clock period, voltage/phase/time interpolation, slew and contention |
| PI p. 7, Figs. 3–5, Eqs. (1)–(2) | Four branches, width changes, passive resistor summation | Waveform assumption stated; 3:1 phasor is 18.435°, not automatically a 22.5° time step |
| PI pp. 7–8, Figs. 6–8 | Finite-feedback inverter, hundreds-of-mV summing-node swing, 16 branches and MUXes | Independent node KCL and finite-gain condition; no ideal virtual-ground assumption throughout cycle |
| PI p. 8, Eq. (3); p. 9, Fig. 9 | $m$ counts I branches, decreasing phase characteristic, quarter-period estimate | Keep source's code orientation; correct 28-GHz quadrant separation and minimum uniform intervals |
| PI p. 9, Figs. 10–11 | Resistor sequence, unresolved 400-fs target, fine series stack | Exact ideal conductance extension distinct from physical weights; fine-code monotonicity condition |
| PI pp. 9–10, Figs. 12–13 | 156–362-fs steps, four quadrants, transmission gates, input load and attenuation | Explicit endpoints/quadrant sweep, codebook requirements, driver-versus-total power |
| PI p. 10, Fig. 14 | Noise 1 MHz–200 GHz, 60-fs peak-to-peak spread and divide-by-six RMS estimate | Report source estimate; require actual crossing statistics and record-dependent confidence |
| CDR p. 11, Figs. 1–3 | Receiver variants, full-rate VCO, random data and long runs | Keep PI-based half-rate system separate; specify data quality and acquisition limits |
| CDR p. 12, Figs. 4–6 | Samples, storage/alignment and XOR decisions | True sample-to-FF map and truth table, clock-reference convention, no-information case |
| CDR p. 13, Figs. 7–9, Eqs. (1)–(3) | Gm output/series RC, distinct voltage LPF diagram, tracking/residual transfer and damping | Independent type-I/type-II/finite-output-resistance models; damping factor 1/2 |
| CDR p. 14, Figs. 10–11 | CML feedback terminals, symmetric three-device current-steering groups, load change | Explicit connections, current XNOR versus voltage XOR; do not infer undrawn $M_7$ |
| CDR pp. 14–15, Fig. 12 | Finite average PD gain, random-data averaging, asymmetry and dead region | Transition-density/Gaussian extension; no universal constant bang-bang gain |
| CDR pp. 14–15, Fig. 13 | Center-tapped core/buffer, varactors, power and kickback isolation | Distinguish oscillator versus common-source buffer and full/half inductance |
| CDR p. 15, Figs. 14–16; p. 116, Fig. 17 | Acquisition/control ripple, clock/data eye and periodic-input noise test | Source results separate; no fixed peak-to-peak/RMS ratio, frequency-capture proof or low-BER guarantee |

## Independently derived discrepancies and qualifications

1. **Clock period:** 56-Gb/s UI is 17.857 ps; a 28-GHz clock period is 35.714 ps, so quadrature spacing is 8.929 ps. PI p. 8's $(17.4\text{ ps}/4)/(0.4\text{ ps})\approx11$ mixes data and clock timing. At least 23 uniform intervals are required; 16 uniform intervals are 558 fs.
2. **Voltage versus angle:** Linear voltage weighting gives uniformly weighted time only in the overlapping equal-slope ramp model. Quadrature sinusoids obey an arctangent; source Eq. (3) counts I branches while the project's increasing code counts Q branches. No sign/index correction is silently applied to raw sources.
3. **Feedback/mismatch:** A source summing node swinging hundreds of millivolts is not an ideal virtual ground during the complete waveform. Thermometer monotonicity is provable for constant positive weights, not every loaded/mismatched transient. A fixed fine branch cannot halve every nonuniform coarse step exactly; endpoints and rollover need an explicit codebook.
4. **Timing noise:** Source PI <10-fs RMS is estimated from roughly 60-fs peak-to-peak by dividing by six. Gaussian peak-to-peak spread has no universal RMS conversion without sample count/correlation/confidence. Static phase quantization, random electronic jitter and loop limit cycles are separate budgets. Common input clock jitter passes through equal-weight interpolation rather than averaging away.
5. **Power boundaries:** PI's approximately 0.9-mW estimate concerns two input clock drivers, not complete final PI consumption. CDR reports VCO/buffer current and XOR currents but no complete power subtotal demonstrating <10 mW. Source targets remain visibly distinct from results.
6. **Alexander signs:** The source late/early patterns are retained; physical correction requires gate voltage polarity and tuning sign. The current-steering XOR's output current is high for equal inputs, while its pulled-up voltage is high for unequal inputs. The four FF sample alignment is part of the detector function.
7. **Damping:** CDR Fig. 9(b)'s voltage-filter model gives $\omega_n^2=K_{pd}K_\omega\omega_p$ and $2\zeta\omega_n=\omega_p$. The following original prose omits the factor 1/2 from $\zeta$. This discrepancy was checked against the original page and independent state equations.
8. **Filter models:** An ideal Gm injecting into the top of the **series** RC in CDR Fig. 7 yields $Z=R+1/(sC)$ and a type-II loop. Fig. 9 instead uses a unity-DC single-pole **voltage** filter/type-I loop. Finite Gm output resistance gives lead–lag $Z=r_o(1+sRC)/[1+s(R+r_o)C]$, not automatically the latter model. Source device/output-impedance information is insufficient to identify one complete physical loop or its unique bandwidth.
9. **Holdover:** No transition yields zero intended differential correction, not zero oscillator noise/mismatch/leakage. Ideal capacitor hold and dissipative finite-output-resistance filtering cannot be combined without a DC bias/hold model. Actual encoded run lengths and frequency offset determine timing drift.
10. **Jitter observations:** Source recovered-clock/data spreads of 400/520 fspp and periodic-input noise spread of 150 fspp are distinct tests. The latter uses a 28-GHz periodic data pattern in a 56-GHz/full-rate loop and a 100-ns observation; it is not a half-rate VCO test or a random-data RMS/BER result. Data pattern changes detector gain and acquisition behavior.
11. **Source implementation limits:** Clock/differential routing, XOR load, metastability, Gm topology, oscillator tuning gain, actual EM ports and terminal stress still require a complete netlist/PDK. The annotated CML width range includes $M_7$ although no seventh transistor is drawn; none is invented in the note.

These are source qualifications and independent model derivations, not claimed publisher corrections or reproductions of the reported transistor results.

## Independent analytical verification

```powershell
python code/razavi_fifth_batch_analysis.py
```

The script uses NumPy/Matplotlib, locates outputs from its own directory, and needs no PDK. Checks include direct sinusoidal crossings versus phasor angle, independent complex phase perturbation, exact ideal predistortion, positive-weight monotonicity, feedback-inverter KCL, Alexander sample-pattern truth tables, XOR current polarity, both loop transfer polynomials versus independently stamped state equations, finite-output-resistance filter KCL, Gaussian average gain and charge/frequency integration of leakage drift. Mixed-scale state variables are normalized before the linear solves to avoid numerical conditioning errors.

| Model / condition | Independent result |
|---|---:|
| UI / half-rate clock period / quadrant | 17.8571 / 35.7143 / 8.92857 ps |
| Uniform intervals needed for 400 fs | At least 23 |
| Equal 16-branch phasor minimum / maximum step | 378.380 / 706.847 fs |
| Uniform 16 / 32 interval | 558.036 / 279.018 fs |
| First 16-branch step / 3I+1Q phase | 3.81407° / 18.43495° |
| Exact ideal 16-unit conductance spread | 1.82068 |
| Equal-weight independent / common phase variance ratio | 0.5 / 1 |
| Two 16-fF clock drivers, 28 GHz, 0.95 V | 0.80864 mW |
| Illustrative sigmoid best $\tau$ / jitter, 1-mV noise | 5.78098 ps / 20.9908 fs RMS |
| Hypothetical uniform quantization, 362-fs step | 104.500 fs RMS, not source electronic jitter |
| Type-I illustrative $f_n$ / correct damping | 20 MHz / 0.707107 |
| Missing-half source damping at those parameters | 1.414214 |
| Matched-pole type-II illustrative resistor | 2.81349 kΩ; not source's 1 kΩ |
| Source 1-kΩ / 4-pF series-RC zero | 39.7887 MHz; not established CDR bandwidth |
| Finite-$r_o$ illustration, 10 kΩ, pole | 3.61716 MHz |
| Gaussian averaged gain, 200 fs, 0.5 density, 20 mV | 0.113381 V/rad |
| Type-I illustrative steady error, 100 ppm at 56 GHz | 22.6880° |
| Long run, 1,000 bits, 100-ppm mismatch | 1.78571-ps drift |
| Leakage illustration, 20 nA / 4 pF / 100 ns | 0.5 mV; 0.446429-ps drift at $K_f=1$ GHz/V |
| 50° / 10° at 56 GHz | 2.48016 / 0.496032 ps |
| Source VCO/buffer / two-XOR tail power subtotal | 2.85 / 0.76 mW |

Both generated plots were visually inspected. All 22 original PDF hashes / 156 page counts passed. Fifteen reviewed entries cover 97 pages; seven pending entries cover 59 pages. Authored local links, math delimiters, whitespace and Python syntax passed. Numerical results are independent ideal/illustrative models, not a recreation of source transistor waveforms, noise extraction, final codebook or post-layout loop. Concrete implementation tests remain in the notes.
