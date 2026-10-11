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
  const checkLabels = ['Read and redrew the circuit', 'Derived equations and budgets', 'Verified and answered the self-check'];
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
    } catch { storageMessage = 'Local records could not be read; you can still use the page and export your plan.'; }
    ready = true;
  });
  $effect(() => {
    const saved = { track, level, hours, start, checks, notes };
    if (ready) {
      try { localStorage.setItem('circuits-razavi-roadmap-v1', JSON.stringify(saved)); }
      catch { storageMessage = 'The browser blocked saving; export your plan to keep a record.'; }
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
    const lines = ['# Razavi article roadmap', '', `Track: ${tracks[track].title}; background: ${level === 'beginner' ? 'beginner' : 'analog foundation'}; ${hours} hours/week; estimated ${total} hours / ${weeks.length} weeks.`, 'Catalog checked: 2026-10-05. Durations are planning estimates, not guarantees of mastery.', '', 'Source: https://www.seas.ucla.edu/brweb/journal.html', ''];
    for (const stage of selected) {
      lines.push(`## ${stage.title} (${stage.hours} hours)`, '', stage.goal, '', ...stage.tasks.map(task => `- ${task}`), '', ...stage.articles.map(id => `- [${article(id).title}](${article(id).url})`), '', ...checkLabels.map((label, i) => `- [${checks[`${stage.id}:${i}`] ? 'x' : ' '}] ${label}`), '', `Self-check: ${stage.checkpoint}`, `Suggested reasoning: ${stage.hints}`, '', `Notes: ${notes[stage.id] ?? ''}`, '');
    }
    lines.push('## Weekly schedule', '');
    for (const week of weeks) lines.push(`- Week ${week.number}${start ? ` (from ${weekDate(start, week.number)})` : ''}: ${week.tasks.map(task => `${task.stage.title} ${task.hours}h`).join('; ')}`);
    const url = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' }));
    const link = document.createElement('a'); link.href = url; link.download = `razavi-${track}-plan.md`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
</script>

<main lang="en" class="roadmap">
  <header class="intro">
    <div class="eyebrow mono">READ → DERIVE → VERIFY</div>
    <h1>Turn an article catalog into your learning roadmap.</h1>
    <p>Build intuition with Razavi circuit columns, then move through design articles to research papers. Follow prerequisites and produce something verifiable at every step.</p>
    <div class="source-line"><a href="https://www.seas.ucla.edu/brweb/journal.html" target="_blank" rel="noreferrer">Original UCLA catalog ↗</a><span>Checked 2026-10-05 · {articles.length} PDF links · 22 Analog Mind articles</span></div>
  </header>

  <section class="settings" aria-label="Customize your roadmap">
    <div class="track-options"><span class="label">Choose a track</span><div class="track-buttons">
      {#each Object.entries(tracks) as [id, value]}
        <button class:chosen={track === id} aria-pressed={track === id} onclick={() => changeTrack(id as Track)}>{value.title}<span>{value.description}</span></button>
      {/each}
    </div></div>
    <div class="inputs">
      <label>Starting point<select bind:value={level}><option value="foundation">Analog-circuit foundation</option><option value="beginner">Start with devices and small signals</option></select></label>
      <label>Weekly study time<select bind:value={hours}><option value={3}>3 hours · Light</option><option value={6}>6 hours · Steady</option><option value={10}>10 hours · Focused</option><option value={15}>15 hours · Intensive</option></select></label>
      <label>Start date (optional)<input type="date" bind:value={start} /></label>
      <button class="export" onclick={exportPlan}>Export Markdown ↓</button>
    </div>
  </section>

  <section class="overview" aria-label="Plan overview">
    <div><strong class="mono">{weeks.length}<small>weeks</small></strong><span>Estimated at {hours} h/week</span></div>
    <div><strong class="mono">{total}<small>hours</small></strong><span>Read + derive + verify</span></div>
    <div class="progress-block"><strong class="mono">{completed} / {selected.length}<small>stages</small></strong><progress value={completed} max={selected.length} aria-label="Stage completion progress"></progress></div>
    <button class="next" onclick={() => { if (next) choose(next.id); tab = 'map'; }} disabled={!next}>{next ? `Next: ${next.title} →` : 'All stages in this track are checked off'}</button>
  </section>
  <p class="save-message" aria-live="polite">{storageMessage || 'Progress and notes stay in this browser; shared-stage records remain when switching tracks. Completion is a personal record, not a proficiency certification.'}</p>
  <nav class="view-tabs" aria-label="Roadmap views">
    <button aria-pressed={tab === 'map'} onclick={() => tab = 'map'}>Learning roadmap</button>
    <button aria-pressed={tab === 'weeks'} onclick={() => tab = 'weeks'}>Weekly plan</button>
    <button aria-pressed={tab === 'library'} onclick={() => tab = 'library'}>Article catalog <span class="mono">{articles.length}</span></button>
  </nav>

  {#if tab === 'map'}
    <RouteGraph {track} {level} {hours} activeId={active.id} completed={completedIds} started={startedIds} onChoose={chooseFromGraph} />
    <div class="map-layout">
      <article class="detail" aria-label="Stage details">
        <div class="detail-top"><span class="label">{active.subtitle} · ~ {active.hours} h</span><a href="#route-graph">Back to the graph ↑</a></div>
        <h2 class="detail-heading" tabindex="-1" bind:this={detailHeading}>{active.title}</h2><p class="goal">{active.goal}</p>
        <div class="prerequisite"><span>Prerequisites</span>{active.prerequisites.length ? active.prerequisites.map(id => route(track, level).find(stage => stage.id === id)?.title ?? 'Feedback and circuit fundamentals').join(' → ') : active.id === 'entry' ? 'Basic algebra; use an analog-circuit textbook alongside the readings' : 'MOS small signals, differential pairs, and basic frequency-domain analysis'}</div>
        <h3>Suggested reading order</h3>
        {#if active.articles.length}
          <ol class="reading">
            {#each active.articles as id}
              {@const item = article(id)}
              <li><a href={item.url} target="_blank" rel="noreferrer">{item.title} ↗</a><div class="metadata"><span>{item.group}{'issue' in item ? ` · ${item.issue}` : ''}</span><span class:reviewed={item.reviewed}>{item.reviewed ? 'Source and derivations verified' : 'Catalog checked · Full-text verification pending'}</span></div>
                {#if 'note' in item && item.note}<a class="note-link" href={`/learn/razavi/notes/${item.note.replace('.md', '').toLowerCase()}/`}>Read the research note →</a>{/if}
              </li>
            {/each}
          </ol>
        {:else}<p class="muted">Review this stage with an analog-circuit textbook before entering the columns. Use the experiment below to check your intuition.</p>{/if}
        {#if active.lab}<a class="lab-link" href={active.lab.href}>{active.lab.title} <span>Open the interactive experiment →</span></a>{/if}
        <h3>Stage tasks</h3><ol class="tasks">{#each active.tasks as task}<li>{task}</li>{/each}</ol>
        <div class="checkpoint"><h3>After reading, try to answer</h3><p>{active.checkpoint}</p><button aria-expanded={answerOpen} onclick={() => answerOpen = !answerOpen}>{answerOpen ? 'Hide suggested reasoning −' : 'Show suggested reasoning +'}</button>{#if answerOpen}<p class="hint">{active.hints}</p>{/if}</div>
        <fieldset><legend>My stage record</legend>{#each checkLabels as label, i}<label><input type="checkbox" bind:checked={checks[`${active.id}:${i}`]} />{label}</label>{/each}</fieldset>
        <label class="notes-label" for="learning-notes">Learning notes · Key equations, assumptions, and questions</label><textarea id="learning-notes" rows="4" bind:value={notes[active.id]} placeholder="For example: Which parameters does this equation hold fixed? What do I still need to verify?"></textarea>
      </article>
    </div>
  {:else if tab === 'weeks'}
    <section class="weekly" aria-label="Weekly study plan"><h2>Turn {hours} hours per week into tangible learning outputs.</h2><p class="muted">Stages may span weeks. Aim for about 40% reading, 40% derivation or experiments, and 20% review. Estimates include selected extension readings; allow more time as needed.</p>
      {#each weeks as week}<div class="week"><div><strong class="mono">W{String(week.number).padStart(2, '0')}</strong>{#if start}<small>From {weekDate(start, week.number)}</small>{/if}</div><div>{#each week.tasks as task}<button onclick={() => { choose(task.stage.id); tab = 'map'; }}><span>{task.stage.title}</span><span class="mono">{task.hours} h →</span></button>{/each}</div></div>{/each}
    </section>
  {:else}
    <section class="library" aria-label="Complete article catalog"><h2>Find articles by question; read them along a track.</h2><p class="muted">The full catalog includes teaching columns, research papers, and other articles. Selected tracks do not require all 148 articles. Use Inverter Applications Part 1–5 as a toolbox by function, and read the AI design experiments after learning independent verification.</p><div class="search"><label>Search title, author, or year<input type="search" bind:value={query} placeholder="For example: comparator, PLL, 2023" /></label><label>Article type<select bind:value={group}><option value="all">All</option><option>Analog Mind</option><option>A Circuit for All Seasons</option><option>Research and other articles</option></select></label></div><p class="result-count" aria-live="polite">{matches.length} articles found</p>
      {#each matches as item}<article class="library-row"><a href={item.url} target="_blank" rel="noreferrer">{item.title} ↗</a><span class="metadata">{item.group} · {item.reviewed ? 'Source and derivations verified' : 'Full-text verification pending'}</span><details><summary>Source citation</summary><p>{item.citation}</p></details></article>{/each}
      {#if !matches.length}<p>No matching articles. Try a shorter keyword or another article type.</p>{/if}
    </section>
  {/if}
  <footer class="scope"><strong>How to use this roadmap</strong><p>Follow dependencies first, then extend by interest. Read each article in three passes: identify the problem and topology → derive key relationships independently → check assumptions and verification conditions. Classic columns explain mechanisms, Analog Mind demonstrates design tradeoffs, and research papers support close topic study.</p><p>The catalog and original links were checked on 2026-10-05. Seven articles have verified notes; other reading tasks are study suggestions, not claims of completed full-text research. Durations estimate self-study with simplified-model verification, excluding fabrication and full PDK design. Use the original PDF when website citations disagree on dates or pages.</p></footer>
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
