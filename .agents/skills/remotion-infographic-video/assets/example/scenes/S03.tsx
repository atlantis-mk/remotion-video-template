// 示例场景 S03 数字：来源角标示范、对比柱（示意）、数字滚动。上屏数字都带来源角标。
import React from 'react';
import { CompareBars, NumberRoll, SourceBadge } from '../components';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';
import { ShotSequence } from './ShotSequence';
import type { SceneProps } from './types';
import { shotByNo } from './useLines';

const S03: React.FC<SceneProps> = ({ section, shots }) => {
  const L = useLayout();
  const s5 = shotByNo(shots, 5), s6 = shotByNo(shots, 6), s7 = shotByNo(shots, 7);
  const h = L.font('h1');
  return (
    <>
      <ShotSequence shot={s5} section={section} gap={L.font('h3')}>
        <div style={{ fontFamily: FONT_SANS, fontWeight: 900, fontSize: h, color: COLORS.text, textAlign: 'center', lineHeight: 1.2 }}>每个数字都有出处</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: L.font('h3') * 0.5 }}>
          <span style={{ fontFamily: FONT_SANS, fontSize: L.font('h3'), color: COLORS.textDim }}>没有来源，就不上屏</span>
          <SourceBadge text="据 PRD" />
        </div>
      </ShotSequence>
      <ShotSequence shot={s6} section={section}>
        <CompareBars
          items={[{ label: '段转场', value: 5, tone: 'green' }, { label: '镜头入场', value: 3, tone: 'gold' }]}
          at={4}
          unit=" 种"
          source="据 PRD F-07"
          illustrative
        />
      </ShotSequence>
      <ShotSequence shot={s7} section={section} gap={L.font('h3') * 0.6}>
        <div style={{ fontFamily: FONT_SANS, fontWeight: 700, fontSize: L.font('h2'), color: COLORS.text }}>自检最多</div>
        <NumberRoll value={3} from={0} at={4} duration={20} suffix="轮" tone="green" source="据 PRD F-11" />
      </ShotSequence>
    </>
  );
};
export default S03;
