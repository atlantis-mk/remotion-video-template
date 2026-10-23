import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { TOKENS } from '../theme/tokens';
import { alpha, toneColor, type ToneName } from '../theme/colors';

export type GlassPanelProps = { children: React.ReactNode; tone?: ToneName; radius?: 'sm' | 'md' | 'lg' | 'pill'; delay?: number; style?: React.CSSProperties };

/** 玻璃面板：半透明填充 + 描边 + 背景模糊 + 段色顶边光 */
export const GlassPanel: React.FC<GlassPanelProps> = ({ children, tone, radius = 'lg', delay = 0, style }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const o = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const edge = tone ? toneColor(tone) : TOKENS.glass.border;
  return (
    <div
      style={{
        position: 'relative',
        boxSizing: 'border-box',
        padding: 36 * L.unit,
        borderRadius: TOKENS.radius[radius] * L.unit,
        background: TOKENS.glass.fill,
        border: `${Math.max(1, 1.5 * L.unit)}px solid ${TOKENS.glass.border}`,
        boxShadow: `${TOKENS.glass.shadow}, inset 0 ${2 * L.unit}px 0 ${tone ? alpha(edge, 0.55) : TOKENS.glass.border}`,
        backdropFilter: `blur(${TOKENS.glass.blur * L.unit}px) saturate(${TOKENS.glass.saturate}%)`,
        opacity: o,
        maxWidth: '100%',
        ...style,
      }}
    >
      {children}
    </div>
  );
};
export default GlassPanel;
