#!/usr/bin/env bash
# Local uninstall script for llm-inline
# Usage: ./uninstall-locally.sh
set -euo pipefail

TARGET_DIR="$HOME/.local/bin"

rm -f "$TARGET_DIR/llmi"
echo "✅ llm-inline 卸载完成！"