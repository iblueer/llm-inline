#!/usr/bin/env bash
# Local install script for llm-inline
# Usage: ./install-locally.sh
set -euo pipefail

# Resolve script directory reliably
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Delegate to activate.sh (creates venv, installs deps, writes wrapper)
bash "$SCRIPT_DIR/activate.sh"

# Ensure ~/.local/bin on PATH for future shells (idempotent)
LOCAL_BIN_LINE='export PATH="$HOME/.local/bin:$PATH"'
if [[ -n "${HOME:-}" ]]; then
  if ! grep -qs "\.local/bin" "$HOME/.zshrc" 2>/dev/null; then
    printf "\n" >> "$HOME/.zshrc" 2>/dev/null || true
    echo "$LOCAL_BIN_LINE" >> "$HOME/.zshrc"
    echo "ℹ️  已将 ~/.local/bin 写入 ~/.zshrc"
  fi
  if ! grep -qs "\.local/bin" "$HOME/.bashrc" 2>/dev/null; then
    printf "\n" >> "$HOME/.bashrc" 2>/dev/null || true
    echo "$LOCAL_BIN_LINE" >> "$HOME/.bashrc"
    echo "ℹ️  已将 ~/.local/bin 写入 ~/.bashrc"
  fi
fi

# Auto-enable shell integration (idempotent, append at end)
CONF_DIR="$HOME/.config/llmi"
if [[ -r "$CONF_DIR/llmi.zsh" ]]; then
  if ! grep -qs "source .*llmi.zsh" "$HOME/.zshrc" 2>/dev/null; then
    printf "\n" >> "$HOME/.zshrc" 2>/dev/null || true
    echo "source $CONF_DIR/llmi.zsh" >> "$HOME/.zshrc"
    echo "✅ 已写入 zsh 集成到 ~/.zshrc（文件末尾）"
  fi
fi
if [[ -r "$CONF_DIR/llmi.bash" ]]; then
  if ! grep -qs "source .*llmi.bash" "$HOME/.bashrc" 2>/dev/null; then
    printf "\n" >> "$HOME/.bashrc" 2>/dev/null || true
    echo "source $CONF_DIR/llmi.bash" >> "$HOME/.bashrc"
    echo "✅ 已写入 bash 集成到 ~/.bashrc（文件末尾）"
  fi
fi

echo "✅ 安装完成。现在可以运行: llmi ask \"你的问题\""
echo "ℹ️  已自动写入 shell 配置。请执行：\n   source ~/.zshrc  或  source ~/.bashrc  以使 Tab 快捷生效（或重开一个终端）。"