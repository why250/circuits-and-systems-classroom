# CMOS Inverter Drivers and Power Circuits

This note connects matched voltage-mode drivers, PAM4, feedforward equalization, local-transmit cancellation and Class-D conversion. Source IDs P3–P5 refer to the fully reviewed [CMOS inverter series](CMOS-Inverter-Applications.md). Equations are independent ideal-load models; source eyes, GHz operation and power figures remain source transistor simulations.

## 1. SST drive and the power boundary

| Symbol | Meaning / units |
|---|---|
| $Z_0,R_T,R_{on}$ | One-line characteristic impedance, total source termination, inverter on-resistance (Ω) |
| $V_{DD},v_d=v_p-v_n$ | Supply and differential load voltage (V) |
| $R_L,C_L$ | Resistive/capacitive load (Ω, F) |
| $P_{src},P_L$ | Power drawn at the specified supply and delivered to the load (W) |
| $T_b,a_k$ | Symbol interval (s), signed FFE tap coefficients |

An inverter's conducting PMOS or NMOS provides a source impedance. For an initially matched single-ended line $Z_0$ and total termination $R_T=Z_0$, its launch swing is $V_{DD}Z_0/(R_T+Z_0)=V_{DD}/2$. A differential SST bridge drives a $2Z_0$ load through two $R_T=Z_0$ paths. For a held complementary symbol,

$$
I=\frac{V_{DD}}{2R_T+2Z_0}=\frac{V_{DD}}{4Z_0},\qquad
P_{src}=\frac{V_{DD}^2}{4Z_0},\qquad P_L=\frac{V_{DD}^2}{8Z_0}.
$$

Differential output levels are $\pm V_{DD}/2$, so differential **peak-to-peak** swing is $V_{DD}$. The ideal resistive driver efficiency is 50%; this says nothing about the predriver or switching energy [P3, pp. 15–17, Figs. 8–9]. The source's CML comparison draws $V_{DD}^2/Z_0$ for its particular swing/current definition, giving a fourfold driver-core advantage. It is not a general fourfold complete-transmitter reduction.

At $V_{DD}=0.95$ V and $Z_0=50$ Ω, the ideal full-swing SST bridge draws 4.5125 mW, while that CML comparison draws 18.05 mW. P3 reports **4 mW including its predriver**. This is below the ideal held-symbol matched-bridge value; nonlinear resistance, actual load swing and averaging/budget definitions must be resolved before equating the source number with the ideal benchmark.

A physical $R_S=25$ Ω plus inverter $R_{on}=25$ Ω can reduce termination variability relative to an all-MOS 50-Ω target, at the cost of larger gates and predriver power. Reflection coefficient is $\Gamma_S=(R_T-Z_0)/(R_T+Z_0)$ in the linear impedance model; a signal-dependent $R_{on}$ makes termination time/code dependent. Sweep supply, corners, output level and both edge polarities.

## 2. PAM4 weights must include channel loading

P3 pp. 16–17, Fig. 10 combines MSB and LSB inverter outputs through impedances $1.5Z_0$ and $3Z_0$. With binary rail voltages $b_MV_{DD},b_LV_{DD}$ and matched channel load $Z_0$, KCL gives

$$
\boxed{v_o=V_{DD}\frac{2b_M+b_L}{6}}.
$$

The four single-ended levels are $0,V_{DD}/6,V_{DD}/3,V_{DD}/2$. The source resistance is $(1.5Z_0)\parallel(3Z_0)=Z_0$. A complementary opposite leg yields differential levels $-V_{DD}/2,-V_{DD}/6,+V_{DD}/6,+V_{DD}/2$; adjacent differential spacing is $V_{DD}/3$. Omitting channel conductance would give twice the single-ended swing.

MOS output resistance is nonlinear; source Fig. 11 shows unequal eye heights and suggests strengthening the LSB path by about 10%. That is a source-specific adjustment, not a general binary-weight correction. Include switching glitches, skew, code-dependent impedance and gain calibration. Source “112 Gb/s” is **56 Gbaud PAM4**, with two 56-Gb/s binary streams. It is not a 112-GHz symbol clock.

P5 pp. 12–13, Fig. 8 instead uses resistive-feedback inverters with bipolar current-steering DACs. For an isolated high-impedance input source, input follows output at low frequency and output conductance is $G_m+g_o$, giving $R_{out}=1/(G_m+g_o)$. With finite input-source conductance $g_s$,

$$
Y_{out}=g_o+g_F+(G_m-g_F)\frac{g_F}{g_s+g_F}.
$$

A low-impedance preceding source suppresses feedback, so $R_{out}$ can be much larger than $1/G_m$. Match the actual driven structure, not a floating-input test. DAC current must include positive and negative values to retain complementary output/common mode; NMOS-only zero-to-positive current is insufficient.

For load $Z_0$, replace output resistance by $r_o\parallel Z_0$ in the [feedback input model](CMOS-Inverter-Analog-Front-Ends.md). Its input time constant approximately equals $C_{in}(R_F+r_o\parallel Z_0)/[1+G_m(r_o\parallel Z_0)]$, as in P5 Eq. (4). Source 112-Gb/s eye and 3.4 mW do not establish a flat output termination versus frequency.

## 3. Analog FFE is a waveform filter

P3 pp. 19–20 and p. 159, Figs. 16–17 forms delayed replicas with inverter chains, using crossed differential paths for negative taps. Its ideal waveform filter is

$$
y(t)=\sum_k a_kx(t-kT_b),\qquad H_{FFE}(\omega)=\sum_k a_ke^{-j\omega kT_b}.
$$

The channel symbol response must be sampled from a **pulse response at the decision phase**. For normalized illustrative taps $h=[1,0.08,0.03]$ and FFE $a=[1,-0.08]$, convolution gives $[1,0,0.0236,-0.0024]$. Canceling the first postcursor leaves later ISI. An impulse-response graph alone does not identify the NRZ pulse taps without pulse shaping and sample timing.

P3 mentions an 8% postcursor but implements a −12.5% drive-strength ratio and about 17-ps inverter-chain delay at 56 Gb/s. The actual UI is 17.857 ps. These are source optimized choices, not the exact discrete filter above. Loaded nonlinear driver strength is not automatically a linear tap coefficient. PVT changes both analog delay and coefficient; the useful residual compensation must be evaluated with eyes/BER and the actual channel model.

## 4. Bidirectional hybrid and delay matching

P5 pp. 16–17, Fig. 18 drives a line with total source termination $R_{on}+R_T\approx Z_0$. The local line node A contains attenuated local TX plus the desired remote TX. Feed a complementary local replica through $R_2$ and A through $R_1$ into resistive-feedback receive inverter Inv4, whose input B approximates a virtual ground. With local voltage transfer $a$ to A and complementary replica transfer $-b$,

$$
i_{B,local}=\left(\frac{a}{R_1}-\frac{b}{R_2}\right)v_{TX},\qquad
\frac{R_2}{R_1}=\frac{b}{a}
$$

for ideal cancellation. A matched initial launch suggests $a\approx1/2$ and full-rail replica $b\approx1$, hence $R_2\approx2R_1$. Source $R_1=600$ Ω and $R_2=1.4$ kΩ account for its actual loaded paths; they are not exact ratios for every frequency. The series sensing path also loads A, so its resistance should be large relative to the line impedance.

After perfect DC gain trim, relative delay $\delta t$ leaves normalized residual $1-e^{-j\omega\delta t}\approx j\omega\delta t$. With relative replica gain error $\epsilon$,

$$
\frac{v_{res}}{v_{local}}\approx-\epsilon+j\omega\delta t.
$$

Timing cancellation gets harder at high frequency even when resistor cancellation is accurate. The final transmission-gate replica in **Fig. 18(d)** replaces the two-inverter cascade of (c); prose references (c) again, which is a source figure-reference error. Fig. 19 reports a residual about 20 mVpp plus glitches; this is not complete suppression or a quantified echo-cancellation bandwidth. Independent local/remote patterns, skew, line reflections and PVT must be tested.

## 5. Class-D: differential waveform, loss and distortion

P4 pp. 15–17, Fig. 18 makes two complementary inverter legs into an H-bridge. For an ideal triangle spanning $V_{min},V_{max}$ and a comparator output high when $v_{in}>v_{tr}$, slowly varying input produces

$$
D=\frac{v_{in}-V_{min}}{V_{max}-V_{min}},\qquad
\overline v_{diff}=V_{DD}(2D-1)
$$

for the chosen bridge polarity and unclipped input. The LC network suppresses PWM switching components. With two equal inductors $L$ and capacitors $C$ to ground, odd-mode load is $R_L/2$ per leg and the unloaded resonance is $1/(2\pi\sqrt{LC})$. Source $L=10$ μH, $C=100$ nF give 159.15 kHz, between its 20-kHz signal and 2-MHz PWM carrier. Include load damping and capacitor/inductor parasitics rather than assuming ideal unity signal gain.

Conduction loss is approximately $I_{rms}^2(R_{on,p}+R_{on,n})$ across the conducting bridge diagonal. Switching loss includes gate charging, overlap/crowbar current, parasitic capacitance, dead-time distortion and filter loss. Low $R_{on}$ requires large gates; reducing it alone does not optimize total efficiency.

**Source swing qualification:** P4 p. 16 calls the load's differential swing 750 mVpp and reports 35-mW output/45-mW supply power. A sinusoidal **750-mVpp differential** voltage into 8 Ω delivers only

$$
P_L=V_{pp,diff}^2/(8R_L)=8.789\text{ mW}.
$$

Its Fig. 19(b) plots two complementary **leg voltages**, each about 750 mVpp. Their difference is about 1.5 Vpp and delivers 35.156 mW, consistent with the reported power. Read the plot as two leg signals and preserve the prose discrepancy; do not treat 750 mVpp differential as 35 mW. Reported efficiency $35/45=77.78\%$ is consistent with that differential interpretation. The third harmonic at −64 dBc is a source spectral observation, not −100-dB total audio distortion. Closed-loop linearization still requires stability, dead time and load tests.

## 6. Verification

![Independent charge and driver models](figures/inverter_charge_driver_models.png)

The [analysis script](code/razavi_sixth_batch_analysis.py) checks PAM4 KCL, fixed-symbol bridge power against resistor dissipation, pulse-tap convolution and Class-D differential arithmetic. The plotted hybrid model uses illustrative 1% gain error/0.5-ps skew, not the source transient. No channel EM extraction, transistor eye/BER or power-stage simulation was performed. Full source qualifications are in the [sixth-batch record](sources/razavi-sixth-batch-verification.md).
