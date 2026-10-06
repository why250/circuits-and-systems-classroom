<script lang="ts">
  import GuidedInterleaving from './GuidedInterleaving.svelte';
  import TimeInterleaving from './TimeInterleaving.svelte';
  let mode = $state<'guided' | 'free'>('guided');
</script>

<div class="lesson-modes" lang="zh-CN" aria-label="学习方式">
  <div class="mode-buttons">
    <button type="button" aria-pressed={mode === 'guided'} onclick={() => mode = 'guided'}>引导实验</button>
    <button type="button" aria-pressed={mode === 'free'} onclick={() => mode = 'free'}>完整实验台</button>
  </div>
  <span>时间交织 ADC · 从两路采样到失配频谱</span>
</div>
<!-- Keep both modes mounted so switching does not discard a learner's experiment. -->
<div hidden={mode !== 'guided'}><GuidedInterleaving /></div>
<div hidden={mode !== 'free'}><TimeInterleaving /></div>

<style>
  .lesson-modes { max-width: 1480px; margin: 0 auto; padding: 14px 24px 0; display: flex; flex-wrap: wrap; align-items: center; gap: 10px 20px; }
  .mode-buttons { display: flex; border: 1px solid var(--rule); border-radius: 6px; padding: 3px; gap: 3px; }
  button { border: 0; border-radius: 4px; padding: 6px 14px; background: transparent; color: var(--ink-2); font: 13px var(--sans); cursor: pointer; }
  button[aria-pressed='true'] { background: var(--brand-soft); color: var(--brand); }
  span { color: var(--ink-3); font-size: 12px; }
  [hidden] { display: none; }
</style>
