// 组件注册表（架构 v1.6 §4.12）：GenericScene 与 storyboard 校验共用的组件清单。
// 本文件只含元数据、不导入 remotion/React，可在 vitest 与 Node 中直接读取；组件实现映射见 ./index.ts。
export type ComponentGroup = 'container' | 'text' | 'data' | 'compliance' | 'media';

export interface ComponentMeta {
  group: ComponentGroup;
  summary: string;
  /** 必填 props（GenericScene 缺失时按 shot 数据补默认值） */
  required: readonly string[];
}

export const registry = {
  GlassPanel: { group: 'container', summary: '玻璃面板容器', required: ['children'] },
  Split: { group: 'container', summary: '横屏左右 / 竖屏上下分栏', required: ['primary', 'secondary'] },
  Shot: { group: 'container', summary: '镜头入场 push/rise/zoom，12 帧模糊→清晰', required: ['entrance', 'at', 'children'] },
  SectionTransition: { group: 'container', summary: '段转场 wipe/zoom/blur/slide/iris，入 14 帧/出 10 帧 + 光带', required: ['type', 'durationInFrames', 'tone', 'children'] },
  SlamTitle: { group: 'text', summary: '砸入大字', required: ['text', 'at'] },
  ImpactShake: { group: 'text', summary: '落地震动', required: ['at', 'children'] },
  KeywordPulse: { group: 'text', summary: '关键词脉冲强调', required: ['text', 'range'] },
  StepList: { group: 'text', summary: '步骤条逐个点亮', required: ['items', 'ranges'] },
  NumberRoll: { group: 'data', summary: '数字滚动（传 source 时自动带来源角标）', required: ['value', 'at'] },
  CompareBars: { group: 'data', summary: '对比柱（illustrative 时自带“示意”）', required: ['items', 'at'] },
  SourceBadge: { group: 'compliance', summary: '来源角标 / 素材署名', required: ['text'] },
  IllustrativeTag: { group: 'compliance', summary: '固定“示意”标', required: [] },
  MediaCard: { group: 'media', summary: '媒体卡片 3D 倾斜，带署名角标', required: ['src', 'at'] },
  FollowCTA: { group: 'media', summary: '关注引导', required: ['text', 'at'] },
  HoldFade: { group: 'media', summary: '定格淡出', required: ['startAt', 'durationInFrames', 'children'] },
} as const satisfies Record<string, ComponentMeta>;

export type ComponentName = keyof typeof registry;
export const COMPONENT_NAMES = Object.keys(registry) as ComponentName[];
export const isComponentName = (n: string): n is ComponentName => Object.prototype.hasOwnProperty.call(registry, n);
export default registry;
