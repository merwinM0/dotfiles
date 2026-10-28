#!/usr/bin/env bash
# 在 Rust 工作区中执行。只通过 Cargo 官方 clean 命令清理本工作区产物。
# 依赖：bash、cargo、jq、realpath、du (Linux/GNU coreutils)
set -euo pipefail

usage() {
  cat <<'USAGE'
用法（在 Rust workspace 中执行）：
  target-guard.sh status                 显示 target 体积和建议
  target-guard.sh trim                   超出阈值时仅清理 dev profile
  target-guard.sh clean-release --yes    明确清理 release profile
  target-guard.sh clean-all --yes        明确清理所有 Cargo 构建产物

环境变量：RUST_TARGET_MAX_MIB（默认 3072，即 3 GiB）
为安全起见，清理仅允许发生在当前 workspace 内部的 Cargo target 目录。
USAGE
}

mode="${1:-status}"
case "$mode" in
  -h|--help|help) usage; exit 0 ;;
  status|trim|clean-release|clean-all) ;;
  *) usage >&2; exit 2 ;;
esac

for cmd in cargo jq realpath du dirname; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '缺少命令：%s；没有执行任何清理。\n' "$cmd" >&2
    exit 1
  fi
done

limit="${RUST_TARGET_MAX_MIB:-3072}"
if ! [[ "$limit" =~ ^[1-9][0-9]*$ ]]; then
  printf 'RUST_TARGET_MAX_MIB 必须是正整数（MiB）。\n' >&2
  exit 2
fi

# 不在目标目录以外执行 cargo clean，避免误处理其他工作区。
manifest="$(cargo locate-project --workspace --message-format plain)"
workspace="$(realpath -- "$(dirname -- "$manifest")")"
metadata="$(cargo metadata --no-deps --format-version 1)"
target="$(printf '%s\n' "$metadata" | jq -er '.target_directory')"
target="$(realpath -m -- "$target")"

if [[ ! -d "$target" ]]; then
  printf '工作区：%s\ntarget：%s（尚不存在）\n' "$workspace" "$target"
  exit 0
fi

used="$(du -sm -- "$target" | awk '{print $1}')"
printf '工作区：%s\ntarget：%s\n已用：%s MiB；阈值：%s MiB\n' \
  "$workspace" "$target" "$used" "$limit"

if [[ "$mode" == status ]]; then
  if (( used > limit )); then
    echo '已超阈值。请先确认是否仍需 debug 产物；满足条件时可运行 trim。'
  else
    echo '未超过阈值；保留缓存以加快后续构建。'
  fi
  exit 0
fi

# realpath 会解析符号链接：target 在 workspace 外部，可能是共享或全局缓存。
case "$target" in
  "$workspace"/*) ;;
  *) echo '安全拦截：target 不位于当前 workspace 内部，拒绝自动清理。' >&2; exit 3 ;;
esac

if [[ "$target" == "$workspace" ]]; then
  echo '安全拦截：target 不得是 workspace 根目录。' >&2
  exit 3
fi

case "$mode" in
  trim)
    if (( used <= limit )); then
      echo '未超过阈值；无需清理。'
      exit 0
    fi
    echo '超过阈值，清理当前 workspace 的 dev profile（会影响下次 debug 编译速度）。'
    cargo clean --manifest-path "$manifest" --profile dev
    ;;
  clean-release)
    if [[ "${2:-}" != '--yes' ]]; then
      echo '请显式附加 --yes 后再清理 release 产物。' >&2
      exit 2
    fi
    cargo clean --manifest-path "$manifest" --release
    ;;
  clean-all)
    if [[ "${2:-}" != '--yes' ]]; then
      echo '请显式附加 --yes 后再清理全部构建产物。' >&2
      exit 2
    fi
    cargo clean --manifest-path "$manifest"
    ;;
esac

if [[ -d "$target" ]]; then
  remaining="$(du -sm -- "$target" | awk '{print $1}')"
else
  remaining=0
fi
printf '清理完成。剩余：%s MiB。\n' "$remaining"
if (( remaining > limit )); then
  echo '仍超过阈值；可能有 release/其他 profile 产物。不会擅自继续删除。'
fi
