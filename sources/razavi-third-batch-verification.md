# Razavi Analog Mind: Third-Batch Verification

Review date: **2026-10-05**. This batch covers three high-speed link articles and **19 original PDF pages**. The source PDFs, extracted text, page previews and raw Marker conversions remain under gitignored `reference/razavi/`. Stable URLs, DOI, issue metadata, hashes and progress are recorded in the [source manifest](razavi-analog-mind.json). Full reading, original-page review, conversion review and independent analytical calculations are separate evidence categories.

## Review coverage and article boundaries

| Source | PDF / printed pages | Reviewed scope | Knowledge note |
|---|---|---|---|
| Broadband I/O, Spring 2021 | PDF 1–7 / printed 6–11, 15 | Full article, all page previews, mutual-inductance dots, topology variants, matching, transient behavior and references | [Broadband I/O and T-Coil Design](../Broadband-IO-and-T-Coil-Design.md) |
| Equalizer Part One, Fall 2021 | PDF 1–6 / printed 7–11, 160 | Full article, all page previews, channel ladder, RC bridge, pole placement, loading and programming | [Continuous-Time Linear Equalizer](../Continuous-Time-Linear-Equalizer.md) |
| Equalizer Part Two, Winter 2022 | PDF 1–6 / printed 7–12 | Full article, all page previews, signed taps, clocks, latch/summer connections, noise, recovery, source eyes and formal corrections | [Decision-Feedback Equalizer and CML Latch](../Decision-Feedback-Equalizer-and-CML-Latch.md) |

The upper part of I/O's printed p. 15 belongs to Circuit Intuitions and is excluded. The upper part of CTLE's printed p. 160 is a VLSI symposium report and is excluded. Their Analog Mind continuations and references are included. Part Two's correction section is relevant to this batch and the previously reviewed bandgap. Older works appearing in article bibliographies were not separately read and are not represented as reviewed sources.

## Marker conversion review

All three PDFs converted successfully with **Marker 1.10.2**, CUDA, inference batch size 1, all pages, page separators enabled and no LLM service. The existing installed environment/model cache was reused. Conversion process exit status was zero. Original PDF bytes are unchanged and SHA256 matches are checked against both conversion records and the acquisition manifest.

| Source | Zero-based page separators | Markdown image references | Metadata / links |
|---|---|---:|---|
| Broadband I/O | 0–6, complete | 15 | JSON parses; all resolve |
| CTLE | 0–5, complete | 11 | JSON parses; all resolve |
| DFE | 0–5, complete | 17 | JSON parses; all resolve |

Converted text was inspected for the important matching/transfer expressions, CTLE bridge factor and pole placement, and DFE timing, BER and published corrections. Representative extracted circuit images were visually checked: I/O Fig. 4, CTLE Fig. 4, DFE Fig. 5 and DFE Fig. 9. The images preserve useful connectivity, but text alone cannot establish transistor terminals or crossing-wire connections.

| Source | Actual conversion observations / treatment |
|---|---|
| Broadband I/O | Eq. (7) reads the mutual term as `M_S` rather than $Ms$. Eqs. (9)–(10) preserve the original article's subsequently corrected expressions; this is a source issue, not an OCR repair. The numbering jumps to (19) after the intermediate center-node expression, so original anchors govern. Printed p. 11 heavily flattens voltage ratios, $t=0^+$, node subscripts and units into italic fragments. The Fig. 4 extracted image preserves inductive dots, the bridge and center capacitor. Shared p. 15 retains unrelated circuits/text ahead of the continuation. |
| CTLE | Eqs. (1)–(3), the $g_mR_S/2$ bridge factor and pole-placement Eq. (8) are readable and agree with original-page checks. One prose reference reads `C_1` where the discussion concerns $C_S$. Later prose converts Ω to `X`, distorts the Nyquist-frequency expression and flattens the BER exponent. Fig. 4's extracted image clearly shows the single source-to-source bridge and separate current sinks. Shared p. 160 retains the unrelated symposium report. |
| DFE | Timing and BER equations are readable; the text retains the source's dimensionally incorrect “4σ variance” phrase. Transistor-size prose around Fig. 5 becomes `5 3 nm n0 m`, and the resistor expression becomes `1mA # RD ... 500 X`; values require the original image. Complementary clock overbars are lost in some prose. One summer-alignment sentence reads $V_R$ instead of the output-node $V_B$. Figs. 5 and 9 are usable extracted images, including crossed regeneration and feedback wiring. Corrected polynomials (4)–(5) and the bandgap gate correction are retained. |

Raw conversions are preserved, not silently rewritten or used as the authored notes. This review covers important formulas, boundaries and representative figures; it does not certify every OCR character.

## Original source anchors and treatment

| Source locator | Checked material | Project treatment |
|---|---|---|
| I/O p. 6, Figs. 1–2, Eqs. (1)–(2) | 470-fF load, 50-Ω terminations, bandwidth/return loss, 40-Gb/s edges | Distinguish loaded bandwidth from −10-dB matching and negative reflection dB from positive return loss |
| I/O pp. 7–9, Figs. 3–5, Eqs. (3)–(26) | Coupled-coil dots, classic/current/voltage/RX variants, matching, all-pass/low-pass nodes | Explicit MNA and corrected general polynomials; qualify group-delay flatness and excitation symmetry |
| I/O pp. 9–10, Figs. 6–7 | Current-mode values, 70-fF pad and 25-pH extra coil | Retain source eye/matching outcomes as source simulations; independent ideal model separate |
| I/O pp. 10–11, Figs. 8–10 | Voltage-mode source, ideal-step dip, component labels | Derive negative ideal step excursion and record 300-fF prose / 330-fF Fig. 10 discrepancy |
| I/O pp. 11, 15, Fig. 11 | RX center-node output and 350-fF load | Separate matching from actual channel/sampler validation |
| CTLE p. 7, Fig. 1 | One channel section, twelve-section loss, source/load 50 Ω | Independent ABCD and 25-node ladder, DC/insertion-loss normalization |
| CTLE p. 8, Figs. 2–3 | Analog equalization, Nyquist pattern, long-run transition and notch claim | Distinguish steady periodic and history-dependent behavior; qualify DFE recovery of channel zeros |
| CTLE pp. 9–10, Figs. 4–6, Eqs. (1)–(8) | Single bridge factor, zeros/poles, small boost, cascade pole limit | KCL derivation, generalized plateau fraction, exact pole example versus practical source capacitance |
| CTLE pp. 10–11, Figs. 7–9 | 600-pH peaking, two nonidentical loaded stages, eye, headroom/power | Separate source results from illustrative loaded model and Part Two's starting summary |
| CTLE pp. 11, 160 | Programmable source capacitors | Finite-frequency boost versus unchanged ideal asymptote; switch-resistance/off-capacitance extension |
| DFE pp. 7–9, Figs. 1–4, Eqs. (1)–(3) | Postcursors, timing, BER and narrow-pulse estimates | Signed discrete decisions, NRZ symbol-pulse extension and per-chip BER/yield distinction |
| DFE pp. 9–10, Figs. 5–7 | CML terminal connections, bias/clock network, overdrive recovery, mismatch | Explicit sensing/regeneration phases; corrected device labeling, local ODE, illustrative reversal model |
| DFE pp. 10–11, Figs. 8–11 | Integrated noise, summer polarities and sizing, degeneration | Consistent noise reference, RSS assumptions, current ratio versus voltage tap |
| DFE pp. 11–12, Figs. 12–14 | Third tap, omitted second tap, eye/data check and power | Residual ISI and feedback-error extension; eye opening does not establish $10^{-12}$ BER |
| DFE pp. 11–12, Eqs. (4)–(5), correction prose | Formal I/O polynomial and bandgap gate corrections | Apply in knowledge notes and link the dated bandgap supplement |

## Formal corrections and design qualifications

1. **T-coil erratum:** Part Two p. 11 replaces I/O Eqs. (9)–(10) with general $N,D$ polynomials containing $C_BC_E(L^2-M^2)$. The authored I/O note uses these corrected expressions and checks them against independent coupled-inductor MNA, including detuned bridge values. Original PDFs and raw conversions remain intact.
2. **Bandgap erratum:** Part Two p. 12 corrects bandgap Fig. 9: gates of $M_c,M_d$ connect to drains of $M_a,M_b$, respectively. The [bandgap note](../Low-Voltage-Bandgap-Reference.md) and [second-batch record](razavi-second-batch-verification.md) now include a dated supplement. Core temperature/current and passive-filter calculations are unaffected.
3. **I/O values and response:** Voltage-driver prose and its 250-pH/25-fF coil values imply 300-fF $C_E$, while Fig. 10 labels 330 fF. Both are recorded. Flat all-pass magnitude at the far node does not imply a monotonic step or a clean eye. Center-current injection has a different transfer.
4. **Delay flatness:** $k=0.5$, $\zeta=\sqrt3/2$ gives low-frequency group-delay flatness for the ideal second-order center response, not constant delay at every frequency.
5. **CTLE model versus source:** Ideal $g_mR_D=4$, bridge boost 3 gives DC gain 1.333 and 9.542-dB asymptotic boost. These do not reproduce practical loaded gains. Exactly placing the degeneration pole at $28/3$ GHz requires 127.9 fF with the stated $g_m,R_S$; the article's practical choice is 150 fF.
6. **CTLE source summaries:** Part One reports a 250-mV / 13-ps eye; Part Two introduces a 220-mV / 13.6-ps eye and approximately 13-dB Nyquist boost. Keep each report's locator rather than inventing identical saved conditions.
7. **DFE taps and probability:** An impulse-derived tap is an initial estimate. Actual NRZ symbol response, sampling phase and nonlinear recovery matter. Offset standard deviation is not variance. Offset yield and noise-conditioned BER are separate quantities.
8. **CML state and labeling:** In Fig. 5, $M_3$ drain is $Y$ and gate is $X$; $M_4$ drain is $X$ and gate is $Y$. Explicit terminal review prevents relying on device order in prose. Finite sensing and prior state matter in addition to regeneration gain.
9. **Source limits:** The final source eye and correct finite data sequence are not a measured/post-layout BER result. The 9.5-mW CTLE/DFE subtotal is not full receiver/transceiver power. No project PDK simulation or silicon validation is claimed.

## Independent analytical verification

Run from the repository root, or use the script's absolute path from another directory:

```powershell
python code/razavi_third_batch_analysis.py
```

The script uses NumPy and Matplotlib, locates figures relative to itself and needs no PDK. It checks coupled-inductor MNA against corrected polynomials, symmetric current injection, channel ABCD against a separately stamped ladder, CTLE gain against half-circuit KCL, DFE recurrence against residual convolution, and NRZ-pulse integration.

| Calculation | Independent result |
|---|---|
| Unpeaked I/O, 470 fF, 50-Ω terminations | Loaded $f_{3dB}=13.5451$ GHz; −10-dB matching 4.51503 GHz |
| Ideal T-coil, $C_E=400$ fF, $k=0.5$, $R=50$ Ω | $L=333.333$ pH, $C_B=33.333$ fF, $f_n=27.5664$ GHz, $\zeta=0.866025$ |
| Ideal voltage-mode step / final value | Minimum approximately −0.398681 |
| Twelve-section channel at 28 GHz | DC-normalized loss 21.5477 dB |
| Ideal CTLE, 10 mS / 400 Ω / 400 Ω / 150 fF | DC gain 1.3333, $B=3$, $f_z=2.65258$ GHz, $f_p=7.95775$ GHz |
| Pole / Nyquist for 95% plateau | 0.386556 at $B=2$; 0.351000 at $B=3$ |
| Exact capacitor for $f_p=28/3$ GHz | 127.892 fF |
| Two identical single-pole output limits | Bandwidth factor 0.643594 |
| Noiseless signed symbol margins | 0.69 / 0.91 / 0.97 for no DFE / tap 1 / taps 1+3 |
| Mismatch standard deviations | Pair 10.328 mV; referred RSS offset 11.547 mV |
| Independent noise RSS / conservative full eye | 3.00167 mV / 134.606 mV |
| Illustrative recovery at 70 / 100 mV | 9.11895 / 7.51658 ps versus 8.92857-ps ideal half cycle |
| First-order impulse / NRZ cursor, sample at half UI | 0.367879 / 0.974410 |
| Forced-error example at $h_1=0.22$ / 0.7 | 1 / 51 total errors, including the forced error |
| Zero-error 95% bound for $10^{-12}$ at 56 Gb/s | Approximately $2.996\times10^{12}$ bits / 53.4952 seconds, assuming independent errors |

All three generated figures were visually inspected. The perfect-match curve is below the I/O plot's visible dB range and is explicitly annotated. The Gaussian plot includes enough low-amplitude range to show both fixed-offset cases. Script execution, local links, math delimiters, metadata, hashes and manifest counts are checked before delivery. These are analytical checks, not transistor/EM simulations, clocked noise extraction or measured BER; implementation test plans remain in each note.
