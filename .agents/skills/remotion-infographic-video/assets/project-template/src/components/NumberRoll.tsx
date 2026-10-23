import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { EASE } from '../theme/motion';
import { toneGradient, type ToneName } from '../theme/colors';
import { COLORS } from '../theme/tokens';
import { FONT_MONO, FONT_SANS } from '../theme/fonts';
import { SourceBadge } from './SourceBadge';

export type NumberRollProps = {
  value: number; from?: number; at: number; duration?: number; prefix?: string; suffix?: string;
  decimals?: number; tone?: ToneName; source?: string; size?: 'display' | 'h1' | 'h2';
};

/** 数字滚动：at 起 duration 帧由 from 滚到 value；传 source 时自动渲染来源角标 */
export const NumberRoll: React.FC<NumberRollProps> = ({ value, from = 0, at, duration = 24, prefix = '', suffix = '', decimals = 0, tone = 'gold', source, size = 'display' }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const v = interpolate(frame, [at, at + duration], [from, value], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE });
  const g = toneGradient(tone);
  const fs = L.font(size);
  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', gap: fs * 0.12 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: fs * 0.08 }}>
        {prefix ? <span style={{ fontFamily: FONT_SANS, fontWeight: 700, fontSize: fs * 0.4, color: COLORS.text }}>{prefix}</span> : null}
        <span
          style={{
            fontFamily: FONT_MONO, fontWeight: 800, fontSize: fs, lineHeight: 1, fontVariantNumeric: 'tabular-nums',
            background: `linear-gradient(180deg, ${g[0]}, ${g[1]} 60%, ${g[2]})`, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
          }}
        >
          {v.toFixed(decimals)}
        </span>
        {suffix ? <span style={{ fontFamily: FONT_SANS, fontWeight: 700, fontSize: fs * 0.4, color: COLORS.text }}>{suffix}</span> : null}
      </div>
      {source ? <SourceBadge text={source} /> : null}
    </div>
  );
};
export default NumberRoll;
