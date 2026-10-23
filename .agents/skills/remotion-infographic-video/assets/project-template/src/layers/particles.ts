// 背景粒子纯函数（NF-05）：同 width/height/seed/count → 完全相同输出；不使用全局随机数。
// 不导入 remotion，便于单测；伪随机为字符串种子哈希 + mulberry32，行为与 Remotion random(seed) 一样确定。
export interface Particle { x: number; y: number; r: number; speed: number; opacity: number; phase: number }

function hash(str: string): number {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h >>> 0;
}

/** 由种子字符串得到 [0,1) 的确定性随机数 */
export function seeded(seed: string): number {
  let t = (hash(seed) + 0x6d2b79f5) >>> 0;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

export function particles(width: number, height: number, seed: string, count: number): Particle[] {
  const unit = Math.min(width, height);
  const out: Particle[] = [];
  for (let i = 0; i < count; i++) {
    const k = `${seed}:${width}x${height}:${i}`;
    out.push({
      x: seeded(`${k}:x`) * width,
      y: seeded(`${k}:y`) * height,
      r: unit * (0.001 + seeded(`${k}:r`) * 0.0024),
      speed: 0.25 + seeded(`${k}:v`) * 0.9,
      opacity: 0.15 + seeded(`${k}:a`) * 0.45,
      phase: seeded(`${k}:p`) * Math.PI * 2,
    });
  }
  return out;
}
