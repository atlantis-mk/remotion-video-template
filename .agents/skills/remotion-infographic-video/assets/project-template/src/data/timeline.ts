// 自动生成，勿手改。来源：voice/timeline.json + storyboard.json（scripts/build_timeline.py）
export type SectionTransitionType = 'wipe' | 'zoom' | 'blur' | 'slide' | 'iris';
export type ShotEntrance = 'push' | 'rise' | 'zoom';
export type LineData = { id: string; section: string; from: number; to: number };
export type SectionData = { id: string; title: string; from: number; to: number; transition: SectionTransitionType; palette: { a: string; b: string } };
export type ShotData = { shot_no: number; section: string; line_ids: string[]; description: string; component: string; entrance: ShotEntrance; from: number; to: number; props?: Record<string, unknown>; asset_ids?: string[]; display_numbers?: { text: string; source_claim_id: string }[]; illustrative?: boolean };

export const FPS = 30;
export const AUDIO_SECONDS = 2.0;
export const TOTAL_FRAMES = 60;
export const LINES: readonly LineData[] = [
  {
    id: "01",
    section: "S01",
    from: 0,
    to: 60
  }
];
export const SECTIONS: readonly SectionData[] = [
  {
    id: "S01",
    title: "占位",
    from: 0,
    to: 60,
    transition: "zoom",
    palette: {
      a: "gold",
      b: "blue"
    }
  }
];
export const SHOTS: readonly ShotData[] = [
  {
    shot_no: 1,
    description: "占位",
    component: "SlamTitle",
    entrance: "zoom",
    props: {
      text: "占位"
    },
    section: "S01",
    line_ids: [
      "01"
    ],
    from: 0,
    to: 60
  }
];
