// 示例场景 S04 画幅：横竖分栏对比（代码绘制的画布示意）+ 媒体卡片 3D 倾斜（自制示意图，带署名角标）
import React from 'react';
import { IllustrativeTag, MediaCard, SourceBadge, Split } from '../components';
import { useLayout } from '../layout/useLayout';
import { CANVAS_PRESETS } from '../layout/presets';
import { COLORS } from '../theme/tokens';
import { alpha, toneColor } from '../theme/colors';
import { FONT_MONO, FONT_SANS } from '../theme/fonts';
import { ShotSequence } from './ShotSequence';
import type { SceneProps } from './types';
import { shotByNo } from './useLines';

const Frame: React.FC<{ label: string; ratio: number; boxW: number; boxH: number; tone: 'gold' | 'blue' }> = ({ label, ratio, boxW, boxH, tone }) => {
  const L = useLayout();
  const w = Math.min(boxW, boxH * ratio);
  const c = toneColor(tone);
  return (
    <div style={{ width: w, height: w / ratio, borderRadius: 20 * L.unit, border: `${Math.max(2, 3 * L.unit)}px solid ${c}`, background: alpha(c, 0.1), display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 * L.unit, boxShadow: `0 0 ${40 * L.unit}px ${alpha(c, 0.3)}` }}>
      <span style={{ fontFamily: FONT_SANS, fontWeight: 900, fontSize: L.font('h3'), color: COLORS.text }}>{label}</span>
    </div>
  );
};

/** 代码绘制的示意图（SVG data URI）：一张“信息图”样张，无第三方素材 */
const sampleChart = (): string => {
  const g = COLORS.gold, b = COLORS.blue, gr = COLORS.green, bg = COLORS.card, ln = COLORS.line;
  const bars = [0.45, 0.7, 0.55, 0.9, 0.75].map((v, i) => `<rect x="${60 + i * 100}" y="${300 - v * 220}" width="60" height="${v * 220}" rx="8" fill="${i % 2 ? b : g}"/>`).join('');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 315"><rect width="560" height="315" fill="${bg}"/><g stroke="${ln}" stroke-width="1">${[60, 120, 180, 240, 300].map((y) => `<line x1="40" x2="540" y1="${y}" y2="${y}"/>`).join('')}</g>${bars}<polyline points="90,200 190,150 290,170 390,90 490,110" fill="none" stroke="${gr}" stroke-width="6" stroke-linecap="round"/></svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
};

const S04: React.FC<SceneProps> = ({ section, shots }) => {
  const L = useLayout();
  const s8 = shotByNo(shots, 8), s9 = shotByNo(shots, 9);
  const lp = CANVAS_PRESETS.landscape, pp = CANVAS_PRESETS.portrait;
  const cols = L.columns === 2;
  const boxW = cols ? (L.content.w - L.gap) / 2 * 0.8 : L.content.w * 0.8;
  const boxH = cols ? L.content.h * 0.62 : (L.content.h - L.gap) / 2 * 0.62;
  return (
    <>
      <ShotSequence shot={s8} section={section} gap={L.font('h3') * 0.5}>
        <div style={{ width: '100%', height: L.content.h * 0.82 }}>
          <Split
            primary={<Frame label={`横屏 ${lp.width}×${lp.height}`} ratio={lp.width / lp.height} boxW={boxW} boxH={boxH} tone="gold" />}
            secondary={<Frame label={`竖屏 ${pp.width}×${pp.height}`} ratio={pp.width / pp.height} boxW={boxW} boxH={boxH} tone="blue" />}
          />
        </div>
        <div style={{ display: 'flex', gap: 12 * L.unit, alignItems: 'center' }}>
          <span style={{ fontFamily: FONT_MONO, fontSize: L.font('body'), color: COLORS.textDim }}>同一份数据 · 切换画幅</span>
          <SourceBadge text="据 PRD F-10" />
        </div>
      </ShotSequence>
      <ShotSequence shot={s9} section={section} gap={L.font('h3') * 0.4}>
        <MediaCard src={sampleChart()} at={0} tilt={4} attribution="自制示意图 · 代码绘制" />
        <IllustrativeTag />
      </ShotSequence>
    </>
  );
};
export default S04;
