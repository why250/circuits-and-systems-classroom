<script lang="ts">
  import { onMount } from 'svelte';
  import RouteGraph from './RouteGraph.svelte';
  import { article, articles, route, schedule, tracks, weekDate, type Track, type Level } from './plan';
  let track = $state<Track>('adc');
  let level = $state<Level>('foundation');
  let hours = $state(6);
  let start = $state('');
  let selectedId = $state('feedback');
  let checks = $state<Record<string, boolean>>({});
  let notes = $state<Record<string, string>>({});
  let ready = $state(false);
  let storageMessage = $state('');
  let query = $state('');
  let group = $state('all');
  let tab = $state<'map' | 'weeks' | 'library'>('map');
  let answerOpen = $state(false);
  let detailHeading = $state<HTMLHeadingElement>();
  const checkLabels = ['已阅读并重画电路', '已完成推导与预算', '已验证并回答自查'];
  const selected = $derived(route(track, level));
  const active = $derived(selected.find(stage => stage.id === selectedId) ?? selected[0]);
  const total = $derived(selected.reduce((sum, stage) => sum + stage.hours, 0));
  const weeks = $derived(schedule(selected, hours));
  const completed = $derived(selected.filter(stage => checkLabels.every((_, i) => checks[`${stage.id}:${i}`])).length);
  const next = $derived(selected.find(stage => !checkLabels.every((_, i) => checks[`${stage.id}:${i}`])));
  const allStages = $derived([...new Map((['adc', 'pll', 'links'] as Track[]).flatMap(id => route(id, level)).map(stage => [stage.id, stage])).values()]);
  const completedIds = $derived(allStages.filter(stage => checkLabels.every((_, i) => checks[`${stage.id}:${i}`])).map(stage => stage.id));
  const startedIds = $derived(allStages.filter(stage => checkLabels.some((_, i) => checks[`${stage.id}:${i}`]) || notes[stage.id]?.trim()).map(stage => stage.id));
  const matches = $derived(articles.filter(item => (group === 'all' || item.group === group) && `${item.title} ${item.citation}`.toLowerCase().includes(query.toLowerCase().trim())));
  onMount(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('circuits-razavi-roadmap-v1') ?? 'null');
      if (saved && typeof saved === 'object') {
        if (saved.track in tracks) track = saved.track;
        if (saved.level === 'beginner' || saved.level === 'foundation') level = saved.level;
        if ([3, 6, 10, 15].includes(saved.hours)) hours = saved.hours;
        if (typeof saved.start === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(saved.start)) start = saved.start;
        if (saved.checks && typeof saved.checks === 'object') checks = Object.fromEntries(Object.entries(saved.checks).filter(([, value]) => typeof value === 'boolean')) as Record<string, boolean>;
        if (saved.notes && typeof saved.notes === 'object') notes = Object.fromEntries(Object.entries(saved.notes).filter(([, value]) => typeof value === 'string')) as Record<string, string>;
      }
    } catch { storageMessage = '本地记录不可读取；你仍可使用网页并导出计划。'; }
    ready = true;
  });
  $effect(() => {
    const saved = { track, level, hours, start, checks, notes };
    if (ready) {
      try { localStorage.setItem('circuits-razavi-roadmap-v1', JSON.stringify(saved)); }
      catch { storageMessage = '浏览器未允许保存；请导出计划以保留记录。'; }
    }
  });
  function choose(id: string) { selectedId = id; answerOpen = false; }
  function changeTrack(value: Track) { track = value; selectedId = 'feedback'; answerOpen = false; }
  function chooseFromGraph(value: Track, id: string, openDetail = true) {
    track = value; choose(id);
    if (openDetail) requestAnimationFrame(() => {
      detailHeading?.focus({ preventScroll: true });
      detailHeading?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    });
  }
  function exportPlan() {
    const lines = ['# Razavi 文章学习路线', '', `方向：${tracks[track].title}；基础：${level === 'beginner' ? '入门' : '已有模拟基础'}；每周 ${hours} 小时；估算 ${total} 小时 / ${weeks.length} 周。`, '目录核对：2026-10-05；时长为规划估算，不代表掌握保证。', '', '来源：https://www.seas.ucla.edu/brweb/journal.html', ''];
    for (const stage of selected) {
      lines.push(`## ${stage.title}（${stage.hours} 小时）`, '', stage.goal, '', ...stage.tasks.map(task => `- ${task}`), '', ...stage.articles.map(id => `- [${article(id).title}](${article(id).url})`), '', ...checkLabels.map((label, i) => `- [${checks[`${stage.id}:${i}`] ? 'x' : ' '}] ${label}`), '', `自查：${stage.checkpoint}`, `参考思路：${stage.hints}`, '', `笔记：${notes[stage.id] ?? ''}`, '');
    }
    lines.push('## 每周安排', '');
    for (const week of weeks) lines.push(`- 第 ${week.number} 周${start ? `（${weekDate(start, week.number)} 起）` : ''}：${week.tasks.map(task => `${task.stage.title} ${task.hours}h`).join('；')}`);
    const url = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' }));
    const link = document.createElement('a'); link.href = url; link.download = `razavi-${track}-plan.md`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
</script>

<main lang="zh-CN" class="roadmap">
  <header class="intro">
    <div class="eyebrow mono">READ → DERIVE → VERIFY</div>
    <h1>把文章目录，变成你的学习路线。</h1>
    <p>从 Razavi 的经典电路专栏建立直觉，经设计文章走向研究论文。沿先修关系阅读，每一步都留下可检查的产出。</p>
    <div class="source-line"><a href="https://www.seas.ucla.edu/brweb/journal.html" target="_blank" rel="noreferrer">UCLA 原始目录 ↗</a><span>2026-10-05 核对 · {articles.length} 个 PDF 链接 · 22 篇 Analog Mind</span></div>
  </header>

  <section class="settings" aria-label="定制学习路线">
    <div class="track-options"><span class="label">选择方向</span><div class="track-buttons">
      {#each Object.entries(tracks) as [id, value]}
        <button class:chosen={track === id} aria-pressed={track === id} onclick={() => changeTrack(id as Track)}>{value.title}<span>{value.description}</span></button>
      {/each}
    </div></div>
    <div class="inputs">
      <label>起点<select bind:value={level}><option value="foundation">已有模拟电路基础</option><option value="beginner">从器件与小信号入门</option></select></label>
      <label>每周投入<select bind:value={hours}><option value={3}>3 小时 · 轻量</option><option value={6}>6 小时 · 稳步</option><option value={10}>10 小时 · 集中</option><option value={15}>15 小时 · 深入</option></select></label>
      <label>开始日期（可选）<input type="date" bind:value={start} /></label>
      <button class="export" onclick={exportPlan}>导出 Markdown ↓</button>
    </div>
  </section>

  <section class="overview" aria-label="计划摘要">
    <div><strong class="mono">{weeks.length}<small>周</small></strong><span>按 {hours} 小时 / 周估算</span></div>
    <div><strong class="mono">{total}<small>小时</small></strong><span>阅读 + 推导 + 验证</span></div>
    <div class="progress-block"><strong class="mono">{completed} / {selected.length}<small>阶段</small></strong><progress value={completed} max={selected.length} aria-label="阶段完成进度"></progress></div>
    <button class="next" onclick={() => { if (next) choose(next.id); tab = 'map'; }} disabled={!next}>{next ? `下一步：${next.title} →` : '本路线已全部勾选完成'}</button>
  </section>
  <p class="save-message" aria-live="polite">{storageMessage || '进度与笔记保存在当前浏览器；切换路线会保留共同阶段记录。勾选完成是自我记录，不代表能力认证。'}</p>
  <nav class="view-tabs" aria-label="路线视图">
    <button aria-pressed={tab === 'map'} onclick={() => tab = 'map'}>学习路线</button>
    <button aria-pressed={tab === 'weeks'} onclick={() => tab = 'weeks'}>每周计划</button>
    <button aria-pressed={tab === 'library'} onclick={() => tab = 'library'}>文章目录 <span class="mono">{articles.length}</span></button>
  </nav>

  {#if tab === 'map'}
    <RouteGraph {track} {level} {hours} activeId={active.id} completed={completedIds} started={startedIds} onChoose={chooseFromGraph} />
    <div class="map-layout">
      <article class="detail" aria-label="阶段详情">
        <div class="detail-top"><span class="label">{active.subtitle} · ~ {active.hours} h</span><a href="#route-graph">返回路线图 ↑</a></div>
        <h2 class="detail-heading" tabindex="-1" bind:this={detailHeading}>{active.title}</h2><p class="goal">{active.goal}</p>
        <div class="prerequisite"><span>先修</span>{active.prerequisites.length ? active.prerequisites.map(id => route(track, level).find(stage => stage.id === id)?.title ?? '反馈与基础电路').join(' → ') : active.id === 'entry' ? '基本代数；同时配合模拟电路教材' : 'MOS 小信号、差分对、基本频域分析'}</div>
        <h3>建议阅读顺序</h3>
        {#if active.articles.length}
          <ol class="reading">
            {#each active.articles as id}
              {@const item = article(id)}
              <li><a href={item.url} target="_blank" rel="noreferrer">{item.title} ↗</a><div class="metadata"><span>{item.group}{'issue' in item ? ` · ${item.issue}` : ''}</span><span class:reviewed={item.reviewed}>{item.reviewed ? '原文与推导已核验' : '目录已核对 · 深读待核验'}</span></div>
                {#if 'note' in item && item.note}<a class="note-link" href={`/learn/razavi/notes/${item.note.replace('.md', '').toLowerCase()}/`}>阅读已有研究笔记 →</a>{/if}
              </li>
            {/each}
          </ol>
        {:else}<p class="muted">先用模拟电路教材复习本阶段，再进入专栏。下面的实验可用于检查直觉。</p>{/if}
        {#if active.lab}<a class="lab-link" href={active.lab.href}>{active.lab.title} <span>打开互动实验 →</span></a>{/if}
        <h3>本阶段要做什么</h3><ol class="tasks">{#each active.tasks as task}<li>{task}</li>{/each}</ol>
        <div class="checkpoint"><h3>读完后，试着回答</h3><p>{active.checkpoint}</p><button aria-expanded={answerOpen} onclick={() => answerOpen = !answerOpen}>{answerOpen ? '收起参考思路 −' : '展开参考思路 +'}</button>{#if answerOpen}<p class="hint">{active.hints}</p>{/if}</div>
        <fieldset><legend>我的阶段记录</legend>{#each checkLabels as label, i}<label><input type="checkbox" bind:checked={checks[`${active.id}:${i}`]} />{label}</label>{/each}</fieldset>
        <label class="notes-label" for="learning-notes">学习笔记 · 关键公式、假设与疑问</label><textarea id="learning-notes" rows="4" bind:value={notes[active.id]} placeholder="例如：这一公式固定了哪些参数？我还需要验证什么？"></textarea>
      </article>
    </div>
  {:else if tab === 'weeks'}
    <section class="weekly" aria-label="每周学习计划"><h2>每周 {hours} 小时，把阅读落到产出上。</h2><p class="muted">阶段可以跨周。建议每周约 40% 阅读、40% 推导或实验、20% 复盘。时间包含精选拓展阅读，可按实际难度延长。</p>
      {#each weeks as week}<div class="week"><div><strong class="mono">W{String(week.number).padStart(2, '0')}</strong>{#if start}<small>{weekDate(start, week.number)} 起</small>{/if}</div><div>{#each week.tasks as task}<button onclick={() => { choose(task.stage.id); tab = 'map'; }}><span>{task.stage.title}</span><span class="mono">{task.hours} h →</span></button>{/each}</div></div>{/each}
    </section>
  {:else}
    <section class="library" aria-label="完整文章目录"><h2>按问题找文章，按路线读文章。</h2><p class="muted">完整目录含教学专栏、研究论文及其他文章。精选路线不会要求读完全部 148 篇。长系列可留作工具箱：反相器应用 Part 1–5 按功能回查，AI 设计实验放在独立验证之后。</p><div class="search"><label>搜索标题、作者或年份<input type="search" bind:value={query} placeholder="例如 comparator、PLL、2023" /></label><label>文章类型<select bind:value={group}><option value="all">全部</option><option>Analog Mind</option><option>A Circuit for All Seasons</option><option>研究与其他文章</option></select></label></div><p class="result-count" aria-live="polite">找到 {matches.length} 篇</p>
      {#each matches as item}<article class="library-row"><a href={item.url} target="_blank" rel="noreferrer">{item.title} ↗</a><span class="metadata">{item.group} · {item.reviewed ? '原文与推导已核验' : '深读待核验'}</span><details><summary>来源引用</summary><p>{item.citation}</p></details></article>{/each}
      {#if !matches.length}<p>没有匹配文章，请缩短关键词或切换文章类型。</p>{/if}
    </section>
  {/if}
  <footer class="scope"><strong>怎样使用这张路线</strong><p>优先按依赖关系学习，再按兴趣拓展。每篇读三遍：识别问题与拓扑 → 独立推导关键关系 → 检查假设与验证条件。经典专栏帮助理解机制，Analog Mind 展示设计取舍，研究论文用于专题精读。</p><p>目录与原始链接核对于 2026-10-05；7 篇已有核验笔记，其余阅读任务是学习建议，未声称完成全文研究。时长是自学估算，包含简化模型验证，不包含流片或完整 PDK 设计。网站引用存在日期/页码差异时，以原始 PDF 为准。</p></footer>
</main>

<style>
  .roadmap { max-width: 1200px; margin: auto; padding: 42px 32px; }
  .intro { padding-bottom: 28px; } .eyebrow { color: var(--brand); font-size: 11px; letter-spacing: .12em; }
  h1 { font-size: clamp(28px, 3.3vw, 42px); line-height: 1.3; letter-spacing: -.04em; font-weight: 600; margin: 12px 0; }
  .intro p { color: var(--ink-2); max-width: 720px; font-size: 16px; line-height: 1.8; }
  .source-line { display: flex; flex-wrap: wrap; gap: 8px 22px; color: var(--ink-3); font-size: 12px; } .source-line a { color: var(--brand); text-decoration: none; }
  button, input, select, textarea { font: inherit; } button { cursor: pointer; } button:disabled { cursor: default; opacity: .6; } input, select, textarea { color: var(--ink); background: var(--plot); border: 1px solid var(--rule); border-radius: 5px; }
  .settings { border-block: 1px solid var(--rule); padding: 22px 0; } .track-options > span { display: block; margin-bottom: 10px; }
  .track-buttons { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .track-buttons button { padding: 16px 18px; text-align: left; border: 1px solid var(--rule); border-radius: 6px; color: var(--ink); background: transparent; font-weight: 600; }
  .track-buttons button span { display: block; color: var(--ink-2); font-size: 12px; line-height: 1.6; margin-top: 7px; font-weight: 400; }
  .track-buttons button.chosen { border-color: var(--brand); background: color-mix(in srgb, var(--brand-soft) 40%, transparent); }
  .inputs { display: flex; flex-wrap: wrap; align-items: end; gap: 16px; margin-top: 20px; } .inputs label, .search label { display: grid; gap: 7px; color: var(--ink-2); font-size: 12px; } select, input[type='date'], input[type='search'] { padding: 9px 11px; min-height: 40px; }
  .export { margin-left: auto; min-height: 40px; padding: 8px 16px; border: 1px solid var(--rule); background: var(--plot); color: var(--ink); border-radius: 5px; }
  .overview { display: grid; grid-template-columns: 1fr 1fr 1.2fr 1.6fr; gap: 24px; align-items: center; padding: 26px 0 10px; } .overview > div { display: grid; gap: 6px; } .overview strong { font-size: 27px; font-weight: 450; } .overview small { font: 12px var(--sans); color: var(--ink-2); margin-left: 8px; } .overview span { color: var(--ink-3); font-size: 11px; } progress { width: 100%; height: 6px; accent-color: var(--brand); }
  .next { text-align: left; line-height: 1.6; border: 0; border-left: 2px solid var(--brand); padding: 10px 14px; color: var(--brand); background: var(--brand-soft); border-radius: 0 5px 5px 0; }
  .save-message { color: var(--ink-3); font-size: 11px; margin: 12px 0 24px; }
  .view-tabs { display: flex; gap: 24px; border-bottom: 1px solid var(--rule); margin-bottom: 24px; } .view-tabs button { color: var(--ink-2); background: none; padding: 10px 0 14px; border: 0; border-bottom: 2px solid transparent; } .view-tabs button[aria-pressed='true'] { color: var(--brand); border-color: var(--brand); } .view-tabs span { font-size: 11px; margin-left: 5px; }
  .map-layout { max-width: 900px; margin: auto; }
  .detail { min-width: 0; padding: 26px 28px; border: 1px solid var(--rule); background: var(--plot); border-radius: 7px; } .detail-top { display: flex; justify-content: space-between; color: var(--ink-3); font-size: 12px; }
  .detail-top a { color: var(--brand); text-decoration: none; white-space: nowrap; }.detail-heading { scroll-margin-top: 90px; }.detail-heading:focus { outline: none; }
  h2 { font-size: 24px; font-weight: 550; letter-spacing: -.025em; margin: 12px 0; } .goal { font-size: 15px; line-height: 1.8; color: var(--ink-2); }
  .prerequisite { color: var(--ink-2); font-size: 12px; padding: 12px 0 20px; border-bottom: 1px solid var(--rule); }.prerequisite span { color: var(--ink-3); margin-right: 12px; }
  h3 { font-size: 13px; font-weight: 600; margin: 24px 0 12px; } ol { padding-left: 20px; } .reading li { padding: 5px 0 12px 4px; } .reading a { line-height: 1.5; text-decoration-color: var(--rule); text-underline-offset: 4px; } .metadata { display: flex; flex-wrap: wrap; gap: 5px 14px; color: var(--ink-3); font-size: 10px; margin-top: 7px; }.reviewed { color: var(--brand); }.note-link { display: inline-block; margin-top: 8px; font-size: 11px; color: var(--brand); }
  .tasks li { margin-bottom: 10px; line-height: 1.8; color: var(--ink-2); padding-left: 3px; } .lab-link { display: flex; flex-wrap: wrap; gap: 6px 12px; justify-content: space-between; padding: 14px; border: 1px solid var(--rule); border-radius: 5px; text-decoration: none; color: var(--brand); font-size: 12px; }
  .checkpoint { border-left: 2px solid var(--s1); background: var(--s1-soft); padding: 12px 18px; margin: 24px 0; } .checkpoint h3 { margin-top: 0; } .checkpoint p { line-height: 1.8; } .checkpoint button { background: none; border: 0; color: var(--s1); padding: 6px 0; font-size: 12px; } .hint { color: var(--ink-2); font-size: 13px; }
  fieldset { border: 0; border-top: 1px solid var(--rule); margin: 0; padding: 14px 0; } legend { padding-right: 12px; font-size: 12px; color: var(--ink-2); } fieldset label { display: flex; gap: 10px; align-items: center; padding: 7px 0; font-size: 12px; } input[type='checkbox'] { width: 16px; height: 16px; accent-color: var(--brand); }.notes-label { display: block; font-size: 12px; margin: 12px 0 8px; color: var(--ink-2); } textarea { width: 100%; padding: 12px; line-height: 1.7; resize: vertical; }
  .muted { color: var(--ink-2); line-height: 1.8; } .weekly, .library { max-width: 850px; } .week { display: grid; grid-template-columns: 130px 1fr; border-bottom: 1px solid var(--rule); padding: 18px 0; gap: 16px; }.week > div:first-child { display: grid; align-content: start; gap: 6px; color: var(--brand); }.week small { color: var(--ink-3); font-size: 11px; }.week button { width: 100%; display: flex; gap: 12px; justify-content: space-between; background: none; border: 0; color: var(--ink); padding: 7px 0; text-align: left; }.week button span:last-child { white-space: nowrap; color: var(--ink-3); font-size: 12px; }
  .search { display: grid; grid-template-columns: 1fr 220px; gap: 16px; margin-top: 24px; } .result-count { color: var(--ink-3); font-size: 12px; }.library-row { padding: 16px 0; border-bottom: 1px solid var(--rule); }.library-row > a { text-decoration: none; font-weight: 500; }.library-row details { font-size: 11px; color: var(--ink-3); margin-top: 8px; }.library-row summary { cursor: pointer; }
  .scope { border-top: 1px solid var(--rule); margin-top: 36px; padding-top: 24px; font-size: 12px; color: var(--ink-3); line-height: 1.9; }.scope strong { color: var(--ink-2); }
  @media (max-width: 900px) { .detail { padding: 22px; }.overview { grid-template-columns: 1fr 1fr 1fr; }.next { grid-column: 1 / -1; }.roadmap { padding: 30px 22px; } }
  @media (max-width: 640px) { .roadmap { padding: 24px 16px; }.track-buttons { grid-template-columns: 1fr; gap: 8px; }.track-buttons button { padding: 12px 14px; }.track-buttons button span { margin-top: 3px; }.inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }.inputs label, .inputs input, .inputs select { min-width: 0; width: 100%; }.export { width: 100%; font-size: 11px; }.overview { gap: 14px; }.overview strong { font-size: 21px; }.overview small { margin-left: 4px; font-size: 10px; }.view-tabs { gap: 18px; }.detail { padding: 20px 16px; } h2 { font-size: 21px; }.search { grid-template-columns: 1fr; }.week { grid-template-columns: 85px 1fr; gap: 10px; } }
  @media print { .settings, .view-tabs, .export, .next, .save-message { display: none; }.roadmap { padding: 0; }.detail { border: 0; } }
</style>
