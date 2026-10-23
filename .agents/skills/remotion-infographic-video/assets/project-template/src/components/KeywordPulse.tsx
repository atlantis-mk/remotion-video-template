import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { alpha, toneColor, type ToneName } from '../theme/colors';
import { FONT_SANS } from '../theme/fonts';
import type { Range } from '../timing/lines';

export type KeywordPulseProps = { text: string; range: Range; tone?: ToneName };

/** 关键词脉冲：区间内呼吸式放大 + 光晕 */
export const KeywordPulse: React.FC<KeywordPulseProps> = ({ text, range, tone = 'gold' }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const c = toneColor(tone);
  const inP = interpolate(frame, [range.from, range.from + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const pulse = frame >= range.from && frame < range.to ? 0.5 + 0.5 * Math.sin(((frame - range.from) / 18) * Math.PI * 2) : 0;
  return (
    <span
      style={{
        display: 'inline-block',
        fontFamily: FONT_SANS,
        fontWeight: 900,
        fontSize: L.font('h1'),
        color: c,
        opacity: inP,
        transform: `scale(${0.96 + pulse * 0.06})`,
        textShadow: `0 0 ${(16 + pulse * 26) * L.unit}px ${alpha(c, 0.6)}`,
        padding: `0 ${0.2 * L.font('h1')}px`,
      }}
    >
      {text}
    </span>
  );
};
export default KeywordPulse;
