import React from 'react';
import { useLayout } from '../layout/useLayout';

export type SplitProps = { primary: React.ReactNode; secondary: React.ReactNode; ratio?: number };

/** 分栏：横屏（columns=2）左右并排，竖屏（columns=1）上下堆叠；ratio 为 primary 所占比例 */
export const Split: React.FC<SplitProps> = ({ primary, secondary, ratio = 0.5 }) => {
  const L = useLayout();
  const row = L.columns === 2;
  const r = Math.min(0.8, Math.max(0.2, ratio));
  return (
    <div style={{ display: 'flex', flexDirection: row ? 'row' : 'column', gap: L.gap, width: '100%', height: '100%', alignItems: 'stretch' }}>
      <div style={{ flex: r, minWidth: 0, minHeight: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{primary}</div>
      <div style={{ flex: 1 - r, minWidth: 0, minHeight: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{secondary}</div>
    </div>
  );
};
export default Split;
