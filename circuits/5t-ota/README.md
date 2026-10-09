# Five-transistor OTA circuit assets

The user exported `Five-transistor OTA.icproj.json` from
[this Analog Canvas Gallery circuit](https://analog-canvas.tokenzhang.com/g/tckfnzbrkf)
on 2026-10-07. That file remains unchanged. It contains five MOS devices,
SKY130 NFET/PFET bindings and supply/input/output/bias ports.

`educational.icproj.json` is a generated copy with the same geometry,
connectivity and W/L. It names the tail node X and mirror node Y and uses
the authored `NMOS_EDU` / `PMOS_EDU` LEVEL=1 models. Original SKY130
`XM1`–`XM5` subcircuit calls become primitive `M1`–`M5` calls.
This is a declared model replacement, not a process-model conversion.

The port order is `VDD VSS vinp vinn vout vb`. Original internal nodes
export as `net0` = X and `net1` = Y. M5 is the note's M_tail; there is no
separate bias-replica transistor in this circuit.

`provenance.json` records the source hash, electrical extraction and structural
comparison results. Original and teaching exports each match an independently
written reference for their intended bindings and dimensions. All D/G/S/B
connections and port order are checked. This does not establish SKY130 performance.

From the classroom repository root, regenerate with:

```sh
node code/export_5t_ota.mjs /path/to/analog-canvas
```

The script uses existing built `dist/` packages in analog-canvas and writes
only to this classroom repository. It preserves the original and generates
the teaching project, SVG/PNG drawings and both core netlists.
Rerun [the lab](../../simulations/5t-ota/README.md) after regeneration.

This exporter checks the specific supplied Gallery circuit. After an electrical
change, review reference connections, dimensions, node mapping, formulas and
testbenches together; do not silently accept a mismatched reference.
