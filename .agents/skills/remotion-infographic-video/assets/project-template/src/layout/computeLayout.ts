// 布局核心纯函数（架构 v1.6 §5）。渲染（useLayout）与安全区检测（scripts/safe-area.mjs 经页面内探针）共用。
// 不导入 remotion，可在 vitest 中直接测试。所有尺寸由画布宽高 + tokens.layout 比例推导。
import { CANVAS_PRESETS } from './presets';

export type Orientation = 'landscape' | 'portrait';
export type FontKey = 'display' | 'h1' | 'h2' | 'h3' | 'body' | 'caption';
type Sides = { top: number; right: number; bottom: number; left: number };
type PerOrientation<T> = { landscape: T; portrait: T };

export interface LayoutTokens {
  fontSizes: Record<FontKey, number>;
  headingScale: PerOrientation<number>;
  safe: PerOrientation<Sides>;
  subtitleBand: PerOrientation<number>;
  hudBand: PerOrientation<number>;
  columnGap: number;
}

export interface Layout {
  width: number;
  height: number;
  orientation: Orientation;
  /** = min(w,h) / 基准短边；横屏与竖屏两种预设下均为 1 */
  unit: number;
  /** 安全边距（绝对 px） */
  safe: Sides;
  /** 安全区矩形（绝对 px） */
  safeRect: { x: number; y: number; w: number; h: number };
  /** 内容区 = 安全区 − HUD 带 − 字幕带 */
  content: { x: number; y: number; w: number; h: number };
  columns: 1 | 2;
  /** 栏间距（px） */
  gap: number;
  font: (k: FontKey) => number;
  /** 字幕带垂直中心 */
  subtitleY: number;
  subtitleBand: { y: number; h: number };
  hud: { x: number; y: number; w: number; h: number };
}

/** 基准短边：取 presets 横屏高度（唯一常量处），避免在此写死数字 */
export const BASE_SHORT_SIDE: number = CANVAS_PRESETS.landscape.height;

const HEADINGS: ReadonlySet<FontKey> = new Set<FontKey>(['display', 'h1', 'h2']);

export function computeLayout(width: number, height: number, tokens: LayoutTokens): Layout {
  const orientation: Orientation = width >= height ? 'landscape' : 'portrait';
  const unit = Math.min(width, height) / BASE_SHORT_SIDE;
  const s = tokens.safe[orientation];
  const safe = { top: s.top * height, right: s.right * width, bottom: s.bottom * height, left: s.left * width };
  const safeRect = { x: safe.left, y: safe.top, w: width - safe.left - safe.right, h: height - safe.top - safe.bottom };
  const hudH = tokens.hudBand[orientation] * height;
  const subH = tokens.subtitleBand[orientation] * height;
  const content = { x: safeRect.x, y: safeRect.y + hudH, w: safeRect.w, h: safeRect.h - hudH - subH };
  const subtitleBand = { y: height - safe.bottom - subH, h: subH };
  const scale = tokens.headingScale[orientation];
  const font = (k: FontKey) => tokens.fontSizes[k] * unit * (HEADINGS.has(k) ? scale : 1);
  return {
    width, height, orientation, unit, safe, safeRect, content,
    columns: orientation === 'landscape' ? 2 : 1,
    gap: tokens.columnGap * width,
    font,
    subtitleY: subtitleBand.y + subH / 2,
    subtitleBand,
    hud: { x: safeRect.x, y: safeRect.y, w: safeRect.w, h: hudH },
  };
}

/** 矩形 a 是否完全位于 b 内（容差 tol px） */
export function rectInside(a: { x: number; y: number; w: number; h: number }, b: { x: number; y: number; w: number; h: number }, tol = 1): boolean {
  return a.x >= b.x - tol && a.y >= b.y - tol && a.x + a.w <= b.x + b.w + tol && a.y + a.h <= b.y + b.h + tol;
}
