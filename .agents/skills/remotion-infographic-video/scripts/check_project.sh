#!/usr/bin/env bash
# 步骤 7：自检。用法：bash scripts/check_project.sh <slug> [--aspect landscape|portrait|both] [--determinism]
# 顺序（任一失败即停，退出 7）：tsc → compositions(片长 ±1 帧) → 每段中点抽帧 → 安全区/署名页否定检查 → 静态检查 → (可选)确定性
# 报告：<slug>/check/report.json（Schema: assets/schemas/check-report.schema.json）；调用记录 <slug>/check/attempts.json，总调用 ≤3。
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/lib/check_project_impl.py" "$@"
