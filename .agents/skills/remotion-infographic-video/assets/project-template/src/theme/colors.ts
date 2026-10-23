// 色名 → 色值（只认 tokens.json 中的色名，storyboard palette 也用色名）。
import { COLORS, TOKENS } from './tokens';

export type ToneName = 'gold' | 'green' | 'red' | 'blue' | 'purple';
const TONE_SET = new Set<string>(TOKENS.tones as readonly string[]);

export const isTone = (n: string): n is ToneName => TONE_SET.has(n);
/** 色名转色值；未知色名回退 gold */
export const toneColor = (name: string | undefined): string => {
  const c = (COLORS as Record<string, string>)[name ?? 'gold'];
  return c ?? COLORS.gold;
};
/** 色名的三段渐变 */
export const toneGradient = (name: string | undefined): readonly string[] => {
  const g = (TOKENS.gradients as Record<string, readonly string[]>)[name ?? 'gold'];
  return g ?? TOKENS.gradients.gold;
};
/** 给 #RRGGBB 加透明度（0..1），非 6 位 hex 原样返回 */
export const alpha = (hex: string, a: number): string => {
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return hex;
  const v = Math.round(Math.min(1, Math.max(0, a)) * 255).toString(16).padStart(2, '0');
  return hex + v;
};
