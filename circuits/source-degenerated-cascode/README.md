# Source-degenerated cascode circuit assets

The user supplied `(a1) Folded-cascode amplifiers..icproj.json` on 2026-10-10.
Connectivity identifies a resistor-loaded, source-degenerated NMOS cascode,
with one signal input/output and external VB. Both devices are NMOS in one
series branch; there is no folded branch or differential pair.

The directory and source filename now reflect that topology. The renamed
`Source-degenerated cascode amplifier.icproj.json` preserves the original
bytes, including its historical internal title and SKY130 binding. Its
SHA-256 and old names are recorded in `provenance.json`.

Effective parameters are inherited from per-type defaults: M1/M2 W=1 um,
L=150 nm, nf=m=1; RE=RL=50 ohm. Both bodies bind to global ground.
Do not assume an absent instance-level parameter means the device has no size.

The companion [analysis](../../Source-Degenerated-Cascode-Analysis.md) and
[schematic/simulation](../../Source-Degenerated-Cascode-Schematic-and-Simulation.md)
notes define E at M1 source and X at M1 drain/M2 source. The schematic uses
the project's own embedded primitives, placements and routes, with explicit
teaching labels and effective values.

`educational.icproj.json` is a separate schema-68 copy with a primitive
`NMOS_EDU` binding and embedded teaching model. Its geometry, W/L, unit
multiplicity, resistor values and connectivity match the source. The unit
SKY130 wrapper NF is omitted from the primitive binding, preserving total W.
The exporter re-extracts the teaching copy to check its electrical identity. It has
not been round-tripped through a built Canvas installation in this checkout.
The executed, independently checked simulation artifact is the generated
SPICE core, not a claim of live editor validation.

Regenerate the source extraction and SVG, from any directory:

```sh
python /path/to/circuits-and-systems-classroom/code/export_cascode.py
```

The extractor supports only this flat schema-68 project's route/contact and
bulk-binding representation. It rejects changed device connections,
dimensions, multiplicity or resistor values pending reference review. It
does not depend on, install or build packages in the sibling Canvas checkout.

`original-sky130.cir` keeps the original wrapper and global ground. No PDK
was run. The educational core promotes ground to an explicit VSS port for
negative-rail measurements; normal baseline VSS=0 reproduces original wiring.
Its RLVAL/REVAL parameters default to 50 ohm; testbench overrides identify
experiments, not changes to the original.

See [the lab instructions](../../simulations/source-degenerated-cascode/README.md)
for actual testbenches, numerical evidence and reproduction.
