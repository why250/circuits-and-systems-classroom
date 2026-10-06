import { describe, it, expect } from 'vitest';
import { articles, article, route, schedule, weekDate, type Track, type Level } from '../src/illustrations/razavi-roadmap/plan';
import { graphLayout, stageWeeks, stageNames, trackIds, svgDiagram, excalidrawDiagram } from '../src/illustrations/razavi-roadmap/graph';

describe('Razavi reading routes', () => {
  it('references real catalog entries and puts prerequisites before their dependents', () => {
    for (const track of ['adc', 'pll', 'links'] as Track[]) {
      for (const level of ['beginner', 'foundation'] as Level[]) {
        const stages = route(track, level);
        const seen = new Set<string>();
        for (const stage of stages) {
          expect(seen.has(stage.id)).toBe(false);
          stage.prerequisites.forEach(id => expect(seen.has(id)).toBe(true));
          stage.articles.forEach(id => expect(article(id).url).toMatch(/^https:\/\/www\.seas\.ucla\.edu\/brweb\/papers\/Journals\//));
          seen.add(stage.id);
        }
      }
    }
    expect(articles.filter(item => item.group === 'Analog Mind')).toHaveLength(22);
    expect(articles.filter(item => item.reviewed)).toHaveLength(7);
  });
  it('conserves learning hours and weekly capacity when stages cross weeks', () => {
    for (const track of ['adc', 'pll', 'links'] as Track[]) {
      for (const hours of [3, 6, 10, 15]) {
        const stages = route(track, 'beginner');
        const plan = schedule(stages, hours);
        const total = stages.reduce((sum, stage) => sum + stage.hours, 0);
        expect(plan.length).toBe(Math.ceil(total / hours));
        expect(plan.flatMap(week => week.tasks).reduce((sum, task) => sum + task.hours, 0)).toBe(total);
        plan.forEach(week => expect(week.tasks.reduce((sum, task) => sum + task.hours, 0)).toBeLessThanOrEqual(hours));
        for (const stage of stages) expect(plan.flatMap(week => week.tasks).filter(task => task.stage.id === stage.id).reduce((sum, task) => sum + task.hours, 0)).toBe(stage.hours);
      }
    }
    expect(schedule(route('adc', 'foundation'), 0)).toEqual([]);
  });
  it('keeps date-only schedules stable over year boundaries', () => {
    expect(weekDate('2026-12-28', 2)).toBe('2027/1/4');
    expect(weekDate('2026-10-05', 1)).toBe('2026/10/5');
  });
});

describe('route diagram and portable exports', () => {
  it('covers every stage once and connects only existing nodes, flowing downward', () => {
    for (const level of ['beginner', 'foundation'] as Level[]) {
      const graph = graphLayout(level);
      const expectedIds = new Set(trackIds.flatMap(track => route(track, level).map(stage => stage.id)));
      expect(graph.nodes).toHaveLength(expectedIds.size);
      expect(new Set(graph.nodes.map(node => node.id))).toEqual(expectedIds);
      for (const edge of graph.edges) {
        const from = graph.nodes.find(node => node.id === edge.from);
        const to = graph.nodes.find(node => node.id === edge.to);
        expect(from).toBeDefined(); expect(to).toBeDefined();
        expect(to!.y).toBeGreaterThanOrEqual(from!.y + graph.cardHeight);
      }
      for (const node of graph.nodes) {
        expect(stageNames[node.id]).toBeTruthy();
        expect(node.x + graph.cardWidth).toBeLessThanOrEqual(graph.width);
        expect(node.y + graph.cardHeight).toBeLessThanOrEqual(graph.height);
      }
    }
  });
  it('assigns shared stages their actual week range in each independent route', () => {
    expect(stageWeeks('adc', 'foundation', 6).feedback).toBe('第 1–2 周');
    expect(stageWeeks('adc', 'beginner', 6).entry).toBe('第 1–3 周');
    expect(stageWeeks('adc', 'beginner', 6).feedback).toBe('第 4–5 周');
    expect(stageWeeks('adc', 'foundation', 6).capstone).toBe('第 16–17 周');
    expect(stageWeeks('links', 'foundation', 6).capstone).toBe('第 15–16 周');
  });
  it('exports an editable scene with unique IDs and finite coordinates plus a standalone SVG', () => {
    const options = { track: 'pll' as Track, level: 'beginner' as Level, hours: 6, completed: ['entry', 'feedback'], started: ['phaseNoise'] };
    const scene = JSON.parse(excalidrawDiagram(options));
    expect(scene.type).toBe('excalidraw'); expect(scene.version).toBe(2);
    expect(new Set(scene.elements.map((element: { id: string }) => element.id)).size).toBe(scene.elements.length);
    const labels = scene.elements.filter((element: { type: string }) => element.type === 'text');
    expect(labels.find((element: { id: string }) => element.id === 'text-feedback').text).toContain('已完成');
    expect(labels.find((element: { id: string }) => element.id === 'text-phaseNoise').text).toContain('学习中');
    expect(labels.find((element: { id: string }) => element.id === 'text-recovery').text).toContain('待学习');
    for (const element of scene.elements) {
      expect([element.x, element.y, element.width, element.height].every(Number.isFinite)).toBe(true);
      expect(element.width).toBeGreaterThanOrEqual(0); expect(element.height).toBeGreaterThanOrEqual(0);
    }
    const svg = svgDiagram(options);
    expect(svg).toContain('xmlns="http://www.w3.org/2000/svg"');
    expect(svg).toContain('PLL / 射频时钟'); expect(svg).toContain('CDR 时钟恢复');
    expect(svg).toContain('进度为导出时快照');
  });
});
