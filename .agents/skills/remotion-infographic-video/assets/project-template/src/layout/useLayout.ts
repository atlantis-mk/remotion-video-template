import { useVideoConfig } from 'remotion';
import { LAYOUT_TOKENS } from '../theme/tokens';
import { computeLayout, type Layout, type LayoutTokens } from './computeLayout';

/** 所有组件只通过本 hook 取尺寸，禁止读画布常量 */
export const useLayout = (): Layout => {
  const { width, height } = useVideoConfig();
  return computeLayout(width, height, LAYOUT_TOKENS as unknown as LayoutTokens);
};
