// 本地字体（SIL OFL 1.1，许可证见 public/fonts/OFL-*.txt）：Noto Sans SC Regular/Bold + JetBrains Mono。
// 渲染前用 delayRender 等待加载完成，保证离线与确定性（NF-05）。
import { cancelRender, continueRender, delayRender, staticFile } from 'remotion';
import { TOKENS } from './tokens';

export const FONT_SANS = `${TOKENS.fonts.sans}, sans-serif`;
export const FONT_MONO = `${TOKENS.fonts.mono}, ${TOKENS.fonts.sans}, monospace`;

const FACES: { family: string; file: string; weight: string }[] = [
  { family: TOKENS.fonts.sans, file: 'fonts/NotoSansSC-Regular.ttf', weight: '100 500' },
  { family: TOKENS.fonts.sans, file: 'fonts/NotoSansSC-Bold.ttf', weight: '600 900' },
  { family: TOKENS.fonts.mono, file: 'fonts/JetBrainsMono-Medium.ttf', weight: '100 900' },
];

let ready: Promise<void> | null = null;
/** 开始加载字体（幂等），渲染等待其完成；返回的 Promise 供安全区探针等待 */
export const ensureFonts = (): Promise<void> => {
  if (ready) return ready;
  if (typeof document === 'undefined' || typeof FontFace === 'undefined') return (ready = Promise.resolve());
  const handle = delayRender('加载本地字体');
  ready = Promise.all(
    FACES.map((f) => new FontFace(f.family, `url(${staticFile(f.file)})`, { weight: f.weight }).load().then((ff) => { document.fonts.add(ff); })),
  )
    .then(() => continueRender(handle))
    .catch((e) => cancelRender(e));
  return ready;
};
