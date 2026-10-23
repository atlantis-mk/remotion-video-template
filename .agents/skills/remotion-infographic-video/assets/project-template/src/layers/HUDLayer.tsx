import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { SECTIONS, TOTAL_FRAMES } from '../data/timeline';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { alpha, toneColor } from '../theme/colors';
import { FONT_MONO, FONT_SANS } from '../theme/fonts';

/** HUD 层：左上段号 + 段名，右侧总进度条（位于安全区顶部的 HUD 带内） */
export const HUDLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const cur = SECTIONS.find((s) => frame >= s.from && frame < s.to) ?? SECTIONS[SECTIONS.length - 1];
  const fs = L.font('caption');
  const c = toneColor(cur?.palette.a);
  const prog = TOTAL_FRAMES > 0 ? Math.min(1, frame / TOTAL_FRAMES) : 0;
  return (
    <AbsoluteFill data-layer="hud" style={{ pointerEvents: 'none' }}>
      <div style={{ position: 'absolute', left: L.hud.x, top: L.hud.y, width: L.hud.w, height: fs * 1.6, display: 'flex', alignItems: 'center', gap: fs * 0.7 }}>
        {cur ? (
          <>
            <span style={{ fontFamily: FONT_MONO, fontSize: fs, fontWeight: 700, color: COLORS.bg, background: c, borderRadius: fs * 0.3, padding: `0 ${fs * 0.4}px`, lineHeight: 1.4 }}>{cur.id}</span>
            <span style={{ fontFamily: FONT_SANS, fontSize: fs, fontWeight: 700, color: COLORS.text, lineHeight: 1.4 }}>{cur.title}</span>
          </>
        ) : null}
        <div style={{ flex: 1 }} />
        <div style={{ width: L.hud.w * 0.22, height: Math.max(2, 4 * L.unit), borderRadius: 4 * L.unit, background: alpha(COLORS.text, 0.12), overflow: 'hidden' }}>
          <div style={{ width: `${prog * 100}%`, height: '100%', background: c }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
export default HUDLayer;
