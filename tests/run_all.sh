#!/usr/bin/env bash
# 一键运行测试。用法：bash tests/run_all.sh [gate|unit|contract|static|integration|agent|ts|all|release]
#   all     = 自动门禁：L1～L4 + TS + 追溯检查；L5 在未设置 AGENT_RUNNER 时整体 SKIP（UR-1=B，人工评测），不计入失败
#             L1～L4/TS 出现任何 FAIL、ERROR 或 SKIP → 退出码非 0
#   release = 发布门禁：python3 tools/release_gate.py（先跑 all，再核对 agent-eval/archive/ 中 AE-01～AE-15 各 1 份有效 PASS 存档，
#             skill_md_sha256 = 当前 SKILL.md，并用 evaluate.py 复判；架构 v1.7 §7.3.1）
# 环境变量：SKILL_DIR（默认 ../.agents/skills/remotion-infographic-video，v1.11 A-21）、AGENT_RUNNER（可选，见 agent-eval/run_case.py）
set -uo pipefail
cd "$(dirname "$0")"
what="${1:-all}"; rc=0
py() {  # $1=层；$2=allow_skip
  local log; log="$(mktemp)"
  python3 -m unittest discover -s "py/$1" -t . -p 'test_*.py' -v 2>&1 | tee "$log"
  [ "${PIPESTATUS[0]}" -eq 0 ] || rc=1
  if [ "${2:-0}" != 1 ] && grep -qE "skipped=[0-9]+|\.\.\. skipped" "$log"; then
    echo "!! $1 层出现 SKIP：按 FAIL 计（只有 L5 可 SKIP）"; rc=1; fi
  rm -f "$log"
}
tsrun() {
  local log; log="$(mktemp)"
  (cd ts && { [ -d node_modules ] || npm ci --no-audit --no-fund; } && npx vitest run) 2>&1 | tee "$log"
  [ "${PIPESTATUS[0]}" -eq 0 ] || rc=1
  grep -qE "[0-9]+ (skipped|todo)" "$log" && { echo "!! TS 层出现 skip/todo：不允许"; rc=1; }
  rm -f "$log"
}
gate_all() {
  for l in gate unit contract static integration; do py "$l"; done
  py agent_eval 1
  [ -n "${AGENT_RUNNER:-}" ] || echo "== L5：未设置 AGENT_RUNNER → 15 个 AE 判 SKIP（人工评测，发布前须过 release 门禁）"
  tsrun
  python3 tools/trace.py --check || rc=1
}
case "$what" in
  gate) py gate ;; unit) py unit ;; contract) py contract ;; static) py static ;; integration) py integration ;; agent) py agent_eval 1 ;;
  ts) tsrun ;;
  all) gate_all ;;
  release) python3 tools/release_gate.py || rc=1 ;;
  *) echo "unknown: $what"; exit 2 ;;
esac
echo "== 判定（$what）：$([ $rc -eq 0 ] && echo '通过' || echo '未通过（存在 FAIL/ERROR/不允许的 SKIP 或人工存档缺失），不能判定完成')"
exit $rc
