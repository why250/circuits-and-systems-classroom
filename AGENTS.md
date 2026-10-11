# Project guidance

## Language

- Maintain this project's documentation, teaching content, UI text, exports, code comments, and skill resources in English.
- Keep one English version of each document. Do not retain Chinese or bilingual versions unless the user explicitly requests them later.
- Communicate with the user in Chinese; the conversation language does not determine the language of project artifacts.
- Preserve equations, technical assumptions, numerical results, source provenance, and links when translating existing material.

## Circuit analysis and simulation documents

- When a circuit topic includes an analytical reference and a simulation study, maintain separate `<Topic>-Analysis.md` and `<Topic>-Schematic-and-Simulation.md` documents, following the 5T document pair. The analytical reference contains topology, signal definitions, symbolic derivations, assumptions and applicability limits. Put reconstructed schematics, teaching-model parameters, example bias/load, testbenches, simulation curves, numerical comparisons and execution evidence in the companion.
- In the simulation companion, keep each metric's relevant derivation beside its testbench, plots and comparison. Use the [per-metric learning template](.agents/skills/circuit-analysis-to-simulation/references/metric-learning-template.md) for figure coverage and evidence requirements. Link to the analytical reference for the general treatment.
- Link both documents to each other and catalog them separately in `README.md`. Preserve existing equations and evidence when splitting a combined note. Creating an analytical note alone does not require inventing a simulation companion or claiming unrun validation.
