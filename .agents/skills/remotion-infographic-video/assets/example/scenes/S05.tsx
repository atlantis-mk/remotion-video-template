// 示例场景 S05 结尾：关注引导 + 定格淡出（在末句内收束，片长 = 配音长度，不加额外帧）
import React from 'react';
import { FollowCTA, HoldFade, SlamTitle } from '../components';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';
import { ShotSequence } from './ShotSequence';
import type { SceneProps } from './types';
import { shotByNo, shotRange } from './useLines';

const FADE = 18;

const S05: React.FC<SceneProps> = ({ section, shots }) => {
  const L = useLayout();
  const s10 = shotByNo(shots, 10), s11 = shotByNo(shots, 11);
  const r11 = s11 ? shotRange(s11, section) : { from: 0, to: FADE };
  const len11 = r11.to - r11.from;
  return (
    <>
      <ShotSequence shot={s10} section={section} gap={L.font('h3')}>
        <div style={{ fontFamily: FONT_SANS, fontSize: L.font('h3'), fontWeight: 700, color: COLORS.textDim }}>复制文件夹 · 填好密钥</div>
        <FollowCTA text="说「开始制作」" at={4} />
      </ShotSequence>
      <ShotSequence shot={s11} section={section}>
        <HoldFade startAt={Math.max(0, len11 - FADE)} durationInFrames={FADE}>
          <SlamTitle text="关注我，下期见" at={0} size="h1" tone="gold" />
        </HoldFade>
      </ShotSequence>
    </>
  );
};
export default S05;
