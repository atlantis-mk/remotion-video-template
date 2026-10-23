// L1 单元（TS）：背景粒子 particles(width,height,seed,count) —— src/layers/particles.ts（Q-22）（NF-05、F-10）
import { describe, expect, test } from 'vitest';
import { load } from './helpers';

async function particles() {
  const m = await load('layers/particles');
  expect(typeof m.particles).toBe('function'); return m.particles;
}
describe('particles', () => {
  test('[T-DET-01] NF-05 相同 width/height/seed/count 输出完全一致；不同 seed 输出不同', async () => {
    const p = await particles();
    expect(p(1920, 1080, 'bg', 46)).toEqual(p(1920, 1080, 'bg', 46));
    expect(p(1920, 1080, 'bg', 46)).not.toEqual(p(1920, 1080, 'other', 46));
  });
  test('[T-DET-02] F-10 R-05 Particle{x,y,r,speed,opacity,phase} 均为有限数；0≤x<w、0≤y<h、r>0、0<opacity≤1；同参数深相等；随画布尺寸变化（不写死 1080/1920）', async () => {
    const p = await particles();
    for (const [w, h] of [[1920, 1080], [1080, 1440], [1280, 720]]) {
      const ps = p(w, h, 'bg', 46); expect(ps.length).toBe(46);
      for (const q of ps) {
        for (const k of ['x', 'y', 'r', 'speed', 'opacity', 'phase']) expect(typeof (q as any)[k], k).toBe('number');
        for (const k of ['x', 'y', 'r', 'speed', 'opacity', 'phase']) expect(Number.isFinite((q as any)[k]), k).toBe(true);
        expect(q.x).toBeGreaterThanOrEqual(0); expect(q.x).toBeLessThan(w);
        expect(q.y).toBeGreaterThanOrEqual(0); expect(q.y).toBeLessThan(h);
        expect(q.r).toBeGreaterThan(0);
        expect(q.opacity).toBeGreaterThan(0); expect(q.opacity).toBeLessThanOrEqual(1);
      }
      expect(p(w, h, 'bg', 46)).toEqual(ps);   // R-05：同参数两次调用深相等
    }
    expect(p(1920, 1080, 'bg', 46)).not.toEqual(p(1080, 1440, 'bg', 46));
  });
  test('[T-DET-03] NF-05 粒子数严格等于 count 参数（参考项目 46），且不依赖 Math.random', async () => {
    const p = await particles(); const orig = Math.random;
    Math.random = () => { throw new Error('禁止 Math.random'); };
    try { expect(p(1920, 1080, 'bg', 46).length).toBe(46); expect(p(1920, 1080, 'bg', 10).length).toBe(10); }
    finally { Math.random = orig; }
  });
});
