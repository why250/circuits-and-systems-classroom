# Floating Inverter Amplifier (FIA)

A floating inverter amplifier is a dynamic differential amplifier powered during amplification by a capacitor between isolated supply rails. This note revises the earlier static-gain treatment using Razavi's inverter series Part 3, pp. 13–14, Figs. 4–5. Full original-page review and independent analytical models support the discussion; no PDK, transistor-level noise simulation or measured result is claimed. See the [series map](CMOS-Inverter-Applications.md) and [verification record](sources/razavi-sixth-batch-verification.md).

## Topology, phases and definitions

Two CMOS inverters share an upper rail U and lower rail L. Their separate inputs are $v_{i1},v_{i2}$; their outputs X,Y have capacitors $C_X,C_Y$ to ground. Reservoir $C_R$ connects U to L. During reset, switches restore U to $V_{DD}$, L to ground and both outputs to the selected common-mode bias. During amplification, these supply/reset connections open and the input difference steers charge while $C_R$ discharges through the inverter devices. Observe the differential output at a specified time T after release.

| Symbol | Meaning / units |
|---|---|
| $v_{id}=v_{i1}-v_{i2}$ | Differential input (V) |
| $v_{od}=v_X-v_Y$ | Differential output (V), negative for a positive input under the chosen polarity |
| $C_L=C_X=C_Y$ | Equal per-output load (F), not the sum of both loads |
| $G_d(t),g_d(t)$ | Effective differential transconductance / output conductance (S) along the amplification trajectory |
| $V_R=V_U-V_L$, $I_R$ | Reservoir voltage (V), discharging through-current (A) |
| $A_d(T)$ | Differential endpoint gain, $v_{od}(T)/v_{id}$ for zero initial differential state |
| $S_{i,d}$ | One-sided equivalent differential current PSD (A²/Hz) |

The input/common-mode operating point, device body connections and switch timing matter. Effective differential parameters must be extracted for this topology; they cannot automatically be copied from an inverter on ideal fixed rails.

## Common-mode preservation is a charge constraint

If the isolated rails and reservoir have no charge path to ground, gates and bulks draw no current, and $C_X,C_Y$ are the only grounded output capacitors, total output charge satisfies

$$
\Delta(C_Xv_X+C_Yv_Y)=0.
$$

For equal loads this gives $\Delta(v_X+v_Y)=0$, preserving arithmetic output common mode. Unequal loads preserve the weighted sum instead. Reservoir-to-ground parasitics, device body paths, leakage, clock injection and the following sampler break the ideal constraint. Input common mode can still change device current, gain and amplification time even when the ideal output common mode is preserved. P3 Fig. 4(e)'s common-mode equivalent supports this ideal limit, not immunity to every supply or input disturbance.

## Gain at the sampling instant

Linearize differential motion along the time-varying rail trajectory. For equal loads and locally linear operation,

$$
C_L\frac{dv_{od}}{dt}+g_d(t)v_{od}=-G_d(t)v_{id}.
$$

For constant input difference and zero initial output difference, integrating the state equation gives

$$
\boxed{A_d(T)=-\frac{1}{C_L}\int_0^T G_d(u)
\exp\left[-\frac{1}{C_L}\int_u^Tg_d(v)\,dv\right]du}.
$$

A retained initial output adds $v_{od}(0)\exp[-\int_0^Tg_d/C_L]$. If both coefficients remain constant, the endpoint gain is

$$
A_d(T)=-\frac{G_d}{g_d}(1-e^{-g_dT/C_L}).
$$

Only sustained coefficients and adequate time lead to the frozen value $-G_d/g_d$. For negligible output conductance, $A_d(T)=-\int_0^TG_d(u)du/C_L$. If current self-quenches rapidly, the integral can stop growing well below the frozen gain. A single $C_L/g_m$ settling rule does not describe every FIA trajectory, and rail motion can cause later drift after an initial fast response.

The independent script illustrates $G_d(t)=1\text{ mS}\,e^{-t/(0.4\text{ ns})}$, $g_d=G_d/10$, $C_L=0.2$ pF. At 2 ns the discretized endpoint magnitude is 1.8037, despite a frozen ratio of 10. These chosen coefficients explain the distinction; they do not fit or reproduce the source transistor waveform.

P3 reports $C_R=4$ pF, $C_X=C_Y=0.2$ pF, a 10-mV differential input, gain about 4 and an initial response about 1 ns. Fig. 5 also shows subsequent output movement. The reservoir/load ratio is 20, but it is neither a gain of 20 nor 40. The predecessor's $2C_T/C_X$ charge-steering expression applies to its NMOS circuit, not universally to the FIA.

## Reservoir droop and energy

Define $I_R>0$ as through-current discharging the reservoir:

$$
C_R\frac{dV_R}{dt}=-I_R(t),\qquad
\Delta V_R=-\frac{Q_R}{C_R},\qquad Q_R=\int_0^T I_R(t)dt.
$$

$Q_R$ includes the common through-current needed to establish amplification, not merely the difference of output capacitor charges. A differential output amplitude therefore cannot establish reservoir droop by itself. Select $C_R$ from allowed rail trajectory, integrated current, gain/noise requirements and reset time; there is no universal $C_R\ge10C_L$ rule.

Reservoir energy released from $V_0$ to $V_1$ is

$$
E_{released}=\tfrac12C_R(V_0^2-V_1^2).
$$

For ordinary recharge from a fixed $V_{DD}$ back to $V_0=V_{DD}$, source energy is

$$
E_{supply}=V_{DD}C_R(V_{DD}-V_1).
$$

The difference between supply energy and restored capacitor energy is reset-path dissipation. Output reset, clock drivers, input circuitry and following-stage loads add separate consumption. Energy-recovery recharge would need its own explicit topology. A generic efficiency of 0.7–0.9 is not established here.

The source's 160 µW at 100 MHz corresponds to 1.6 pJ/cycle under its simulated power boundary. Completely discharging and recharging 4 pF from zero at 0.95 V would instead draw $C_RV_{DD}^2=3.61$ pJ/cycle. This benchmark is not the same trajectory or power boundary; it does not contradict partial reservoir discharge.

## Sampled noise uses a time-domain kernel

For locally white equivalent differential current noise, use the one-sided convention

$$
\langle i_n(t)i_n(t')\rangle=\tfrac12 S_{i,d}(t)\delta(t-t').
$$

Its variance at the observation time is

$$
\boxed{\sigma_{od}^2(T)=\frac{1}{2C_L^2}\int_0^T S_{i,d}(u)
\exp\left[-\frac{2}{C_L}\int_u^Tg_d(v)dv\right]du}.
$$

For input reference divide by $|A_d(T)|^2$. This formula assumes deterministic coefficients and white local noise; flicker, input/rail noise and reset-to-amplify correlations require the full two-time covariance kernel. Reservoir noise can modulate gain and couple through parasitics; floating rails do not prove zero contribution.

Independent output reset capacitors would initially contribute $2kT/C_L$ differential variance, subsequently weighted by the homogeneous decay. Actual reset switches and floating-charge constraints can correlate the initial states and change this result. Initial covariance and amplification noise must be combined according to their correlation.

An expression proportional to $kT/g_m$ has units V²/Hz. It cannot be labeled sampled voltage variance without the integration kernel or bandwidth. Similarly, a reservoir's equilibrium $kT/C_R$ voltage variance is not automatically an additive input-referred FIA variance. Reset duration and actual coupling must be included.

## Switched-capacitor use and finite gain

For a defined settled inverting capacitor-feedback phase with sample-to-feedback ratio $r=C_S/C_F$, ideal retained bias and zero previous charge, summing-node charge balance gives gain magnitude

$$
\frac{v_o}{v_{in}}=\frac{r}{1+(1+r)/A}.
$$

The denominator includes the noise gain $1+r$, rather than only $1/A$. The [charge-domain note](CMOS-Inverter-Charge-Domain-Circuits.md) derives the retained state and leaky-integrator recurrence from the exact two-phase connections of P5 Fig. 10(c). That source uses an autozeroed inverter, not this floating-reservoir amplifier. A time-varying FIA substituted into a switched-capacitor loop needs phase-specific charge and dynamic feedback equations; its open-loop endpoint gain alone does not establish settling accuracy.

## Verification and implementation plan

![Independent charge and dynamic-amplifier models](figures/inverter_charge_driver_models.png)

[The script](code/razavi_sixth_batch_analysis.py) checks the dynamic endpoint against an integrated model and reproduces the illustrative plot. Design validation requires a complete transistor netlist and PDK:

- Save both rail trajectories, reservoir through-current, weighted output charge and sample-time gain across reset/release/amplify phases. Sweep input common mode, differential amplitude, reservoir/load ratio and observation time.
- Include clock overlap/skew, output sampler loading, leakage and device-to-ground parasitics. Check late-time drift and reset recovery across PVT.
- Extract offset/mismatch and decision or sampled-output noise at the actual observation time, retaining reset correlations. Compare integrated source energy with every driver and reset contribution.
- Check terminal voltages and body paths throughout switching; gain-enhancement variants need their own defined feedback, body bias and stability analysis.

The previous note's unreferenced process sizing, >90-dB gain, body-bias enhancement and cross-topology performance rankings are not supported by the reviewed source and have been removed. Further literature can support separate topology-specific studies.

## References and access

1. B. Razavi, [“Fifty Applications of the CMOS Inverter—Part 3”](https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_1_2025.pdf), *IEEE Solid-State Circuits Magazine*, Winter 2025, pp. 12–20, 159, [DOI 10.1109/MSSC.2024.3498732](https://doi.org/10.1109/MSSC.2024.3498732). Full article and original pages reviewed; FIA pp. 13–14, Figs. 4–5.
2. The original FIA paper identified in that article's bibliography, [DOI 10.1109/JSSC.2019.2960485](https://doi.org/10.1109/JSSC.2019.2960485), is a further source, not separately full-text reviewed in this batch. No additional measured claims are attributed to it here.
