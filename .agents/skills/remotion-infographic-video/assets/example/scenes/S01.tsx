// 示例场景 S01 钩子：砸入大字 + 落地震动 + 关键词脉冲（段色光晕由背景层按 palette 自动生成）
import React from 'react';
import { ImpactShake, KeywordPulse, SlamTitle } from '../components';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';
import { ShotSequence } from './ShotSequence';
import type { SceneProps } from './types';
import { shotByNo, shotRange } from './useLines';

const S01: React.FC<SceneProps> = ({ section, shots }) => {
  const L = useLayout();
  const s1 = shotByNo(shots, 1), s2 = shotByNo(shots, 2);
  const r2 = s2 ? shotRange(s2, section) : { from: 0, to: 0 };
  return (
    <>
      <ShotSequence shot={s1} section={section}>
        <ImpactShake at={6} intensity={1.2}>
          <SlamTitle text="一个选题 → 一条视频" at={0} size="display" tone="gold" />
        </ImpactShake>
      </ShotSequence>
      <ShotSequence shot={s2} section={section} gap={L.font('h3')}>
        <KeywordPulse text="全自动" range={{ from: 0, to: r2.to - r2.from }} tone="gold" />
        <div style={{ fontFamily: FONT_SANS, fontSize: L.font('h3'), fontWeight: 700, color: COLORS.textDim, textAlign: 'center' }}>写稿 · 配音 · 动画 · 成片</div>
      </ShotSequence>
    </>
  );
};
export default S01;
