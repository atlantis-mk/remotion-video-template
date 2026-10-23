import React from 'react';
import { useLayout } from './useLayout';

/** 场景内容区容器：绝对定位到 layout.content，子元素默认居中；场景只在这里面布局 */
export const ContentArea: React.FC<{ children: React.ReactNode; align?: 'center' | 'start'; style?: React.CSSProperties }> = ({ children, align = 'center', style }) => {
  const L = useLayout();
  return (
    <div
      style={{
        position: 'absolute', left: L.content.x, top: L.content.y, width: L.content.w, height: L.content.h,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: align === 'center' ? 'center' : 'flex-start',
        boxSizing: 'border-box', ...style,
      }}
    >
      {children}
    </div>
  );
};
export default ContentArea;
