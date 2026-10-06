# Razavi's Analog Mind: Sources and Knowledge Map

This collection uses Behzad Razavi's **The Analog Mind** column as a starting point for reusable circuit knowledge. Research notes explain mechanisms, derive equations, state assumptions, and extend the analysis where useful. They are not transcriptions or line-by-line translations.

**Acquisition snapshot: 2026-10-04; research updated: 2026-10-05.** The [UCLA journal page](https://www.seas.ucla.edu/brweb/journal.html) yields **22 PDF-confirmed articles, 156 PDF pages**, spanning Summer 2020 through Summer 2026. All original PDFs are acquired locally. **All 22 articles and 156 pages** have full-text and original-page review, organized into functional knowledge notes with independent analytical checks; **zero source-research entries remain pending**. All 22 Marker conversions were separately reviewed with recorded defects. These counts apply to this snapshot, not future additions or other Razavi columns; physical implementation validation remains separate.

## Completed Topics

| Topic | Knowledge note | Independent extensions |
|---|---|---|
| Bootstrapped sampling | [Bootstrapped Sampling Switch](Bootstrapped-Sampling-Switch.md) | Functional charge model, parasitics/body effect, ADC noise and bandwidth budget, clock/driver demands, coherent sampling and folded harmonics |
| Dynamic comparison | [StrongARM Comparator Design](StrongARM-Comparator-Design.md) | Explicit transistor connections, phase-local regeneration, mismatch/yield, offset-aware noise extraction, reset/kickback and verification plan |
| Discrete-time analysis | [z-Transform for Analog Designers](Z-Transform-for-Analog-Designers.md) | ROC/causality, CDS covariance, leaky integrators, actual-loop STF/NTF, noise integration and BIBO qualifications |
| Voltage references | [Low-Voltage Bandgap Reference](Low-Voltage-Bandgap-Reference.md) | CTAT/PTAT KCL, resistor temperature coefficients, separate slope/output trimming, loaded noise filter, startup and absolute accuracy |
| Power regulation | [LDO Regulator Design](LDO-Regulator-Design.md) | Explicit supply/reference/load transfer, PSD/SSB conventions, oscillator pushing/spurs, dropout, charge balance and power accounting |
| Optical receiver front end | [Transimpedance Amplifier Design](Transimpedance-Amplifier-Design.md) | Loaded/unloaded gain, finite-bandwidth feedback, BER/ENBW, NRZ spectra, noise integration and long-run droop |
| Continuous-time filtering | [Tow–Thomas Biquadratic Filter](Tow-Thomas-Biquadratic-Filter.md) | State equations, Q-dependent cascade bandwidth, exact finite-gain KCL, noise coefficients, common mode and capacitor programming |
| Broadband interfaces | [Broadband I/O and T-Coil Design](Broadband-IO-and-T-Coil-Design.md) | Corrected general polynomials, coupled-inductor MNA, matched all-pass/low-pass nodes, pad loading and negative step excursion |
| Linear equalization | [Continuous-Time Linear Equalizer](Continuous-Time-Linear-Equalizer.md) | Channel ladder/ABCD, bridge KCL, exact plateau/pole placement, output peaking, bridge noise and finite-frequency programming |
| Decision-feedback equalization | [Decision-Feedback Equalizer and CML Latch](Decision-Feedback-Equalizer-and-CML-Latch.md) | NRZ symbol taps, explicit latch connections, timing/recovery, BER versus offset yield, signed cancellation and error propagation |
| Millimeter-wave oscillation | [Millimeter-Wave VCO Design](Millimeter-Wave-VCO-Design.md) | Half-tank conventions, startup/swing, tuning loss, switch-node KCL, control noise/spurs and nonlinear charge/AM-to-PM |
| Programmable division | [Millimeter-Wave Frequency Divider](Millimeter-Wave-Frequency-Divider.md) | Boolean states, weighted modulus words, explicit clocked-inverter paths, charge sharing, retention and clock power |
| Frequency synthesis | [Millimeter-Wave Frequency Synthesizer](Millimeter-Wave-Frequency-Synthesizer.md) | Exact filter KCL, loop dynamics, PSD conventions, duty-aware noise scaling, source extrapolation limits and spur budgets |
| Sampling phase | [Phase Interpolator Design](Phase-Interpolator-Design.md) | Waveform/phasor distinction, finite feedback KCL, conductance predistortion, fine-code ordering, quadrants and timing noise |
| Clock and data recovery | [Clock and Data Recovery](Clock-and-Data-Recovery.md) | Aligned Alexander samples, current/voltage XOR polarity, separate loop models, transition-dependent gain, relative jitter and holdover |
| Inverter applications: analog | [Analog Front Ends](CMOS-Inverter-Analog-Front-Ends.md) | Exact feedback/CTLE KCL, active inductance, port conventions, replica linearity, compensation and translated impedances |
| Inverter applications: timing | [Clock and Timing Circuits](CMOS-Inverter-Clock-and-Timing-Circuits.md) | Buffer power boundaries, ring scaling, crystal startup, divider bounds, duty-loop sign and signed converter range |
| Inverter applications: decisions | [Memory and Comparators](CMOS-Inverter-Memory-and-Comparators.md) | Stored charge/state, read disturb, PUF ambiguity/repeatability and autozero false-seed timing |
| Inverter applications: drivers | [Drivers and Power Circuits](CMOS-Inverter-Drivers-and-Power-Circuits.md) | Loaded PAM4, SST energy, waveform FFE, hybrid delay errors and differential Class-D power |
| Inverter applications: charge | [Charge-Domain Circuits](CMOS-Inverter-Charge-Domain-Circuits.md), [FIA](Floating-Inverter-Amplifier.md) | Packet startup, retained integrator charge, finite gain, floating-rail endpoint gain and sampled noise |
| AI-assisted design review | [AI-Assisted Analog Design Review](AI-Assisted-Analog-Design-Review.md) | Terminal/bias constraints, impedance limits, loop sign, ring states, incremental supply resistance, timed gain and historical-score boundaries |

[Comparator Noise Calculation](Comparator-Noise-Calculation.md) was also revised to include offset and trial uncertainty and to clarify energy-based comparison metrics. The [first-batch verification record](sources/razavi-first-batch-verification.md) identifies checked source pages, figures, equations, corrections and reproducible numerical checks. No project PDK simulation or silicon measurement is claimed.

The [second-batch verification record](sources/razavi-second-batch-verification.md) covers another 26 PDF pages and distinguishes original formula discrepancies from conversion errors. The [third-batch verification record](sources/razavi-third-batch-verification.md) covers 19 further pages of I/O and equalizer design, including formal corrections to the earlier T-coil polynomials and bandgap OTA wiring. The first fifteen reviewed PDFs were converted using Marker 1.10.2 and checked for page boundaries, important formulas and representative figure extraction. Known OCR/diagram defects are recorded separately; the converted Markdown remains an auxiliary artifact. Independent extensions go beyond the source articles, while unmet source specifications remain visible.

The [fourth-batch verification record](sources/razavi-fourth-batch-verification.md) covers 21 further original pages of VCO, divider and synthesizer research. All three conversions were reviewed for critical formulas, page boundaries and representative circuit images. It distinguishes reference configurations, source equation discrepancies, pump reset-duty scaling and analytical models from physical implementation results.

The [fifth-batch verification record](sources/razavi-fifth-batch-verification.md) covers 11 further original pages of phase interpolation and CDR. It records half-rate/full-rate architecture boundaries, period/phase conventions, current-versus-voltage gate polarity and the different filter models. Both conversions were reviewed against original pages; OCR defects and incorrect internal anchors are recorded separately. Conversion status remains separate in the manifest.

The [sixth-batch verification record](sources/razavi-sixth-batch-verification.md) covers all 48 original pages of CMOS inverter applications Parts 1–5. The [functional map](CMOS-Inverter-Applications.md) connects five new topic notes and the revised FIA note. Source arithmetic, topology/port conventions, retained charge and time-varying gain are checked independently. All five conversions are reviewed with recorded defects, separately from the original-page research.

The [seventh-batch verification record](sources/razavi-seventh-batch-verification.md) covers the final 11 original pages and all 50 numbered questions in the two AI experiment articles. It separates historical grades from current-model evaluation, original headroom/model qualifications from conversion defects, and independent circuit checks from implementation results. Both conversions were reviewed. This completes all 22 articles in the acquisition snapshot.

## Complete Source Inventory

Issue dates and DOI below come from the PDFs. PDF page count differs from printed magazine pages, especially for continuation pages. `?` marks a printed page not yet confirmed. A **reviewed** entry means full reading and original-page inspection plus an authored note and analytical checks. Marker conversion is a separate status in the [machine-readable manifest](sources/razavi-analog-mind.json).

| Issue | Article / original PDF | DOI | PDF pages | Printed pages | Research status |
|---|---|---|---:|---|---|
| Summer 2020 | [The z-Transform for Analog Designers](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2020.pdf) | [10.1109/MSSC.2020.3002137](https://doi.org/10.1109/MSSC.2020.3002137) | 7 | 8–14 | [Reviewed](Z-Transform-for-Analog-Designers.md) |
| Fall 2020 | [The Design of a Comparator](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2020.pdf) | [10.1109/MSSC.2020.3021865](https://doi.org/10.1109/MSSC.2020.3021865) | 7 | 8–14 | [Reviewed](StrongARM-Comparator-Design.md) |
| Winter 2021 | [The Design of a Bootstrapped Sampling Circuit](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2021.pdf) | [10.1109/MSSC.2020.3036143](https://doi.org/10.1109/MSSC.2020.3036143) | 6 | 7–12 | [Reviewed](Bootstrapped-Sampling-Switch.md) |
| Spring 2021 | [The Design of Broadband I/O Circuits](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_2_2021.pdf) | [10.1109/MSSC.2021.3072299](https://doi.org/10.1109/MSSC.2021.3072299) | 7 | 6–11, 15 | [Reviewed](Broadband-IO-and-T-Coil-Design.md) |
| Summer 2021 | [The Design of a Low-Voltage Bandgap Reference](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2021.pdf) | [10.1109/MSSC.2021.3088963](https://doi.org/10.1109/MSSC.2021.3088963) | 8 | 6–12, 16 | [Reviewed](Low-Voltage-Bandgap-Reference.md) |
| Fall 2021 | [The Design of an Equalizer-Part One](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2021.pdf) | [10.1109/MSSC.2021.3111426](https://doi.org/10.1109/MSSC.2021.3111426) | 6 | 7–11, 160 | [Reviewed](Continuous-Time-Linear-Equalizer.md) |
| Winter 2022 | [The Design of an Equalizer-Part Two](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2022.pdf) | [10.1109/MSSC.2021.3126997](https://doi.org/10.1109/MSSC.2021.3126997) | 6 | 7–12 | [Reviewed](Decision-Feedback-Equalizer-and-CML-Latch.md) |
| Spring 2022 | [The Design of An LDO Regulator](https://www.seas.ucla.edu/brweb/papers/Journals/BR_Magzine5.pdf) | [10.1109/MSSC.2022.3167308](https://doi.org/10.1109/MSSC.2022.3167308) | 5 | 7–10, 17 | [Reviewed](LDO-Regulator-Design.md) |
| Summer 2022 | [The Design of a Millimeter-Wave VCO](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_2_2022.pdf) | [10.1109/MSSC.2022.3184443](https://doi.org/10.1109/MSSC.2022.3184443) | 7 | 6–12 | [Reviewed](Millimeter-Wave-VCO-Design.md) |
| Fall 2022 | [The Design of a Millimeter-Wave Frequency Divider](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_Fall_2022.pdf) | [10.1109/MSSC.2022.3205805](https://doi.org/10.1109/MSSC.2022.3205805) | 6 | 6–10, 16 | [Reviewed](Millimeter-Wave-Frequency-Divider.md) |
| Winter 2023 | [The Design of a Transimpedance Amplifier](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2023.pdf) | [10.1109/MSSC.2022.3219682](https://doi.org/10.1109/MSSC.2022.3219682) | 5 | 7–10, ? | [Reviewed](Transimpedance-Amplifier-Design.md) |
| Spring 2023 | [The Design of a Millimeter-Wave Frequency Synthesizer](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_2_2023.pdf) | [10.1109/MSSC.2023.3269456](https://doi.org/10.1109/MSSC.2023.3269456) | 8 | 6–13 | [Reviewed](Millimeter-Wave-Frequency-Synthesizer.md) |
| Fall 2023 | [The Design of a Phase Interpolator](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2023.pdf) | [10.1109/MSSC.2023.3315653](https://doi.org/10.1109/MSSC.2023.3315653) | 5 | 6–10 | [Reviewed](Phase-Interpolator-Design.md) |
| Winter 2024 | [The Design of a Biquadratic Filter](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2024.pdf) | [10.1109/MSSC.2023.3336149](https://doi.org/10.1109/MSSC.2023.3336149) | 8 | 6–13 | [Reviewed](Tow-Thomas-Biquadratic-Filter.md) |
| Summer 2024 | [Fifty Applications of the CMOS Inverter-Part 1](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2024.pdf) | [10.1109/MSSC.2024.3419528](https://doi.org/10.1109/MSSC.2024.3419528) | 8 | 7–14 | [Reviewed](CMOS-Inverter-Applications.md) |
| Fall 2024 | [Fifty Applications of the CMOS Inverter-Part 2](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2024.pdf) | [10.1109/MSSC.2024.3473737](https://doi.org/10.1109/MSSC.2024.3473737) | 9 | 12–20 | [Reviewed](CMOS-Inverter-Applications.md) |
| Winter 2025 | [Fifty Applications of the CMOS Inverter-Part 3](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2025.pdf) | [10.1109/MSSC.2024.3498732](https://doi.org/10.1109/MSSC.2024.3498732) | 10 | 12–20, 159 | [Reviewed](CMOS-Inverter-Applications.md) |
| Spring 2025 | [Fifty Applications of the CMOS Inverter-Part 4](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_2_2025.pdf) | [10.1109/MSSC.2025.3561955](https://doi.org/10.1109/MSSC.2025.3561955) | 11 | 8–18 | [Reviewed](CMOS-Inverter-Applications.md) |
| Summer 2025 | [Fifty Applications of the CMOS Inverter-Part 5](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2025.pdf) | [10.1109/MSSC.2025.3581644](https://doi.org/10.1109/MSSC.2025.3581644) | 10 | 9–17, 28 | [Reviewed](CMOS-Inverter-Applications.md) |
| Fall 2025 | [Analog Design Experiments With AI-Part 1](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2025.pdf) | [10.1109/MSSC.2025.3611213](https://doi.org/10.1109/MSSC.2025.3611213) | 5 | 11–15 | [Reviewed](AI-Assisted-Analog-Design-Review.md) |
| Spring 2026 | [Analog Design Experiments With AI-Part 2](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_2_2026.pdf) | [10.1109/MSSC.2026.3686589](https://doi.org/10.1109/MSSC.2026.3686589) | 6 | 8–13 | [Reviewed](AI-Assisted-Analog-Design-Review.md) |
| Summer 2026 | [The Design of a Clock and Data Recovery Circuit](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_3_2026.pdf) | [10.1109/MSSC.2026.3706674](https://doi.org/10.1109/MSSC.2026.3706674) | 6 | 11–15, 116 | [Reviewed](Clock-and-Data-Recovery.md) |

## Metadata and Source Qualifications

- The website calls the bootstrapped sampler Summer 2021; its PDF is **Winter 2021**. DOI year and issue year can also differ legitimately.
- The millimeter-wave VCO and divider entries lack the website's Analog Mind label; their PDF first pages confirm the column, so both are included.
- The frequency-synthesizer website citation gives pp. 7–17, while the downloaded PDF's printed pages are 6–13. Preserve both in the manifest and use the reviewed PDF for source locators; no publisher correction was checked.
- Wide page spans can represent real continuation pages: CDR is pp. 11–15, 116, and LDO is pp. 7–10, 17. Shared final pages may contain unrelated material. A large span is not the article length.
- The TIA's final PDF page was visually reviewed, but has no confirmed printed page number. Cite PDF p. 5 and retain `null` in the manifest, rather than inferring p. 11 from the website.
- Shared-page boundaries and conversion defects for every article are recorded in its batch evidence. No pending source-research entry remains in this snapshot; that status does not imply physical design validation.

## Research Sequence

1. **Foundations completed:** sampling switch, comparator, and z-transform. These link device behavior to acquisition, noise and discrete-time systems.
2. **Analog building blocks completed:** low-voltage bandgap, LDO, transimpedance amplifier, and biquadratic filter. Notes cover startup/operating point, feedback/stability, noise and realistic loading, with implementation tests still pending.
3. **High-speed links completed at the analytical level:** broadband I/O, equalizer Parts One/Two, millimeter-wave VCO/divider/synthesizer, phase interpolator and CDR now have reviewed notes. Implementation/PDK validation remains pending. Separate channel models, circuit implementation and loop-level behavior.
4. **CMOS inverter applications completed at the analytical level:** Parts 1–5 now have a functional map, five companion notes and a corrected FIA note. Physical implementation remains pending; the older ring-amplifier note was not revalidated by this batch.
5. **AI-assisted design methodology completed at the analytical level:** Parts 1–2 now have one review-method note covering both articles, all 50 historical questions and selected independent circuit checks. Source grades and assumptions are recorded without claiming a new current-model benchmark.

This sequence records the completed source and analytical research. Additional original papers, textbooks, process documentation and independent derivations can support each topic; PDF publication boundaries do not limit the knowledge base. Circuit implementation and physical validation require their own specifications and evidence.

## Local Materials and Reproduction

| Material | Location | Role |
|---|---|---|
| Original PDF + extracted text | `reference/razavi/<source>.pdf`, `.txt` | Preserved source and searchable text; gitignored |
| Marker conversion | `reference/razavi/marker/<source>/` | Auxiliary Markdown, images, metadata and `conversion.json`; gitignored |
| Original-page previews | `reference/razavi/<topic>-page-<n>.png` | Equation and connection checks; gitignored |
| Source inventory | [sources/razavi-analog-mind.json](sources/razavi-analog-mind.json) | Stable URLs, checksums, issue data and independent progress fields |
| Reviewed-source evidence | [sources/razavi-first-batch-verification.md](sources/razavi-first-batch-verification.md) | Coverage, locators, discrepancies and analytical verification |
| Building-block evidence | [sources/razavi-second-batch-verification.md](sources/razavi-second-batch-verification.md) | 26-page review, conversion defects, formula qualifications and independent circuit models |
| Broadband-link evidence | [sources/razavi-third-batch-verification.md](sources/razavi-third-batch-verification.md) | 19-page review, formal errata, coupled-coil/channel checks and decision/timing models |
| Millimeter-wave evidence | [sources/razavi-fourth-batch-verification.md](sources/razavi-fourth-batch-verification.md) | 21-page review, cross-source boundaries, tuning/divider/filter checks and duty-aware noise scaling |
| Sampling-clock evidence | [sources/razavi-fifth-batch-verification.md](sources/razavi-fifth-batch-verification.md) | 11-page review, phase/code conventions, detector/filter connections and loop/holdover checks |
| Inverter applications evidence | [sources/razavi-sixth-batch-verification.md](sources/razavi-sixth-batch-verification.md) | 48-page review, functional coverage, source/conversion distinctions and dynamic/charge/noise models |
| AI design review evidence | [sources/razavi-seventh-batch-verification.md](sources/razavi-seventh-batch-verification.md) | 11-page review, all 50 historical questions, model/score boundaries, conversion defects and independent circuit checks |

Acquire/update local PDFs with `python code/razavi_analog_mind_sources.py` in a Python environment containing `pypdf`. Existing files are reused; review status is preserved only when the PDF checksum matches. Updating the source inventory may require revising this snapshot/index.

The Marker helper, adapted from why-wiki's preprocessing API pattern, uses an installed `marker-pdf` environment and loads models once for a batch. It saves directly into per-source directories, leaves PDF bytes unchanged, uses page separators, and does not enable an LLM service. Initial model downloads need cache/network access; a small inference batch reduces GPU memory demand.

```powershell
python code/convert_research_pdf.py reference/razavi/BR_SSCM_1_2021.pdf reference/razavi/BR_SSCM_4_2020.pdf reference/razavi/BR_SSCM_3_2020.pdf --output-root reference/razavi/marker --batch-size 1
python code/razavi_first_batch_analysis.py
python code/convert_research_pdf.py reference/razavi/BR_SSCM_3_2021.pdf reference/razavi/BR_Magzine5.pdf reference/razavi/BR_SSCM_1_2023.pdf reference/razavi/BR_SSCM_1_2024.pdf --output-root reference/razavi/marker --batch-size 1
python code/razavi_second_batch_analysis.py
python code/convert_research_pdf.py reference/razavi/BR_SSCM_2_2021.pdf reference/razavi/BR_SSCM_4_2021.pdf reference/razavi/BR_SSCM_1_2022.pdf --output-root reference/razavi/marker --batch-size 1
python code/razavi_third_batch_analysis.py
python code/convert_research_pdf.py reference/razavi/BR_SSCM_2_2022.pdf reference/razavi/BR_SSCM_Fall_2022.pdf reference/razavi/BR_SSCM_2_2023.pdf --output-root reference/razavi/marker --batch-size 1
python code/razavi_fourth_batch_analysis.py
python code/convert_research_pdf.py reference/razavi/BR_SSCM_4_2023.pdf --output-root reference/razavi/marker --batch-size 1
$env:OMP_NUM_THREADS='4'
python code/convert_research_pdf.py reference/razavi/BR_SSCM_3_2026.pdf --output-root reference/razavi/marker --batch-size 4
python code/razavi_fifth_batch_analysis.py
python code/convert_research_pdf.py reference/razavi/BR_SSCM_3_2024.pdf reference/razavi/BR_SSCM_4_2024.pdf reference/razavi/BR_SSCM_1_2025.pdf reference/razavi/BR_SSCM_2_2025.pdf reference/razavi/BR_SSCM_3_2025.pdf --output-root reference/razavi/marker --batch-size 4
python code/razavi_sixth_batch_analysis.py
python code/convert_research_pdf.py reference/razavi/BR_SSCM_4_2025.pdf reference/razavi/BR_SSCM_2_2026.pdf --output-root reference/razavi/marker --batch-size 4
python code/razavi_seventh_batch_analysis.py
```

Marker `--page-range 0-5` means zero-based inclusive PDF pages, while source references normally use printed pages or one-based PDF pages. Preserve all three distinctions. Converted equations and figure images must still be checked against the originals. Only original-page review and independent reasoning establish a reliable knowledge note.
