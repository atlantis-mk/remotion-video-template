import React, { useMemo } from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { SECTIONS } from '../data/timeline';
import { useLayout } from '../layout/useLayout';
import { COLORS, TOKENS } from '../theme/tokens';
import { alpha, toneColor } from '../theme/colors';
import { particles } from './particles';

/** 背景层：渐变底 + 透视网格 + 段色光晕（按段交叉淡化）+ 粒子（固定种子）+ 噪点 + 暗角。全部按 width/height 生成。 */
export const BackgroundLayer: React.FC<{ palette?: { a: string; b: string } }> = ({ palette }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const L = useLayout();
  const { width: W, height: H, unit } = L;
  const cell = 80 * unit;
  const ps = useMemo(() => particles(W, H, 'bg', TOKENS.background.particles), [W, H]);
  const gridShift = (frame * 0.6 * unit) % cell;
  const t = frame / fps;
  const glowSize = Math.max(W, H) * 0.62;
  const blur = TOKENS.background.glowBlur * unit;
  const sections = palette ? [{ id: 'fixed', from: 0, to: Number.MAX_SAFE_INTEGER, palette }] : SECTIONS;
  return (
    <AbsoluteFill data-layer="background" style={{ backgroundColor: COLORS.bg, overflow: 'hidden' }}>
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bg} 0%, ${COLORS.card} 55%, ${COLORS.bg} 100%)` }} />
      {sections.map((s) => {
        const op = palette ? 1 : interpolate(frame, [s.from - 20, s.from + 10, s.to - 10, s.to + 20], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        if (op <= 0) return null;
        const a = toneColor(s.palette.a), b = toneColor(s.palette.b);
        return (
          <AbsoluteFill key={s.id} style={{ opacity: op }}>
            <div style={{ position: 'absolute', width: glowSize, height: glowSize, left: -glowSize * 0.3 + Math.sin(t * 0.35) * 90 * unit, top: H * 0.08 + Math.cos(t * 0.28) * 120 * unit, borderRadius: '50%', background: `radial-gradient(circle, ${alpha(a, 0.24)} 0%, ${alpha(a, 0.07)} 40%, transparent 70%)`, filter: `blur(${blur}px)` }} />
            <div style={{ position: 'absolute', width: glowSize * 0.9, height: glowSize * 0.9, right: -glowSize * 0.35 + Math.cos(t * 0.3) * 80 * unit, bottom: H * 0.06 + Math.sin(t * 0.25) * 140 * unit, borderRadius: '50%', background: `radial-gradient(circle, ${alpha(b, 0.2)} 0%, ${alpha(b, 0.05)} 45%, transparent 70%)`, filter: `blur(${blur}px)` }} />
          </AbsoluteFill>
        );
      })}
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${alpha(COLORS.text, 0.045)} 1px, transparent 1px), linear-gradient(90deg, ${alpha(COLORS.text, 0.045)} 1px, transparent 1px)`,
          backgroundSize: `${cell}px ${cell}px`,
          backgroundPosition: `0px ${-gridShift}px`,
          transform: `perspective(${1400 * unit}px) rotateX(18deg) scale(1.25)`,
          transformOrigin: '50% 100%',
          maskImage: 'radial-gradient(ellipse 85% 70% at 50% 45%, black 30%, transparent 85%)',
          WebkitMaskImage: 'radial-gradient(ellipse 85% 70% at 50% 45%, black 30%, transparent 85%)',
        }}
      />
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        {ps.map((p, i) => {
          const y = (((p.y - frame * p.speed * 1.4 * unit) % H) + H) % H;
          const x = p.x + Math.sin(frame / 40 + p.phase) * 14 * unit;
          const tw = 0.6 + 0.4 * Math.sin(frame / 18 + p.phase);
          return <circle key={i} cx={x} cy={y} r={p.r * 1.6} fill={COLORS.text} opacity={p.opacity * tw} />;
        })}
      </svg>
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0, opacity: TOKENS.background.noiseOpacity, mixBlendMode: 'overlay' }}>
        <filter id="bg-noise">
          <feTurbulence type="fractalNoise" baseFrequency={0.9 / Math.max(unit, 0.25)} numOctaves={2} seed={Math.floor(frame / 2) % 50} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#bg-noise)" />
      </svg>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 80% 65% at 50% 48%, transparent 55%, ${alpha(COLORS.bg, 0.75)} 100%)` }} />
    </AbsoluteFill>
  );
};
export default BackgroundLayer;
