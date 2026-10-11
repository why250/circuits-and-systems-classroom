<!-- Input: supplied BJT differential-pair topology. Output: analytical formulas, derivations and applicability conditions. -->
# Analysis of a Resistor-Loaded, Emitter-Degenerated BJT Differential Pair

This analytical reference covers the supplied [CML buffer topology](circuits/bjt-degenerated-differential-pair/CML%20buffer.icproj.json): differential/common-mode gains, internal-node movement, impedance, CMRR, PSRR, noise, poles/zeros, and settling. It follows the topic organization of [the 5T differential-amplifier analysis](5T-Differential-Amplifier-Analysis.md), while deriving the equations for this resistor-loaded BJT circuit.

**Scope:** general mechanisms, symbolic equations and the assumptions under which they hold. The separate [schematic and simulation companion](BJT-Degenerated-Differential-Pair-Schematic-and-Simulation.md) contains the source reconstruction, educational model, example bias, executable testbenches, simulation plots, numerical comparisons and reproduction evidence.

## 1. Circuit Topology and Definitions

The actual circuit has two resistive collector loads and two output terminals. It is a **differential voltage amplifier with a transconductance input stage**, also usable as a CML buffer. Its 1 kΩ resistors provide current-to-voltage conversion; there is no current-mirror active load or differential-to-single-ended mirror conversion.

| Source component/node | Connection or role | Saved value |
|---|---|---|
| Q1 | Collector = `voutn`, base = `vinp`, emitter = E1 | NPN, multiplier 1 |
| Q2 | Collector = `voutp`, base = `vinn`, emitter = E2 | NPN, multiplier 1 |
| Q3 | Collector = X, base = `vb`, emitter = E3 | NPN tail sink, multiplier 1 |
| RD1, RD2 | VDD to the respective collector | 1 kΩ each |
| R3, R2 | E1/E2 to X | 50 Ω each |
| R1 | E3 to ground | 50 Ω |
| Substrate S | Grounded through saved unrouted electrical connections | External SKY130 terminal |

The [companion document](BJT-Degenerated-Differential-Pair-Schematic-and-Simulation.md) provides the reconstructed schematic, extracted netlist and source-connectivity evidence.

Define input and output quantities before assigning gain signs:

$$
v_d=v_{inp}-v_{inn},\qquad v_{cm}=\frac{v_{inp}+v_{inn}}{2},
$$
$$
v_{od}=v_{outp}-v_{outn},\qquad v_{oc}=\frac{v_{outp}+v_{outn}}{2}.
$$

For differential excitation, $v_{inp}=+v_d/2$ and $v_{inn}=-v_d/2$. Increasing `vinp` raises Q1 current and lowers `voutn`; it lowers Q2 current and raises `voutp`. Consequently, $v_{od}/v_d$ and $v_{outp}/v_d$ are **positive**, while $v_{outn}/v_d$ is negative.

| Symbol | Definition | Unit/assumption |
|---|---|---|
| $R_D$ | Each collector resistor | Ω; matched baseline |
| $R_E$ | Each input-pair emitter resistor, R2/R3 | Ω |
| $R_T$ | Tail emitter resistor, R1 | Ω |
| $I_T$ | Q3 collector current = sum of Q1/Q2 emitter currents | A |
| $I_C,I_B$ | Each input transistor's quiescent collector/base current | A |
| $\alpha,\beta$ | $I_C/I_E$, $I_C/I_B$ | $\alpha=\beta/(\beta+1)$ in the simple forward model |
| $V_T$ | Thermal voltage, $kT/q$ | V; 25.865 mV at 27 °C |
| $g_m,g_\pi,g_o$ | Transconductance, base-emitter conductance, output conductance | S; $g_\pi=1/r_\pi$, $g_o=1/r_o$ |
| $r_t$ | Resistance seen into Q3 collector with bias/supply AC grounded | Ω; includes R1 degeneration |
| $C_\pi,C_\mu$ | Linearized base-emitter/base-collector capacitance | F |
| $C_L$ | Equal external load capacitance from each output to the lower rail | F; a load parameter, absent from the saved source |
| $s,\omega,f$ | Complex frequency, angular frequency, frequency | $s=j\omega$, $\omega=2\pi f$ |

The simple formulas assume matched devices, forward-active operation, low-impedance input/bias voltage sources, and equal loads. Finite $r_\pi$ and $r_o$ are retained where needed. BJT base current and shot noise must not be replaced by MOS gate-current or channel-noise assumptions.

## 2. DC Bias and Headroom

### 2.1 Bias equations

At zero differential input, symmetry gives

$$
I_{E1}=I_{E2}=\frac{I_T}{2},\qquad I_C\simeq\alpha\frac{I_T}{2},
$$
$$
V_{E3}=I_{E3}R_T,\qquad V_b=V_{BE3}+I_{E3}R_T,
$$
$$
V_{E1}=V_{E2}=V_{CM}-V_{BE},\qquad
V_X=V_{CM}-V_{BE}-\frac{I_TR_E}{2},
$$
$$
V_{OC}=V_{DD}-I_CR_D.
$$

Q3 collector current is not its emitter current: $I_{E3}=I_T+I_{B3}$. Thus $(V_b-0.7\ \mathrm V)/R_T$ is only a rough estimate, not a bias solution. $V_{BE}$ depends exponentially on current, and Early effect makes $I_T$ depend weakly on $V_X$.

For the simple forward BJT model,

$$
g_m\simeq\frac{I_C}{V_T},\quad r_\pi\simeq\frac{\beta}{g_m},\quad r_o\simeq\frac{V_A}{I_C}.
$$

The device parameters refer to a selected bias point. These approximations explain their scale without replacing the derivatives of a more complete BJT model.

### 2.2 Forward-active constraints

Require conducting BE junctions and reverse-biased BC junctions. A strict baseline criterion is

$$
V_X>V_b,\qquad V_{outn}>V_{inp},\qquad V_{outp}>V_{inn}.
$$

At balanced input, this suggests the implicit common-mode bounds

$$
\boxed{V_b+V_{BE}+\frac{I_TR_E}{2}<V_{CM}<V_{DD}-I_CR_D.}
$$

Currents and junction voltages vary with common mode, so solve the bias and check the inequalities across a sweep. These bounds use $V_{BC}<0$, rather than treating the approximate 0.2 V saturated $V_{CE}$ as sufficient for an active-region small-signal model. Unequal inputs require checking each collector separately.

## 3. Differential Gain and Current Steering

### 3.1 Mechanism and first approximation

Matched differential excitation makes $v_X=0$ by symmetry. This is a **virtual ground for this excitation**, not a physical short and not the common-mode behavior. Each input transistor sees $R_E$ to this virtual ground.

Ignoring Early effect initially, emitter KCL gives

$$
\frac{v_e}{R_E}=(g_m+g_\pi)(v_b-v_e),
$$
$$
v_\pi=\frac{v_b}{1+(g_m+g_\pi)R_E},\qquad
G_d=\frac{i_c}{v_b}=\frac{g_m}{1+(g_m+g_\pi)R_E}.
$$

Therefore,

$$
\boxed{A_{dd}\equiv\frac{v_{od}}{v_d}\simeq G_dR_D,\qquad
A_{sd}\equiv\frac{v_{outp}}{v_d}\simeq\frac{G_dR_D}{2}.}
$$

The factor of two matters: with resistor loads there is no mirror that combines both branch signal currents into one output. With $g_mR_E\gg1$, $G_d\simeq\alpha/R_E$ and $A_{dd}\simeq\alpha R_D/R_E$. Raising bias then yields diminishing gain improvement.

### 3.2 Closed form with finite beta and Early effect

Let $G_D=1/R_D$ and $G_E=1/R_E$. At DC, the half-circuit equations are

$$
\begin{bmatrix}
G_D+g_o&-(g_m+g_o)\\
-g_o&G_E+g_m+g_\pi+g_o
\end{bmatrix}
\begin{bmatrix}v_c\\v_e\end{bmatrix}
=\begin{bmatrix}-g_m\\g_m+g_\pi\end{bmatrix}v_b.
$$

For any effective emitter-to-ground conductance $G$, define

$$
F=\frac{G_D}{G_D+g_o},\qquad
D(G)=G+g_\pi+F(g_m+g_o),
$$
$$
H(G)=\frac{v_c}{v_b}=
\frac{g_og_\pi-g_mG}{(G_D+g_o)D(G)}.
$$

The matched differential gains are

$$
\boxed{A_{dd}=-H(G_E),\qquad A_{sd}=-\frac{H(G_E)}{2}.}
$$

This is exact within the stated DC hybrid-pi model, neglecting reverse-junction $g_\mu$. That approximation requires a reverse-biased BC junction with conductance small relative to the retained terms. It is not the simpler $g_m(r_o\parallel R_D)$ of an undegraded common-emitter stage.

### 3.3 Large-signal linearity

With a fixed tail current, negligible Early effect, and constant $\alpha$, define $\delta=(I_{C1}-I_{C2})/(I_{C1}+I_{C2})$. The two BE exponentials and resistor drops give

$$
\boxed{v_d=2V_T\operatorname{atanh}(\delta)+R_EI_T\delta,\qquad
v_{od}=\alpha I_TR_D\delta.}
$$

Without degeneration, $\delta=\tanh(v_d/(2V_T))$. Degeneration adds the linear term $R_EI_T\delta$, increasing the useful input range. Differentiating at $\delta=0$ recovers $G_dR_D$ with $g_m=\alpha I_T/(2V_T)$.

This steering relation assumes a fixed tail current and forward-active operation of both input devices and Q3. Changing tail current, finite Early effect and headroom limits alter the large-signal curve. The derivative describes only the local gain around balanced input.

## 4. Tail Resistance, Internal Nodes, Common-Mode Gain, and CMRR

### 4.1 Tail output resistance with finite beta

With Q3 base and lower rail AC grounded, let $G_T=1/R_T$ and use Q3 parameters with subscript 3. Its emitter voltage obeys

$$
v_{e3}=\frac{g_{o3}}{G_T+g_{m3}+g_{\pi3}+g_{o3}}v_X.
$$

Substituting into $i_{c3}=g_{o3}v_X-(g_{m3}+g_{o3})v_{e3}$ yields

$$
\boxed{r_t=\frac{G_T+g_{m3}+g_{\pi3}+g_{o3}}{g_{o3}(G_T+g_{\pi3})}
=r_{o3}+(1+g_{m3}r_{o3})(R_T\parallel r_{\pi3}).}
$$

Finite beta limits the resistance boost because the base is fixed by an ideal bias source. This collector resistance includes tail-emitter degeneration and differs from the intrinsic $r_{o3}$.

### 4.2 Common-mode mechanism and exact DC solution

Both emitters now move together. Tail KCL gives

$$
2\frac{v_e-v_X}{R_E}=\frac{v_X}{r_t},\qquad
v_X=\frac{2r_t}{R_E+2r_t}v_e.
$$

Each half-circuit therefore sees the common-mode emitter impedance $R_E+2r_t$, rather than $R_E$. Set $G_C=1/(R_E+2r_t)$ in the preceding closed form:

$$
\boxed{A_{sc}\equiv\frac{v_{outp}}{v_{cm}}=H(G_C),\qquad
\frac{v_e}{v_{cm}}=\frac{g_\pi+Fg_m}{D(G_C)}.}
$$
$$
\frac{v_X}{v_{cm}}=\frac{2r_t}{R_E+2r_t}\frac{g_\pi+Fg_m}{D(G_C)}.
$$

Neglecting $g_o$ in the input pair gives the useful approximation

$$
A_{sc}\simeq-\frac{g_mR_D}{1+(g_m+g_\pi)(R_E+2r_t)}
\simeq-\frac{\alpha R_D}{2r_t}
$$

for a large tail impedance. The exact numerator contains $g_og_\pi$: a product small in absolute terms can matter for a very small common-mode gain. Even $r_t\to\infty$ does not force single-ended common-mode gain to zero when finite beta and Early effect are both retained.

In this circuit the high tail resistance allows X to **track common-mode input almost one-for-one**. A high-impedance tail is not an AC-ground condition for common-mode excitation.

### 4.3 Define the CMRR being quoted

Single-ended CMRR, using the same output for both gains, is

$$
\boxed{\mathrm{CMRR}_{se}=\left|\frac{A_{sd}}{A_{sc}}\right|,
\qquad \mathrm{CMRR}_{se,dB}=20\log_{10}\mathrm{CMRR}_{se}.}
$$

The first-order approximation is

$$
\mathrm{CMRR}_{se}\simeq
\frac{1+(g_m+g_\pi)(R_E+2r_t)}{2[1+(g_m+g_\pi)R_E]}.
$$

It approaches $g_mr_t$ without input degeneration, and approximately $r_t/R_E$ with strong input degeneration. Increasing tail resistance improves rejection, while input degeneration reduces differential gain.

For the **differential output**, ideal matched common-mode excitation produces $v_{outp}=v_{outn}$ and hence $A_{dc}=v_{od}/v_{cm}=0$. Its ideal CMRR is unbounded. That symmetry result is not a finite production specification; device/load mismatch, unequal source impedances, and asymmetric parasitics establish practical rejection.

## 5. Input and Output Impedance

### 5.1 Differential input resistance

With negligible Early effect, each base sees

$$
R_{in,half}=r_\pi+(\beta+1)R_E,
\qquad
\boxed{R_{in,d}=2[r_\pi+(\beta+1)R_E].}
$$

Define the differential input-port current as $i_d=(i_{bp}-i_{bn})/2$, so $Z_{in,d}=v_d/i_d$. A DC input driver must also supply each base current $I_B$; finite beta therefore affects both bias loading and input impedance.

Common-mode input impedance is different because the shared tail moves. In the same simple model, each input sees approximately $r_\pi+(\beta+1)(R_E+2r_t)$ under equal common-mode drive. Capacitive input impedance and a finite source resistance require the full frequency-dependent equations.

### 5.2 Output resistance and port conventions

With a transistor base AC grounded and an emitter resistance $R$, its collector resistance is

$$
r_{c,deg}=r_o+(1+g_mr_o)(R\parallel r_\pi).
$$

For a pure differential output test, use $R=R_E$:

$$
R_{out,half,d}=R_D\parallel r_{c,deg},\qquad
R_{out,d}=2R_{out,half,d}.
$$

For common output motion, replace $R_E$ by $R_E+2r_t$. Injecting a current into **only one output** while leaving the other free excites both modes, so

$$
R_{out,se}=\frac{R_{out,half,d}+R_{out,half,c}}{2}
$$

in the matched DC model. The one-output and differential-output port definitions must be kept distinct when calculating gain or an output time constant.

The collector resistors limit the loaded output resistance. Quoting the intrinsic BJT $r_o$ as the amplifier output resistance would overestimate gain and the output time constant.

## 6. Power-Supply Rejection and Bias Sensitivity

### 6.1 Supply references are part of the definition

For supply analysis, introduce a lower-rail perturbation $v_{ss}$ at the bottom of R1 and the external output capacitors. Hold the input common-mode reference fixed. Two bias-reference choices must be distinguished:

- **Fixed bias:** the Q3 base is held at global ground in AC.
- **Tracking bias:** $v_b-v_{ss}$ is held constant, so $v_b=v_{ss}$ in AC.

The saved topology has ground rather than a separate VSS pin. Splitting this reference defines a supply-sensitivity model. Substrate parasitics require a four-terminal device model and are outside the intrinsic three-terminal equations here.

For a selected single-ended output,

$$
H_{DD}=\frac{v_{outp}}{v_{dd}},\quad H_{SS}=\frac{v_{outp}}{v_{ss}},\quad
H_B=\frac{v_{outp}}{v_b},\qquad
\mathrm{PSRR}_{se}^{\pm}=\left|\frac{A_{sd}}{H_{DD/SS}}\right|.
$$

### 6.2 Why upper-rail coupling is large

At low frequency and with negligible Early effect, the collector current is almost supply independent and the resistor drop is almost constant. Thus

$$
\boxed{H_{DD}\simeq1.}
$$

The output common mode follows VDD. This follows from a **resistor to VDD**, not from treating a mirror output transistor as diode connected. Matched outputs follow together, so the differential supply transfer is zero in the symmetric model.

### 6.3 Why lower-rail rejection depends on the bias generator

Eliminate Q3 emitter voltage in its low-frequency equations:

$$
i_{c3}=\frac{v_X-v_{ss}}{r_t}+G_{B3}(v_b-v_{ss}),
$$
$$
G_{B3}=\frac{g_{m3}G_T-g_{o3}g_{\pi3}}
{G_T+g_{m3}+g_{\pi3}+g_{o3}}.
$$

If the base does not track the lower rail, the rail changes $V_{BE3}$ and therefore tail current. Approximately,

$$
H_B\simeq-\frac{\alpha R_DG_{B3}}{2},\qquad
H_{SS,\,fixed\ bias}\simeq- H_B.
$$

For tracking bias, linearity gives

$$
\boxed{H_{SS,\,tracking}=H_{SS,\,fixed}+H_B.}
$$

At DC, translating all inputs, bias, and rails together by the same voltage translates the outputs by that voltage. Consequently,

$$
A_{sc}+H_{DD}+H_{SS,\,fixed}+H_B=1,
$$
$$
H_{SS,\,tracking}=1-H_{DD}-A_{sc}\simeq-A_{sc}
$$

when $H_{DD}\simeq1$. The common-mode/negative-PSRR correspondence requires this particular bias-reference choice; it is not automatic.

## 7. Noise Analysis

### 7.1 Conventions and included mechanisms

All PSDs here are **one-sided**: current PSD in A²/Hz, voltage PSD in V²/Hz, amplitude spectral density (ASD) in V/√Hz, and finite-band integrated noise in V RMS. Input reference is the same differential $v_d$ used for $A_{dd}$. Uncorrelated source powers are summed before taking a square root.

Use an independent-source BJT noise model [2, 3]: collector shot PSD $2q|I_C|$, base shot PSD $2q|I_B|$, explicit resistor Norton PSD $4kT/R$, and optional base-emitter flicker PSD $\mathrm{KF}|I_B|^{\mathrm{AF}}/f$. The formulas below neglect intrinsic base/collector/emitter series resistances and assume ideal external voltage sources. Physical series resistance and source noise must be added when present.

Collector and base sources are treated as independent. Advanced physical models may require noise correlations. Bias-source noise, finite source resistance, mismatch and sampling aliases are outside this baseline.

### 7.2 Low-frequency derivation with negligible Early effect

Let $a=1+(g_m+g_\pi)R_E$ and $G_d=g_m/a$.

**Input collector shot noise.** For a collector-to-emitter noise source $i_{nc}$, emitter KCL changes $v_e$ and partially cancels the direct collector-current disturbance. The residual collector current is

$$
i_{out,nc}=i_{nc}\frac{1+g_\pi R_E}{a}.
$$

Referred through $G_d$, each device contributes $2qI_C[(1+g_\pi R_E)/g_m]^2$. The two devices give

$$
S_{v,collector}\simeq\frac{4qI_C}{g_m^2}(1+g_\pi R_E)^2.
$$

**Input base shot noise.** With ideal base voltage sources, a base-to-emitter noise source creates an emitter disturbance through $R_E$, leading to the equivalent input voltage $R_Ei_{nb}$ in this approximation:

$$
S_{v,base}\simeq4qI_BR_E^2.
$$

**Emitter resistor thermal noise.** Each series resistor's $4kTR_E$ voltage noise is equivalent to a branch input voltage; the differential sum is

$$
S_{v,R_E}\simeq8kTR_E.
$$

**Collector resistor thermal noise.** The two load-current PSDs produce differential output voltage noise $8kTR_D$, giving

$$
S_{v,R_D}\simeq\frac{8kT}{R_DG_d^2}.
$$

Therefore the engineering white-noise estimate is

$$
\boxed{S_{v,white}\simeq
\frac{4qI_C}{g_m^2}(1+g_\pi R_E)^2
+4qI_BR_E^2+8kTR_E+\frac{8kT}{R_DG_d^2}.}
$$

This replaces the MOS $4kT\gamma g_m$ channel-noise expressions. In the matched circuit, Q3 and R1 noise drive common output motion and cancel at the **differential output**. They do contribute to a single-ended noise measurement; cancellation is lost with mismatch.

Adding physical base resistance or finite driver impedance changes base-noise propagation. The ideal-source expression above must then be extended, rather than omitting the new current-to-voltage conversion.

### 7.3 Flicker noise and finite integration

For ngspice's Gummel–Poon KF/AF convention [3], and the same low-frequency approximation,

$$
S_{v,1/f}\simeq 2R_E^2\frac{\mathrm{KF}|I_B|^{\mathrm{AF}}}{f}.
$$

KF is an empirical model coefficient used with currents in amperes and frequency in hertz; it is not the MOS area/$C_{ox}$ coefficient. Its value and AF must be specified by the chosen model. If $S_{v,1/f}=K_v/f$ and the white PSD is $S_0$, the low-frequency corner estimate is $f_c=K_v/S_0$.

For $S_v=S_0+K_v/f$ over a band where that approximation holds,

$$
v_{n,rms}^2=S_0(f_H-f_L)+K_v\ln\frac{f_H}{f_L},\qquad f_L>0.
$$

Input-referred integration does not include an extra output-pole rolloff: output noise has already been divided by the signal gain. Output RMS instead integrates $S_{v,out}$. Finite integration limits are part of the noise definition.

## 8. Poles, Zeros, and Transfer Function

### 8.1 Differential half-circuit, including BJT charge

There is no mirror node, so a mirror pole and its associated zero cannot be imported from the 5T OTA. Under matched differential drive, X is fixed by symmetry; Q3's common-mode dynamics do not enter the differential transfer.

Set $C_o=C_L+C_\mu$ and introduce $C_x=\partial Q_{BE}/\partial V_{BC}$, a signed cross-charge derivative. Forward diffusion charge can depend on BC voltage through Early effect. $C_x$ represents a controlled charge derivative, not a standalone negative capacitor. A reciprocal $C_\pi/C_\mu$-only model neglects this coupling; retain it when the selected charge model includes it [4].

With reverse-junction conductance neglected, the exact differential half-circuit equations for this charge model are

$$
\begin{bmatrix}
G_D+g_o+sC_o&-(g_m+g_o)\\
sC_x-g_o&G_E+g_m+g_\pi+g_o+sC_\pi
\end{bmatrix}
\begin{bmatrix}v_c\\v_e\end{bmatrix}
=\begin{bmatrix}sC_\mu-g_m\\g_m+g_\pi+s(C_\pi+C_x)\end{bmatrix}v_b.
$$

Define $B=G_E+g_m+g_\pi+g_o$. Cramer's rule gives

$$
H_d(s)=\frac{v_c}{v_b}=\frac{N(s)}{D(s)},\qquad
\boxed{A_{dd}(s)=-H_d(s),\quad A_{sd}(s)=-\frac{H_d(s)}{2},}
$$
$$
D(s)=C_oC_\pi s^2+
[(G_D+g_o)C_\pi+C_oB+(g_m+g_o)C_x]s
+(G_D+g_o)B-g_o(g_m+g_o),
$$
$$
N(s)=C_\mu C_\pi s^2+
[C_\mu B+g_oC_\pi+(g_m+g_o)C_x]s
+g_og_\pi-g_mG_E.
$$

Setting $s=0$ recovers the DC gain above. Roots of $D$ are poles; roots of $N$ are zeros. Factors for an LHP zero use $1+s/\omega_z$; an RHP zero uses $1-s/\omega_z$. Their signs are determined from these roots rather than a copied template.

### 8.2 Bandwidth estimates and interpretation of roots

For a dominant load capacitance,

$$
\omega_{p,o}\simeq\frac{1}{R_{out,half,d}C_o}.
$$

A rough emitter-node scale is $\omega_{p,e}\sim B/C_\pi$. Node coupling shifts both scales; solve the roots of $D(s)$ for the selected bias and load. The actual −3 dB frequency is the crossing $|A_{dd}(j2\pi f)|=|A_{dd}(0)|/\sqrt{2}$ and need not equal the magnitude of one pole.

Base-collector feedforward can produce an RHP zero; emitter dynamics and the selected charge model determine the remaining roots. Finite source impedance adds input states and Miller loading. Root locations are model- and bias-dependent, rather than transferable process-independent frequencies.

## 9. Settling, Slew, and Stability Limits

### 9.1 Small open-loop step

For a dominant-pole response,

$$
\tau\simeq\frac{1}{|s_{p1}|},\qquad
t_\epsilon\simeq\tau\ln\frac{1}{\epsilon}.
$$

The single-exponential estimate assumes a dominant stable pole and a small step within the local linear range. Additional poles and zeros change residues and the response shape. A pole and a zero at different frequencies do not by themselves establish a slow settling tail; evaluate the complete response. Settling accuracy is normalized to the final output change, with an explicit input-edge time reference.

### 9.2 Large steps and feedback

For each output, the actual charge balance is

$$
C_L\frac{dV_{out}}{dt}=\frac{V_{DD}-V_{out}}{R_D}-I_C
$$

when parasitic charge terms can be neglected. Thus this resistor-loaded circuit does not have a universal single-ended slew rate $I_T/C_L$. Immediately after ideal full steering from the balanced state, with fixed tail current and output voltages still at their old values, the approximate magnitudes are $\alpha I_T/(2C_L)$ per output and $\alpha I_T/C_L$ differentially. Subsequent resistor current and BJT saturation change those slopes.

Large-signal slew and saturation recovery are distinct from local linear settling. An open-loop transfer does not establish closed-loop phase margin: a feedback analysis must define sensing polarity, feedback factor, loading and the loop-break model. Increasing $C_L$ generally lowers a dominant output bandwidth and lengthens small-signal settling; decreasing it can expose emitter/input dynamics.

## 10. Applicability and Companion Study

These equations distinguish signed single-ended and differential gains, finite-beta/Early-effect common-mode response, intrinsic and loaded impedances, bias-reference-dependent PSRR, BJT shot noise, resistor noise and charge-model dynamics. Matching is used for modal cancellation; practical mismatch and asymmetric parasitics require the full circuit equations. The source's four-terminal substrate behavior is not established by the intrinsic BJT model.

For the example parameters, schematic, executed experiments, curves and numerical accuracy of the approximations, see [BJT Emitter-Degenerated Differential Pair: Schematic and Simulation](BJT-Degenerated-Differential-Pair-Schematic-and-Simulation.md). The formulas here do not specify process corners, a calibrated flicker coefficient, a statistical mismatch distribution, a bias generator, or a closed-loop design.

## References and Source Status

1. [User-supplied CML buffer project](circuits/bjt-degenerated-differential-pair/CML%20buffer.icproj.json), schema 68; full saved connectivity and bindings inspected. [The 5T analysis](5T-Differential-Amplifier-Analysis.md) supplies the topic organization. Circuit-level derivations above are for the actual resistor-loaded BJT topology.
2. [ngspice BJT documentation](https://nmg.gitlab.io/ngspice-manual/bjts/bipolarjunctiontransistors_bjts.html) and [official documentation index](https://ngspice.sourceforge.io/docs.html), consulted for Gummel–Poon model context.
3. [ngspice BJT noise implementation](https://github.com/ngspice/ngspice/blob/master/src/spicelib/devices/bjt/bjtnoise.c), relevant independent-source and KF/AF definitions inspected on 2026-10-11. The specific simulator version and executed model behavior are recorded in the companion.
4. [BJT charge/linearization implementation](https://github.com/ngspice/ngspice/blob/master/src/spicelib/devices/bjt/bjtload.c) and [OP parameter access](https://github.com/ngspice/ngspice/blob/master/src/spicelib/devices/bjt/bjtask.c), relevant cross-charge definitions inspected on 2026-10-11. Model-specific numerical values and validation remain in the companion.
