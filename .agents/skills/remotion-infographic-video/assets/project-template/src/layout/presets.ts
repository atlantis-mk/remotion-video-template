// 画布与封面尺寸的唯一常量处：其他文件禁止写死画布尺寸，一律从这里或 useLayout() 取。
// 横屏 16:9、竖屏 3:4（v1.3）。
export const CANVAS_PRESETS = { landscape: { width: 1920, height: 1080 }, portrait: { width: 1080, height: 1440 } } as const;
export const COVER_PRESETS = { landscape: [[1920, 1080]], portrait: [[1080, 1440]] } as const;
export type Aspect = keyof typeof CANVAS_PRESETS;
