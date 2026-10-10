<!--
Input: user-exported schema-68 Analog Canvas circuit and inherited parameters | Output: independently derived analytical reference | Position: Analysis before the companion derivation/simulation lab
-->
# Source-Degenerated Cascode Amplifier: Analysis

This note follows the topics of [the five-transistor differential-amplifier analysis](5T-Differential-Amplifier-Analysis.md), with equations independently derived for the uploaded circuit. [The companion schematic and simulation note](Source-Degenerated-Cascode-Schematic-and-Simulation.md) supplies intermediate derivations, actual ngspice plots, numerical comparisons and reproducible execution evidence. The declared educational model passed all checks across 26 testbenches on 2026-10-10; the original SKY130 bindings were structurally extracted, not process-simulated.

## Circuit Topology and Identity

The uploaded filename was `(a1) Folded-cascode amplifiers..icproj.json`. Its connectivity shows **two NMOS devices stacked in one branch**, with the current path VDD → RL → M2 → M1 → RE → VSS. It is a **resistor-loaded, source-degenerated cascode amplifier**, with one signal input and one output. The supplied circuit contains no differential pair, current mirror or folded branch.

The source is now [Source-degenerated cascode amplifier.icproj.json](circuits/source-degenerated-cascode/Source-degenerated%20cascode%20amplifier.icproj.json) in `circuits/source-degenerated-cascode/`. Its bytes, SKY130 bindings and historical internal project title remain unchanged; the filesystem names identify the actual circuit. [Provenance](circuits/source-degenerated-cascode/provenance.json) records the old name, hash, connectivity and effective parameters.

![Uploaded topology with internal nodes E and X](figures/source-degenerated-cascode/schematic.svg)

| Element | Role and terminals | Effective original parameters |
|---|---|---|
| M1 | Common-source input; D=X, G=VIN, S=E, B=VSS | W=1 µm, L=0.15 µm, nf=m=1 |
| M2 | Common-gate cascode; D=OUT, G=VB, S=X, B=VSS | W=1 µm, L=0.15 µm, nf=m=1 |
| RE | Source degeneration; E to VSS | 50 Ω |
| RL | Output load; VDD to OUT | 50 Ω |

These values are inherited from `defaults.instancesByType`, rather than explicit instance overrides. VB is an external bias, **not a second signal input**. The output capacitor CL is an additional testbench load, absent from the supplied project.

## Symbols and Assumptions

| Symbol | Definition | Unit |
|---|---|---|
| $v_i,v_b,v_E,v_X,v_o$ | Incremental VIN, VB, source, interstage and output voltages, relative to fixed external ground | V |
| $g_{mi},g_{mbi},g_{di}$ | Positive gate/body transconductance and drain conductance; $g_{di}=1/r_{oi}$ | S |
| $R_E,R_L,R_{out},R_{stack}$ | Degeneration, load, loaded output and transistor-stack output resistances | Ω |
| $G_m$ | Output-short-circuit current transconductance magnitude | S |
| $C_L,C_{gsi},C_{gdi},C_{gbi}$ | External load and OP small-signal device capacitances | F |
| $\gamma_n,\gamma_b$ | Channel thermal-noise coefficient and threshold body-effect coefficient | dimensionless, V$^{1/2}$ |
| $S_v,e_n,v_{n,rms}$ | One-sided voltage PSD, amplitude density and finite-band RMS | V²/Hz, V/$\sqrt{\mathrm{Hz}}$, V |

Unless otherwise stated, both devices conduct in saturation, supplies and VB are AC grounded, the input source is ideal, and low-frequency equations neglect capacitances and tiny junction leakage. Define

$$
k_1=g_{m1}+g_{mb1}+g_{d1},\quad
k_2=g_{m2}+g_{mb2}+g_{d2},\quad D_1=1+k_1R_E,
$$

$$
a=\frac{g_{m1}}{D_1},\qquad b=\frac{g_{d1}}{D_1},\qquad
\Delta=k_2+b(1+g_{d2}R_L).
$$

Here $i$ is the incremental series current flowing OUT → M2 → M1 → RE. General equations precede numerical choices; no typical supply, bias or resistance is silently assumed.

## DC Bias, Saturation and Output Headroom

The branch has one DC current:

$$
I_D=I_{D1}=I_{D2},\qquad V_E=V_{SS}+I_DR_E,\qquad
V_O=V_{DD}-I_DR_L.
$$

For the separately declared LEVEL=1 teaching model,

$$
I_{Di}=\frac{K_P}{2}\frac{W_i}{L_i}
\left(V_{GSi}-V_T(V_{SBi})\right)^2(1+\lambda V_{DSi}),
$$

$$
V_T(V_{SB})=V_{T0}+\gamma_b\left(\sqrt{\Phi+V_{SB}}-\sqrt\Phi\right).
$$

$V_{GS1}=V_{IN}-V_E$ and $V_{GS2}=V_B-V_X$. Both bodies connect to VSS, so their thresholds generally differ. Determine bias from both device currents and both resistor voltage drops. Setting $V_X=V_B-V_{T0}$ omits M2's overdrive and body effect; setting OUT to half the supply omits current balance.

Saturation requires

$$
V_X-V_E\ge V_{OV1},\qquad V_O-V_X\ge V_{OV2}.
$$

Near a fixed current, the output lower limit is approximately $V_X+V_{OV2}$. Combining both devices' headroom gives the minimum feasible level $V_{SS}+I_DR_E+V_{OV1}+V_{OV2}$. Supply voltage and available current limit the upper end. These are local estimates: changing input or load changes current, X and overdrives, so a large excursion needs a new operating-point solution.

With original RL=50 Ω, $I_DR_L$ is small and OUT lies near VDD. Increasing RL raises voltage gain but lowers DC OUT until the cascode loses saturation. The companion explicitly distinguishes the original 50 Ω case from a 10 kΩ load experiment.

## Signal Gain $A_v$

M1 gives

$$
i=g_{m1}v_i+g_{d1}v_X-k_1v_E,\qquad v_E=iR_E,
$$

so $i=av_i+bv_X$. M2 gives $i=g_{d2}v_o-k_2v_X$ and the load gives $v_o=-iR_L$. Solving produces

$$
\boxed{A_v=\frac{v_o}{v_i}=-\frac{R_Lak_2}{\Delta}
=-\frac{g_{m1}R_L}
{D_1+\dfrac{g_{d1}}{k_2}(1+g_{d2}R_L)}}.
$$

The sign is negative: increasing VIN increases current and the drop across RL, lowering OUT. If the output-conductance corrections are small,

$$
\boxed{A_v\approx-\frac{g_{m1}R_L}{1+(g_{m1}+g_{mb1})R_E}}.
$$

Under strong degeneration, $(g_{m1}+g_{mb1})R_E\gg1$, with RL still dominating output resistance,

$$
A_v\approx-\frac{g_{m1}}{g_{m1}+g_{mb1}}\frac{R_L}{R_E}.
$$

Only after neglecting body effect does this reduce to $-R_L/R_E$. Original RE=50 Ω gives weak degeneration at the selected bias; the strong-degeneration formula is inappropriate there.

## Output Resistance and Effective Transconductance

With VIN and VB grounded in AC, the resistance looking down into M1's drain is

$$
R_1=\frac{D_1}{g_{d1}}=r_{o1}+
\left[1+(g_{m1}+g_{mb1})r_{o1}\right]R_E.
$$

Looking down into M2's drain,

$$
\boxed{R_{stack}=r_{o2}+k_2r_{o2}R_1
=\frac{k_2+b}{b g_{d2}}}.
$$

Equivalently, $R_{stack}=r_{o2}+[1+(g_{m2}+g_{mb2})r_{o2}]R_1$; the $g_{d2}$ already included in $k_2$ supplies the unity term.

The circuit output resistance includes the resistor load:

$$
\boxed{R_{out}=R_L\parallel R_{stack}}.
$$

Define the output-short-circuit transconductance magnitude as

$$
G_m=\frac{ak_2}{k_2+b},\qquad \boxed{A_v=-G_mR_{out}}.
$$

The cascode can make $R_{stack}$ very large, but $R_L\ll R_{stack}$ implies $R_{out}\approx R_L$. Using $-g_mR_{stack}$ as the gain of this resistor-loaded circuit would omit its dominant load.

## Internal Node Gains and Input Impedance

$$
\boxed{A_E=\frac{v_E}{v_i}=\frac{R_Eak_2}{\Delta}
=-\frac{R_E}{R_L}A_v},
$$

$$
\boxed{A_X=\frac{v_X}{v_i}=-\frac{a(1+g_{d2}R_L)}{\Delta}}.
$$

E rises with the input and supplies local negative feedback; X moves oppositely. For small relevant $g_d$ corrections, $A_X\approx-a/k_2$, limiting M1 drain movement and its gate-drain Miller multiplication.

An ideal MOS gate has infinite DC input resistance. Real leakage, protection and bias networks alter this. At finite frequency,

$$
Y_{in}(s)=s\left[C_{gs1}(1-A_E(s))+C_{gd1}(1-A_X(s))+C_{gb1}\right],
$$

$$
C_{in,LF}\approx C_{gs1}(1-A_E(0))+C_{gd1}(1-A_X(0))+C_{gb1},\qquad
Z_{in}=1/Y_{in}.
$$

An external source resistance $R_S$ adds an input charging limitation. The present ideal-voltage-source benches do not include that pole.

## Bias Coupling, Common Mode and CMRR

This single-input circuit has no differential input pair, so differential/common-mode gains and CMRR are **not applicable**. Bias transfer is a separate useful measurement.

Allowing an incremental VB gives

$$
\boxed{A_b=\frac{v_o}{v_b}=-\frac{R_L b g_{m2}}{\Delta}},\qquad
\boxed{\left|\frac{A_v}{A_b}\right|=
\frac{g_{m1}k_2}{g_{d1}g_{m2}}}.
$$

As $g_{d1}\to0$, a low-frequency bias disturbance mainly moves X and output coupling tends to zero. Finite M1 output conductance leaves a coupling path. At high frequency M2's $C_{gd2}$ also feeds VB into OUT, so low-frequency rejection is not a broadband guarantee.

A real bias-noise PSD adds input-referred noise $|A_b/A_v|^2S_{v_b}$. The ideal VB source in this lab generates no noise.

## Power Supply Rejection Ratio

Define

$$
A_{s+}=v_o/v_{DD},\qquad A_{s-}=v_o/v_{SS},\qquad
\mathrm{PSRR}^{\pm}=|A_v/A_{s\pm}|.
$$

VIN, VB and the unexcited rail remain fixed to external ground; OUT and CL also reference that ground. The positive supply couples through RL:

$$
\boxed{A_{s+}=\frac{R_{stack}}{R_L+R_{stack}}
=\frac{k_2+b}{\Delta}}.
$$

Since $R_{stack}\gg R_L$, OUT almost follows VDD. A high transistor-stack resistance does not suppress the absolute positive-rail ripple in this circuit.

The negative supply moves RE's lower end and both bodies. Full KCL gives

$$
\boxed{A_{s-}=1-A_v-A_b-A_{s+}
=\frac{R_L\left[ak_2+b(g_{m2}+g_{d2})\right]}{\Delta}}.
$$

The first identity also follows from translating every input, bias and rail equally: every node translates equally at DC. For $g_{d1}\ll g_{m1},k_2$, $A_{s-}\approx-A_v$, so PSRR− is approximately 0 dB under this fixed-external-ground convention.

If input or bias follows VSS, or output is measured as $v_o-v_{SS}$, recombine the corresponding transfers. The 5T OTA tail-current-source expressions do not apply here.

## Thermal Noise

Use one-sided PSDs. For saturated long-channel devices and ideal noisy resistors,

$$
S_{i,Mj}=4k_BT\gamma_n g_{mj},\quad
S_{i,RE}=4k_BT/R_E,\quad S_{i,RL}=4k_BT/R_L.
$$

Separate unit-noise-current KCL gives the low-frequency input-referred result, including finite $g_d$ and body effect:

$$
\boxed{S_{v,in}^{th}=4k_BT\left[
\frac{\gamma_n}{g_{m1}}+
R_E\left(\frac{k_1}{g_{m1}}\right)^2+
\gamma_n g_{m2}\left(\frac{g_{d1}}{g_{m1}k_2}\right)^2+
\frac{1}{G_m^2R_L}\right]}.
$$

The four terms correspond to M1, RE, M2 and RL:

- M1 noise and signal undergo the same degeneration feedback, leaving $4k_BT\gamma_n/g_{m1}$ after input referral.
- RE contributes real noise; body effect increases its weighting relative to a simple $4k_BTR_E$ estimate.
- M2 low-frequency channel noise is suppressed by M1's small drain conductance. Its high-frequency weighting changes.
- RL's input-referred contribution varies as $1/(G_m^2R_L)$. A smaller load lowers its open-circuit voltage noise but also lowers signal gain, and can worsen input-referred noise.

Amplitude density is $e_n=\sqrt{S_v}$, in V/$\sqrt{\mathrm{Hz}}$. Independent powers add, not amplitudes. At any frequency,

$$
S_{v,in}(f)=\frac{\sum_j|h_{j,o}(f)|^2S_{i,j}(f)}{|A_v(f)|^2},\qquad
v_{n,in,rms}=\sqrt{\int_{f_1}^{f_2}S_{v,in}(f)\,df},
$$

where $h_{j,o}$ is each current source's output transimpedance.

## Flicker Noise

In a generic equivalent-gate-voltage description, M1 flicker noise refers directly to VIN; M2's gate-equivalent noise is weighted by $|A_b/A_v|^2$. Actual compact-model KF conventions differ.

This lab specifically uses [ngspice MOS1's noise implementation](https://github.com/ngspice/ngspice/blob/master/src/spicelib/devices/mos1/mos1noi.c). For m=1,

$$
S_{i,j}^{1/f}=\frac{K_F|I_{Dj}|^{A_F}}{fW_j(L_j-2L_D)C_{ox}^2},\qquad
C_{ox}=\epsilon_{ox}/T_{ox}.
$$

AF is the drain-current exponent; frequency dependence remains $1/f$. The low-frequency input coefficient is

$$
B=\frac{K_F|I_{D1}|^{A_F}}{W_1L_{eff,1}C_{ox}^2g_{m1}^2}
+\left(\frac{g_{d1}}{g_{m1}k_2}\right)^2
\frac{K_F|I_{D2}|^{A_F}}{W_2L_{eff,2}C_{ox}^2}.
$$

Where the transfer functions remain approximately their DC values,

$$
S_{v,in}\approx S_w+B/f,\quad f_c\approx B/S_w,\quad
v_{n,in,rms}^2\approx S_w(f_2-f_1)+B\ln(f_2/f_1).
$$

A finite $f_1>0$ is required. A separate illustrative KF=2e−33, AF=1 run is compared with the KF=0 thermal baseline; neither coefficient is fitted to SKY130.

## Poles, Zeros and Bandwidth

Scalar estimates are

$$
\omega_{p,o}\approx1/[R_{out}(C_L+C_{gd2}+C_{db2})],
$$

$$
\omega_{p,X}\sim\frac{g_{d1}+k_2}{C_{gd1}+C_{gs2}+C_{db1}+C_{sb2}},\qquad
\omega_{p,E}\sim\frac{1/R_E+k_1}{C_{gs1}+C_{sb1}}.
$$

Freezing neighboring nodes gives these scales, not the complete coupled roots. In this teaching model, junction capacitances default to zero and both gate voltages are fixed by ideal sources. Therefore, in **E/X/OUT ordering**,

$$
C=\operatorname{diag}(C_{gs1},\ C_{gd1}+C_{gs2},\ C_L+C_{gd2}).
$$

Let $g_E=1/R_E,g_L=1/R_L$, $a_E=g_E+k_1,a_X=g_{d1}+k_2,a_O=g_L+g_{d2}$. Then

$$
G=\begin{bmatrix}a_E&-g_{d1}&0\\-k_1&a_X&-g_{d2}\\0&-k_2&a_O\end{bmatrix},\qquad
(G+sC)\mathbf v=\begin{bmatrix}g_{m1}+sC_{gs1}\\-g_{m1}+sC_{gd1}\\0\end{bmatrix}v_i.
$$

The voltage transfer has $D(s)=\det(G+sC)$ and numerator

$$
\boxed{N(s)=k_2\left[-g_{m1}g_E
+s\left(a_EC_{gd1}+(k_1-g_{m1})C_{gs1}\right)
+s^2C_{gs1}C_{gd1}\right]}.
$$

With both capacitances positive, the constant coefficient is negative and the quadratic coefficient positive, giving two real zeros, one LHP and one RHP. The RHP zero reflects capacitive feedforward competing with the low-frequency inverting path. This circuit has no 5T mirror node or universal mirror zero at twice an internal pole.

When the output pole is well separated, $A_v(s)\approx A_v(0)/(1+s/\omega_{p,o})$. Original RL=50 Ω already has DC gain below unity; there is no conventional falling unity-gain crossing. The 10 kΩ experiment does have one. Extremely high roots extracted from LEVEL=1 verify its mathematics, not short-channel physical bandwidth.

## Small-Signal Settling and Large-Signal Limits

For well-separated poles and a sufficiently small input step,

$$
\Delta v_o(t)\approx A_v(0)\Delta v_i(1-e^{-t/\tau}),\quad
t_\epsilon\approx\tau\ln(1/\epsilon),\quad \tau=1/|p_{slow}|.
$$

This is open-loop small-signal settling, not feedback phase margin or large-signal slew rate. Check final movement and last exit from the specified error band in transient; root positions alone do not establish a slow tail.

For a large signal, the leading output current relation is $C_Ldv_o/dt\approx(V_{DD}-v_o)/R_L-i_{D2}$, with additional device-capacitor currents in the full circuit. Resistive charging and transistor discharge generally differ, and both currents change with bias and voltage. No fixed slew rate or linear swing follows without specifying step size, bias, load and allowed distortion.

## Design Tradeoffs

The original 50 Ω circuit illustrates branch current, body effect, node isolation and loading. For substantial voltage gain, choose RL jointly with current and output headroom; 10 kΩ is a separate demonstration condition, not a silent correction to the source.

Increasing RE strengthens feedback and can make gain depend more on resistance ratio, while reducing current and transconductance and adding source voltage drop and resistor noise. Increasing RL raises gain and reduces its input-referred noise, but lowers output bandwidth and consumes saturation headroom. Increasing device area changes transconductance and flicker noise while increasing capacitance; compare it under explicit bias constraints.

A folded-cascode implementation would redirect input current into a common-gate branch of opposite device polarity, with suitable current sources and biasing. Those missing branches have not been assumed into the uploaded circuit.
