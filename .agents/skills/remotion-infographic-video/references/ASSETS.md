# ASSETS：素材查找 / 生成、授权与署名

> 工具：`scripts/fetch_asset.py`（add / prune / verify / credits-diff），清单 `<slug>/assets-manifest.json`（Schema `assets/schemas/assets-manifest.schema.json`，顶层为对象 `{version: 1, assets: [...]}`）。规则对应 F-08、NF-04。

## 1. 素材从哪来（优先级）
1. 用户主动提供的素材（经 `fetch_asset.py add --file` 校验后使用；不合规就替换，并在交付备注说明）。**任何情况下都不向用户索要素材。**
2. 代码动画：图表、数字、示意图优先用组件画（[COMPONENTS](COMPONENTS.md)），不需要授权。
3. 环境里有图片生成 / 素材搜索的 MCP 工具就优先用；否则用网页搜索找明确授权的图片或视频。
4. AI 生成图：登记时用 `--ai-generated`，来源名称写“AI 生成”。

## 2. 授权规则
- 授权规则以 `assets/licenses.json` 为准（格式见 `assets/schemas/licenses.schema.json`：`allowed`、`no_attribution`、`denied` 三个列表，`no_attribution` 必须是 `allowed` 的子集，否则脚本退出 5）。
- 判定：许可名先规范化（小写，空格/`-`/`_` 合并为一个空格）；命中 `denied`（非商业 NC、禁止演绎 ND、All Rights Reserved、editorial、版权所有等；英文按整词，中文按子串）→ rejected；再与 `allowed` 相等或以“该项 + 空格/版本号”开头 → 可用（如 `CC BY 4.0`）；其余视为授权不明 → rejected。因此 `CC BY-NC 4.0`、`CC BY-ND` 不可用。
- 默认可用：CC0、CC BY、CC BY-SA、Public Domain / 公有领域、Pexels、Unsplash、Pixabay、AI 生成、自制 / 原创、用户提供、代码绘制；其中 CC BY、CC BY-SA 需署名。
- 免署名许可：CC0、公有领域、Pexels、Unsplash、Pixabay、AI 生成、自制、用户提供、代码绘制；其余（如 CC BY、CC BY-SA）需要署名。
- **授权不明（`unknown` / 空）允许登记，但 `usable=false`，不得进入成片**，改用代码动画替代。
- 不用带水印、明显受版权保护的新闻图片、影视截图、商标主视觉。

## 3. 登记与校验
```
python3 scripts/fetch_asset.py add --manifest <slug>/assets-manifest.json --id A03 \
  (--url URL | --file PATH) --content "画面描述" (--source-url URL | --ai-generated) \
  --license "CC BY 4.0" --source-name "Wikimedia Commons" [--author "作者"] \
  [--kind image|video|audio] --aspect landscape|portrait --dest <slug>/project/public/media/
python3 scripts/fetch_asset.py prune  --manifest <slug>/assets-manifest.json --storyboard <slug>/storyboard.json
python3 scripts/fetch_asset.py verify --manifest <slug>/assets-manifest.json --canvas 1920x1080
```
- `add`：下载 / 复制文件，探测尺寸与可打开性，按规则判定 `usage`：
  - 打不开或授权不明 → `rejected`；
  - 短边 ≥ 画布短边 → `fullscreen`（可全屏用）；
  - 否则 → `card-only`（只能放进 `MediaCard` 等卡片）。
- `prune`：未被任何镜头 `asset_ids` 引用的条目置 `usable=false`，因此“可用”即“进入成片”。
- storyboard 的 `asset_ids` 只能引用 manifest 中 `usable=true` 的条目（`validate.py storyboard` 检查）。
- 来源 URL 只存在 manifest 的 `source` 字段（内部留存），对外一律用 `source_name`。

## 4. 署名：三处一致、都不放链接
manifest 中 `needs_attribution && usable` 的每个素材，必须同时出现在：
1. **画面内**：使用该素材的镜头的 `SourceBadge`（作者 / 来源名称 / 许可简写）。由 `build_timeline.py` 从 manifest 生成 `project/src/data/shot-badges.json` 并注入 `MediaCard.attribution`，不要手填。
2. **每个目标平台的简介**：`publish/<平台>/description.txt` 末尾恰好一段，以一行 `素材署名：` 开头，每行 `- [<asset_id>] <作者> · <来源名称> · <许可>`。由 `validate.py publish` 自动补全（幂等），计入简介长度。
3. **交付摘要**：`deliverable.json.credits`，每条 `{id, author, source_name, license}`。

检查：`python3 scripts/fetch_asset.py credits-diff --manifest <slug>/assets-manifest.json --slug-dir <slug>`；三处任一差集非空、或任一平台的 title / description 与 credits 字段命中 URL 正则，退出码 7。步骤 7 自检时只比对画面内部分（`--only badge`），文案部分在步骤 9 复核。

## 5. 不做的事
- 不做片尾署名画面（工程只有 background / scene / hud / subtitle 四层）。
- 署名、角标、简介里不放任何链接。
- 不使用授权不明的素材，不替用户承担未核实的授权风险。
