import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { alpha, toneColor, type ToneName } from '../theme/colors';
import { COLORS } from '../theme/tokens';
import { FONT_MONO, FONT_SANS } from '../theme/fonts';
import type { Range } from '../timing/lines';

export type StepListProps = { items: string[]; ranges: Range[]; activeTone?: ToneName };

/** 步骤条：第 i 项在 ranges[i].from 入场并高亮，区间结束后保持“已完成”态。横屏两列、竖屏单列。 */
export const StepList: React.FC<StepListProps> = ({ items, ranges, activeTone = 'blue' }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const c = toneColor(activeTone);
  const cols = L.columns === 2 && items.length > 5 ? 2 : 1;
  const perCol = Math.ceil(items.length / cols);
  const fs = L.font(items.length > 6 && cols === 1 ? 'body' : 'h3') * (cols === 2 ? 0.9 : 1);
  const col = (k: number) => items.slice(k * perCol, (k + 1) * perCol).map((t, j) => {
    const i = k * perCol + j;
    const r = ranges[i] ?? ranges[ranges.length - 1] ?? { from: 0, to: 0 };
    const inP = interpolate(frame, [r.from, r.from + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    const active = frame >= r.from && frame < r.to;
    return (
      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: fs * 0.6, opacity: 0.25 + inP * 0.75, transform: `translateX(${(1 - inP) * 24 * L.unit}px)` }}>
        <span
          style={{
            fontFamily: FONT_MONO, fontWeight: 700, fontSize: fs * 0.8, width: fs * 1.6, height: fs * 1.6, borderRadius: fs,
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            color: active ? COLORS.bg : COLORS.text, background: active ? c : alpha(c, inP > 0.5 ? 0.25 : 0.08),
          }}
        >
          {i}
        </span>
        <span style={{ fontFamily: FONT_SANS, fontWeight: active ? 700 : 500, fontSize: fs, color: active ? COLORS.text : COLORS.textDim, whiteSpace: 'nowrap' }}>{t}</span>
      </div>
    );
  });
  return (
    <div style={{ display: 'flex', gap: L.gap * 1.5, justifyContent: 'center' }}>
      {Array.from({ length: cols }, (_, k) => (
        <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: fs * 0.55 }}>{col(k)}</div>
      ))}
    </div>
  );
};
export default StepList;
