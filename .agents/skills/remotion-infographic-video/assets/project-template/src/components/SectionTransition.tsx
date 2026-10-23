import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { useLayout } from '../layout/useLayout';
import { EASE, SECTION_IN, SECTION_OUT } from '../theme/motion';
import { alpha, toneColor } from '../theme/colors';

export type SectionTransitionType = 'wipe' | 'zoom' | 'blur' | 'slide' | 'iris';
export type SectionTransitionProps = { type: SectionTransitionType; durationInFrames: number; tone: { a: string; b: string }; children: React.ReactNode };

/** 段转场：入 SECTION_IN 帧、出 SECTION_OUT 帧，入场时扫过一条段色光带；段中间为恒等变换 */
export const SectionTransition: React.FC<SectionTransitionProps> = ({ type, durationInFrames, tone, children }) => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const inP = interpolate(frame, [0, SECTION_IN], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE });
  const outP = interpolate(frame, [durationInFrames - SECTION_OUT, durationInFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE });
  const q = 1 - inP; // 入场剩余量
  let style: React.CSSProperties = {};
  switch (type) {
    case 'wipe':
      style = { clipPath: `inset(0 ${q * 100}% 0 0)` };
      break;
    case 'zoom':
      style = { transform: `scale(${1 + q * 0.18 - outP * 0.06})` };
      break;
    case 'blur':
      style = { filter: q > 0 || outP > 0 ? `blur(${(q + outP) * 24 * L.unit}px)` : undefined };
      break;
    case 'slide':
      style = { transform: `translateX(${(q * 0.12 - outP * 0.06) * L.width}px)` };
      break;
    case 'iris':
      style = { clipPath: `circle(${inP * 75}% at 50% 50%)` };
      break;
  }
  const opacity = Math.min(inP * 1.5, 1) * (1 - outP);
  const band = interpolate(frame, [0, SECTION_IN + 4], [-0.3, 1.3], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ ...style, opacity }}>{children}</AbsoluteFill>
      {frame <= SECTION_IN + 4 ? (
        <AbsoluteFill
          style={{
            pointerEvents: 'none',
            background: `linear-gradient(100deg, transparent ${band * 100 - 12}%, ${alpha(toneColor(tone.a), 0.35)} ${band * 100}%, ${alpha(toneColor(tone.b), 0.2)} ${band * 100 + 6}%, transparent ${band * 100 + 14}%)`,
            mixBlendMode: 'screen',
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};
export default SectionTransition;
