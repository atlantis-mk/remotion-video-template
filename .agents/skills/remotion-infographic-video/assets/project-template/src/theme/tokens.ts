// 自动生成，勿手改。来源：assets/tokens.json（scripts/scaffold_project.py）
export const TOKENS = {
  "colors": {
    "bg": "#070A0F",
    "card": "#121821",
    "text": "#F2F5F8",
    "textDim": "#8B98A8",
    "gold": "#F5C542",
    "green": "#3DDC97",
    "red": "#FF5C5C",
    "blue": "#4DA3FF",
    "purple": "#9B7BFF",
    "line": "#2A3544",
    "badge": "#1A2330",
    "badgeStroke": "#3A4A5C"
  },
  "gradients": {
    "gold": [
      "#FFE08A",
      "#F5C542",
      "#C8901A"
    ],
    "green": [
      "#8CF5C4",
      "#3DDC97",
      "#1E9E66"
    ],
    "red": [
      "#FF9A9A",
      "#FF5C5C",
      "#C23434"
    ],
    "blue": [
      "#9CCBFF",
      "#4DA3FF",
      "#1F6FD1"
    ],
    "purple": [
      "#C8B6FF",
      "#9B7BFF",
      "#6A48D6"
    ]
  },
  "glass": {
    "fill": "rgba(255,255,255,0.06)",
    "border": "rgba(255,255,255,0.12)",
    "blur": 18,
    "saturate": 140,
    "shadow": "0 24px 60px rgba(0,0,0,.45)"
  },
  "radius": {
    "sm": 10,
    "md": 18,
    "lg": 28,
    "pill": 999
  },
  "fonts": {
    "sans": "NotoSansSC",
    "mono": "JetBrainsMono"
  },
  "layout": {
    "$comment": "比例均相对画布；unit = 画布短边 / 基准短边（基准取 presets 横屏高度）。架构 v1.6 §5 比例表。",
    "fontSizes": {
      "display": 168,
      "h1": 120,
      "h2": 68,
      "h3": 42,
      "body": 30,
      "caption": 22
    },
    "headingScale": {
      "landscape": 1.0,
      "portrait": 0.8
    },
    "safe": {
      "landscape": {
        "top": 0.07,
        "right": 0.06,
        "bottom": 0.06,
        "left": 0.06
      },
      "portrait": {
        "top": 0.06,
        "right": 0.07,
        "bottom": 0.06,
        "left": 0.07
      }
    },
    "subtitleBand": {
      "landscape": 0.14,
      "portrait": 0.12
    },
    "hudBand": {
      "landscape": 0.05,
      "portrait": 0.04
    },
    "columnGap": 0.03
  },
  "motion": {
    "fps": 30,
    "spring": {
      "damping": 12,
      "stiffness": 130,
      "mass": 1
    },
    "slam": {
      "damping": 10,
      "stiffness": 160
    },
    "easing": [
      0.2,
      0.8,
      0.2,
      1
    ],
    "sectionIn": 14,
    "sectionOut": 10,
    "shotIn": 12,
    "shotBlur": 12
  },
  "background": {
    "particles": 46,
    "noiseOpacity": 0.07,
    "glowBlur": 30
  },
  "tones": [
    "gold",
    "green",
    "red",
    "blue",
    "purple"
  ]
} as const;

export type Tokens = typeof TOKENS;
export const COLORS = TOKENS.colors;
export const TONES = TOKENS.tones;
export type ToneKey = (typeof TOKENS.tones)[number];
export const LAYOUT_TOKENS = TOKENS.layout;
export const MOTION = TOKENS.motion;
export default TOKENS;
