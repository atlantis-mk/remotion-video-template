#!/usr/bin/env bash
# 安装 Agent Skills 校验器（测试工具，非技能包运行前提）到 tests/.venv（Q-16：PyPI skills-ref==0.1.1，需 Python ≥3.11）
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 11), "skills-ref 需要 Python ≥3.11"'
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install -q "skills-ref==0.1.1"
ls .venv/bin | grep -E '^(skills-ref|agentskills)$' || echo "CLI 未找到，将使用 python -c 'import skills_ref'"
