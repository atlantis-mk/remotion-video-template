// 示例场景 S02 流程：玻璃面板里的步骤条逐个点亮 + 镜头推进到三层结构
import React from 'react';
import { GlassPanel, Shot, SourceBadge, StepList } from '../components';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { alpha, toneColor } from '../theme/colors';
import { FONT_SANS } from '../theme/fonts';
import { ShotSequence } from './ShotSequence';
import type { SceneProps } from './types';
import { rangeOf, shotByNo, shotRange } from './useLines';

const STEPS = ['前置检查', '收题', '写稿', '配音', '分镜', '素材', '建工程', '自检', '渲染', '文案与交付'];
const LAYERS: { name: string; tone: 'blue' | 'purple' | 'gold' }[] = [
  { name: 'HUD 层 + 字幕层', tone: 'gold' },
  { name: '场景层（每段一个场景）', tone: 'purple' },
  { name: '背景层（网格 · 光晕 · 粒子）', tone: 'blue' },
];

const S02: React.FC<SceneProps> = ({ section, shots }) => {
  const L = useLayout();
  const s3 = shotByNo(shots, 3), s4 = shotByNo(shots, 4);
  // 步骤条在镜 3 的两句话里逐个点亮：区间相对镜头起点
  const base = s3 ? shotRange(s3, section).from : 0;
  const all = s3 ? rangeOf(s3.line_ids, section) : { from: 0, to: 1 };
  const step = (all.to - all.from) / STEPS.length;
  const ranges = STEPS.map((_, i) => ({ from: all.from - base + i * step, to: all.from - base + (i + 1) * step }));
  const h = L.font('h2');
  return (
    <>
      <ShotSequence shot={s3} section={section}>
        <GlassPanel tone="blue" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: h * 0.45 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: h * 0.3 }}>
            <span style={{ fontFamily: FONT_SANS, fontWeight: 900, fontSize: h, color: COLORS.text }}>10 个固定步骤</span>
            <SourceBadge text="据 PRD 流程" />
          </div>
          <StepList items={STEPS} ranges={ranges} activeTone="blue" />
        </GlassPanel>
      </ShotSequence>
      <ShotSequence shot={s4} section={section}>
        <Shot entrance="zoom" at={0} style={{ position: 'relative', inset: undefined }}>
          <GlassPanel tone="purple" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: h * 0.35, width: L.content.w * (L.columns === 2 ? 0.6 : 0.95) }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: h * 0.3 }}>
              <span style={{ fontFamily: FONT_SANS, fontWeight: 900, fontSize: h, color: COLORS.text }}>3 层工程结构</span>
              <SourceBadge text="据 PRD F-09" />
            </div>
            {LAYERS.map((l, i) => (
              <div
                key={l.name}
                style={{
                  width: `${100 - i * 0}%`, boxSizing: 'border-box', padding: `${h * 0.25}px ${h * 0.4}px`, borderRadius: 18 * L.unit,
                  border: `${Math.max(1, 2 * L.unit)}px solid ${alpha(toneColor(l.tone), 0.7)}`, background: alpha(toneColor(l.tone), 0.12),
                  fontFamily: FONT_SANS, fontWeight: 700, fontSize: L.font('h3'), color: COLORS.text, textAlign: 'center',
                  transform: `perspective(${1400 * L.unit}px) rotateX(${12}deg)`,
                }}
              >
                {l.name}
              </div>
            ))}
          </GlassPanel>
        </Shot>
      </ShotSequence>
    </>
  );
};
export default S02;
