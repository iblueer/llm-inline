#!/bin/sh
# POSIX shell, supports: curl | sh
set -eu

echo ">>> 开始卸载 llm-inline ..."

INSTALL_ROOT="$HOME/.llmi"
PROJECT_ID="${LLM_PROJECT_ID:-maemolee/llm-inline}"
BEGIN_MARK="# >>> ${PROJECT_ID} BEGIN (managed) >>>"
END_MARK="# <<< ${PROJECT_ID} END   <<<"

# 0) 若当前目录在安装目录下，先切回家目录
case "$PWD" in
  "$INSTALL_ROOT"|"$INSTALL_ROOT"/*) cd "$HOME" ;;
esac

# 1) 删除安装目录
if [ -d "$INSTALL_ROOT" ]; then
  rm -rf "$INSTALL_ROOT"
  echo "✓ 已删除目录 $INSTALL_ROOT"
else
  echo "ℹ 未发现 $INSTALL_ROOT"
fi

# 2) 删除技能目录
SKILLS_DIR="$HOME/.llmi-inline"
if [ -d "$SKILLS_DIR" ]; then
  rm -rf "$SKILLS_DIR"
  echo "✓ 已删除技能目录 $SKILLS_DIR"
else
  echo "ℹ 未发现 $SKILLS_DIR"
fi

# 3) 删除 ~/.local/bin 中的符号链接
LOCAL_BIN_LLMI="$HOME/.local/bin/llmi"
if [ -L "$LOCAL_BIN_LLMI" ]; then
  rm -f "$LOCAL_BIN_LLMI"
  echo "✓ 已删除符号链接 $LOCAL_BIN_LLMI"
elif [ -f "$LOCAL_BIN_LLMI" ]; then
  rm -f "$LOCAL_BIN_LLMI"
  echo "✓ 已删除可执行文件 $LOCAL_BIN_LLMI"
else
  echo "ℹ 未发现 $LOCAL_BIN_LLMI"
fi

remove_block() {
  file="$1"
  if [ -f "$file" ]; then
    tmp=$(mktemp 2>/dev/null || mktemp -t llmi-uninstall)
    awk -v begin="$BEGIN_MARK" -v end="$END_MARK" '
      $0 == begin {skip=1; next}
      $0 == end {skip=0; next}
      skip==0 {print}
    ' "$file" >"$tmp"
    mv "$tmp" "$file"
    echo "✓ 已从 $file 移除 llm-inline 配置块"
  else
    echo "ℹ 未发现 $file"
  fi
}

# 4) 移除shell配置中的llm-inline配置块
remove_block "${ZDOTDIR:-$HOME}/.zshrc"
remove_block "$HOME/.bashrc"

echo
echo ">>> 卸载完成 🎉"
echo "提示：不会删除你的 LLM 配置文件（如 ~/.llm-switch）。如需彻底清理，请检查相关配置。"
