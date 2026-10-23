#!/usr/bin/env node
// 安全区与图层白名单检测（架构 §4.8 步骤 4，F-10 / F-09）。
// 用法（工程根目录）：node scripts/safe-area.mjs --entry src/index.ts --composition Main --frames 10,200 \
//        [--width W --height H] [--props '{"aspect":"portrait"}'] [--out check/safe-area.json] [--credits-frames ...]
// 做法：bundle 工程 → 以 inputProps.safeAreaProbe=true 渲染指定帧（renderStill）→ 页面内探针（src/debug/SafeAreaProbe.tsx）
//       用与渲染相同的 computeLayout() 计算安全区，检查所有可见文本包围盒 ⊆ 安全区、data-layer ∈ {background,scene,hud,subtitle}，
//       结果经 console.log 回传。--credits-frames 为兼容参数：这些帧只做图层白名单检查。
// 退出码：0 通过；1 发现越界文本或非法图层（详情写入 --out 与 stderr）；2 用法错误或渲染失败。
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const PREFIX = '__SAFE_AREA_PROBE__';

function parseArgs(argv) {
  const a = { entry: 'src/index.ts', composition: 'Main', frames: '', 'credits-frames': '', width: '', height: '', props: '{}', out: '' };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (!k.startsWith('--')) continue;
    const key = k.slice(2);
    const eq = key.indexOf('=');
    if (eq >= 0) a[key.slice(0, eq)] = key.slice(eq + 1);
    else a[key] = argv[++i] ?? '';
  }
  return a;
}
const nums = (s) => String(s || '').split(',').map((x) => x.trim()).filter(Boolean).map(Number).filter((n) => Number.isInteger(n) && n >= 0);

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const frames = nums(args.frames);
  const layerOnly = nums(args['credits-frames']).filter((f) => !frames.includes(f));
  let extraProps;
  try { extraProps = JSON.parse(args.props || '{}'); } catch { console.error('[safe-area] --props 不是合法 JSON'); return 2; }
  const inputProps = { ...extraProps, safeAreaProbe: true };
  const entry = path.resolve(args.entry);
  if (!fs.existsSync(entry)) { console.error(`[safe-area] 入口不存在：${entry}`); return 2; }

  const serveUrl = await bundle({ entryPoint: entry, onProgress: () => undefined });
  const composition = await selectComposition({ serveUrl, id: args.composition, inputProps, logLevel: 'error' });
  const errors = [];
  if (args.width && Number(args.width) !== composition.width) errors.push(`画布宽 ${composition.width} ≠ 期望 ${args.width}`);
  if (args.height && Number(args.height) !== composition.height) errors.push(`画布高 ${composition.height} ≠ 期望 ${args.height}`);
  const all = [...frames.map((f) => [f, 'full']), ...layerOnly.map((f) => [f, 'layers'])];
  if (!all.length) all.push([0, 'full']);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'safe-area-'));
  const results = [];
  for (const [rawFrame, mode] of all) {
    const frame = Math.min(rawFrame, composition.durationInFrames - 1);
    let probe = null;
    await renderStill({
      composition, serveUrl, frame, inputProps, output: path.join(tmp, `f${frame}.png`), imageFormat: 'png', logLevel: 'error',
      onBrowserLog: (log) => {
        const t = log.text || '';
        const i = t.indexOf(PREFIX);
        if (i >= 0) { try { probe = JSON.parse(t.slice(i + PREFIX.length)); } catch { /* 忽略 */ } }
      },
    });
    if (!probe) { errors.push(`帧 ${frame}：未收到安全区探针结果（src/debug/SafeAreaProbe 未挂载？）`); continue; }
    const r = { frame, mode, texts: probe.texts, layers: probe.layers, bad_layers: probe.badLayers, violations: mode === 'full' ? probe.violations : [], safe: probe.safe };
    if (r.bad_layers.length) errors.push(`帧 ${frame}：出现白名单外的 data-layer：${r.bad_layers.join(',')}`);
    for (const v of r.violations) errors.push(`帧 ${frame}：文本越出安全区「${v.text}」 box=${JSON.stringify(v.box)}`);
    results.push(r);
    console.error(`[safe-area] frame ${frame} (${mode}): texts=${probe.texts} layers=${probe.layers.join('|')} violations=${r.violations.length}`);
  }
  fs.rmSync(tmp, { recursive: true, force: true });
  const report = { ok: errors.length === 0, composition: args.composition, width: composition.width, height: composition.height, frames: results, errors };
  if (args.out) { fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true }); fs.writeFileSync(args.out, JSON.stringify(report, null, 2)); }
  for (const e of errors) console.error(`[safe-area] ${e}`);
  console.log(JSON.stringify({ ok: report.ok, errors: errors.slice(0, 20) }));
  return report.ok ? 0 : 1;
}

main().then((c) => process.exit(c), (e) => { console.error(`[safe-area] ${e?.stack || e}`); process.exit(2); });
