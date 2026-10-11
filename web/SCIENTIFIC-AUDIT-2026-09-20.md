# Main-site scientific and computational audit

Date: 2026-09-20. Audit baseline: `2ac7385`. During the audit, the independent interleaved-ADC UI update `a111081` entered the main branch. Final verification retained that UI update and the corrected computational models.

The scope was the lessons listed on the [Circuits & Systems Classroom](https://circuits-and-systems.tokenzhang.com/) homepage at the time, plus the external Bode tool. Tutorials on the old domain redirect here. Experimental pages absent from the homepage and the complete ADCToolbox Python library were outside the comprehensive audit scope.

Conclusion: the basic theory was largely correct, but the original version could not be considered entirely computationally correct or rigorously worded. Errors significantly changed readings, and some simplified models or empirical metrics were presented as rigorous conclusions. The on-site issues below were addressed in this revision. The external tool still has a known marginal-stability classification issue.

## Findings by entry

| Homepage entry | Audit finding | Revision |
|---|---|---|
| Aliasing and Nyquist zones | Frequency folding, actual retained sample times, and coherent-sampling calculations were correct | Qualified real-signal phase mirroring, ideal sinusoidal sample equivalence, harmonic locations versus spurs, and the baseline for per-bin noise increase |
| Binary vs redundant SAR | Ideal successive approximation, weight reconstruction, independent training/testing, and the basic mismatch model were valid; the "unrecoverable fraction" interpretation was invalid | Renamed it "fraction of inputs with analog DAC error exceeding 1 LSB"; corrected remaining ranges and full-scale ideal codes; explained one-sided redundancy recovery |
| Analog output analysis panel | Harmonic phase calculation was wrong, with other misleading diagnostic displays; the browser version was not numerically equivalent to every Python dashboard case | Corrected phase signs, Nyquist mirroring, and initial transients in linear settling; retained glitches in the PDF; removed invented harmonic labels for a new residual fundamental; clarified code units and model origins |
| Time-interleaved ADCs | Arbitrary-factor decimation shortened the record to `ceil(4096/D)`, causing severe leakage and poor frequency resolution; spur markers used the wrong channel sequence | Analyze 4096 retained samples at each output rate; recompute spurs from the actual visited channel sequence and verify predicted markers against FFT lines |
| Integer-N vs fractional-N | Frequency equations, basic loop implementation, and noise dimensions were valid; the dBc denominator was inexact and important model conditions were missing | Normalize spectra to the actual carrier; state finite word length, reference-rate behavioral model, noise assumptions, jitter readings, and spur thresholds |
| Bode plots & stability (external link) | Sampled magnitude/phase and time responses were correct; marginal-stability classification was not rigorous | Retained the link with qualified homepage wording; external source code was not changed; counterexamples follow |

## 1. Interleaved ADC: record length and spurs after decimation

For a 4096-point, 12-bit, 0.4 V peak sinusoid at 1 GS/s, targeting about 100 MHz, with no channel mismatch and only quantization plus 0.3 LSB rms thermal noise:

| Decimation factor | Original output points | Original SNDR | Corrected output points and SNDR |
|---|---|---|---|
| 1 | 4096 | 68.786 dB | 4096 points, about 68.9 dB |
| 3 | 1366 | **8.477 dB** | 4096 points, about 68.9 dB |
| 5 | 820 | **4.695 dB** | 4096 points, about 68.9 dB |
| 17 | 241 | **14.774 dB** | 4096 points, about 68.9 dB |

The independent noise budget is

`SNR = 10 log10[(0.4²/2) / ((1/12 + 0.3²)/4096²)] ≈ 68.9 dB`.

The original implementation generated only 4096 high-rate samples and retained every Dth sample, leaving `ceil(4096/D)` points for the output FFT. When D did not divide 4096, the truncated record was no longer coherent; the window spread carrier, interleaving spurs, and harmonics. Although sinusoidal fitting could recover nearly correct SNDR values, a spectrum with only a few dozen points lacked resolution and could not visually align prediction markers with lines.

The revision analyzes 4096 output samples for every D: high-rate ADC samples `0, D, 2D, …, 4095D`. For this memoryless converter model, computing those samples directly is exactly equivalent to generating `4096D` points and discarding intermediate ones. It also avoids generating more than a million unused points during each slider update at D=255. The input is coherent within that record, so a 4096-point rectangular-window FFT is used throughout. Output rate remains `fs/D`; inputs, harmonics, interleaving spurs, and broadband noise all fold through direct decimation without an antialias filter.

New assertions cover D=1, 2, 3, 17, 53, 63, 127, 255: FFT length stays 4096 and the fundamental bin is `fold(KD,4096)`. Line-by-line checks at D=53, M=8 also verify predicted interleaving-spur frequencies and dBFS against actual FFT lines.

Another issue was channel selection after decimation. Retained samples come from `c = kD mod M`, visiting only `M/gcd(M,D)` channels. The original implementation folded spur frequencies without first adding complex amplitudes, so it still drew mismatch spurs when D=M. The revision forms the actual visited channel sequence and takes its DFT. With only one channel retained, static mismatch becomes fixed gain, phase, and DC rather than interleaving spurs.

New tests take FFTs of analytical mismatch waveforms directly and verify spur frequencies, powers, and carrier ratios for D=1, 2, 3, 4, 5, 8, including the doubled mean-square power at Nyquist for the same peak amplitude.

## 2. Analog analysis panel: harmonic phase and diagnostic scope

The phase convention is `A cos(ωt + φ)`. For a fit `a cos(ωt) + b sin(ωt)`, use `φ = atan2(-b,a)`, not `atan2(b,a)`. Relative harmonic phase is `φh − hφ1`.

For a known two-tone signal with φ1=0.37 rad and φh=0.81 rad:

| Component | Correct relative phase | Original decomposition plot | Original FFT polar plot | Both corrected plots |
|---|---|---|---|---|
| H2 | 0.07 rad | −0.07 | 0.07 | 0.07 |
| H5 (above Nyquist) | −1.04 rad | 1.04 | −2.66 | −1.04 |

Conjugate the mirrored H5 spectral coefficient before calculating relative phase. The polar plot now shows phases only for clearly identified harmonic orders, avoiding a mixture of absolute noise-bin phases and relative harmonic phases.

Other changes:

- Warm up the linear settling model so startup transients are not called steady-state distortion. With all independent error controls at zero, sinusoidal-fit residuals are below 1e−8 LSB.
- Extend the PDF x-axis over all error samples. The old ±3.5 rms range omitted rare large glitches; new assertions ensure all 4096 samples enter the histogram.
- Retain all sampled points in the phase plane to prevent uniformly spaced display subsampling from skipping glitches. Axis ticks adapt to the actual range under large errors.
- Stop calling the largest residual/envelope spectral peak the "input" or inventing H2–H5 from it.
- Rename "Resolution" to "Code scale": this control converts a 1 V full-scale range to LSBs; it does not automatically add a quantizer with that bit depth to every model.
- State that the page is a 4096-point browser adaptation using known-frequency fitting. Drift, noncoherent AM, fixed quantization levels, and simplified diagnostic plots prevent claims of case-by-case numerical equivalence to Python's 65536-point batch examples.

These are fault-signature examples. One error plot cannot uniquely identify a circuit fault, and AM/PM variance decomposition is not a unique identification method for arbitrary nonlinearities and mixed noise.

## 3. SAR: an error threshold is not unrecoverable information

The original `lostInputs` measured `|x − Σ(actual_weight × decision)| > 1 LSB`. This does not prove that "no digital weights can repair the result."

Counterexample: two actual weights `[2.8,1]` and a decision bias of +0.5 LSB. Bit string `01` corresponds to inputs in `[0.5,2.3)`. At input 2.125, analog DAC reconstruction is 1, an error of 1.125 LSB. Assigning digital reconstruction 1.4 to this bit string reduces the error to 0.725 LSB, with maximum error across the entire interval no greater than 0.9 LSB.

The actual limitation is that digital postprocessing cannot create new observations inside an input interval sharing the same decision code. Excessively wide intervals limit recoverable resolution; the "fraction with analog reconstruction error >1 LSB" alone does not measure that information limit.

This revision:

- Corrected the meaning of the fraction, shading, summaries, and comments.
- Changed remaining DAC ranges to bounds after the current decision and clarified that they are only an outer envelope, not a guarantee of no internal gaps.
- Made final-bit decision errors visible in range plots and saturated full-scale ideal codes at `2^N−1`.
- Explained that this unipolar, positive-weight accumulation search mainly tolerates false rejections; it cannot subtract an already falsely accepted weight. The final stage has no later weights for recovery.

Also verified point-by-point rounding for both ideal arrays, independent training/test records, coherent test frequencies, and the jitter approximation `−20 log10(2πfinσt)`. Across 450 noiseless combinations of 5 bit depths, 3 training lengths, 3 mismatch levels, 5 chip instances, and 2 arrays, calibrated weights were finite. This does not guarantee identifiability for arbitrary rank-deficient training data. ENOB uses the displayed `(SNDR−1.76)/6.02` without compensation for the −0.5 dBFS input amplitude.

## 4. PLL: correct shaping order, incorrect dBc denominator

MASH was checked using independent closed-form remainder relationships rather than the same carry-update code. With `M=2^24`, input word F, and zero initial state:

`r3[k] = F (k+1)(k+2)(k+3)/6 mod M`, `e3[k] = −r3[k]/M`.

Verified sample by sample:

- `y[k]−α = Δ³e3[k]`: third-order shaping of the divider word.
- `Σ(y[k]−α) = Δ²e3[k]`: second-order shaping of accumulated phase.
- A first-order accumulator has accumulated error `−r1[k]/M`, bounded but without a remaining difference-shaping factor.

An accumulator is therefore a first-order delta-sigma implementation, not a parallel unrelated concept. Rational control words without dither produce deterministic sequences; they do not guarantee smaller spurs at every frequency than a first-order implementation.

The old PLL spectrum divided `exp(jφ)` sideband power by unit total power but labeled the result dBc relative to the actual carrier. Strong phase modulation attenuates the carrier, making the difference substantial. The denominator is now measured carrier power `|Σw exp(jφ)/Σw|²`. The Python comparison script received the same correction; jitter values do not change as a result.

Independent analytical verification: for φ(t)=βcos(ωmt), carrier amplitude is J0(β) and the first sideband is J1(β). A β=0.8 rad test checks carrier power, `20log10|J1/J0|`, and jitter `β/(2πfout√2)`. White phase noise is compared against `L=σφ²/fref` to check for factor-of-two errors in one-sided phase-noise power.

Typical output at 5.005 GHz, 40 MHz reference, and 1 MHz bandwidth: browser integer-mode jitter=188.30 fs and MASH=2682.42 fs; independent Python random sequences give 188.1 fs and 2681.7 fs. Differences are consistent with random noise sampling. In a hidden strong-modulation accumulator test, the old −4.68 dB "sideband/total power" becomes about +12.48 dBc "sideband/remaining carrier." A positive value does not imply extra total power.

The page now states 24-bit frequency steps, linear phase detection/behavioral loop, white reference noise and VCO 1/f² assumptions, no DTC/CP mismatch, finite-record detrended jitter, and spur detection thresholds. It is not a transistor-level PLL simulation and does not guarantee a chip's accuracy.

## 5. Aliasing: correct values require qualified comparisons

- Checked `|f − fs round(f/fs)|`, actual retained times, and consistent folding of harmonics 2 and 3.
- Real-signal spectra at `f` and `−f` require conjugation. Sampling equivalence of ideal aliased sinusoids does not mean samples containing quantization, distortion, and thermal noise lie exactly on the ideal curve.
- The output FFT here is always 4096 points. Relative to the original `D×4096`-point FFT of the same capture, per-bin noise rises by about `10log10(D)`. Across different D values with 4096-point output spectra, white-noise power per bin should remain roughly unchanged. Both comparisons were verified.
- H2/H3 controls set polynomial coefficients relative to the undistorted sinusoidal amplitude. The cubic term also changes the fundamental, so measured dBc may differ slightly. Coincident frequencies require complex-amplitude addition.

## 6. External Bode tool: known unresolved issue

Target: [many-question/bode-sketch v1.5](https://many-question.github.io/bode-sketch/). HTML retrieved on 2026-09-20 had SHA-256 `07cbc4f501573909d3a5ad39cd216c540b2765121be6d098554a3df06ea28da7`. Conclusions apply to that version.

Spot checks of calculation functions in the actual online script:

| Transfer function / test | Result |
|---|---|
| `H(s)=1/(s+1)`, ω=1 rad/s | −3.010300 dB, −45°; correct |
| Step response of the same system at t=1, 2 s | 0.632120559, 0.864664717; matches `1−exp(−t)` |
| Step response of `H(s)=1/(s+1)²` | Matches `1−(1+t)exp(−t)` |
| `H(s)=(s−1)/(s+1)` | Constant 0 dB magnitude and correct RHP-zero phase |
| Unity negative-feedback open loop `L(s)=10/(s+1)³` | Correctly identifies two RHP closed-loop poles |
| Unity negative-feedback open loop `L(s)=2/(s−1)` | Correctly identifies a stable closed loop |
| **`L(s)=8/(s+1)³`** | **Incorrectly labeled stable**; characteristic polynomial `(s+3)(s²+3)` has poles ±j√3. This marginal case is not asymptotically/BIBO stable |
| **`L(s)=1/s²`** | **Incorrectly labeled stable**; closed loop `1/(s²+1)` has poles ±j |

The classification primarily computes `Z=N+P` and displays stable when `Z===0`, without reliably detecting boundary cases where the curve passes through −1 or closed-loop poles lie on the imaginary axis. A finite 420-point frequency sample is also not rigorous proof of stability for arbitrary high-order or narrow-resonance systems.

No third-party repository was changed or received a submission. The homepage link now notes that marginal stability requires independent checking. The tool remains suitable for exploring magnitude, phase, poles, zeros, and responses, but should not be used for stability sign-off.

## Verification and boundaries

- Added 26 analytical/physical-invariant checks in `tests/scientific-audit.test.ts` covering the six on-site entries above.
- Passed 242 model tests, Astro/Svelte/Worker type checks, and static build.
- Passed the 15 reference scripts in `python .github/toolbox-drift.py`. Expected output was updated only after explaining and verifying the PLL carrier-normalization change.
- Used an actual browser to inspect six on-site pages, decimation controls, abnormal-sample displays, and the production build. Preserved visitor analytics, MIT License, and navigation.

This is an audit of public teaching models and important boundary conditions, not a formal proof over an infinite input space. Model validity conditions were added to the lessons. Actual ADC nonlinearity, time-varying errors, alias collisions, calibration identifiability, and actual PLL device noise still need verification under specific measurement conditions.
