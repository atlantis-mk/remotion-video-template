// 安全区探针（F-10，§4.8 步骤 4）：仅当 inputProps.safeAreaProbe === true 时启用（scripts/safe-area.mjs 传入）。
// 在页面内用与渲染相同的 computeLayout() 计算安全区，检查：
//   ① 所有可见文本的包围盒（Range.getClientRects）⊆ 安全区；② data-layer 只取四个白名单值。
// 结果经 console.log 以固定前缀输出，由 safe-area.mjs 通过 onBrowserLog 收集。
import { useEffect, useState } from 'react';
import { continueRender, delayRender, getInputProps, useCurrentFrame, useVideoConfig } from 'remotion';
import { computeLayout, type LayoutTokens } from '../layout/computeLayout';
import { LAYOUT_TOKENS } from '../theme/tokens';
import { ensureFonts } from '../theme/fonts';

export const PROBE_PREFIX = '__SAFE_AREA_PROBE__';
const ALLOWED_LAYERS = ['background', 'scene', 'hud', 'subtitle'];

type Box = { x: number; y: number; w: number; h: number };

const effectiveOpacity = (el: Element | null): number => {
  let o = 1;
  for (let e = el; e && e instanceof HTMLElement; e = e.parentElement) {
    const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
    o *= Number(cs.opacity || '1');
  }
  return o;
};

const measure = (width: number, height: number, frame: number) => {
  const L = computeLayout(width, height, LAYOUT_TOKENS as unknown as LayoutTokens);
  const safe: Box = L.safeRect;
  const layers = Array.from(document.querySelectorAll('[data-layer]')).map((e) => e.getAttribute('data-layer') ?? '');
  const badLayers = Array.from(new Set(layers.filter((v) => !ALLOWED_LAYERS.includes(v))));
  const violations: { text: string; box: Box; role: string | null }[] = [];
  let texts = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const s = (n.textContent ?? '').trim();
    const el = n.parentElement;
    if (!s || !el || el.closest('[data-layer="background"]') || el.closest('script,style,svg title')) continue;
    if (effectiveOpacity(el) < 0.05) continue;
    const r = document.createRange();
    r.selectNodeContents(n);
    const rects = Array.from(r.getClientRects()).filter((q) => q.width > 0.5 && q.height > 0.5);
    if (!rects.length) continue;
    texts++;
    const x1 = Math.min(...rects.map((q) => q.left)), y1 = Math.min(...rects.map((q) => q.top));
    const x2 = Math.max(...rects.map((q) => q.right)), y2 = Math.max(...rects.map((q) => q.bottom));
    const box = { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
    const tol = 2;
    if (box.x < safe.x - tol || box.y < safe.y - tol || box.x + box.w > safe.x + safe.w + tol || box.y + box.h > safe.y + safe.h + tol) {
      violations.push({ text: s.slice(0, 40), box, role: el.closest('[data-role]')?.getAttribute('data-role') ?? null });
    }
  }
  return { frame, width, height, safe, texts, layers: Array.from(new Set(layers)), badLayers, violations };
};

export const SafeAreaProbe: React.FC = () => {
  const enabled = (getInputProps() as { safeAreaProbe?: boolean }).safeAreaProbe === true;
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const [handle] = useState(() => (enabled ? delayRender('安全区探针') : null));
  useEffect(() => {
    if (handle === null) return;
    let done = false;
    ensureFonts().then(() => {
      requestAnimationFrame(() => requestAnimationFrame(() => {
        if (done) return;
        done = true;
        try {
          console.log(PROBE_PREFIX + JSON.stringify(measure(width, height, frame)));
        } finally {
          continueRender(handle);
        }
      }));
    });
  }, [handle, width, height, frame]);
  return null;
};
export default SafeAreaProbe;
