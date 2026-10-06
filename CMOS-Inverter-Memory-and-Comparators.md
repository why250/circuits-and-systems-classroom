# CMOS Inverter Memory and Comparators

An inverter pair can retain a state, amplify a small imbalance or expose device mismatch. Those functions require different operating sequences. This note covers latches/SRAM in P1 and PUF/comparator structures in P4 of the fully reviewed [inverter series](CMOS-Inverter-Applications.md). The analytical extensions below do not establish PDK timing, SRAM yield or hardware-security strength.

## 1. Storage paths and timing

| Circuit / source | Transparent or write path | Retention mechanism | Principal constraint |
|---|---|---|---|
| T-gate static latch, P1 pp. 7–8, Fig. 3 | CK-high input T-gate to Inv1 input | CK-low feedback T-gate closes Inv1/Inv2 loop | Clock overlap, feedback/input contention and setup/hold |
| Tristate static latch, P1 pp. 8–9, Fig. 4 | Enabled input C²MOS inverter followed by Inv1 | Input disabled, clocked feedback inverter enabled | Series-device drive, overlap and retained-state noise margin |
| SR latch, P1 p. 9, Fig. 5 | S pulls $\bar Q$ low; R pulls Q low | Cross-coupled inverters | Pull-down strength must overcome opposing PMOS; simultaneous S/R is invalid |
| Dynamic latch, P1 pp. 9–10, Fig. 6 | CK-high T-gate tracks input at X | Charge on X while T-gate is off | Leakage, injection, clock feedthrough and finite maximum hold time |
| SRAM, P1 pp. 9–10, Fig. 7 | Wordline enables two access NMOS to bitlines | Cross-coupled inverters | Read disturb, write ability and bitline capacitance |

For Fig. 3, input NMOS gate is CK and input PMOS gate $\bar{CK}$; feedback gate polarities are reversed. Clock controls are complementary phases, not separate series signal switches. Inv1 output is Q; Inv2 returns its complement to the held node. An inverter restores voltage levels and isolates storage from the next stage's capacitance.

For a held capacitance $C_H$ with net leakage $I_L$, a constant-leakage estimate gives

$$
|\Delta V|\approx|I_L|T_H/C_H,\qquad
T_H\le C_H\Delta V_{allow}/|I_L|.
$$

This is a bound based on specified leakage/noise margin, not an indefinite retention guarantee. Turn-off adds $\Delta Q/C_H$; clock feedthrough adds a capacitance-divider contribution. Increasing $C_H$ improves retention but loads acquisition.

P1 evaluates latches through a two-latch feedback divide-by-two arrangement. Reported input limits are about 30 GHz for T-gate static, 27 GHz for tristate static and 44 GHz for dynamic. Currents/powers differ: the source reports 300 μW for the first divider, 300 μA for the second and 250 μA for the dynamic divider. At 0.95 V the latter two correspond to 285 and 237.5 μW if the stated currents encompass their circuits. The article's approximate 15-Gb/s inference from the first divider is a heuristic; divider periodic operation does not establish random-data setup/hold, metastability or BER.

## 2. Regeneration is a competition of conductance and initial conditions

Around a symmetric cross-coupled equilibrium, let $v_d=v_1-v_2$ and define node capacitance $C$ and restoring output conductance $g_o$. A positive-feedback pair has approximately

$$
C\frac{dv_d}{dt}=(G_m-g_o)v_d+i_{d,seed}.
$$

If $G_m>g_o$, $\tau=C/(G_m-g_o)$ and a seed grows exponentially until nonlinear limiting. A delay to decision $V_D$ is $t_D\approx\tau\ln(V_D/|v_{d0}|)$ after the seed has been applied. A finite $v_{d0}$ is essential: exact mathematical symmetry does not resolve into a selected state by itself.

For SRAM read, a precharged bitline raises the cell's low node through its access transistor. A simple divider approximation with access resistance $R_A$ and cell pull-down $R_D$ gives $V_{low}\approx V_{BL}R_D/(R_A+R_D)$; require it below the actual opposite inverter switching boundary. The access transistor is a nonlinear source follower, so this is not a transistor sizing rule. Writing imposes an opposing strength requirement. P1's example $C_B=40$ fF and low-node excursion near 0.2 V retains its state in the source simulation; read/write butterfly curves and Monte Carlo margins remain necessary.

## 3. Mismatch-based PUF: bias, ambiguity and repeatability

P4 pp. 8–9, Figs. 1–3 starts with a self-biased inverter establishing a random trip-related voltage, followed by an amplifying and limiting chain. Let the centered first-stage imbalance be $X\sim\mathcal N(\mu,\sigma^2)$ and the effective input decision threshold be $b$:

$$
P(bit=1)=\Phi((\mu-b)/\sigma).
$$

It is 1/2 only for a centered threshold and symmetric distribution. A static per-die PUF value is not fresh random entropy on each read. Correlation between cells, systematic gradients and repeatability across voltage/temperature/aging determine usable identity information.

If the total linear gain magnitude is $A$ and a half-rail output excursion is required, the ambiguous region is approximately

$$
|X|<\frac{V_{DD}}{2A},\qquad
P_{amb}=\operatorname{erf}\!\left(\frac{V_{DD}}{2\sqrt2A\sigma}\right)
$$

for zero mean. P4 p. 9 states $A=200,V_{DD}\approx1$ V but quotes 0.5 mV. The consistent bound is **2.5 mV**; for $\sigma=10$ mV the ideal ambiguous fraction is about **19.74%**. The earlier individual limiter example $A_C=20$ and 25 mV is consistent. The source's actual example uses 0.6 V and gains near 10 per stage, and its histogram is visibly biased; the ideal 1-V calculation must not be substituted for that result.

For a fixed enrolled imbalance $x$ and independent Gaussian read disturbance of standard deviation $\sigma_n$, a single-read error probability against its stable sign is $Q(|x|/\sigma_n)$. PVT shifts are often systematic rather than independent random noise. Enrollment/masking, bias correction and temperature testing can reduce unstable bits; a device-mismatch histogram alone proves neither uniqueness nor unclonability. The source calls fuses another identification mechanism, but a programmed ID is not by itself a physical unclonability proof.

## 4. Offset-canceled regenerative comparator

P4 p. 10, Fig. 4 contains two capacitively cross-coupled inverters. During autozero, S1 and S2 short each inverter's output to its input, storing the individual trip-point differences on $C_1,C_2$ while $C_3,C_4$ couple the external inputs. The nodes need not have equal DC voltage to be balanced.

After opening S1/S2, swapping $v_{in1},v_{in2}$ changes each external voltage by the full initial differential value, with opposite sign. Local charge conservation seeds the two nodes. The connecting capacitors attenuate the loop and add load; shorting $C_1,C_2$ produces the final fast regeneration phase. The chronology must be explicit: autozero, release/swap, bypass, then observation. A bypass switch not shown at transistor level cannot be assigned a nonexistent size or ideal timing guarantee.

Equal 10-fF source capacitors and 2-μm/30-nm NMOS/PMOS devices yield a reported $\tau=9.1$ ps. For two inputs differing by factor two, the predicted decision-time shift is $\tau\ln2=6.31$ ps, provided they share the same regeneration trajectory and decision threshold. Source power is 0.18 mW.

Unequal reset-switch charges create a false differential seed even when static offset was stored. If a parasitic seed $v_p$ is released at time zero and the desired effective signal $v_s$ arrives after $t_g$, a necessary magnitude condition is

$$
|v_p|e^{t_g/\tau}<|v_s|,\qquad
t_g<\tau\ln(|v_s|/|v_p|).
$$

It is not sufficient against later noise or kickback. Source simulations require input change within about 20 ps of release to keep residual offset below 1.5 mV for a 10-mV trip mismatch. Twenty picoseconds is a source operating result, not an offset-cancellation constant. Reset $kT/C$, charge correlations, leakage and regeneration noise remain after autozero.

## 5. Built-in threshold programming

P4 pp. 14–16, Fig. 16 replaces a flash resistor ladder by source-degenerated inverters. Let NMOS degeneration be $R_N$, PMOS degeneration $R_P$, and let both currents equal $I$ at the trip point $V_M$. In a long-channel square-law illustration,

$$
V_M=V_{TN}+IR_N+\sqrt{2I/\beta_N},
$$

$$
V_{DD}-V_M=|V_{TP}|+IR_P+\sqrt{2I/\beta_P}.
$$

Adding gives an implicit current equation; subtracting exposes the threshold shift. NMOS degeneration generally shifts $V_M$ upward, PMOS degeneration downward. The current changes with the resistors, so equally spaced resistor codes do not imply equally spaced thresholds, even before mismatch/body effect.

The source uses 200-Ω units and reports negative shifts 10.5/9.3 mV and positive shifts 7.2/6.4 mV. Their asymmetry requires transistor-strength/threshold calibration. A regenerated comparator downstream adds its own offset, and flash DNL/INL depend on **actual ordered threshold spacing**, not merely resistor values.

## 6. Verification scope

The [analytical script](code/razavi_sixth_batch_analysis.py) checks the PUF gain/range arithmetic and independent logic/charge-related models in the companion notes. The comparator/SRAM equations here pass dimensional, polarity and limiting checks; no transistor Monte Carlo or SRAM yield simulation was run. Implementation tests should sweep read/write strength, retained-node leakage, release-to-input gap, clock overlap, PUF repeatability and false-decision rate with a specified decision time. Related [StrongARM](StrongARM-Comparator-Design.md) and [comparator noise](Comparator-Noise-Calculation.md) notes use different topology and statistical definitions. Source/OCR evidence is in the [sixth-batch record](sources/razavi-sixth-batch-verification.md).
