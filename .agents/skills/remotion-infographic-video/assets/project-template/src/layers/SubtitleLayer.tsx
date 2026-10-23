import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { CUES } from '../data/subtitles';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { alpha } from '../theme/colors';
import { FONT_SANS } from '../theme/fonts';

/** 字幕层：读 subtitles 数据，垂直居中于 layout.subtitleY（安全区底部的字幕带内），最多两行 */
export const SubtitleLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const L = useLayout();
  const cue = CUES.find((c) => frame >= c.from && frame < c.to);
  const fs = L.font('h3') * (L.columns === 1 ? 0.95 : 1);
  return (
    <AbsoluteFill data-layer="subtitle" style={{ pointerEvents: 'none' }}>
      {cue ? (
        <div style={{ position: 'absolute', left: L.content.x, width: L.content.w, top: L.subtitleY, transform: 'translateY(-50%)', display: 'flex', justifyContent: 'center' }}>
          <span
            style={{
              fontFamily: FONT_SANS, fontWeight: 700, fontSize: fs, lineHeight: 1.35, color: COLORS.text, textAlign: 'center',
              maxWidth: L.content.w * 0.92, textShadow: `0 ${2 * L.unit}px ${10 * L.unit}px ${alpha(COLORS.bg, 0.9)}`,
              display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
            }}
          >
            {cue.text}
          </span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
export default SubtitleLayer;
