// 自动生成，勿手改。来源：job.json（scripts/scaffold_project.py）
import { CANVAS_PRESETS } from '../layout/presets';

export const JOB_META = {
  "topic": "示例选题",
  "slug": "example",
  "aspect": "landscape",
  "fps": 30
} as const;
export type Aspect = 'landscape' | 'portrait';
export const ASPECT: Aspect = "landscape";
export const JOB = { ...JOB_META, aspect: ASPECT, ...CANVAS_PRESETS[ASPECT] };
export default JOB;
