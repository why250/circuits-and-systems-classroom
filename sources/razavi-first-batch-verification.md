# Analog Mind: First-Batch Source Verification

Review date: 2026-10-04. Original PDFs remain under gitignored `reference/razavi/`; stable download links, checksums and metadata are in [the source manifest](razavi-analog-mind.json). Source inspection, analytical checks and circuit simulation are separate statuses.

## Review Coverage

| Source | PDF / printed pages | Review coverage | Project note |
|---|---|---|---|
| Bootstrapped sampling, Winter 2021 | PDF 1–6 / printed 7–12 | Full text and all rendered pages, including topology, equation, final circuit and references | [Bootstrapped Sampling Switch](../Bootstrapped-Sampling-Switch.md) |
| Comparator, Fall 2020 | PDF 1–7 / printed 8–14 | Full text and all rendered pages, including transistor connections, mismatch, regeneration, noise and kickback | [StrongARM Comparator Design](../StrongARM-Comparator-Design.md) |
| z-transform, Summer 2020 | PDF 1–7 / printed 8–14 | Full text and all rendered pages, including all delay/filter/feedback diagrams and numbered equations | [z-Transform for Analog Designers](../Z-Transform-for-Analog-Designers.md) |

PDF extraction supported navigation and reading; original rendered pages supplied the reference for equations and connectivity. Marker is an auxiliary local conversion stage, with its status recorded independently in the source manifest. Generated Markdown does not establish review completion.

## Marker Conversion Review

Local conversion uses Marker 1.10.2 with page separators, no LLM service, and inference batch size 1. The existing Python/CUDA environment and cached models are reused. The initial restricted cache read caused a false download attempt/file collision; using the installed cache resolved that problem. The default inference batch then exceeded the 8-GB GPU's available memory; reducing the batch allowed conversion to proceed. No model package or user cache was deleted or modified to repair these issues.

The converted Markdown and extracted images remain under gitignored `reference/razavi/marker/<source>/`, separate from the authored notes. Each completed conversion records its input SHA256 in `conversion.json` and confirms unchanged original PDF bytes. Human review here checks page boundaries, generated image references and important formulas/connectivity against the already reviewed original pages; it does not certify every OCR character or rewrite the raw conversion.

| Converted source | Observed defects and treatment |
|---|---|
| Bootstrapped sampler | Six zero-based page separators retained. Printed p. 8's text-layer mathematics remains garbled (LSB, attenuation and subscripts). On printed p. 10, Fig. 7's transistor drawing is reduced to inline arrow expressions rather than a usable extracted circuit image; use the original page. Fig. 9's converted caption misreads $M_5$ and $C_B$. Eq. (1) is usable, but its correctness is established by the original p. 7 and independent noise-budget derivation. |
| Comparator | Seven page separators retained; source Fig. 1's extracted image preserves the core connections and waveforms. Text substitutions include $C_Y\to C_v$ and misread $X/Y$ and device indices; printed pp. 10–11's RSS expressions remain garbled. Eqs. (2)–(6) are readable, but the source's incorrect time-constant prose is also preserved and still needs independent correction. Printed p. 13 changes the counted output node $V_X$ to $V_S$ in the noise-extraction prose; use the original page. |
| z-transform | Seven page separators retained. On printed p. 10, the inline $z=e^{T_{CK}j\omega}$ is misread as an exponent involving $T_{CK}/\omega$, and Eq. (12)'s number is lost. On printed p. 11, the Nyquist condition $z^{-1}\to-1$ loses its minus sign. Printed p. 12's Fig. 10 is replaced by an incomplete LaTeX array rather than an extracted diagram. Eqs. (17)–(22) remain usable, but feedback signs are established by original Fig. 15 and independent state recurrence. |

## Checked Source Anchors

| Source locator | What was checked | Project treatment |
|---|---|---|
| Sampler p. 7, Fig. 1, Eq. (1) | Switch roles; differential $2kT/C_1$; signal $A^2/2$; quantization $\Delta^2/12$ | Retain single-ended/differential distinction; derive a capacitance budget |
| Sampler pp. 8–9, Figs. 2–5 | Phase coverage, FFT of held values, distortion versus main-switch width | Independent coherent-record/alias calculations; source simulations labeled |
| Sampler pp. 10–11, Figs. 6–9 | Turn-off, wells, isolation, recharge and bootstrap droop | Explain incremental failures without mixing different lumped capacitance models |
| Sampler p. 12, Figs. 10–11 | Protection, moving control, startup, final dimensions and HD3 | Preserve separate startup/protection/bandwidth roles; PDK stress remains unverified |
| Comparator p. 8, Fig. 1 | Cross-coupled gates, reset connections and phases | Explicit terminal table and phase-local model |
| Comparator p. 9, Eq. (1); pp. 10–11, Figs. 4–8 | Pair mismatch, effective length, offset contributions, core-delay criterion | RSS/yield calculation; dimensions remain source-specific |
| Comparator p. 12, Eqs. (2)–(6), Figs. 11–12 | Exponential regeneration, initial state, time shifts | Re-derive time constant; separate regeneration and total delay |
| Comparator pp. 13–14, Figs. 13–16 | Decade shifts, 16% decision method, noise and kickback | Joint offset/noise extraction and finite-trial uncertainty |
| z-transform pp. 8–9, Eqs. (1)–(11), Figs. 1–5 | Delay, sampled representation, mode mapping, delay/advance sign | ROC, zero-state, dimensional expansion condition and causality qualifications |
| z-transform pp. 10–12, Eqs. (12)–(16), Figs. 6–12 | Summing signs, magnitudes, DC/Nyquist zeros, factorization | Independent frequency plots and endpoint checks |
| z-transform p. 13, Eqs. (17)–(22), Figs. 13–15 | Delaying integrator, feedback signs, noise injection | STF/NTF plus an independently implemented time-domain recurrence |
| z-transform pp. 13–14, Figs. 16–18 | Two-cycle filters, periodic response, stability mapping | Causal BIBO qualifications and accumulator counterexample |

## Corrections and Qualifications

1. **Issue metadata:** The sampler PDF is Winter 2021; the website labels it Summer 2021. Its DOI contains 2020 but its issue year is 2021.
2. **Continuation pages:** Large spans are not automatically errors. The 2026 CDR PDF has six pages: 11–15 and 116. The 2022 LDO PDF has five: 7–10 and 17. A shared continuation page can also contain unrelated columns; future reviews must isolate the article's own section.
3. **Sampler phase count:** On p. 8, $f_S/f_{in}=P/Q$ in lowest terms repeats after $P$ clock samples and $Q$ input cycles. The statement “only Q values” conflicts with this relation; its $500/57$ example correctly gives 500 clock cycles. Distinct phases and distinct sine amplitudes are different counts.
4. **Comparator regeneration units:** On p. 12, the original prose gives $\tau_{reg}=g_m/C_X$. That expression has units s$^{-1}$; solving $C_Xdv/dt=g_mv$ gives $\tau_{reg}=C_X/g_m$. The rendered PDF confirms the ordering, so this is not an OCR correction.
5. **Pure-delay approximation:** On p. 8 of the z-transform article, $1-sT_D$ has a right-half-plane zero as an approximation to $e^{-sT_D}$. The exact exponential has no finite zeros; require $|sT_D|\ll1$.
6. **Stability:** Unit-circle modes may persist, but such poles do not generally establish BIBO stability. An ideal accumulator grows with bounded DC input; repeated poles and hidden state modes need further analysis.
7. **Four-tap factorization:** On printed p. 12, the z-transform article's intermediate expression lacks grouping around $1-z^{-1}$ before the $-z^{-2}(1-z^{-1})$ term. The expanded polynomial and final factorization are consistent; the project verifies $1-z^{-1}-z^{-2}+z^{-3}=(1-z^{-1})^2(1+z^{-1})$ independently.

These observations concern the reviewed copies and independent derivations. No publisher erratum was checked.

## Independent Verification

`python code/razavi_first_batch_analysis.py` checks:

- Rounded/exact LSB budgets: 445.35/466.98 fF per side; attenuation limit: 44.48 $\Omega$.
- 4096 coprime input phases, distinct harmonic bins, and a 2.41-GHz third-harmonic alias.
- Nonzero-offset noise extraction; 4.735-mV offset RSS and 70.90% illustrative ±5-mV yield.
- A 5.7-ps decade shift yielding a 2.4755-ps local regeneration time constant.
- FIR magnitudes/factorization, accumulator recurrences, and independently implemented feedback STF/NTF.
- The in-band white-error integral and its large-OSR approximation.

Plots are generated from these equations and visually reviewed. No claim is made of source-figure reproduction, PDK validation, measured yield, actual BER or nonlinear ADC performance.
