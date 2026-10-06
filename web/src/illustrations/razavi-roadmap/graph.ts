import { route, schedule, tracks, type Level, type Stage, type Track } from './plan';

export const trackIds: Track[] = ['adc', 'pll', 'links'];
export const commonIds = new Set(['entry', 'feedback', 'regeneration', 'supplies', 'capstone']);
export const stageNames: Record<string, string> = {
  entry: '器件与小信号', feedback: '反馈 · 带宽 · 噪声', regeneration: '正反馈与再生',
  sampling: '采样与自举开关', comparator: '比较器设计', discrete: '开关电容与 z 域',
  architecture: 'ADC 架构与交织', adcResearch: 'ADC 论文复现',
  oscillators: '振荡器与 VCO', phaseNoise: '相位噪声与 jitter', divider: '分频与环路动态',
  synthesizer: '整数 / 分数 N PLL', pllResearch: '低 jitter PLL 复现',
  frontEnd: 'TIA 与高速前端', equalization: 'CTLE / DFE 均衡', timing: 'DLL 与相位插值',
  recovery: 'CDR 时钟恢复', supplies: '参考 · 电源 · 滤波', capstone: '自己的设计审查',
};
export function branch(track: Track, level: Level): Stage[] {
  return route(track, level).filter(stage => !commonIds.has(stage.id));
}
export function stageWeeks(track: Track, level: Level, hours: number): Record<string, string> {
  const ranges: Record<string, number[]> = {};
  for (const week of schedule(route(track, level), hours)) {
    for (const task of week.tasks) (ranges[task.stage.id] ??= []).push(week.number);
  }
  return Object.fromEntries(Object.entries(ranges).map(([id, weeks]) => [id,
    weeks[0] === weeks[weeks.length - 1] ? `第 ${weeks[0]} 周` : `第 ${weeks[0]}–${weeks[weeks.length - 1]} 周`,
  ]));
}

export interface GraphNode { id: string; stage: Stage; track?: Track; x: number; y: number }
export interface GraphEdge { from: string; to: string; track?: Track }
export function graphLayout(level: Level) {
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const width = 1000, cardWidth = 270, cardHeight = 80;
  const shared = route('adc', level).filter(stage => ['entry', 'feedback', 'regeneration'].includes(stage.id));
  shared.forEach((stage, i) => {
    nodes.push({ id: stage.id, stage, x: 365, y: 70 + i * 106 });
    if (i) edges.push({ from: shared[i - 1].id, to: stage.id });
  });
  const branchY = 70 + shared.length * 106 + 56;
  trackIds.forEach((track, column) => {
    const stages = branch(track, level);
    stages.forEach((stage, i) => {
      nodes.push({ id: stage.id, stage, track, x: 30 + column * 335, y: branchY + i * 112 });
      edges.push({ from: i ? stages[i - 1].id : 'regeneration', to: stage.id, track });
    });
  });
  const tailY = branchY + Math.max(...trackIds.map(track => branch(track, level).length)) * 112 + 24;
  const adcRoute = route('adc', level);
  for (const [index, id] of ['supplies', 'capstone'].entries()) {
    nodes.push({ id, stage: adcRoute.find(stage => stage.id === id)!, x: 365, y: tailY + index * 106 });
  }
  trackIds.forEach(track => edges.push({ from: branch(track, level).at(-1)!.id, to: 'supplies', track }));
  edges.push({ from: 'supplies', to: 'capstone' });
  return { nodes, edges, width, height: tailY + 200, cardWidth, cardHeight, branchY };
}

interface ExportOptions { track: Track; level: Level; hours: number; completed: string[]; started?: string[] }
const escapeXml = (text: string) => text.replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' })[char]!);
const status = (id: string, options: ExportOptions) => options.completed.includes(id) ? '已完成' : options.started?.includes(id) ? '学习中' : '待学习';
const stroke = (track: Track | undefined, selected: Track) => !track || track === selected ? '#256b65' : '#929da8';

/** A standalone overview; personal notes are deliberately absent from diagram exports. */
export function svgDiagram(options: ExportOptions): string {
  const graph = graphLayout(options.level);
  const ranges = Object.fromEntries(trackIds.map(track => [track, stageWeeks(track, options.level, options.hours)]));
  const node = (id: string) => graph.nodes.find(item => item.id === id)!;
  const edges = graph.edges.map(edge => {
    const from = node(edge.from), to = node(edge.to);
    const x1 = from.x + 135, y1 = from.y + graph.cardHeight, x2 = to.x + 135, y2 = to.y;
    const mid = (y1 + y2) / 2;
    return `<path d="M${x1} ${y1} V${mid} H${x2} V${y2 - 5}" fill="none" stroke="${stroke(edge.track, options.track)}" stroke-width="2" marker-end="url(#arrow)"/>`;
  }).join('');
  const cards = graph.nodes.map(item => {
    const selected = !item.track || item.track === options.track;
    const completed = options.completed.includes(item.id);
    const line = `${item.stage.hours} 小时 · ${ranges[item.track ?? options.track][item.id]} · ${status(item.id, options)}`;
    return `<g><rect x="${item.x}" y="${item.y}" width="270" height="80" rx="10" fill="${completed ? '#e1f1e9' : selected ? '#f0f7f5' : '#f7f8fa'}" stroke="${stroke(item.track, options.track)}"/><text x="${item.x + 16}" y="${item.y + 31}" font-size="18" fill="#172b32">${escapeXml(stageNames[item.id])}</text><text x="${item.x + 16}" y="${item.y + 58}" font-size="13" fill="#53666d">${escapeXml(line)}</text></g>`;
  }).join('');
  const labels = trackIds.map((track, i) => `<rect x="${30 + i * 335}" y="${graph.branchY - 43}" width="270" height="29" fill="#ffffff"/><text x="${165 + i * 335}" y="${graph.branchY - 21}" text-anchor="middle" font-size="18" fill="${stroke(track, options.track)}">${escapeXml(tracks[track].title)}</text>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${graph.width}" height="${graph.height}" viewBox="0 0 ${graph.width} ${graph.height}" role="img" aria-labelledby="title desc"><title id="title">Razavi 学习路线图</title><desc id="desc">共同基础、三条学习分支与综合设计。箭头为建议阅读顺序，具体先修见网页。每周 ${options.hours} 小时。</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#929da8"/></marker></defs><rect width="100%" height="100%" fill="#ffffff"/><g font-family="system-ui, sans-serif"><text x="30" y="32" font-size="23" font-weight="600">Razavi 学习路线 · ${escapeXml(tracks[options.track].title)}</text><text x="30" y="53" font-size="12" fill="#53666d">每周 ${options.hours} 小时；箭头为建议顺序。参考、电源与滤波可在反馈之后穿插学习。</text>${edges}${labels}${cards}<text x="30" y="${graph.height - 14}" font-size="12" fill="#53666d">来源：www.seas.ucla.edu/brweb/journal.html · 周次按各方向独立估算 · 进度为导出时快照</text></g></svg>`;
}

export function excalidrawDiagram(options: ExportOptions): string {
  const graph = graphLayout(options.level);
  const ranges = Object.fromEntries(trackIds.map(track => [track, stageWeeks(track, options.level, options.hours)]));
  let sequence = 0;
  function base(id: string, type: string, x: number, y: number, width: number, height: number, color = '#256b65') {
    const seed = ++sequence;
    return { id, type, x, y, width, height, angle: 0, strokeColor: color, backgroundColor: 'transparent', fillStyle: 'solid', strokeWidth: 1, strokeStyle: 'solid', roughness: 1, opacity: 100, groupIds: [] as string[], frameId: null, roundness: null as null | { type: number }, seed, version: 1, versionNonce: seed, isDeleted: false, boundElements: null, updated: 0, link: null, locked: false };
  }
  function text(id: string, value: string, x: number, y: number, width: number, height: number, fontSize: number) {
    return { ...base(id, 'text', x, y, width, height, '#172b32'), text: value, originalText: value, fontSize, fontFamily: 2, textAlign: 'left', verticalAlign: 'top', containerId: null, autoResize: true, lineHeight: 1.25 };
  }
  const elements: unknown[] = [
    text('heading', `Razavi 学习路线 · ${tracks[options.track].title}`, 30, 8, 850, 30, 23),
    text('description', `每周 ${options.hours} 小时；箭头为建议阅读顺序。参考、电源与滤波可在反馈之后穿插学习。`, 30, 42, 930, 20, 13),
  ];
  for (const edge of graph.edges) {
    const from = graph.nodes.find(node => node.id === edge.from)!, to = graph.nodes.find(node => node.id === edge.to)!;
    const x = from.x + 135, y = from.y + 80, dx = to.x - from.x, dy = to.y - y;
    elements.push({ ...base(`edge-${edge.from}-${edge.to}`, 'arrow', x, y, Math.abs(dx), dy, stroke(edge.track, options.track)), points: [[0, 0], [0, dy / 2], [dx, dy / 2], [dx, dy]], lastCommittedPoint: null, startBinding: null, endBinding: null, startArrowhead: null, endArrowhead: 'arrow', elbowed: false });
  }
  trackIds.forEach((track, i) => {
    const backdrop = base(`track-bg-${track}`, 'rectangle', 30 + i * 335, graph.branchY - 43, 270, 29, '#ffffff');
    backdrop.backgroundColor = '#ffffff'; backdrop.roughness = 0;
    elements.push(backdrop, text(`track-${track}`, tracks[track].title, 30 + i * 335, graph.branchY - 39, 270, 25, 18));
  });
  for (const node of graph.nodes) {
    const box = base(`box-${node.id}`, 'rectangle', node.x, node.y, 270, 80, stroke(node.track, options.track));
    box.backgroundColor = options.completed.includes(node.id) ? '#e1f1e9' : !node.track || node.track === options.track ? '#f0f7f5' : '#f7f8fa';
    box.roundness = { type: 3 }; box.groupIds = [`group-${node.id}`];
    const label = text(`text-${node.id}`, `${stageNames[node.id]}\n${node.stage.hours}h · ${ranges[node.track ?? options.track][node.id]} · ${status(node.id, options)}`, node.x + 16, node.y + 17, 238, 46, 17);
    label.groupIds = box.groupIds;
    elements.push(box, label);
  }
  elements.push(text('source', '来源：www.seas.ucla.edu/brweb/journal.html · 周次按各方向独立估算 · 进度为导出时快照', 30, graph.height - 30, 930, 18, 12));
  return JSON.stringify({ type: 'excalidraw', version: 2, source: 'https://why250-circuits-classroom.pages.dev/learn/razavi/', elements, appState: { viewBackgroundColor: '#ffffff', gridSize: null }, files: {} }, null, 2);
}
