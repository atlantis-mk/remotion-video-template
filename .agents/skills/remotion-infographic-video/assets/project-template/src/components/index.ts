// 组件实现映射：键集合必须与 registry.ts 完全一致（由类型保证）。
import type React from 'react';
import type { ComponentName } from './registry';
import { GlassPanel } from './GlassPanel';
import { Split } from './Split';
import { Shot } from './Shot';
import { SectionTransition } from './SectionTransition';
import { SlamTitle } from './SlamTitle';
import { ImpactShake } from './ImpactShake';
import { KeywordPulse } from './KeywordPulse';
import { StepList } from './StepList';
import { NumberRoll } from './NumberRoll';
import { CompareBars } from './CompareBars';
import { SourceBadge } from './SourceBadge';
import { IllustrativeTag } from './IllustrativeTag';
import { MediaCard } from './MediaCard';
import { FollowCTA } from './FollowCTA';
import { HoldFade } from './HoldFade';

export { GlassPanel, Split, Shot, SectionTransition, SlamTitle, ImpactShake, KeywordPulse, StepList, NumberRoll, CompareBars, SourceBadge, IllustrativeTag, MediaCard, FollowCTA, HoldFade };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const COMPONENT_MAP: Record<ComponentName, React.FC<any>> = {
  GlassPanel, Split, Shot, SectionTransition, SlamTitle, ImpactShake, KeywordPulse, StepList, NumberRoll, CompareBars, SourceBadge, IllustrativeTag, MediaCard, FollowCTA, HoldFade,
};
