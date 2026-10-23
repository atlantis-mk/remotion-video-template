// 自动生成，勿手改。来源：assets-manifest.json（scripts/build_timeline.py）
export type AssetData = { id: string; file: string; kind: string; usage: 'fullscreen' | 'card-only' | 'rejected'; usable: boolean; width: number | null; height: number | null; attribution: string };
export const ASSETS: readonly AssetData[] = [];
export const ASSET_BY_ID: Record<string, AssetData> = Object.fromEntries(ASSETS.map((a) => [a.id, a]));
export type ShotBadge = { shot_no: number; asset_id: string; text: string };
export const SHOT_BADGES: readonly ShotBadge[] = [];
