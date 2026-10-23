import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { SECTIONS } from './data/timeline';
import { BackgroundLayer } from './layers/BackgroundLayer';
import { HUDLayer } from './layers/HUDLayer';
import { SubtitleLayer } from './layers/SubtitleLayer';
import { SectionTransition } from './components/SectionTransition';
import { SceneRouter } from './scenes/SceneRouter';
import { SafeAreaProbe } from './debug/SafeAreaProbe';
import type { Aspect } from './layout/presets';
import { COLORS } from './theme/tokens';

export type MainProps = { aspect?: Aspect; safeAreaProbe?: boolean };

const ROOT_STYLE: React.CSSProperties = { backgroundColor: COLORS.bg };

/** 主片：配音 + 背景层 + 各段场景（段转场包裹）+ HUD 层 + 字幕层。只有这四个 data-layer，无片尾署名层；片长 = 配音帧数。 */
export const Main: React.FC<MainProps> = () => {
  return (
    <AbsoluteFill style={ROOT_STYLE}>
      {/* @test-inject:layers */}
      <Audio src={staticFile('audio/full.mp3')} />
      <BackgroundLayer />
      <AbsoluteFill data-layer="scene">
        {SECTIONS.map((s) => (
          <Sequence key={s.id} from={s.from} durationInFrames={Math.max(1, s.to - s.from)} name={`${s.id} ${s.title}`}>
            <SectionTransition type={s.transition} durationInFrames={Math.max(1, s.to - s.from)} tone={s.palette}>
              <SceneRouter section={s} />
            </SectionTransition>
          </Sequence>
        ))}
      </AbsoluteFill>
      <HUDLayer />
      <SubtitleLayer />
      <SafeAreaProbe />
    </AbsoluteFill>
  );
};
export default Main;
