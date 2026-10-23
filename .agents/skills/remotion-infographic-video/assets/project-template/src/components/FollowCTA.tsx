import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { springIn } from '../theme/motion';
import { alpha, toneGradient } from '../theme/colors';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';

export type FollowCTAProps = { text: string; at: number };

/** 关注引导：胶囊按钮弹入 + 光泽扫过 */
export const FollowCTA: React.FC<FollowCTAProps> = ({ text, at }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const L = useLayout();
  const s = springIn(frame - at, fps);
  const g = toneGradient('gold');
  const fs = L.font('h2');
  const shine = interpolate((frame - at) % 60, [0, 30], [-30, 130], { extrapolateRight: 'clamp' });
  return (
    <div
      style={{
        display: 'inline-flex', alignItems: 'center', gap: fs * 0.4, transform: `scale(${0.6 + s * 0.4})`, opacity: Math.min(1, s * 1.4),
        padding: `${fs * 0.35}px ${fs * 0.9}px`, borderRadius: fs, fontFamily: FONT_SANS, fontWeight: 900, fontSize: fs, color: COLORS.bg,
        background: `linear-gradient(100deg, ${g[1]} ${shine - 20}%, ${g[0]} ${shine}%, ${g[1]} ${shine + 20}%)`,
        boxShadow: `0 ${10 * L.unit}px ${40 * L.unit}px ${alpha(COLORS.gold, 0.4)}`, whiteSpace: 'nowrap',
      }}
    >
      <span style={{ fontSize: fs * 0.8 }}>＋</span>
      {text}
    </div>
  );
};
export default FollowCTA;
