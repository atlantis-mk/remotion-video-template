// L1/L2（TS）：段/句帧区间纯函数、组件注册表、ajv 交叉校验 Schema（F-06、F-07、F-09、F-15）
import { describe, expect, test } from 'vitest';
import Ajv2020 from 'ajv/dist/2020';
import { json, load } from './helpers';

const LINES = [{ id: '01', section: 'S01', from: 0, to: 90 }, { id: '02', section: 'S01', from: 90, to: 200 }, { id: '03', section: 'S02', from: 200, to: 301 }];

describe('frame helpers (src/timing/lines.ts，Q-22)', () => {
  test('[T-FR-01] F-06 resolveLine(frame, lines, sectionStartFrame)：段内本地帧 → 所在句；末帧 300 属于末句', async () => {
    const m = await load('timing/lines');
    expect(m.resolveLine(0, LINES, 0).id).toBe('01'); expect(m.resolveLine(90, LINES, 0).id).toBe('02');
    expect(m.resolveLine(100, LINES, 200).id).toBe('03'); expect(m.resolveLine(0, LINES, 200).id).toBe('03');
  });
  test('[T-FR-02] F-06 lineLocalRange(id, lines, sectionStartFrame) 返回句相对段起点的本地帧区间', async () => {
    const m = await load('timing/lines');
    expect(m.lineLocalRange('03', LINES, 200)).toEqual({ from: 0, to: 101 });
    expect(m.lineLocalRange('02', LINES, 0)).toEqual({ from: 90, to: 200 });
  });
  test('[T-FR-03] F-06 timing/lines.ts 是纯函数模块：不导入 remotion（vitest 无需 Remotion 运行时）', async () => {
    const { readFileSync, existsSync } = await import('node:fs'); const path = await import('node:path');
    const { TEMPLATE_SRC } = await import('./helpers'); const f = path.join(TEMPLATE_SRC, 'timing', 'lines.ts');
    if (!existsSync(f)) throw new Error(`未实现：缺少 ${f}`);
    expect(readFileSync(f, 'utf8')).not.toMatch(/from\s+['"]remotion['"]/);
  });
});

describe('registry', () => {
  test('[T-REG-01] F-09 F-07 components/registry 注册架构 §4.12 清单全部组件', async () => {
    const m = await load('components/registry');
    const reg = m.registry ?? m.COMPONENTS ?? m.default; expect(reg).toBeTruthy();
    for (const n of ['GlassPanel', 'Split', 'Shot', 'SectionTransition', 'SlamTitle', 'ImpactShake', 'KeywordPulse', 'StepList',
      'NumberRoll', 'CompareBars', 'SourceBadge', 'IllustrativeTag', 'MediaCard', 'FollowCTA', 'HoldFade']) expect(Object.keys(reg)).toContain(n);
  });
});

describe('ajv cross-check', () => {
  const ajv = () => new Ajv2020({ allErrors: true, strict: false });
  test('[T-AJV-01] F-07 示例 storyboard.json 通过 storyboard.schema.json（ajv 2020-12）', () => {
    const v = ajv().compile(json('assets/schemas/storyboard.schema.json'));
    expect(v(json('assets/example/storyboard.json')), JSON.stringify(v.errors)).toBe(true);
  });
  test('[T-AJV-02] F-05 F-15 示例 timeline.fixture.json 与 MCP fixture 通过同一 timeline.schema.json', async () => {
    const v = ajv().compile(json('assets/schemas/timeline.schema.json'));
    expect(v(json('assets/example/timeline.fixture.json')), JSON.stringify(v.errors)).toBe(true);
    const { readFileSync } = await import('node:fs');
    const good = JSON.parse(readFileSync(new URL('../fixtures/mcp_timeline_good.json', import.meta.url), 'utf8'));
    const bad = JSON.parse(readFileSync(new URL('../fixtures/mcp_timeline_bad.json', import.meta.url), 'utf8'));
    expect(v(good)).toBe(true); expect(v(bad)).toBe(false);
  });
  test('[T-AJV-03] F-07 storyboard 中 palette 只能用 tokens 色名，不能用色值', () => {
    const v = ajv().compile(json('assets/schemas/storyboard.schema.json'));
    const sb = structuredClone(json('assets/example/storyboard.json')); sb.sections[0].palette.a = '#F5C542';
    expect(v(sb)).toBe(false);
  });
});
