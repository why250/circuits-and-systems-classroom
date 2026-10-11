# Per-metric learning template

Use this when writing a circuit learning note or reorganizing an analysis so readers can follow **derivation → testbench → simulation curves → numerical comparison**. This is a reading structure, not a fixed catalog of amplifier tests. Select metrics and experiments that answer the user's question.

Apply this structure to the simulation companion within the project's [analysis/simulation document separation rule](../../../../AGENTS.md). The general analytical reference remains separate.

## What each stage should establish

| Stage | Learner's question | Evidence to place beside it |
|---|---|---|
| Derivation | Why should the circuit behave this way? What can I predict? | Mechanism, declared assumptions, key intermediate equations, sign/units, and a numerical or qualitative prediction |
| Testbench | What experiment would distinguish this prediction from a competing explanation? | Linked netlist, bias/load, stimulus and normalization, measured nodes, sweep range, and measurement definition |
| Simulation curves | Does the behavior follow the prediction, and where does it change? | Actual simulator data overlaid with identified analytical predictions; axes, units, operating conditions and marked assumption boundaries |
| Numerical comparison | How close is the result, and what does the difference mean? | Equation/prediction, measured result, meaningful discrepancy, explanation and applicable range |

Before executing a test, predict the sign, trend, limiting behavior or expected value. A prediction computed from simulator OP parameters is useful, but identify those parameters as simulator-derived. Independent verification then concerns the circuit equations and their solution, not an independently predicted device model or operating point.

## Adaptable Markdown block

Replace the instructional text below with the metric's actual content. Short answers may combine paragraphs; do not publish empty headings or template instructions.

~~~~markdown
### Metric name: derivation to simulation

Explain the physical mechanism and define the metric, polarity/reference,
units, load and operating conditions. State the model and approximation.

Show the intermediate equation(s) needed to verify the result, then its
final expression. Give the expected sign, trend or value before the test.
Identify any prediction parameters taken from simulation OP.

**Testbench.** Link the executed deck. Describe bias, excitation, measured
quantity, sweep/time window and extraction rule. State what is held fixed.

Place the simulation figure here, next to the equations it tests.
Overlay the analytical prediction where informative; label its source.
Mark regions where the derivation's assumptions no longer hold.

| Quantity and condition | Equation / independent prediction | Simulation | Discrepancy |
|---|---|---|---|
| The selected observable | Evaluated prediction with units | Measured result with units | Meaningful error or approximation difference |

Explain the agreement or discrepancy, the usable range and what the test
does not establish. Link the raw data and execution/check report.

Optionally change one relevant condition and predict the change first.
Explain the resulting curve in terms of the same mechanism.
~~~~

## Comparisons that teach rather than merely match

- Distinguish an equality within a declared model from an engineering approximation. For an equality, use a tolerance justified by solver accuracy and acquisition. For an approximation, report its observed error and where it stops being useful; do not tune parameters merely to force agreement.
- For nonzero quantities, relative error may be useful: `(measured - predicted) / predicted`. Use an absolute error with units near zero. For dB quantities, report a difference in dB, rather than a percentage of the dB value. A magnitude-only comparison does not verify polarity or phase; compare signed or complex transfers when those matter.
- Measurement rules belong to the testbench explanation: a local DC derivative needs its step size; a crossing needs its direction and interpolation; settling needs its final-value definition, error normalization, edge reference and last-exit window; integrated noise needs finite frequency limits and PSD units.
- A single operating-point number cannot show a mechanism or its validity range. Use a frequency, bias, amplitude, load or time sweep when it exposes the relevant behavior. Scalar OP parameters may be shown in a table or bar chart and connected to a sweep; not every parameter needs its own testbench.
- If the curves disagree, investigate topology, polarity, references, normalization, bias, units and omitted terms. Show the disagreement and its explanation. If a test is unrun, label it as a proposed experiment and retain any completed independent calculation without claiming simulation verification.
- End with one concrete interpretation: why the result matters for the circuit, where the formula applies, or what changes when one assumption is relaxed. Do not infer fabrication accuracy or learning effectiveness from numerical consistency alone.

## Figure coverage before delivery

- Review each metric section for a nearby figure that demonstrates the equation being checked. A numerical results table or a plot located only in an earlier, unrelated section does not replace that metric's visual evidence. A composite figure may cover several related metrics; explain which panel verifies each result.
- For frequency response, show actual simulated magnitude and phase with the independently derived transfer overlaid under the same bias, load, input normalization and frequency grid. Magnitude alone does not distinguish an LHP zero from an RHP zero.
- For poles and zeros, include a complex-plane root map and mark the positive frequency scales `abs(s_k)/(2*pi)` on the response plots. Distinguish signed complex root locations from frequencies on the `j*omega` sweep. Label whether roots come from an analytical polynomial or a simulator PZ analysis; an AC overlay does not turn polynomial roots into simulator-extracted roots.
- For bandwidth, mark the declared gain crossing and use a magnified view when it is close to a pole's frequency scale. State the reference level and interpolation rule. A dominant-pole magnitude is an estimate, not automatically the measured -3 dB bandwidth.
- Scalar OP quantities may use a table or bar chart when a sweep would add no relevant information. If a metric has no plotted experiment because it is outside scope, unrun or unsupported by the selected model, state that reason and its verification status locally rather than implying full coverage.
- Retain the executed data and rerunnable plotting entry point, produce a PNG reading version and an export-friendly format, and inspect the generated layout. Label analytical versus simulated traces and place raw-data/testbench links beside the corresponding comparison.

The [BJT differential-pair companion, Section 8](../../../../BJT-Degenerated-Differential-Pair-Schematic-and-Simulation.md#8-poles-zeros-and-transfer-function) demonstrates a root map, magnitude/phase overlays and a bandwidth detail. Use its reading structure rather than copying its model-specific roots or numerical tolerances.

## Reuse a case without freezing its parameters

The [5T OTA case](5t-ota-case.md) links the executed companion note, testbenches, plots and scripts. It demonstrates this reading path and known simulator details. Use those links for case-specific equations and results; do not copy historical metric counts or numerical tables into this template. Derive and test the topology of each new circuit on its own terms.
