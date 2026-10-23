import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

export type HoldFadeProps = { startAt: number; durationInFrames: number; children: React.ReactNode };

/** 定格淡出：startAt 起 durationInFrames 帧内淡出并轻微放大（片尾在末句内收束，不加额外帧） */
export const HoldFade: React.FC<HoldFadeProps> = ({ startAt, durationInFrames, children }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [startAt, startAt + Math.max(1, durationInFrames)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return <div style={{ opacity: 1 - p, transform: `scale(${1 + p * 0.04})`, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>{children}</div>;
};
export default HoldFade;
