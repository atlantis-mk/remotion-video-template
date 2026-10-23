import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
export const SKILL_DIR = path.resolve(process.env.SKILL_DIR ?? path.join(here, '..', '..', '.agents', 'skills', 'remotion-infographic-video'));
export const TEMPLATE_SRC = path.join(SKILL_DIR, 'assets', 'project-template', 'src');
/** 被测文件不存在时抛出断言错误（在 test() 内调用 → 用例 FAIL，而不是套件加载错误） */
export async function load(rel: string): Promise<any> {
  const candidates = [rel, rel + '.ts', rel + '.tsx'].map((r) => path.join(TEMPLATE_SRC, r));
  const f = candidates.find((c) => existsSync(c));
  if (!f) throw new Error(`未实现：缺少 ${path.join(TEMPLATE_SRC, rel)}.ts`);
  return import(pathToFileURL(f).href);
}
export function json(rel: string): any {
  const f = path.join(SKILL_DIR, rel);
  if (!existsSync(f)) throw new Error(`未实现：缺少 ${f}`);
  return JSON.parse(readFileSync(f, 'utf8'));
}
