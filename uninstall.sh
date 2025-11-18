#!/usr/bin/env bash
# Uninstall script for llm-inline
set -euo pipefail

TARGET_DIR="$HOME/.local/bin"

rm -f "$TARGET_DIR/llmi"
echo "✅ llm-inline 卸载完成！"