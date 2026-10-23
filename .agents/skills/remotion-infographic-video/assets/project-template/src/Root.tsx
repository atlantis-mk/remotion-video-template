import React from 'react';
import { Composition, Still, type CalculateMetadataFunction } from 'remotion';
import { Main, type MainProps } from './Main';
import { Cover, type CoverProps } from './Cover';
import { FPS, TOTAL_FRAMES } from './data/timeline';
import { ASPECT } from './data/job';
import { CANVAS_PRESETS, COVER_PRESETS } from './layout/presets';
import { ensureFonts } from './theme/fonts';

ensureFonts();

/** 默认画幅取 job.aspect；--props='{"aspect":"portrait"}' 时同一工程切换为竖屏（A-17）。片长恒为 TOTAL_FRAMES。 */
const calcMain: CalculateMetadataFunction<MainProps> = ({ props }) => {
  const size = CANVAS_PRESETS[props.aspect ?? ASPECT];
  return { width: size.width, height: size.height, fps: FPS, durationInFrames: TOTAL_FRAMES };
};

/** 封面尺寸由 props 决定（render.sh 按 COVER_PRESETS 逐个传入） */
const calcCover: CalculateMetadataFunction<CoverProps> = ({ props }) => ({ width: props.width, height: props.height });

const [coverW, coverH] = COVER_PRESETS[ASPECT][0];

export const Root: React.FC = () => (
  <>
    <Composition
      id="Main"
      component={Main}
      fps={FPS}
      durationInFrames={TOTAL_FRAMES}
      width={CANVAS_PRESETS[ASPECT].width}
      height={CANVAS_PRESETS[ASPECT].height}
      defaultProps={{ aspect: ASPECT } satisfies MainProps}
      calculateMetadata={calcMain}
    />
    <Still id="Cover" component={Cover} width={coverW} height={coverH} defaultProps={{ width: coverW, height: coverH } satisfies CoverProps} calculateMetadata={calcCover} />
  </>
);
