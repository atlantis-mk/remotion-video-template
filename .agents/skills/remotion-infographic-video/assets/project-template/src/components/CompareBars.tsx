import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { EASE } from '../theme/motion';
import { alpha, toneColor, toneGradient, type ToneName } from '../theme/colors';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';
import { NumberRoll } from './NumberRoll';
import { SourceBadge } from './SourceBadge';
import { IllustrativeTag } from './IllustrativeTag';

export type CompareBarsProps = { items: { label: string; value: number; tone?: ToneName }[]; at: number; unit?: string; source?: string; illustrative?: boolean };

/** 对比柱：柱高按最大值归一，数值用 NumberRoll 滚动；illustrative 时自带“示意”，source 时带来源角标 */
export const CompareBars: React.FC<CompareBarsProps> = ({ items, at, unit = '', source, illustrative }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const max = Math.max(1, ...items.map((i) => i.value));
  const barMaxH = L.content.h * (L.columns === 2 ? 0.42 : 0.34);
  const barW = Math.min(L.content.w / (items.length * 2.2), 220 * L.unit);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 * L.unit }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: barW * 0.9 }}>
        {items.map((it, i) => {
          const tone = it.tone ?? (['gold', 'blue', 'green', 'purple', 'red'] as const)[i % 5];
          const p = interpolate(frame, [at + i * 6, at + i * 6 + 22], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE });
          const g = toneGradient(tone);
          return (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 * L.unit }}>
              <NumberRoll value={it.value} at={at + i * 6} duration={22} suffix={unit} tone={tone} size="h2" />
              <div
                style={{
                  width: barW, height: Math.max(2, barMaxH * (it.value / max) * p), borderRadius: `${12 * L.unit}px ${12 * L.unit}px 0 0`,
                  background: `linear-gradient(180deg, ${g[0]}, ${g[2]})`, boxShadow: `0 0 ${30 * L.unit}px ${alpha(toneColor(tone), 0.35)}`,
                }}
              />
              <span style={{ fontFamily: FONT_SANS, fontSize: L.font('body'), fontWeight: 700, color: COLORS.text }}>{it.label}</span>
            </div>
          );
        })}
      </div>
      {source || illustrative ? (
        <div style={{ display: 'flex', gap: 12 * L.unit, alignItems: 'center' }}>
          {source ? <SourceBadge text={source} /> : null}
          {illustrative ? <IllustrativeTag /> : null}
        </div>
      ) : null}
    </div>
  );
};
export default CompareBars;
