import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { springIn } from '../theme/motion';
import { toneGradient, type ToneName } from '../theme/colors';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';

export type SlamTitleProps = { text: string; at: number; size?: 'display' | 'h1'; tone?: ToneName };

/** 砸入大字：从放大模糊砸到 1 倍，渐变填色；超宽自动换行（宽度不超过内容区） */
export const SlamTitle: React.FC<SlamTitleProps> = ({ text, at, size = 'display', tone = 'gold' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const L = useLayout();
  const s = springIn(frame - at, fps, 'slam');
  const scale = interpolate(s, [0, 1], [2.4, 1]);
  const o = interpolate(frame - at, [0, 4], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const g = toneGradient(tone);
  return (
    <div style={{ width: '100%', textAlign: 'center', transform: `scale(${scale})`, opacity: o }}>
      <span
        style={{
          fontFamily: FONT_SANS,
          fontWeight: 900,
          fontSize: L.font(size),
          lineHeight: 1.15,
          letterSpacing: '0.02em',
          background: `linear-gradient(180deg, ${g[0]}, ${g[1]} 55%, ${g[2]})`,
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          color: 'transparent',
          textShadow: 'none',
          filter: `drop-shadow(0 ${6 * L.unit}px ${18 * L.unit}px ${COLORS.bg})`,
          wordBreak: 'keep-all',
          overflowWrap: 'anywhere',
        }}
      >
        {text}
      </span>
    </div>
  );
};
export default SlamTitle;
