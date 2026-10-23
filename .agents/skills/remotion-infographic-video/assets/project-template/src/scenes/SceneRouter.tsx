import React from 'react';
import { SHOTS, type SectionData } from '../data/timeline';
import { SCENES } from './index';
import { GenericScene } from './GenericScene';

/** 段 → 场景：优先用 src/scenes/<Sxx>.tsx（由 build_timeline 注册到 scenes/index.ts），否则回退 GenericScene */
export const SceneRouter: React.FC<{ section: SectionData }> = ({ section }) => {
  const shots = SHOTS.filter((s) => s.section === section.id);
  const Scene = SCENES[section.id] ?? GenericScene;
  return <Scene section={section} shots={shots} />;
};
export default SceneRouter;
