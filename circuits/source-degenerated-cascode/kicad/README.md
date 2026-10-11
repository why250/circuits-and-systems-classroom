# KiCad graphical DC laboratory

Open `cascode-dc.kicad_sch` in KiCad 10. This is a native, editable schematic,
not an image or a SPICE subcircuit hidden behind one block. The two MOSFETs,
both resistors, four DC sources and load capacitor are individually editable.
KiCad uses its bundled open-source ngspice engine. No cloud service, PDK,
account or separate simulator installation is required.

The current saved circuit has been adjusted to R1=1 kohm, V2=0.85 V,
V3=1.4 V and m=10 for both MOSFETs; R2 remains 50 ohm. Its structure-focused
AC/noise/transient study is in [the main companion](../../../Source-Degenerated-Cascode-Schematic-and-Simulation.md).
Run `python code/run_cascode_structure.py` from the repository root to
reproduce it. Baseline values and the historical first experiment below
describe the original m=1 circuit, not the current saved settings.

## Start on this Windows computer

Use the **Cascode DC Lab** shortcut on the Desktop or in the Start menu.
**KiCad 10** opens the general project manager. The official KiCad 10.0.6
distribution was extracted to `%LOCALAPPDATA%\Programs\KiCad\10.0` because
the current process cannot perform a machine-wide administrator installation.
This is a per-user deployment, not a registered system installer; the shortcuts
provide the launch entry points. File associations and PATH were not changed.
The official installer SHA-256 is
`9e24dc47119f7c472128c2f293c5e3f35569274a44c905e60a7514d47c16ce48`;
its KiCad Services Corporation digital signature was verified.

Keep the repository directory structure intact: both MOSFETs use the same
[`models.lib`](../../../simulations/source-degenerated-cascode/models.lib)
as the original command-line testbenches. The path in each model binding is
relative to the project. Standard KiCad symbols are embedded in the schematic.

## Change a parameter and run OP

1. Hover over a component and press **E**, or double-click it, to open Symbol
   Properties. Change **Value** for a DC source, resistor or capacitor.
2. Save the schematic with **Ctrl+S**.
3. Open **Inspect > Simulator** from the schematic editor. The project automatically
   loads `cascode-dc.wbk`; if needed use **File > Open Workbook** to load it.
4. Select the **OP** tab and click the blue Run triangle, or press **R** in
   the simulator. The console prints the node voltages and device currents.
   OP does not produce a waveform plot.
5. In the schematic editor, enable **View > Show OP Voltages** and optionally
   **Show OP Currents** to display the solved values on the drawing.
6. After another parameter edit, run OP again. Old annotations describe the
   last successful run, so always rerun before interpreting them.

| Schematic reference | Meaning | Baseline Value | Edit to control |
|---|---|---|---|
| V1 | VDD supply | 1.8 | Positive rail voltage |
| V2 | VIN input DC bias | 0.75 | Series current |
| V3 | VB cascode gate bias | 1.25 | Internal X voltage and saturation headroom |
| V4 | VSS rail relative to external ground | 0 | Negative rail voltage |
| R1 | RL load resistor | 50 | Output DC voltage and gain |
| R2 | RE source degeneration | 50 | Degeneration and current |
| C1 | CL output capacitance | 1p | Dynamic response; open circuit at DC |
| M1, M2 | NMOS_EDU devices | w=1u l=150n m=1 | Device geometry |

For the sources and passive devices, the model is configured to read **Value**;
there is no separate `Sim.Params` override hiding a different voltage or
resistance. For M1/M2, use **Simulation Model > Parameters** to edit `w`, `l`
and `m`. Their visible `Sim.Params` field displays the actual stored parameters.
Do not replace the MOS **Value** with a voltage or geometry string: it identifies
the model. Never add `.option scale=1u` to these SI-suffixed MOS dimensions.

## First experiment

Run the unchanged baseline first:

| Measurement | RL=50 ohm | RL=10 kohm |
|---|---:|---:|
| OUT | 1.797036 V | 1.207320 V |
| E | 2.963581 mV | 2.963401 mV |
| X | 0.419283 V | 0.417184 V |
| Supply current | 59.2716 uA | 59.2680 uA |
| M1 saturation margin | 0.119991 V | 0.117892 V |
| M2 saturation margin | 1.085557 V | 0.495443 V |

Then change R1's **Value** from `50` to `10k`, save and rerun OP. OUT should
move to approximately 1.20732 V. Return R1 to `50` to restore the baseline.
The current into V1 is negative when it supplies power; its magnitude is the
positive supply current. Keep both MOS bulk pins connected to **VSS**, not
to their respective source pins. External ground **0** is intentionally
distinct from the VSS node; the zero-volt V4 source connects the two at baseline.

To assess saturation, inspect `vds` and `vdsat` for each device and also confirm
it is conducting. The command-line bridge reports `id`, `vgs`, `von`, `vds`,
`vdsat`, `gm`, `gds`, `gmbs`, and `vds-vdsat` directly. OP node voltages alone
do not establish that both MOSFETs have adequate saturation margin.

## Sweep bias instead of guessing one point

The workbook also includes:

- **DC / V3:** VB from 0.9 to 1.7 V in 2 mV steps, with VIN fixed.
- **DC / V2:** VIN from 0.45 to 1.05 V in 0.5 mV steps, with VB fixed.

Select the desired DC tab and run it. OUT, X and E are selected for plotting.
Every point solves a new DC operating point. These analyses use the current
schematic component values; they do not restore R1 or the other source settings.
The swept source is overridden by the sweep for that analysis.
The simulator's parameter tuner is available for plotted analyses such as DC
sweeps; it is **not** available for OP. Commit a tuned value back to the
schematic before saving if it is meant to become the circuit's new value.

## One schematic for the user and scripts

The shared editing source for this graphical lab is **cascode-dc.kicad_sch**:

```text
User edits graphical schematic ─┐
                               ├─ saved .kicad_sch ─ KiCad SPICE export ─ ngspice
LLM edits native schematic ─────┘
```

Generated SPICE is derived output. Editing an exported `.cir` does not update
the schematic. The original `cascode-core.cir` and 26 published testbenches
remain the historical validated experiment; they are not automatically
overwritten when this debugging project changes.

From the repository root, export and run the **saved** schematic:

```powershell
python code/run_cascode_kicad.py
```

This Windows bridge uses `kicad-cli.exe` and the **same bundled ngspice DLL**
as the GUI. It requires only standard Python, writes a relocatable SPICE deck,
an OP log and a JSON report to
`simulations/source-degenerated-cascode/kicad-results/`, and does not alter
the schematic. Unsaved GUI edits are not visible to the script. For another
KiCad installation, pass `--kicad-dir 'C:\Program Files\KiCad\10.0'`.

To verify the original nominal settings against the original hierarchical
decks, including both 50-ohm and 10-kohm loads:

```powershell
python code/run_cascode_kicad.py --check-baseline
```

This optional check is intended for the baseline, not arbitrary edited bias
values. The script also checks all terminal tuples and deliberately rejects
structural changes until its reference topology is reviewed.
KiCad exports a flat circuit with `/OUT`, `/X`, `/E` node names and numbered
passives/sources. Its text differs from the hierarchical original, but the
connections, models, dimensions and baseline parameters are equivalent.

You can inspect the GUI's actual deck using **Simulation > Show SPICE Netlist**.
For an independent simulator installation, use **File > Export > Netlist** in
the schematic editor and select SPICE, or use KiCad's CLI:

```powershell
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch export netlist --format spice -o cascode.cir circuits/source-degenerated-cascode/kicad/cascode-dc.kicad_sch
```

The standalone export includes the circuit and schematic directives, not the
workbook's active analysis. Add `.op` before `.end` for a standalone OP run,
or load the deck in an interactive ngspice session and issue `op`.

## Draw another circuit manually

Create a KiCad project, place `Simulation_SPICE:VDC`, `Device:R`, `Device:C`
and **Simulation_SPICE:NMOS_Substrate**, then wire the explicit D/G/S/B pins.
Use labels for the named nets and the SPICE ground `0`. Bind each MOS through
**Simulation Model > SPICE model from file**, select `models.lib`, choose
`NMOS_EDU`, and map **1=D, 2=G, 3=S, 4=B**. Set `w=1u`, `l=150n`, `m=1`.
Use unique references with numeric suffixes; for example V1, R1, M1.
The present four-terminal schematic is a working reference you can copy and
edit; rebuilding it by hand is optional.

## Scope and references

The LEVEL=1 model is educational, not a SKY130 PDK model. Its 150-nm geometry
does not establish short-channel accuracy. The first bridge check ran on
2026-10-11 with KiCad 10.0.6 and its bundled ngspice-46. Actual data and hashes
are recorded in the [execution report](../../../simulations/source-degenerated-cascode/kicad-results/summary.json).

The graphical workflow was also exercised in KiCad: editing R1's Value to
`10k`, saving and running OP produced OUT=1.20732 V. R1 was then restored to
`50`, saved in KiCad 10's native format and rerun, giving OUT=1.79704 V.
Both DC workbook tabs ran successfully (401 VB points and 1201 VIN points).
The editor was left open with the baseline OP voltage/current overlays visible.

- [KiCad Windows downloads and official mirrors](https://www.kicad.org/download/windows/)
- [KiCad 10 simulation documentation](https://docs.kicad.org/10.0/en/eeschema/eeschema.html#simulator)
- [ngspice documentation](https://ngspice.sourceforge.io/docs.html)
- [ngspice shared C API](https://github.com/ngspice/ngspice/blob/master/src/include/ngspice/sharedspice.h)
