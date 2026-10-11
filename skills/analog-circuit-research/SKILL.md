---
name: analog-circuit-research
description: Research specific analog and mixed-signal circuit topologies, operating mechanisms, derivations, nonidealities, and design tradeoffs, then create or revise traceable Markdown technical notes. Use for bootstrapped switches, amplifiers, comparators, sampling, and noise-processing circuits. Translation alone, formatting, and interactive website development are outside this workflow.
---

# Analog and mixed-signal circuit research

Organize circuit research into technical notes that support understanding and design. Match depth to the user's question: a local equation analysis need not become a full survey, while a new topology study should cover mechanisms, key performance, and design boundaries.

## Define the research scope

- Read the user's schematics, papers, simulation results, and existing notes first to identify the specific topology and version.
- If only a name is given, choose an explicit basic structure and explain the choice and limitations. Without transistor-level connections, a functional model may be studied, but do not call it a complete, directly implementable circuit.
- Define inputs, outputs, nodes, devices, polarities, loads, and metrics. For time-varying circuits, also define phases, initial conditions, clock order, and signal paths.
- Distinguish research explanations, analytical design examples, and designs for a specified process. Without a PDK, specifications, or an actual schematic, do not claim completed device sizing or reliability verification.
- When working in Circuits & Systems Classroom, read the [project conventions](references/classroom-conventions.md) as needed. Follow local conventions in other projects.

## Establish evidence and models

- Prefer original papers, textbooks, and process documentation. Cite important external conclusions nearby. When full text is available, record sections, pages, figures, or equation numbers. State access limits if only abstracts or bibliographic records are available.
- Define separate versions for schematics from different publications. Do not combine equations while omitting structural differences. Existing notes are material to check, not proof of correctness.
- When a source is unavailable, continue independent derivations and record unverified items. Do not invent references, figure numbers, performance figures, or simulation results.
- Establish a symbol and assumption table covering operating regions, body effect, output resistance, parasitics, load, single-ended/differential conventions, time/frequency domains, and model validity.
- When organizing a series or processing PDFs, read [source ingestion and full-text verification](references/source-ingestion.md) as needed. Markdown conversion is only a research aid. Extend topic studies using other primary sources and independent derivations where useful.

## Derive results from mechanisms

- Explain current paths, charge transfer, energy, or feedback before deriving conclusions from KCL, KVL, charge conservation, or state equations. Preserve enough intermediate steps for verification.
- Distinguish model equalities, engineering approximations, and empirical rules. State approximation conditions; do not turn a paper's measurements or process-specific experience into universal design rules.
- For time-varying circuits, distinguish instantaneous small-signal parameters, full-cycle gain, integration response, and final sampled values. Avoid applying static-amplifier equations directly.
- For noise, state one-sided/two-sided PSD conventions, input/output reference points, integration bandwidth, correlations, and sampling conditions. Distinguish V²/Hz, V/√Hz, and integrated V²; state whether aliasing or correlated sampling is included.
- For stability, define feedback paths, loop gain, and signs, and distinguish rad/s from Hz. For settling, distinguish small-signal exponential response, slew, and dynamic bias.

## Select relevant nonidealities

Choose content for the structure and research goal; every note need not contain every metric:

| Circuit type | Priority analysis |
|---|---|
| Amplifiers and feedback circuits | Gain, common mode, noise, stability, settling, slew, power |
| Sampling and switching circuits | Phases and charge conservation, on-resistance, distortion, thermal noise, injection, feedthrough, parasitics, terminal stress |
| Comparators and regenerative circuits | Regeneration time, offset, decision noise, kickback, input common mode, metastability |
| Dynamic or charge-domain circuits | Initial state, cycle response, energy/charge budgets, clocks, correlated noise, leakage |

Explain how parameter changes affect performance and tradeoffs. Fixed VGS does not imply a fixed threshold or on-resistance. A raised gate-to-ground voltage alone does not establish safety or failure; analyze relevant device terminal voltages and process limits.

## Verify and deliver

- Check key equations for dimensions, signs, limiting cases, and order of magnitude. Explain design constraints with numerical examples whose units and conditions are explicit.
- Use computational scripts for complex derivations, parameter sweeps, or reproducible plots as needed. Place scripts in the project's code directory and keep their models and parameters aligned with the notes.
- Label analytical checks, model calculations, SPICE simulation, and measurements separately. An analytical script is not transistor-level verification. If simulation is not run, provide a concrete testbench, stimuli, sweep variables, and criteria.
- Create or update Markdown notes, figures, and indexes only when relevant to the current task. Do not automatically create pages, deploy, commit, or publish.
- Select sections for the task: research scope, topology/timing, symbols and assumptions, mechanisms and derivations, nonidealities, design examples, verification status, references, and open questions. Structure should serve content; do not fill a template with unsupported paragraphs.
- Before delivery, check symbol/unit consistency, derivations or sources for important conclusions, valid relative links, reproducible plots, and truthful source-access status. Identify unverified items that affect design use.

## Usage

Example requests:

> Use $analog-circuit-research to study a bootstrapped switch. Define the functional topology and timing, derive VGS and on-resistance, analyze body effect, parasitics, and sampling errors, and produce a knowledge note. Label conclusions without a PDK as analytical-model results.

> Use $analog-circuit-research to check the existing FIA note against this paper. Revise only gain and noise analysis and preserve the other sections.