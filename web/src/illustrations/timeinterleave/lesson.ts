/** The introductory experiments reuse model.ts; this file holds only the teaching sequence. */
export interface LessonStep {
  title: string;
  aim: string;
  question: string;
  choices: string[];
  answer: number;
  reason: string;
  task: string;
  explanation: string;
  formula: string;
  check: string;
  checkChoices: string[];
  checkAnswer: number;
  checkReason: string;
}

export const lessonSteps: LessonStep[] = [
  {
    title: 'Taking turns',
    aim: 'Combine two ADC sampling schedules into one uniform sequence.',
    question: 'Two ADCs each run at 1 GS/s, with sampling times offset by 0.5 ns. What is the combined sampling rate?',
    choices: ['1 GS/s', '2 GS/s', '4 GS/s'], answer: 1,
    reason: 'Each channel samples every 1 ns. Alternating the two gives a new sample every 0.5 ns, or 2 GS/s.',
    task: 'Switch from two channels to four. Keep the total rate at 2 GS/s and observe the per-channel rate and spacing between samples from the same channel.',
    explanation: 'The spacing between adjacent combined samples determines the total rate. With M uniformly interleaved channels, each channel operates once every M total-clock periods. Four channels need only 0.5 GS/s each; every analog front end must still respond to the input frequency.',
    formula: 'f_channel = f_s / M; t_c[k] = (kM + c) / f_s',
    check: 'If each channel stays at 1 GS/s and you expand from two channels to four, what is the total rate?',
    checkChoices: ['1 GS/s', '2 GS/s', '4 GS/s'], checkAnswer: 2,
    checkReason: 'This question fixes the per-channel rate, so the total is 4 × 1 GS/s = 4 GS/s. The experiment above fixes the total rate.',
  },
  {
    title: 'Offset mismatch',
    aim: 'Identify periodic error that does not depend on input frequency.',
    question: 'The two channels have offsets of +2 mV and −2 mV. How does the mismatch spur location change with input frequency?',
    choices: ['It follows the input', 'It stays at half the total sampling rate', 'It only raises the noise floor'], answer: 1,
    reason: 'Alternating +Δo and −Δo repeats every two samples, corresponding to half the total sampling rate.',
    task: 'Enable the error and compare inputs near 125 MHz and 250 MHz. Find the 1 GHz spur, then disable the error for comparison.',
    explanation: 'Two-channel offset mismatch forms e[n] = Δo·(−1)ⁿ. This alternating sequence is independent of the input, so its frequency stays at f_s/2. Relative offsets in M channels repeat every M samples and can produce spurs at k·f_s/M; amplitudes depend on the actual channel offsets.',
    formula: 'Two channels: e[n] = Δo·(−1)ⁿ → f_spur = f_s/2',
    check: 'What mainly appears if both channels have the same +2 mV offset instead of opposite offsets?',
    checkChoices: ['A DC shift', 'An interleaving spur at f_s/2', 'Random noise'], checkAnswer: 0,
    checkReason: 'A common offset is identical across all samples and mainly appears as DC. Interleaving spurs come from relative offsets between channels.',
  },
  {
    title: 'Gain mismatch',
    aim: 'Observe how periodic gain error shifts the input spectrum.',
    question: 'The channel gains are 1 + ε and 1 − ε. What happens to the interleaving spur when the input changes from about 125 MHz to 250 MHz?',
    choices: ['It stays at 1 GHz', 'It moves from about 875 MHz to 750 MHz', 'It moves from about 125 MHz to 250 MHz'], answer: 1,
    reason: 'Alternating gain error modulates the input by (−1)ⁿ, creating images at f_s/2 ± f_in. Folding into the first Nyquist zone gives f_s/2 − f_in.',
    task: 'Keep gain mismatch fixed and switch between the two input frequencies. Compare image-spur position and amplitude in dBc.',
    explanation: 'Gain error multiplies the input: e[n] = ε·(−1)ⁿ·x[n]. For this two-channel sinusoidal experiment with small mismatch, image amplitude relative to the carrier is approximately ε. Changing input frequency therefore mainly moves the spur; its amplitude in dBc stays nearly constant.',
    formula: 'f_spur = f_s/2 − f_in; L_spur ≈ 20 log₁₀|ε| dBc',
    check: 'If relative gain error ε is halved, how much does the image spur change in dBc?',
    checkChoices: ['Down 3 dB', 'Down 6 dB', 'Position changes, amplitude stays fixed'], checkAnswer: 1,
    checkReason: 'Halving spur voltage gives 20 log₁₀(1/2) ≈ −6.02 dB. Input frequency is unchanged, so the location stays fixed.',
  },
  {
    title: 'Timing mismatch',
    aim: 'Use input slope to explain sensitivity at higher input frequencies.',
    question: 'The channels have fixed sampling offsets +Δt and −Δt. With Δt fixed, how does doubling input frequency change the spur?',
    choices: ['Down 6 dB', 'Nearly unchanged', 'Up 6 dB'], answer: 2,
    reason: 'A small timing error produces voltage error approximately Δt·dx/dt. Sinusoidal slope amplitude is proportional to input frequency, so doubling frequency approximately doubles error amplitude.',
    task: 'Keep timing mismatch at 2 ps and compare inputs near 125 MHz and 250 MHz. Observe spur dBc, then reduce or disable the mismatch.',
    explanation: 'Fixed channel timing mismatch also repeats every two samples, so its image location matches gain mismatch. The amplitude differs: for 2πf_in|Δt| ≪ 1, the relative spur amplitude is approximately 2πf_in|Δt|. Increasing input frequency increases error, giving nearly 6 dB between these two frequencies.',
    formula: 'e[n] ≈ Δt_c·x′(t_n); L_spur ≈ 20 log₁₀(2πf_in|Δt|) dBc',
    check: 'If input frequency doubles while timing mismatch is halved, how does spur dBc change?',
    checkChoices: ['Nearly unchanged', 'Up 6 dB', 'Down 6 dB'], checkAnswer: 0,
    checkReason: 'For small errors, amplitude depends on f_in·Δt. Doubling one and halving the other keeps the product fixed.',
  },
  {
    title: 'Skew and jitter',
    aim: 'Distinguish fixed periodic timing mismatch from random clock jitter.',
    question: 'If fixed channel skew is replaced by independent random jitter with the same 2 ps RMS, what mainly changes in the spectrum?',
    choices: ['A single clear interleaving image remains', 'A distributed noise floor appears', 'Only a DC shift appears'], answer: 1,
    reason: 'Fixed skew repeats by channel and creates discrete spurs. Jitter in this experiment is independent and random for each sample, mainly producing broadband noise.',
    task: 'Switch between fixed skew and random jitter to compare discrete images with the noise floor. Then change input frequency and observe SNDR.',
    explanation: 'This experiment uses zero-mean Gaussian aperture jitter independent from sample to sample. Its voltage error also depends on input slope, but it has no fixed channel period. The small-jitter sinusoidal approximation gives jitter-only SNR = −20 log₁₀(2πf_inσ_t). Real clocks can also have periodic jitter or correlated phase noise, producing different spectra.',
    formula: 'SNR_jitter ≈ −20 log₁₀(2πf_inσ_t)',
    check: 'Do discrete sidebands caused by timing error necessarily prove channel skew?',
    checkChoices: ['Yes, all jitter is white noise', 'No, periodic clock jitter can also produce discrete sidebands'], checkAnswer: 1,
    checkReason: 'Spectral features are diagnostic clues. Check frequency patterns and their dependence on channel count and input frequency. Independent random jitter is only the model used here.',
  },
];
