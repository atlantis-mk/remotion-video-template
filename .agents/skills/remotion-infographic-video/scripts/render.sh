#!/usr/bin/env bash
# 步骤 8：渲染成片 + 封面 + 验收。用法：bash scripts/render.sh <slug> [--covers-only] [--video-only]
# 成片：<slug>/out/video.mp4（h264 + aac）；封面：<slug>/publish/cover_<W>x<H>.png（尺寸取工程 src/layout/presets.ts 的 COVER_PRESETS）。
# 验收：validate.py video（分辨率/30fps/AAC/音视频差 ≤0.1s），不通过退出 7。不包含任何上传/发布动作。
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/lib/render_impl.py" "$@"
