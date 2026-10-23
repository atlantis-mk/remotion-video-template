import React from 'react';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';

export type SourceBadgeProps = { text: string; style?: React.CSSProperties };

/** 来源角标 / 素材署名（只写来源名称，不放链接）。安全区检测通过 data-role 识别。 */
export const SourceBadge: React.FC<SourceBadgeProps> = ({ text, style }) => {
  const L = useLayout();
  const fs = L.font('caption');
  return (
    <span
      data-role="source-badge"
      style={{
        display: 'inline-flex', alignItems: 'center', gap: fs * 0.4,
        fontFamily: FONT_SANS, fontSize: fs, fontWeight: 500, lineHeight: 1.2, color: COLORS.textDim,
        background: COLORS.badge, border: `${Math.max(1, L.unit)}px solid ${COLORS.badgeStroke}`,
        borderRadius: fs, padding: `${fs * 0.25}px ${fs * 0.7}px`, whiteSpace: 'nowrap', ...style,
      }}
    >
      {text}
    </span>
  );
};
export default SourceBadge;
