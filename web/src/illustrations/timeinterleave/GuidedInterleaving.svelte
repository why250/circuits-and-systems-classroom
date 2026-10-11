<script lang="ts">
  import { freqText, nf } from '../../lib/format';
  import EditableRange from './EditableRange.svelte';
  import { lessonSteps } from './lesson';
  import { AMP, jitterOnlySnr, mismatch, read } from './model';
  import SampleTimingChart from './SampleTimingChart.svelte';
  import SpurSpectrum from './SpurSpectrum.svelte';

  const fs = 2e9;
  const bits = 14;
  const options = { fs, analogBandwidth: 20e9, thermalNoiseLsb: 0, jitter: 0, decimation: 1 };
  let stage = $state(0);
  let predictions = $state<(number | null)[]>(lessonSteps.map(() => null));
  let checks = $state<(number | null)[]>(lessonSteps.map(() => null));
  let revealed = $state(lessonSteps.map(() => false));
  let started = $state(false);
  let enabled = $state(true);
  let m = $state(2);
  let inputMHz = $state(125);
  let offsetMv = $state(2);
  let gainPct = $state(0.5);
  let skewPs = $state(2);
  let jitterMode = $state(false);
  let hoverBin = $state<number | null>(null);
  let hoverSample = $state<number | null>(null);

  const step = $derived(lessonSteps[stage]);
  const active = $derived(started && enabled);
  const mm = $derived(mismatch(m, active && stage === 2 ? gainPct / 100 : 0, active && stage === 1 ? offsetMv / 1000 : 0, active && (stage === 3 || (stage === 4 && !jitterMode)) ? skewPs * 1e-12 : 0, 0));
  const r = $derived(read(m, inputMHz * 1e6, mm, bits, 'off', { ...options, jitter: active && stage === 4 && jitterMode ? skewPs * 1e-12 : 0 }));
  // read() already returns outputSpurs in the FFT's power convention, including Nyquist.
  const relevantSpur = $derived(r.spurs.filter(s => s.kind === (stage === 1 ? 'offset' : 'image')).reduce((best, s) => s.dbc > best.dbc ? s : best, { freq: 0, dbc: -Infinity }));
  const spurText = $derived(Number.isFinite(relevantSpur.dbc) ? `${freqText(relevantSpur.freq)} · ${nf(relevantSpur.dbc, 1)} dBc` : 'No mismatch spur');
  const jitterSnr = $derived(jitterOnlySnr(r.fin, active && stage === 4 && jitterMode ? skewPs * 1e-12 : 0));
  const completed = $derived(checks.filter((answer, i) => answer === lessonSteps[i].checkAnswer).length);

  function resetExperiment() {
    m = 2; inputMHz = 125; offsetMv = 2; gainPct = 0.5; skewPs = 2; jitterMode = false;
    enabled = true; hoverBin = hoverSample = null;
  }
  function go(next: number) {
    stage = next;
    started = predictions[next] !== null;
    resetExperiment();
  }
  function predict(answer: number) {
    predictions[stage] = answer;
    started = true;
  }
</script>

<main class="guided" lang="en">
  <header class="intro">
    <div><p class="eyebrow">INTRODUCTORY EXPERIMENTS / TIME-INTERLEAVED ADC</p><h1>Let multiple ADCs take turns sampling</h1><p>You know ordinary ADCs and spectra. Change one condition at a time to connect sampling times, errors, and spectral features.</p></div>
    <div class="progress"><strong>{completed} / {lessonSteps.length}</strong><span>comprehension checks passed</span></div>
  </header>

  <nav class="steps" aria-label="Experiment steps">
    {#each lessonSteps as item, i}
      <button type="button" aria-current={stage === i ? 'step' : undefined} onclick={() => go(i)}>
        <span class="step-index">{checks[i] === item.checkAnswer ? '✓' : i + 1}</span>{item.title}
      </button>
    {/each}
  </nav>

  <div class="experiment">
    <section class="guide" aria-labelledby="step-heading">
      <div class="step-heading"><p class="eyebrow">Experiment {stage + 1} / {lessonSteps.length}</p><h2 id="step-heading">{step.title}</h2><p>{step.aim}</p></div>
      <fieldset class="prediction">
        <legend>① Predict first</legend>
        <p>{step.question}</p>
        <div class="choices">
          {#each step.choices as choice, i}
            <button type="button" aria-pressed={predictions[stage] === i} onclick={() => predict(i)}>{choice}</button>
          {/each}
          <button class="unsure" type="button" aria-pressed={predictions[stage] === -1} onclick={() => predict(-1)}>Not sure yet; let me experiment</button>
        </div>
      </fieldset>

      <section class="operate" aria-labelledby="operate-heading">
        <h3 id="operate-heading">② Run the experiment</h3>
        {#if started}<p>{step.task}</p>{:else}<p class="hint">Choose a prediction or “Not sure yet” to enable the controls. The plots currently show a baseline without mismatch.</p>{/if}
        <fieldset class="controls" disabled={!started}>
          <legend class="sr-only">Parameters for this step</legend>
          {#if stage === 0}
            <div class="switches" aria-label="Channel count">
              <button type="button" aria-pressed={m === 2} onclick={() => m = 2}>Two channels</button>
              <button type="button" aria-pressed={m === 4} onclick={() => m = 4}>Four channels</button>
            </div>
          {:else}
            <div class="switches" aria-label="Error switch">
              <button type="button" aria-pressed={!enabled} onclick={() => enabled = false}>Disable error · Baseline</button>
              <button type="button" aria-pressed={enabled} onclick={() => enabled = true}>Enable current error</button>
            </div>
            {#if stage === 1}<EditableRange id="guided-offset" min={0} max={5} step={0.1} digits={1} unit="mV" bind:value={offsetMv}>Offset RMS</EditableRange>{/if}
            {#if stage === 2}<EditableRange id="guided-gain" min={0} max={1} step={0.05} digits={2} unit="%" bind:value={gainPct}>Gain error RMS</EditableRange>{/if}
            {#if stage === 3 || stage === 4}<EditableRange id="guided-skew" min={0} max={10} step={0.1} digits={1} unit="ps" bind:value={skewPs}>Timing error RMS</EditableRange>{/if}
            {#if stage === 4}
              <div class="switches" aria-label="Timing error type">
                <button type="button" aria-pressed={!jitterMode} onclick={() => jitterMode = false}>Fixed skew</button>
                <button type="button" aria-pressed={jitterMode} onclick={() => jitterMode = true}>Random jitter</button>
              </div>
            {/if}
            <div class="switches" aria-label="Input frequency">
              <button type="button" aria-pressed={inputMHz === 125} onclick={() => inputMHz = 125}>Input ≈125 MHz</button>
              <button type="button" aria-pressed={inputMHz === 250} onclick={() => inputMHz = 250}>Input ≈250 MHz</button>
            </div>
          {/if}
          <button class="reset" type="button" onclick={resetExperiment}>Restore this step</button>
        </fieldset>
        <a class="mobile-jump" href="#guided-observations">View waveforms and spectrum ↓</a>
      </section>

      {#if started}
        <button class="reveal" type="button" aria-expanded={revealed[stage]} onclick={() => revealed[stage] = !revealed[stage]}>{revealed[stage] ? 'Hide explanation and keep observing' : 'Show explanation after observing'}</button>
      {/if}
      {#if started && revealed[stage]}
        <section class="explain" aria-labelledby="explain-heading">
          <h3 id="explain-heading">③ Explain the results</h3>
          <p class="feedback">{predictions[stage] === -1 ? 'Compare your observations with the explanation below.' : predictions[stage] === step.answer ? 'Your prediction matches this model.' : 'Revisit your prediction:'} {step.reason}</p>
          <p>{step.explanation}</p><p class="equation">{step.formula}</p>
        </section>
        <fieldset class="understanding">
          <legend>④ Change a condition and check understanding</legend><p>{step.check}</p>
          <div class="choices">{#each step.checkChoices as choice, i}<button type="button" aria-pressed={checks[stage] === i} onclick={() => checks[stage] = i}>{choice}</button>{/each}</div>
          {#if checks[stage] !== null}<p class="feedback" role="status">{checks[stage] === step.checkAnswer ? 'Correct.' : 'Think again.'} {step.checkReason}</p>{/if}
        </fieldset>
      {/if}
      <div class="step-actions">
        <button type="button" disabled={stage === 0} onclick={() => go(stage - 1)}>Previous</button>
        {#if stage < lessonSteps.length - 1}<button type="button" onclick={() => go(stage + 1)}>Next →</button>{:else}<span>Next topics: M-channel mismatch, bandwidth, and calibration</span>{/if}
      </div>
    </section>

    <section class="observations" id="guided-observations" aria-label="Observations">
      <div class="rates">
        <div><span>Total rate f_s</span><strong>2 GS/s</strong></div>
        <div><span>Per channel f_s / M</span><strong>{m === 2 ? '1' : '0.5'} GS/s</strong></div>
        <div><span>Adjacent / same-channel spacing</span><strong>0.5 / {m / 2} ns</strong></div>
      </div>
      <div class="timing-strip" aria-label="First eight ideal sampling instants">
        {#each Array.from({ length: 8 }, (_, i) => i) as i}
          <div class="tick" class:channel-b={i % m === 1} class:channel-c={i % m === 2} class:channel-d={i % m === 3}>
            <span>{String.fromCharCode(65 + i % m)}</span><b>{nf(i / 2, 1)}</b><small>ns</small>
          </div>
        {/each}
      </div>
      <p class="timing-note">The schedule above shows ideal sample times. Colors identify channels A, B{m === 4 ? ', C, D' : ''}; the waveform uses channel labels 0, 1{m === 4 ? ', 2, 3' : ''}.</p>
      <div class="chart time-view">
        <div class="cap"><span>Time domain · Channel samples and input</span><span>Actual input {freqText(r.fin)}</span></div>
        <SampleTimingChart samples={r.rawData} truth={r.truth} fin={r.fin} {fs} harmonics={{}} decimation={1} hover={hoverSample} onhover={i => hoverSample = i} channelColors={['var(--s1)', 'var(--s2)', 'var(--brand)', 'var(--bad)']} label="Guided time-domain plot: channel samples and ideal input" />
      </div>
      <div class="chart spectrum-view">
        <div class="cap"><span>Output spectrum · 0 to f_s/2</span><span>SNDR <b>{nf(r.raw.sndr, 1)} dB</b></span></div>
        <SpurSpectrum spectrum={r.raw} spurs={r.spurs} harmonics={[]} {bits} fs={r.fsOut} points={r.fftPoints} hover={hoverBin} onhover={b => hoverBin = b} label="Guided output spectrum: carrier, spurs, and noise floor" />
      </div>
      <div class="observation-readout" aria-live="polite">
        <span>{!started ? 'No-mismatch baseline · Make a prediction' : stage === 0 ? 'Ideal interleaving · Quantization remains' : !enabled ? 'Current error disabled · Quantization remains' : stage === 4 && jitterMode ? 'Random jitter · Observe the noise floor' : 'One mismatch enabled · Observe discrete spurs'}</span>
        {#if started && stage > 0}
          <strong>{stage === 4 && jitterMode ? `Jitter-only SNR ${Number.isFinite(jitterSnr) ? nf(jitterSnr, 1) + ' dB' : '∞'}` : `Predicted spur ${spurText}`}</strong>
        {/if}
      </div>
      <details class="model-notes"><summary>Experiment assumptions and plot guidance</summary>
        <p>The model reuses the project time-interleaved ADC simulation verified against a Python reference. The input is a sinusoid with amplitude {AMP} V; total rate is 2 GS/s; the ADC has {bits} bits and a ±0.5 V range. Quantization remains enabled. Thermal noise, source harmonics, and bandwidth mismatch are disabled; all channels share a 20 GHz single-pole analog bandwidth. This lesson performs neither decimation nor calibration.</p>
        <p>Mismatch controls represent RMS across channels with the channel mean removed. Two-channel relative errors have equal magnitude and opposite signs. Common gain, offset, and delay have different effects. Spur predictions are analytical; measured FFTs are affected by quantization and finite records.</p>
        <p>The FFT uses {r.fftPoints} coherently sampled points. Inputs are adjusted to nearby odd bins, so “125 / 250 MHz” are target values. Use the actual input shown in the plots. dBc is a power ratio relative to the carrier; use 20 log₁₀ for voltage-amplitude ratios.</p>
        <p>An alternating sequence at f_s/2 has RMS equal to its peak, while an ordinary sinusoid has RMS equal to peak / √2. The lesson converts analytical Nyquist-endpoint peaks to power before comparison with the FFT to avoid a 3 dB interpretation error.</p>
        <p>Random jitter uses independent Gaussian sequences with a fixed seed for repeatable comparisons. The time plot shows jitter-induced voltage changes at nominal times, rather than individual random time shifts. Fixed-skew time shifts are displayed.</p>
        <p>Each channel rate determines the Nyquist zone of its own digital sequence; analog input bandwidth is a separate constraint. Individual channels may alias, while the complete ideal interleaved sequence is evaluated using the total sampling rate.</p>
      </details>
      <a class="mobile-jump" href="#step-heading">Back to the controls ↑</a>
    </section>
  </div>
  {#if completed === lessonSteps.length}<p class="completion" role="status">You passed all five comprehension checks. Open the full workbench to try more channels and combined errors. Calibration will be covered separately in a later experiment.</p>{/if}
</main>

<style>
  .guided { max-width: 1480px; margin: 0 auto; padding: 24px 24px 36px; }
  .intro { display: flex; align-items: center; justify-content: space-between; gap: 24px; margin-bottom: 22px; }
  h1 { margin: 4px 0 8px; font-size: clamp(22px, 2.2vw, 30px); font-weight: 600; letter-spacing: -.03em; }
  p { margin: 0 0 12px; line-height: 1.75; }
  .intro p:last-child { margin: 0; color: var(--ink-2); }
  .eyebrow { margin: 0; color: var(--brand); font: 11px var(--mono); letter-spacing: .04em; }
  .progress { display: grid; gap: 4px; white-space: nowrap; text-align: right; }
  .progress strong { font: 20px var(--mono); }
  .progress span { color: var(--ink-3); font-size: 12px; }
  .steps { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; margin-bottom: 24px; }
  button { background: var(--plot); border: 1px solid var(--rule); color: var(--ink-2); padding: 8px 12px; border-radius: 5px; font: 13px/1.5 var(--sans); cursor: pointer; text-align: left; }
  button:hover:not(:disabled) { border-color: var(--ink-3); color: var(--ink); }
  button[aria-pressed='true'], button[aria-current='step'] { border-color: var(--brand); background: var(--brand-soft); color: var(--brand); }
  button:disabled { opacity: .5; cursor: default; }
  .steps button { display: flex; align-items: center; gap: 10px; }
  .step-index { font: 12px var(--mono); }
  .experiment { display: grid; grid-template-columns: minmax(340px, 420px) minmax(0, 1fr); gap: 32px; align-items: start; }
  .guide { border-top: 2px solid var(--brand); padding-top: 16px; opacity: 1; }
  .step-heading h2 { margin: 6px 0; font-size: 22px; font-weight: 550; }
  .step-heading > p:last-child { color: var(--ink-2); }
  fieldset { min-width: 0; border: 0; margin: 0; padding: 0; }
  legend, h3 { font-size: 14px; font-weight: 600; margin: 0 0 10px; padding: 0; }
  .prediction, .operate, .explain, .understanding { padding: 18px 0; border-top: 1px solid var(--rule); }
  .prediction { padding-top: 12px; }
  .prediction > p, .understanding > p { margin-top: 8px; }
  .choices { display: grid; gap: 7px; }
  .unsure { background: transparent; color: var(--ink-3); border-style: dashed; }
  .hint, .timing-note { color: var(--ink-3); font-size: 12px; }
  .controls { display: grid; gap: 12px; }
  .switches { display: flex; flex-wrap: wrap; gap: 6px; }
  .switches button { font-size: 12px; padding: 5px 10px; }
  .reset { justify-self: start; padding: 3px 0; border: 0; background: transparent; font-size: 12px; text-decoration: underline; text-underline-offset: 3px; }
  .reveal { width: 100%; text-align: center; background: var(--brand-soft); color: var(--brand); border-color: var(--brand); }
  .explain { margin-top: 20px; }
  .feedback { margin-top: 12px; color: var(--ink-2); }
  .equation { padding: 12px; background: var(--chip); font: 13px/1.8 var(--mono); overflow-wrap: anywhere; border-radius: 4px; }
  .step-actions { border-top: 1px solid var(--rule); padding-top: 18px; margin-top: 18px; display: flex; justify-content: space-between; gap: 12px; align-items: center; }
  .step-actions span { color: var(--ink-3); font-size: 12px; }
  .observations { min-width: 0; position: sticky; top: 16px; display: grid; gap: 12px; }
  .rates { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border: 1px solid var(--rule); border-radius: 5px; padding: 14px 16px; gap: 10px; }
  .rates div { display: grid; gap: 4px; }
  .rates span { color: var(--ink-3); font-size: 12px; }
  .rates strong { font: 15px var(--mono); }
  .timing-strip { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); border-bottom: 1px solid var(--rule); padding-bottom: 12px; gap: 5px; }
  .tick { display: grid; justify-items: center; gap: 2px; padding-top: 8px; border-top: 2px solid var(--s1); color: var(--s1); }
  .channel-b { color: var(--s2); border-color: var(--s2); }
  .channel-c { color: var(--brand); border-color: var(--brand); }
  .channel-d { color: var(--bad); border-color: var(--bad); }
  .tick span { font: 11px var(--mono); }
  .tick b { font: 13px var(--mono); }
  .tick small { color: var(--ink-3); font-size: 10px; }
  .timing-note { margin: -5px 0 0; }
  .time-view { height: 205px; }
  .spectrum-view { height: 265px; }
  .cap { font-size: 12px; min-height: 22px; }
  .cap b { font-size: 12px; }
  .observation-readout { border: 1px solid var(--rule); border-radius: 4px; padding: 10px 12px; display: grid; gap: 4px; font-size: 12px; color: var(--ink-2); }
  .observation-readout strong { font: 12px/1.7 var(--mono); color: var(--ink); }
  .model-notes { color: var(--ink-3); font-size: 12px; }
  summary { cursor: pointer; }
  .model-notes p { margin-top: 12px; }
  .completion { margin: 24px 0 0; padding: 16px; border: 1px solid var(--brand); color: var(--brand); border-radius: 5px; }
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
  .mobile-jump { display: none; }
  @media (max-width: 1000px) { .experiment { grid-template-columns: minmax(320px, 360px) minmax(0, 1fr); gap: 20px; } .rates { padding: 10px; } .rates strong { font-size: 12px; } }
  @media (max-width: 760px) {
    .intro { flex-direction: column; align-items: flex-start; gap: 12px; }
    .progress { display: flex; align-items: baseline; gap: 10px; text-align: left; }
    .guided { padding: 20px 20px 28px; }
    .intro { align-items: start; gap: 12px; }
    .progress strong { font-size: 16px; }
    .steps { display: flex; overflow-x: auto; padding-bottom: 5px; gap: 6px; }
    .steps button { white-space: nowrap; flex: 0 0 auto; }
    .experiment { display: flex; flex-direction: column; gap: 24px; }
    .guide, .observations { width: 100%; }
    .observations { position: static; }
    .mobile-jump { display: inline-block; font-size: 12px; color: var(--brand); margin-top: 12px; text-underline-offset: 3px; }
    .time-view { height: 190px; }
    .spectrum-view { height: 240px; }
  }
</style>
