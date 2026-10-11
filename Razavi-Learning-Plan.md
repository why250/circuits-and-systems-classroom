# Razavi article learning roadmap

Interactive entry: run the classroom locally and open <http://127.0.0.1:4321/learn/razavi/>.
Original catalog: <https://www.seas.ucla.edu/brweb/journal.html>.
Catalog checked on 2026-10-05: 148 PDF links, including 22 confirmed Analog Mind articles.

Read in knowledge-dependency order: **basic circuits → classic columns → Analog Mind design articles → specialized research papers**.
Beginners should first use a textbook to cover MOS operating points, gm/ro, current mirrors, differential pairs, small-signal analysis, and basic frequency-domain analysis. Allow about 18 additional hours.
Do not sort articles solely by publication date. Read each in three passes: identify the problem and connections → derive key relationships → check assumptions and verification boundaries.

## Recommended starting track: ADC / mixed signal

With an analog-circuit foundation, budget about 6 hours per week, totaling approximately **102 hours / 17 weeks**.
This self-study estimate includes reading, derivation, and simplified-model verification. Full PDK design and fabrication require a separate schedule.

| Stage | Estimate | Reading and learning outputs |
|---|---:|---|
| Feedback, bandwidth, and noise budgets | 10 h | Textbook review + classroom feedback experiment; derive A/(1+Aβ) and distinguish bandwidth, stability, and integrated noise |
| Positive feedback and regeneration | 8 h | The Cross-Coupled Pair Part I → The StrongARM Latch; draw connections and explain regeneration |
| Sampling accuracy | 10 h | The Bootstrapped Switch → The Design of a Bootstrapped Sampling Circuit; establish separate RC, kT/C, distortion, and clock budgets |
| Comparator design | 10 h | The Design of a Comparator; distinguish offset, decision noise, metastability, and kickback |
| Discrete-time systems | 12 h | The Switched-Capacitor Integrator → The z-Transform for Analog Designers → The Delta-Sigma Modulator; derive transfer functions from charge conservation and recurrences |
| Converter architectures | 12 h | The Flash ADC → A Tale of Two ADCs → Design Considerations for Interleaved ADCs; compare architecture costs and run an interleaving experiment |
| Close reading of research papers | 16 h | A Predictive SAR ADC Architecture, alongside Performance Bounds of ADC-Based Receivers Due to Clock Jitter; reproduce one key conclusion |
| References, supplies, and filters | 14 h | Bandgap → Low-Voltage Bandgap → LDO → Biquadratic Filter; organize temperature drift, accuracy, stability, and loading limits |
| Design review | 10 h | Analog Design Experiments With AI Part 1–2; deliver specifications, architecture, budgets, independent verification, and open verification items |

Spend about 40% of each week reading, 40% deriving/experimenting, and 20% reviewing. Stages may span weeks; the interactive page allocates work according to the actual time budget.

## Two other tracks

- **PLL / RF clocks:** shared foundations → ring/crystal/mm-wave VCOs → phase noise and jitter → division and loop stability → integer/fractional-N synthesis → close reading of a low-jitter PLL paper → references and supplies → design review. About 110 hours, or 19 weeks at 6 hours per week.
- **High-speed links / CDR:** shared foundations → TIA and broadband I/O → CTLE/DFE → DLL and phase interpolation → CDR → references and supplies → design review. About 96 hours, or 16 weeks at 6 hours per week.

Use long series as a reference toolbox: revisit Fifty Applications of the CMOS Inverter Part 1–5 by function.
Read the AI design experiments after learning to verify results independently.

## Criteria for completing a stage

- Redraw the key connections and explain each phase/signal path.
- Derive one key relationship with explicit symbols, units, and assumptions.
- Check limiting cases through analytical calculations or simulation and answer the stage's self-check question.

The project has seven notes with original-source verification and independent derivations, linked from the interactive page. Recommended tasks for other articles do not mean their full-text research is complete.
Page records stay in the current browser. Export Markdown with checklists, notes, and weekly schedules.