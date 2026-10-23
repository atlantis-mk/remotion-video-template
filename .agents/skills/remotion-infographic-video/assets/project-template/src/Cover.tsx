import React from 'react';
import { AbsoluteFill } from 'remotion';
import { SECTIONS } from './data/timeline';
import { JOB_META } from './data/job';
import { BackgroundLayer } from './layers/BackgroundLayer';
import { SafeAreaProbe } from './debug/SafeAreaProbe';
import { useLayout } from './layout/useLayout';
import { COLORS } from './theme/tokens';
import { alpha, toneColor, toneGradient } from './theme/colors';
import { FONT_SANS } from './theme/fonts';

/** 封面 Still 的尺寸由 props 传入（render.sh：--props='{"width":W,"height":H}'），内部同样走 computeLayout */
export type CoverProps = { width: number; height: number; title?: string };

export const Cover: React.FC<CoverProps> = ({ title }) => {
  const L = useLayout();
  const meta = JOB_META as { topic?: string };
  const text = title ?? meta.topic ?? SECTIONS[0]?.title ?? '';
  const palette = SECTIONS[0]?.palette ?? { a: 'gold', b: 'blue' };
  const maxLines = L.columns === 2 ? 2 : 3;
  const len = Math.max(1, Array.from(text).length);
  const fs = Math.min(L.font('display'), ((L.content.w * maxLines) / len) * 0.9);
  const g = toneGradient(palette.a);
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <BackgroundLayer palette={palette} />
      <AbsoluteFill data-layer="scene">
        <div style={{ position: 'absolute', left: L.content.x, top: L.content.y, width: L.content.w, height: L.content.h, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: fs * 0.4 }}>
          <div style={{ width: fs * 2, height: Math.max(3, 8 * L.unit), borderRadius: 8 * L.unit, background: toneColor(palette.a), boxShadow: `0 0 ${30 * L.unit}px ${alpha(toneColor(palette.a), 0.6)}` }} />
          <div
            style={{
              fontFamily: FONT_SANS, fontWeight: 900, fontSize: fs, lineHeight: 1.18, textAlign: 'center', maxWidth: L.content.w,
              background: `linear-gradient(180deg, ${COLORS.text}, ${g[0]} 70%, ${g[1]})`, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
            }}
          >
            {text}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 14 * L.unit, maxWidth: L.content.w }}>
            {SECTIONS.map((s) => (
              <span key={s.id} style={{ fontFamily: FONT_SANS, fontSize: L.font('body'), fontWeight: 700, color: COLORS.text, padding: `${6 * L.unit}px ${18 * L.unit}px`, borderRadius: 999, border: `${Math.max(1, 1.5 * L.unit)}px solid ${alpha(toneColor(s.palette.a), 0.6)}`, background: alpha(toneColor(s.palette.a), 0.12) }}>
                {s.title}
              </span>
            ))}
          </div>
        </div>
      </AbsoluteFill>
      <SafeAreaProbe />
    </AbsoluteFill>
  );
};
export default Cover;
