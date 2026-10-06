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
  const spurText = $derived(Number.isFinite(relevantSpur.dbc) ? `${freqText(relevantSpur.freq)} · ${nf(relevantSpur.dbc, 1)} dBc` : '当前无失配杂散');
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

<main class="guided" lang="zh-CN">
  <header class="intro">
    <div><p class="eyebrow">入门实验 / TIME-INTERLEAVED ADC</p><h1>让多路 ADC 轮流采样</h1><p>你已经了解普通 ADC 和频谱。接下来每次只改变一个条件，把采样时刻、误差和频谱连起来。</p></div>
    <div class="progress"><strong>{completed} / {lessonSteps.length}</strong><span>理解检查通过</span></div>
  </header>

  <nav class="steps" aria-label="实验步骤">
    {#each lessonSteps as item, i}
      <button type="button" aria-current={stage === i ? 'step' : undefined} onclick={() => go(i)}>
        <span class="step-index">{checks[i] === item.checkAnswer ? '✓' : i + 1}</span>{item.title}
      </button>
    {/each}
  </nav>

  <div class="experiment">
    <section class="guide" aria-labelledby="step-heading">
      <div class="step-heading"><p class="eyebrow">实验 {stage + 1} / {lessonSteps.length}</p><h2 id="step-heading">{step.title}</h2><p>{step.aim}</p></div>
      <fieldset class="prediction">
        <legend>① 先预测</legend>
        <p>{step.question}</p>
        <div class="choices">
          {#each step.choices as choice, i}
            <button type="button" aria-pressed={predictions[stage] === i} onclick={() => predict(i)}>{choice}</button>
          {/each}
          <button class="unsure" type="button" aria-pressed={predictions[stage] === -1} onclick={() => predict(-1)}>还不确定，先做实验</button>
        </div>
      </fieldset>

      <section class="operate" aria-labelledby="operate-heading">
        <h3 id="operate-heading">② 做实验</h3>
        {#if started}<p>{step.task}</p>{:else}<p class="hint">先选一个预测，或选择“还不确定”，即可查看实验操作。图表目前是无失配的基线。</p>{/if}
        <fieldset class="controls" disabled={!started}>
          <legend class="sr-only">本步实验参数</legend>
          {#if stage === 0}
            <div class="switches" aria-label="通道数">
              <button type="button" aria-pressed={m === 2} onclick={() => m = 2}>两路</button>
              <button type="button" aria-pressed={m === 4} onclick={() => m = 4}>四路</button>
            </div>
          {:else}
            <div class="switches" aria-label="误差开关">
              <button type="button" aria-pressed={!enabled} onclick={() => enabled = false}>关闭误差 · 对照</button>
              <button type="button" aria-pressed={enabled} onclick={() => enabled = true}>开启当前误差</button>
            </div>
            {#if stage === 1}<EditableRange id="guided-offset" min={0} max={5} step={0.1} digits={1} unit="mV" bind:value={offsetMv}>失调 RMS</EditableRange>{/if}
            {#if stage === 2}<EditableRange id="guided-gain" min={0} max={1} step={0.05} digits={2} unit="%" bind:value={gainPct}>增益误差 RMS</EditableRange>{/if}
            {#if stage === 3 || stage === 4}<EditableRange id="guided-skew" min={0} max={10} step={0.1} digits={1} unit="ps" bind:value={skewPs}>时间误差 RMS</EditableRange>{/if}
            {#if stage === 4}
              <div class="switches" aria-label="时间误差类型">
                <button type="button" aria-pressed={!jitterMode} onclick={() => jitterMode = false}>固定 skew</button>
                <button type="button" aria-pressed={jitterMode} onclick={() => jitterMode = true}>随机 jitter</button>
              </div>
            {/if}
            <div class="switches" aria-label="输入频率">
              <button type="button" aria-pressed={inputMHz === 125} onclick={() => inputMHz = 125}>输入 ≈125 MHz</button>
              <button type="button" aria-pressed={inputMHz === 250} onclick={() => inputMHz = 250}>输入 ≈250 MHz</button>
            </div>
          {/if}
          <button class="reset" type="button" onclick={resetExperiment}>恢复本步参数</button>
        </fieldset>
        <a class="mobile-jump" href="#guided-observations">查看波形与频谱 ↓</a>
      </section>

      {#if started}
        <button class="reveal" type="button" aria-expanded={revealed[stage]} onclick={() => revealed[stage] = !revealed[stage]}>{revealed[stage] ? '收起解释，继续观察' : '我已观察，查看解释'}</button>
      {/if}
      {#if started && revealed[stage]}
        <section class="explain" aria-labelledby="explain-heading">
          <h3 id="explain-heading">③ 解释结果</h3>
          <p class="feedback">{predictions[stage] === -1 ? '把实验结果与下面的解释对照。' : predictions[stage] === step.answer ? '你的预测与这个模型一致。' : '可以回看你的预测：'} {step.reason}</p>
          <p>{step.explanation}</p><p class="equation">{step.formula}</p>
        </section>
        <fieldset class="understanding">
          <legend>④ 换个条件，检验理解</legend><p>{step.check}</p>
          <div class="choices">{#each step.checkChoices as choice, i}<button type="button" aria-pressed={checks[stage] === i} onclick={() => checks[stage] = i}>{choice}</button>{/each}</div>
          {#if checks[stage] !== null}<p class="feedback" role="status">{checks[stage] === step.checkAnswer ? '答对了。' : '再想一想。'} {step.checkReason}</p>{/if}
        </fieldset>
      {/if}
      <div class="step-actions">
        <button type="button" disabled={stage === 0} onclick={() => go(stage - 1)}>上一步</button>
        {#if stage < lessonSteps.length - 1}<button type="button" onclick={() => go(stage + 1)}>下一步 →</button>{:else}<span>下一阶段：M 路失配、带宽与校准</span>{/if}
      </div>
    </section>

    <section class="observations" id="guided-observations" aria-label="实验观察">
      <div class="rates">
        <div><span>总采样率 f_s</span><strong>2 GS/s</strong></div>
        <div><span>每路 f_s / M</span><strong>{m === 2 ? '1' : '0.5'} GS/s</strong></div>
        <div><span>相邻 / 同路间隔</span><strong>0.5 / {m / 2} ns</strong></div>
      </div>
      <div class="timing-strip" aria-label="前八个理想采样时刻">
        {#each Array.from({ length: 8 }, (_, i) => i) as i}
          <div class="tick" class:channel-b={i % m === 1} class:channel-c={i % m === 2} class:channel-d={i % m === 3}>
            <span>{String.fromCharCode(65 + i % m)}</span><b>{nf(i / 2, 1)}</b><small>ns</small>
          </div>
        {/each}
      </div>
      <p class="timing-note">上方是无误差的采样时刻表；颜色对应通道 A、B{m === 4 ? '、C、D' : ''}。波形图用通道 0、1{m === 4 ? '、2、3' : ''} 标记。</p>
      <div class="chart time-view">
        <div class="cap"><span>时域 · 通道样本与输入</span><span>实际输入 {freqText(r.fin)}</span></div>
        <SampleTimingChart samples={r.rawData} truth={r.truth} fin={r.fin} {fs} harmonics={{}} decimation={1} hover={hoverSample} onhover={i => hoverSample = i} channelColors={['var(--s1)', 'var(--s2)', 'var(--brand)', 'var(--bad)']} label="引导实验时域图：各通道样本与理想输入" />
      </div>
      <div class="chart spectrum-view">
        <div class="cap"><span>输出频谱 · 0 到 f_s/2</span><span>SNDR <b>{nf(r.raw.sndr, 1)} dB</b></span></div>
        <SpurSpectrum spectrum={r.raw} spurs={r.spurs} harmonics={[]} {bits} fs={r.fsOut} points={r.fftPoints} hover={hoverBin} onhover={b => hoverBin = b} label="引导实验输出频谱：载波、杂散与噪声底" />
      </div>
      <div class="observation-readout" aria-live="polite">
        <span>{!started ? '无失配基线 · 先做预测' : stage === 0 ? '理想交织 · 量化仍然存在' : !enabled ? '当前误差已关闭 · 量化仍然存在' : stage === 4 && jitterMode ? '随机 jitter · 观察噪声底' : '单一失配已开启 · 观察离散杂散'}</span>
        {#if started && stage > 0}
          <strong>{stage === 4 && jitterMode ? `Jitter-only SNR ${Number.isFinite(jitterSnr) ? nf(jitterSnr, 1) + ' dB' : '∞'}` : `预测杂散 ${spurText}`}</strong>
        {/if}
      </div>
      <details class="model-notes"><summary>实验假设与读图提示</summary>
        <p>模型沿用本项目经 Python 参考对照的时间交织 ADC 仿真。输入是幅度 {AMP} V 的正弦；总采样率 2 GS/s；ADC 为 {bits} 位、±0.5 V 范围。保留量化；关闭热噪声、源谐波和带宽失配；所有通道共享 20 GHz 单极点模拟带宽。本课不执行抽取或校准。</p>
        <p>失配控制表示通道间 RMS，并去除了通道均值。两路时相对误差等幅反号；共同增益、共同失调与共同延时的作用不同。预测杂散是解析计算，图上实测 FFT 会受到量化和有限记录的影响。</p>
        <p>FFT 使用 {r.fftPoints} 点相干采样，输入会微调至相邻的奇数频点，所以“125 / 250 MHz”是目标值。请以图上实际输入为准。dBc 表示相对于载波的功率比，以电压幅度计算时用 20 log₁₀。</p>
        <p>f_s/2 处的交替序列 RMS 等于其峰值，普通正弦的 RMS 为峰值 / √2。本课将奈奎斯特端点的解析峰值换算为功率，再与 FFT 比较，避免 3 dB 的读图偏差。</p>
        <p>随机 jitter 使用固定种子的独立高斯序列，便于重复比较。时域图在标称时刻显示 jitter 引起的电压变化，不展示逐样本随机时间位移；固定 skew 的时间位移则会显示。</p>
        <p>通道采样率限制单路数字序列的奈奎斯特区；模拟输入带宽是另一项约束。各通道可单独混叠，完整的理想交织序列仍按总采样率判定混叠。</p>
      </details>
      <a class="mobile-jump" href="#step-heading">返回实验操作 ↑</a>
    </section>
  </div>
  {#if completed === lessonSteps.length}<p class="completion" role="status">你已通过五个理解检查。现在可以进入完整实验台，尝试多路交织与多种误差叠加；校准会作为后续实验单独讲解。</p>{/if}
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
