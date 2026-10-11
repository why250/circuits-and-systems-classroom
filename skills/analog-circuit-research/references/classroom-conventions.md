# Circuits & Systems Classroom project conventions

Apply only when the current repository is Circuits & Systems Classroom. Inspect the actual directory and user request first; these are project conventions, not universal requirements for other repositories.

## Document locations and language

- Keep technical Markdown notes in the repository root and write them in English, matching the knowledge base. Communicate with the user in Chinese. Explicit user language requests take precedence.
- Use hyphenated topic filenames such as `Bootstrapped-Sampling-Switch.md`. Use clear English terms in titles and define abbreviations at first use.
- The root `README.md` is the topic catalog. Add the filename and a brief description under the appropriate category when creating a note.
- Keep computational and plotting scripts in `code/` and referenced figures in `figures/`. Name them by topic and use relative links. Scripts should locate the repository from their own paths rather than depending on the user's working directory.
- Git ignores `reference/`, which may hold local materials. Necessary evidence in public notes must have traceable bibliographic information or stable links rather than relying solely on untracked local files.

## Topology names and coordinated renames

- Name circuit topics and asset directories from the inspected device connectivity, load type, output structure and relevant degeneration/feedback. An imported project title or a user-supplied shorthand is a discovery clue; check that it describes the circuit before using it as the technical topic name. A resistor-loaded, emitter-degenerated BJT differential pair should have a name that communicates those features.
- When correcting a topic name, coordinate its circuit/simulation/figure directories, analytical and companion filenames, script names and imports, path constants, document links, catalog entries and run instructions. Preserve unrelated edits and source circuit contents; retain original source identifiers as provenance when the containing topic directory is renamed.
- Validate links, imported modules and runnable entry points after a rename. Regenerate derived artifacts and manifests when their paths or generating scripts change, so recorded paths and hashes match the delivered files. A name correction alone should not change component values, models or bias conditions.

## Writing and evidence

- Write equations with `$...$` and `$$...$$`. Important equations may use `\boxed{}`, with assumptions and validity conditions nearby.
- Use symbol tables for meanings, units, and definitions. State Hz/rad/s, RMS/peak, single-ended/differential conventions, and noise PSD/variance clearly.
- Begin with a brief description of the analysis target and verification status. Label an incomplete topology as a functional model and list connections or timing still needed for implementation.
- When citing paper data, record process, supply, frequency, load, and measurement conditions that affect comparison. Do not make quantitative cross-study rankings without those conditions.
- Source metadata can verify authors, titles, and DOIs, but cannot establish that the full text was read. Use citation numbers to distinguish external material from independent derivations in the note.
- Check repeated historical formats, equations, and typical parameters before reusing them. Do not turn missing assumptions or references in old notes into a standard.

## Scope and indexing

- Maintain the document knowledge base separately from the `web/` interactive classroom. Research notes do not automatically modify pages, routes, or interactive demonstrations.
- If `.PROJECT.md` or `.FOLDER.md` exists and relevant files require synchronization, update the actual file. Do not create ignored empty indexes merely to reproduce old comments.
- Brief HTML comments may record inputs, outputs, and placement at the top of notes. Do not add maintenance instructions pointing to nonexistent files.
- Repository skill sources live in `skills/analog-circuit-research/` for version control. Installed copies should match the source. The skill's `references/` instruction resources are distinct from the repository's ignored `reference/` materials directory.
