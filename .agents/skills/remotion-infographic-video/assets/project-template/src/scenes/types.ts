import type { SectionData, ShotData } from '../data/timeline';

/** 每段场景组件的 props：src/scenes/<Sxx>.tsx 导出 React.FC<SceneProps>（默认导出） */
export type SceneProps = { section: SectionData; shots: ShotData[] };
export type { SectionData, ShotData };
