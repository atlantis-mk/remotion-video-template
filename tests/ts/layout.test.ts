// L1 单元（TS）：computeLayout / presets（F-10）—— 架构 v1.3 §5：横屏 16:9 1920×1080，竖屏 3:4 1080×1440
import { describe, expect, test } from 'vitest';
import { json, load } from './helpers';

async function layout(w: number, h: number) {
  const m = await load('layout/computeLayout');
  const tokens = json('assets/tokens.json');
  expect(typeof m.computeLayout).toBe('function');
  return m.computeLayout(w, h, tokens.layout ?? tokens);
}
const inside = (L: any) => {
  expect(L.safe.left).toBeGreaterThan(0); expect(L.safe.top).toBeGreaterThan(0);
  expect(L.content.x).toBeGreaterThanOrEqual(L.safe.left);
  expect(L.content.y).toBeGreaterThanOrEqual(L.safe.top);
  expect(L.content.x + L.content.w).toBeLessThanOrEqual(L.width - L.safe.right + 1e-6);
  expect(L.content.y + L.content.h).toBeLessThanOrEqual(L.height - L.safe.bottom + 1e-6);
};
const BODY = { h3: 42, body: 30, caption: 22 } as const;
const HEAD = { display: 168, h1: 120, h2: 68 } as const;

describe('computeLayout', () => {
  test('[T-LAY-01] F-10 横屏 1920×1080：landscape、2 列、unit=1、content ⊆ safe ⊆ canvas', async () => {
    const L = await layout(1920, 1080);
    expect(L.orientation).toBe('landscape'); expect(L.columns).toBe(2); expect(L.unit).toBeCloseTo(1);
    inside(L);
  });
  test('[T-LAY-02] F-10 竖屏 3:4 1080×1440：portrait、1 列堆叠、unit=1、content ⊆ safe ⊆ canvas', async () => {
    const L = await layout(1080, 1440);
    expect(L.orientation).toBe('portrait'); expect(L.columns).toBe(1); expect(L.unit).toBeCloseTo(1);
    inside(L);
  });
  test('[T-LAY-03] F-10 字号：unit=min(w,h)/1080；横屏标题级 168/120/68，竖屏 headingScale 0.8 → 134/96/54；h3/body/caption 两种画幅均 42/30/22（随 unit 缩放）', async () => {
    const H = await layout(1920, 1080), V = await layout(1080, 1440);
    for (const [k, v] of Object.entries(HEAD)) { expect(H.font(k)).toBeCloseTo(v, 0); expect(V.font(k)).toBeCloseTo(v * 0.8, 0); }
    for (const [k, v] of Object.entries(BODY)) { expect(H.font(k)).toBeCloseTo(v, 3); expect(V.font(k)).toBeCloseTo(v, 3); }
    const H2 = await layout(3840, 2160); expect(H2.unit).toBeCloseTo(2); expect(H2.font('body')).toBeCloseTo(60, 3);
    const H3 = await layout(1280, 720); expect(H3.unit).toBeCloseTo(720 / 1080, 5);
  });
  test('[T-LAY-04] F-10 安全边距按画布尺寸推导（缩放画布，安全边距等比缩放）', async () => {
    const a = await layout(1920, 1080), b = await layout(3840, 2160);
    for (const k of ['top', 'right', 'bottom', 'left']) expect(b.safe[k]).toBeCloseTo(a.safe[k] * 2, 3);
  });
  test('[T-LAY-05] F-10 字幕 Y 与 HUD 位置位于画布安全区内（横 1920×1080、竖 1080×1440）', async () => {
    for (const [w, h] of [[1920, 1080], [1080, 1440]]) {
      const L = await layout(w, h);
      expect(L.subtitleY).toBeGreaterThan(L.safe.top); expect(L.subtitleY).toBeLessThan(h - L.safe.bottom);
      expect(L.hud.x).toBeGreaterThanOrEqual(L.safe.left); expect(L.hud.y).toBeGreaterThanOrEqual(L.safe.top);
    }
  });
  test('[T-LAY-06] F-10 v1.3 比例表：横屏 左右 0.06w、上 0.07h、下 0.06h；竖屏 左右 0.07w、上 0.06h、下 0.06h（±1px）', async () => {
    const H = await layout(1920, 1080), V = await layout(1080, 1440);
    const near = (a: number, b: number) => expect(Math.abs(a - b)).toBeLessThanOrEqual(1);
    near(H.safe.left, 0.06 * 1920); near(H.safe.right, 0.06 * 1920); near(H.safe.top, 0.07 * 1080); near(H.safe.bottom, 0.06 * 1080);
    near(V.safe.left, 0.07 * 1080); near(V.safe.right, 0.07 * 1080); near(V.safe.top, 0.06 * 1440); near(V.safe.bottom, 0.06 * 1440);
  });
  test('[T-LAY-07] F-10 竖屏 6 个汉字 display 标题放得下：font(display)×6 ≤ content.w；横屏单栏宽 ≥ font(display)×4', async () => {
    const V = await layout(1080, 1440); expect(V.font('display') * 6).toBeLessThanOrEqual(V.content.w);
    const H = await layout(1920, 1080); const colW = (H.content.w - 0.03 * 1920) / 2;
    expect(colW).toBeGreaterThanOrEqual(H.font('display') * 4);
  });
});

describe('presets', () => {
  test('[T-PRE-01] F-10 F-13 CANVAS_PRESETS 横 1920×1080 / 竖 1080×1440；COVER_PRESETS 横 [[1920,1080]] / 竖仅 [[1080,1440]]', async () => {
    const m = await load('layout/presets');
    expect(m.CANVAS_PRESETS.landscape).toEqual({ width: 1920, height: 1080 });
    expect(m.CANVAS_PRESETS.portrait).toEqual({ width: 1080, height: 1440 });
    expect(m.COVER_PRESETS.landscape).toEqual([[1920, 1080]]);
    expect(m.COVER_PRESETS.portrait).toEqual([[1080, 1440]]);
  });
});
