<script lang="ts">
  import { route, tracks, type Track, type Level, type Stage } from './plan';
  import { branch, stageNames, stageWeeks, trackIds, svgDiagram, excalidrawDiagram } from './graph';

  let { track, level, hours, activeId, completed, started, onChoose }: {
    track: Track; level: Level; hours: number; activeId: string;
    completed: string[]; started: string[]; onChoose: (track: Track, id: string, openDetail?: boolean) => void;
  } = $props();
  const shared = $derived(route(track, level).filter(stage => ['entry', 'feedback', 'regeneration'].includes(stage.id)));
  const tail = $derived(route(track, level).filter(stage => ['supplies', 'capstone'].includes(stage.id)));
  const weeks = $derived(Object.fromEntries(trackIds.map(id => [id, stageWeeks(id, level, hours)])));
  function state(id: string) { return completed.includes(id) ? '已完成' : started.includes(id) ? '学习中' : '待学习'; }
  function download(format: 'svg' | 'excalidraw') {
    const options = { track, level, hours, completed, started };
    const content = format === 'svg' ? svgDiagram(options) : excalidrawDiagram(options);
    const url = URL.createObjectURL(new Blob([content], { type: format === 'svg' ? 'image/svg+xml;charset=utf-8' : 'application/json;charset=utf-8' }));
    const link = document.createElement('a'); link.href = url; link.download = `razavi-roadmap.${format}`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
</script>

{#snippet node(stage: Stage, direction: Track)}
  <button class="node" class:active={activeId === stage.id} class:done={completed.includes(stage.id)} class:started={started.includes(stage.id) && !completed.includes(stage.id)}
    aria-label={`${stageNames[stage.id]}，${stage.hours} 小时，${weeks[direction][stage.id]}，${state(stage.id)}，查看阶段详情`}
    aria-current={activeId === stage.id && track === direction ? 'step' : undefined} onclick={() => onChoose(direction, stage.id)}>
    <span class="node-top"><span class="state"><i aria-hidden="true"></i>{state(stage.id)}</span><span class="mono">{stage.hours} h</span></span>
    <strong>{stageNames[stage.id]}</strong>
    <span class="node-bottom"><span>{weeks[direction][stage.id]}</span><span aria-hidden="true">查看任务 ↗</span></span>
  </button>
{/snippet}

<section class="route-graph" id="route-graph" aria-labelledby="graph-title">
  <header class="graph-header">
    <div><span class="eyebrow mono">THE BIG PICTURE</span><h2 id="graph-title">先看全局，再走好每一步。</h2><p>点击节点查看文章与任务。箭头表示建议阅读顺序，具体先修见阶段详情。</p></div>
    <div class="downloads"><button onclick={() => download('svg')}>下载 SVG ↓</button><button onclick={() => download('excalidraw')}>下载 Excalidraw ↓</button></div>
  </header>
  <div class="legend"><span><i class="selected-dot"></i>当前选择</span><span><i class="done-dot"></i>已完成</span><span><i class="started-dot"></i>学习中</span><span class="week-note">每周 {hours} 小时 · 各方向独立估算周次</span></div>

  <div class="common-section">
    <div class="section-label"><span class="mono">01</span> 共同基础 <small>三条路线共享这些知识</small></div>
    <div class="shared-nodes">{#each shared as stage, index}{#if index}<span class="across-arrow" aria-hidden="true">→</span>{/if}{@render node(stage, track)}{/each}</div>
  </div>
  <div class="branch-fan" aria-hidden="true"><svg viewBox="0 0 100 18" preserveAspectRatio="none"><path d="M50 0 V9 M16.667 18 V9 H83.333 V18 M50 9 V18" /></svg></div>
  <div class="mobile-switch" aria-label="路线图方向">
    {#each trackIds as direction}<button aria-pressed={track === direction} onclick={() => onChoose(direction, branch(direction, level)[0].id, false)}>{direction === 'adc' ? 'ADC' : direction === 'pll' ? 'PLL' : '高速链路'}</button>{/each}
  </div>
  <div class="lanes">
    {#each trackIds as direction}
      <div class="lane" class:chosen={track === direction}>
        <button class="lane-heading" aria-pressed={track === direction} onclick={() => onChoose(direction, branch(direction, level)[0].id, false)}><span><span class="mono">02 / {direction.toUpperCase()}</span><strong>{tracks[direction].title}</strong></span><span class="lane-hint">{track === direction ? '当前方向' : '切换方向 →'}</span></button>
        <div class="branch-nodes">
          {#each branch(direction, level) as stage, index}
            {#if index}<span class="down-arrow" aria-hidden="true">↓</span>{/if}
            {@render node(stage, direction)}
          {/each}
        </div>
      </div>
    {/each}
  </div>
  <div class="branch-fan merge" aria-hidden="true"><svg viewBox="0 0 100 18" preserveAspectRatio="none"><path d="M16.667 0 V9 H83.333 V0 M50 0 V18" /></svg></div>
  <div class="common-section finish-section">
    <div class="section-label"><span class="mono">03</span> 补齐系统，交付设计 <small>参考、电源与滤波可在反馈之后穿插学习</small></div>
    <div class="shared-nodes">{#each tail as stage, index}{#if index}<span class="across-arrow" aria-hidden="true">→</span>{/if}{@render node(stage, track)}{/each}</div>
  </div>
  <p class="export-note">导出包含全部方向与当前进度快照。SVG 可直接查看或打印；.excalidraw 文件可在 <a href="https://excalidraw.com/" target="_blank" rel="noreferrer">Excalidraw ↗</a> 中打开编辑，图中修改不会回写网页。</p>
</section>

<style>
  .route-graph { border: 1px solid var(--rule); border-radius: 10px; padding: 26px; background: var(--plot); margin-bottom: 28px; scroll-margin-top: 90px; }
  .graph-header { display: flex; flex-wrap: wrap; gap: 18px; justify-content: space-between; align-items: center; }.eyebrow { color: var(--brand); font-size: 10px; letter-spacing: .1em; }h2 { margin: 8px 0; font-size: 24px; font-weight: 550; letter-spacing: -.03em; }.graph-header p { color: var(--ink-2); font-size: 12px; line-height: 1.8; margin: 0; }
  button { font: inherit; cursor: pointer; }.downloads { display: flex; flex-wrap: wrap; gap: 8px; }.downloads button { color: var(--ink-2); background: var(--ground); border: 1px solid var(--rule); border-radius: 5px; padding: 10px 12px; font-size: 11px; min-height: 40px; }
  .legend { display: flex; flex-wrap: wrap; gap: 12px 18px; align-items: center; color: var(--ink-3); font-size: 11px; margin: 22px 0; }.legend > span { display: inline-flex; gap: 6px; align-items: center; }.legend i, .state i { width: 7px; height: 7px; border: 1px solid var(--rule); border-radius: 50%; flex: none; }.legend .selected-dot { background: var(--brand); border-color: var(--brand); }.legend .done-dot { background: var(--brand-soft); border-color: var(--brand); }.legend .started-dot { background: var(--s1); border-color: var(--s1); }.legend .week-note { margin-left: auto; }
  .section-label { color: var(--ink-2); font-size: 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-bottom: 14px; }.section-label .mono { font-size: 10px; color: var(--brand); }.section-label small { font-size: 11px; color: var(--ink-3); margin-left: auto; }
  .common-section { padding: 18px; background: var(--ground); border: 1px dashed var(--rule); border-radius: 7px; }.shared-nodes { display: flex; gap: 14px; align-items: center; justify-content: center; }.shared-nodes .node { flex: 1; max-width: 360px; }.across-arrow { color: var(--ink-3); }
  .node { width: 100%; min-width: 0; display: grid; gap: 10px; border: 1px solid var(--rule); border-radius: 7px; background: var(--plot); text-align: left; color: var(--ink); padding: 13px 14px; transition: border-color .15s; }.node:hover { border-color: var(--brand); }.node:focus-visible, .lane-heading:focus-visible, .mobile-switch button:focus-visible, .downloads button:focus-visible { outline: 2px solid var(--brand); outline-offset: 3px; }.node.active { border-color: var(--brand); box-shadow: 0 0 0 1px var(--brand); background: var(--brand-soft); }.node.done .state { color: var(--brand); }.node.done .state i { background: var(--brand); border-color: var(--brand); }.node.started .state { color: var(--s1); }.node.started .state i { background: var(--s1); border-color: var(--s1); }.node-top, .node-bottom { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 4px 8px; font-size: 10px; color: var(--ink-3); }.state { display: inline-flex; gap: 6px; align-items: center; }.node strong { font-weight: 550; font-size: 15px; line-height: 1.5; }.node-bottom span:last-child { color: var(--brand); }
  .branch-fan { padding: 0 16px; height: 34px; }.branch-fan svg { width: 100%; height: 100%; }.branch-fan path { fill: none; stroke: var(--rule); stroke-width: 1.5; vector-effect: non-scaling-stroke; }.lanes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }.lane { display: flex; flex-direction: column; border: 1px solid var(--rule); background: var(--ground); border-radius: 8px; padding: 14px; }.lane.chosen { border-color: var(--brand); background: color-mix(in srgb, var(--brand-soft) 35%, var(--ground)); }.lane-heading { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: start; gap: 8px; text-align: left; background: none; border: 0; color: var(--ink-2); padding: 0 0 16px; }.lane-heading > span:first-child { display: grid; gap: 6px; }.lane-heading .mono { font-size: 10px; color: var(--ink-3); }.lane-heading strong { font-size: 14px; font-weight: 550; }.lane-hint { font-size: 10px; line-height: 1.6; color: var(--ink-3); }.chosen .lane-heading strong, .chosen .lane-hint { color: var(--brand); }.branch-nodes { display: flex; flex-direction: column; flex: 1; }.branch-nodes::after { content: ''; flex: 1; width: 1px; background: var(--rule); align-self: center; min-height: 12px; margin-top: 8px; }.down-arrow { display: block; text-align: center; font-size: 14px; color: var(--ink-3); height: 28px; line-height: 28px; }.mobile-switch { display: none; }.export-note { color: var(--ink-3); font-size: 11px; line-height: 1.8; margin: 18px 0 0; }.export-note a { color: var(--brand); text-underline-offset: 3px; }
  @media (prefers-reduced-motion: reduce) { .node { transition: none; } }
  @media (max-width: 800px) { .route-graph { padding: 18px; }.lanes { gap: 10px; }.lane { padding: 10px; }.lane-heading strong { font-size: 12px; }.node { padding: 12px 10px; }.node strong { font-size: 13px; }.shared-nodes { gap: 10px; }.section-label small { width: 100%; margin-left: 0; } }
  @media (max-width: 640px) { .route-graph { padding: 18px 14px; }.graph-header h2 { font-size: 21px; }.graph-header p { font-size: 11px; }.downloads { width: 100%; }.downloads button { flex: 1; }.legend { gap: 10px 14px; }.legend .week-note { width: 100%; margin-left: 0; }.common-section { padding: 14px; }.shared-nodes { flex-direction: column; gap: 8px; }.shared-nodes .node { max-width: none; flex: none; }.across-arrow { transform: rotate(90deg); font-size: 14px; }.branch-fan { width: 1px; margin: 0 auto; padding: 0; background: var(--rule); height: 24px; }.branch-fan svg { display: none; }.mobile-switch { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 10px; }.mobile-switch button { background: var(--ground); border: 1px solid var(--rule); color: var(--ink-2); border-radius: 5px; padding: 10px 6px; font-size: 12px; min-height: 42px; }.mobile-switch button[aria-pressed='true'] { background: var(--brand-soft); border-color: var(--brand); color: var(--brand); }.lanes { grid-template-columns: minmax(0, 1fr); }.lane:not(.chosen) { display: none; }.lane { padding: 14px; }.lane-heading strong { font-size: 14px; }.node { padding: 13px 14px; }.node strong { font-size: 15px; }.branch-nodes::after { display: none; } }
  @media print { .downloads, .mobile-switch, .export-note { display: none; }.route-graph { break-inside: avoid; }.lanes { grid-template-columns: repeat(3, minmax(0, 1fr)); }.lane:not(.chosen) { display: flex; }.node { box-shadow: none; } }
</style>
