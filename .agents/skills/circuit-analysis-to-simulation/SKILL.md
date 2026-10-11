---
name: circuit-analysis-to-simulation
description: Extend preliminary circuit analysis, schematics, or technical notes into reproducible learning documents that connect derivations to actual simulation. Use for checking circuit equations, building SPICE testbenches, enabling graphical circuit debugging with a shared schematic and netlist export, comparing independent calculations with simulation, explaining discrepancies, and extending noise analysis. General knowledge questions, literature organization alone, and teaching website creation are outside this workflow.
---

# Circuit analysis and simulation verification

Use **derivation → testbench → simulation curves → numerical comparison** as the per-metric reading path. Explain the mechanism and assumptions before deriving; make a prediction before running; explain discrepancies and explore applicability boundaries afterward. Deliver readable technical documents, actual simulation data, and rerunnable scripts so learners can trace every conclusion to its basis.

## Define the circuit and analysis depth

- Read the user's preliminary analysis, schematic, models, and existing simulations. Treat older notes as material to verify; correct errors using the actual topology and record why. Do not aim merely to match old equations.
- Select metrics within the user's scope. Local noise verification need not become a complete amplifier design. For a full topic, establish a reliable baseline before adding relevant nonidealities.
- Define device connections, body terminals, input/output polarity, single-ended or differential conventions, internal nodes, load, and bias. Diagrams, model bindings, and netlists must describe the same circuit. Preserve separate identities for source editable projects and teaching models.
- Establish whether the analysis uses an analytical/behavioral model, educational device models, or a specified PDK. A requested PDK or a required mechanism absent from a teaching model takes precedence. Explain parameter choices without claiming process performance; preserve separate source-device and teaching-model identities.
- For compatible MOS teaching studies, default to the project's [versioned LEVEL=1 library and reuse guide](../../../simulations/models/edu-mos-level1/README.md). For compatible NPN BJT teaching studies, use the [versioned Gummel–Poon library and reuse guide](../../../simulations/models/edu-bjt-gummel-poon/README.md); it provides `NPN_EDU`, not a validated PNP or a four-terminal substrate model. Pin the chosen version/hash and choose circuit-specific geometry or area, bias and load; preserve existing local model snapshots. Keep flicker and other mechanism overrides local and follow the selected model's conventions.
- Existing research-document conventions are in [classroom-conventions.md](../../../skills/analog-circuit-research/references/classroom-conventions.md). This skill connects derivation to actual simulation; maintain research notes and teaching pages according to their own goals.

## Enable graphical debugging from a shared schematic

When the user needs to edit and simulate a circuit graphically, provide a native editable schematic as the common circuit source for the user and LLM. Prefer the open-source **KiCad schematic → SPICE export → ngspice** path unless the user chooses another tool. A netlist-only workflow remains suitable for script-only studies; do not migrate unrelated circuits automatically.

- Keep component connections, models, geometry and nominal values in the schematic. Derive the circuit netlist from the saved schematic for both GUI and scripted runs; analysis commands may live in a workbook or generated testbench. Label analysis-specific bias overrides so they are distinguishable from nominal component values.
- Treat exported netlists as derived artifacts. Editing a `.cir` file does not update the schematic. Apply intended circuit changes to the common source, then regenerate and rerun. Scripts cannot see unsaved GUI changes; coordinate with the user before editing a schematic that has pending GUI edits.
- Make sources, passives and device dimensions individually editable. For simple circuits, avoid hiding the topology behind a single subcircuit block. Check whether simulation fields override visible Value fields; a user-facing value must control the intended simulation parameter. Document where MOS geometry and model bindings are edited.
- Reuse the selected model library and explicit terminal mappings, including bulk pins and reference ground. Resolve model paths relative to the project, and preserve device units and scaling. Do not replace an educational model with a PDK or change its physical scope merely to add a GUI.
- Configure a useful OP run and, when relevant, bias sweeps. In KiCad use **Inspect > Simulator**, select OP and run; node voltage/current overlays show the last solved point and require rerunning after edits. OP has no parameter-tuner sliders; edit symbol properties and rerun. DC sweeps can support plotted tuning, but swept sources override their nominal values during that analysis.
- Validate schematic export against the established circuit using terminal connections, models, effective parameters and aligned OP conditions. Reference names, node prefixes, card ordering and flat versus hierarchical representation may differ; byte-identical text is not required. Prefer the same ngspice engine for GUI/script parity checks, and distinguish these consistency checks from independent analytical verification.
- Exercise at least one meaningful parameter change through the GUI: edit, save, run and observe the expected OP change. Restore the intended delivery settings and rerun. Report actual verification separately from untested instructions; a generated schematic must be opened and saved in the target editor before claiming GUI compatibility.
- Keep a scripted export/run entry point for LLM use, with logs and parameter reports appropriate to the study. Preserve existing validated decks as separate baselines unless migration is requested. Structural changes require reviewing any topology-specific checks in the bridge.

For the validated KiCad example and concrete UI/model details, read the [cascode graphical lab guide](../../../circuits/source-degenerated-cascode/kicad/README.md). Its [bridge runner](../../../code/run_cascode_kicad.py) exports the saved schematic and runs KiCad's bundled ngspice DLL; it is a Windows, cascode-specific implementation, not a general netlist importer. Adapt the installation discovery, terminal checks and analyses for another circuit or platform. If reliable native schematic generation is unavailable, let the user draw it manually and assist with model bindings, export and verification; do not describe an image as an editable circuit.

## Derive equations from mechanisms

- Explain current, charge, feedback, or timing first, then derive from KCL/KVL, charge conservation, or state equations. Keep the intermediate steps needed to check signs, coefficients, and node coupling. State the unknown ordering and excitation vector for matrix models.
- Define symbols and units, device operating regions, matching, body effect, output resistance, parasitics, capacitance, reference ground, and load assumptions. Time-varying circuits also require initial conditions and phase boundaries.
- Separate exact relationships within the model from engineering approximations and their conditions. Evaluate approximation errors using the exact model; do not present approximations as equalities across all frequencies or sweep ranges.
- Check dimensions, polarity, limiting cases, and order of magnitude. Identical circuit names do not ensure identical equations for different output terminals, bias references, or excitation definitions.

## Design testbenches that distinguish mechanisms

Specify the equation a metric should test before choosing bias, excitation, measured quantities, postprocessing definitions, and acceptance criteria. One testbench may support several compatible metrics.

- Run the operating point first and check current balance, operating regions, and headroom. Mark sweep boundaries where assumptions fail; baseline saturation does not prove saturation throughout a sweep.
- Choose AC, DC, transient, noise, output-current injection, supply perturbation, PZ, or other analyses according to the metric. Not every topic needs all 5T OTA tests.
- Align comparison conditions and input normalization. Use separate excitations for differential, common-mode, and supply transfer functions, and align frequency axes before calculating CMRR/PSRR. Explain unit AC excitation as a linearized normalization.
- For PSRR, state which input, bias, output, and load references move with the supply. Do not short the PZ input with an additional ideal voltage source. Distinguish small-signal settling, closed-loop settling, and large-signal slew in transient analysis.
- Consult current model/simulator documentation for units, scaling, defaults, and noise mechanisms. Explain the specific effect of missing tool capabilities and continue independent work. Never mark unrun tests complete.

## Calculate independently and execute actual simulations

- Keep two paths: predictions implemented from derived equations, and data produced by the simulator from the netlist. Measuring a metric from simulation waveforms is postprocessing, not an independent prediction.
- Simulation OP values such as gm, gmb, gds, device currents, or capacitances may feed analytical calculations. State that independence then applies to construction and solution of the circuit equations/transfer functions, not to device parameters or bias.
- Use matrix solutions, closed-form relationships, local DC derivatives, time/frequency-domain cross-checks, or PZ reconstruction. Select checks that expose wiring, sign, normalization, or approximation errors; avoid tests that only repeat the same implementation.
- Run locally. Reuse validated scripts and tools, resolve inputs relative to the script, and adapt to the current system. Hide background simulation windows on Windows and write logs to files. Work in a temporary directory and publish results after checks pass.
- Check exit status, logs, data completeness, finite values, and axes. Use physically meaningful tolerances; overly large default absolute tolerances must not hide errors in tiny quantities such as noise power.
- Keep models/netlists, stimuli, raw data, logs, check results, execution date, actual tool versions, and input/script hashes. Images alone are insufficient, and existing images do not replace a current run.
- Do not repeatedly broaden completed verification without reason. Rerun relevant checks for new changes, failures, or unresolved concerns.

## Conditional noise analysis

Use these conventions when studying noise; other topics need no additional noise analysis.

- Distinguish one-sided/two-sided PSD, V²/Hz, V/√Hz, and integrated RMS. Refer noise to the same input used for signal gain. Include source independence or correlation in power calculations.
- Establish a verifiable thermal-noise baseline before adding 1/f noise as needed. Export mechanisms separately or retain comparison tests. Add PSDs/variances before taking the square root; RMS amplitudes cannot be added directly.
- Use the chosen model's exact 1/f parameter definition. Educational coefficients may be selected from a desired corner frequency, but record the basis, actual values, and validation results. Do not equate textbook empirical coefficients with SPICE KF or claim universal NMOS/PMOS ordering.
- State finite integration limits and relate the spectrum to integrated bandwidth; ideal 1/f PSD cannot be integrated down to zero. Distinguish included and excluded mechanisms such as bias-source noise, mismatch, and sampling aliases according to the research goal.
- For the 5T OTA example or ngspice MOS1 1/f analysis, read the [validated case and tool details](references/5t-ota-case.md). Do not reuse case-specific numbers for a different topology.

## Produce the learning document

Keep each metric's derivation, testbench, simulation curves and numerical comparison together, with its prediction and applicability limits. When creating or reorganizing a learning note, use the [per-metric learning template](references/metric-learning-template.md). Scale it to the question rather than adding empty sections or requiring every metric in the OTA example. Keep equations beside their verification plots rather than separating all equations from all figures.

- Generate plots from actual data and label the source of analytical curves. State axes, units, excitation, and load. Keep a PNG reading version and an export-friendly format, and inspect the actual layout.
- Comparison tables should include equations/independent calculations, simulation measurements, necessary errors, and conditions. Explain whether parameter changes affect gain, poles, noise floor, corner frequency, or integrated values.
- Investigate topology, polarity, bias, units, operating regions, reference points, and approximations first when results differ. Do not arbitrarily tune parameters, relax criteria, or hide failures to obtain agreement.
- If the user asks to retain preliminary notes, explain corrections and verification status in a companion document. Otherwise, revise the original within authorization. Preserve useful baselines and comparison cases in new extensions.
- State the executed scope, rerun entry point, and limitations that affect conclusions. Automated checks establish consistency of model and implementation, not process accuracy or proven learning effectiveness.

Example request:

> Use $circuit-analysis-to-simulation to extend the preliminary OTA analysis into a learning document connecting equations to simulation. Check topology and signs, preserve key derivations, build a teaching model, run locally, and compare each metric. Establish a reliable baseline before adding relevant nonidealities.
