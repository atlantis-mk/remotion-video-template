import React from 'react';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { alpha } from '../theme/colors';
import { FONT_SANS } from '../theme/fonts';

export type IllustrativeTagProps = { style?: React.CSSProperties };

/** 固定“示意”标：非真实比例 / 非实拍画面必须带 */
export const IllustrativeTag: React.FC<IllustrativeTagProps> = ({ style }) => {
  const L = useLayout();
  const fs = L.font('caption');
  return (
    <span
      data-role="illustrative-tag"
      style={{
        display: 'inline-block', fontFamily: FONT_SANS, fontSize: fs, fontWeight: 700, lineHeight: 1.2,
        color: COLORS.gold, border: `${Math.max(1, 1.5 * L.unit)}px solid ${alpha(COLORS.gold, 0.6)}`,
        borderRadius: fs * 0.3, padding: `${fs * 0.15}px ${fs * 0.5}px`, ...style,
      }}
    >
      示意
    </span>
  );
};
export default IllustrativeTag;
