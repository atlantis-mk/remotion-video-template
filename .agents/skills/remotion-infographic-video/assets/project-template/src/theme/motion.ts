// 动效参数统一出口：全部取自 tokens.json.motion（spring damping 10–14、stiffness 100–160、bezier(0.2,0.8,0.2,1)）。
import { Easing, interpolate, spring } from 'remotion';
import { MOTION } from './tokens';

const [x1, y1, x2, y2] = MOTION.easing;
export const EASE = Easing.bezier(x1, y1, x2, y2);
export const SECTION_IN = MOTION.sectionIn;
export const SECTION_OUT = MOTION.sectionOut;
export const SHOT_IN = MOTION.shotIn;
export const SHOT_BLUR = MOTION.shotBlur;

/** 标准弹簧：frame 为相对起点的帧（<0 时为 0） */
export const springIn = (frame: number, fps: number, kind: 'spring' | 'slam' = 'spring') =>
  spring({ frame: Math.max(0, frame), fps, config: kind === 'slam' ? { damping: MOTION.slam.damping, stiffness: MOTION.slam.stiffness } : { damping: MOTION.spring.damping, stiffness: MOTION.spring.stiffness, mass: MOTION.spring.mass } });

/** 0..1 缓动进度 */
export const ease01 = (frame: number, start: number, duration: number) =>
  interpolate(frame, [start, start + Math.max(1, duration)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE });
