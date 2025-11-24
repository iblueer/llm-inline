#!/bin/sh
# POSIX; supports: curl | sh
# Debug trace: LLM_INLINE_DEBUG=1 curl .../install.sh | sh
set -eu
[ "${LLM_INLINE_DEBUG:-0}" = "1" ] && set -x

# ----- error trap -----
on_err() {
  code=$?
  echo "✗ 安装失败 (exit=$code)。可能是网络/权限/文件系统问题。" >&2
  echo "提示：若启用了代理可尝试关闭；或设置镜像：export GITHUB_RAW_BASE=raw.fastgit.org 后重试。" >&2
  exit "$code"
}
trap 'on_err' ERR

echo ">>> 开始安装 llm-inline ..."

# ===== Step 0. 基础配置与目录 =====
RAW_HOST="${GITHUB_RAW_BASE:-raw.githubusercontent.com}"
REPO_PATH="maemolee/llm-inline"
BRANCH="main"
BASE_URL="https://${RAW_HOST}/${REPO_PATH}/${BRANCH}"

INSTALL_ROOT="$HOME/.llmi"
BIN_DIR="$INSTALL_ROOT/bin"
COMP_DIR="$INSTALL_ROOT/completions"
SHELL_NAME="$(basename "${LLMI_SHELL:-${SHELL:-}}")"
case "$SHELL_NAME" in
  bash) INIT_FILE="$INSTALL_ROOT/init.bash" ;;
  *) SHELL_NAME=zsh; INIT_FILE="$INSTALL_ROOT/init.zsh" ;;
esac

# 项目标记（可通过 LLM_PROJECT_ID 覆盖）
PROJECT_ID="${LLM_PROJECT_ID:-maemolee/llm-inline}"
BEGIN_MARK="# >>> ${PROJECT_ID} BEGIN (managed) >>>"
END_MARK="# <<< ${PROJECT_ID} END   <<<"

echo "[Step 0] 初始化目录：$INSTALL_ROOT"
mkdir -p "$BIN_DIR" "$COMP_DIR"

# ===== Step 1. 下载核心文件（带重试） =====
fetch() {
  url="$1"; dst="$2"
  echo "[Step 1] 下载 $url -> $dst"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 --retry-delay 1 -o "$dst" "$url"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$dst" "$url"
  else
    echo "需要 curl 或 wget 以下载文件，请先安装其中之一。" >&2
    exit 1
  fi
}

# 下载主要文件
fetch "$BASE_URL/llmi.py"                       "$BIN_DIR/llmi.py"
fetch "$BASE_URL/llmi.bash"                     "$BIN_DIR/llmi.bash"
fetch "$BASE_URL/llmi.zsh"                      "$BIN_DIR/llmi.zsh"
fetch "$BASE_URL/requirements.txt"               "$BIN_DIR/requirements.txt"

# 创建可执行包装器
cat > "$BIN_DIR/llmi" << 'WRAPPER'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llmi
sys.exit(llmi.main() if hasattr(llmi, 'main') else 0)
WRAPPER

# 使包装器可执行
chmod +x "$BIN_DIR/llmi"

# ===== Step 2. 安装Python依赖 =====
echo "[Step 2] 安装Python依赖..."
cd "$BIN_DIR"
if command -v pip3 >/dev/null 2>&1; then
  pip3 install -r requirements.txt --user
elif command -v pip >/dev/null 2>&1; then
  pip install -r requirements.txt --user
else
  echo "警告：未找到pip，请手动安装依赖：pip install -r requirements.txt"
fi

# ===== Step 3. 创建技能目录 =====
SKILLS_DIR="$HOME/.llmi-inline/skills"
echo "[Step 3] 创建技能目录：$SKILLS_DIR"
mkdir -p "$SKILLS_DIR"

# ===== Step 4. 生成 init 脚本 =====
if [ "$SHELL_NAME" = "bash" ]; then
  echo "[Step 4] 生成 init：$INIT_FILE"
  cat >"$INIT_FILE" <<'EINIT'
# llm-inline init for bash (auto-generated)
if [ -f "$HOME/.llmi/bin/llmi.bash" ]; then
  . "$HOME/.llmi/bin/llmi.bash"
fi
EINIT
else
  echo "[Step 4] 生成 init：$INIT_FILE"
  cat >"$INIT_FILE" <<'EINIT'
# llm-inline init (auto-generated)
# 幂等：尽量避免重复影响用户环境

# 补全目录（若未包含则追加）
case ":$fpath:" in
  *":$HOME/.llmi/completions:"*) ;;
  *) fpath+=("$HOME/.llmi/completions");;
esac

# 加载函数本体（仅交互式 zsh）
case "$-" in
  *i*)
    if [ -f "$HOME/.llmi/bin/llmi.zsh" ] && command -v zsh >/dev/null 2>&1; then
      . "$HOME/.llmi/bin/llmi.zsh"
    fi
    ;;
esac

# 补全未初始化则初始化一次
if ! typeset -f _main_complete >/dev/null 2>&1; then
  autoload -Uz compinit
  compinit
fi
EINIT
fi

# ===== Step 5. 幂等修改 rc 文件：唯一标记 + 原子替换 =====
if [ "$SHELL_NAME" = "bash" ]; then
  RC="$HOME/.bashrc"
  echo "[Step 5] 更新 Bash 配置：$RC （标记：$PROJECT_ID ）"
else
  if [ -n "${ZDOTDIR:-}" ]; then
    RC="$ZDOTDIR/.zshrc"
  else
    RC="$HOME/.zshrc"
  fi
  echo "[Step 5] 更新 Zsh 配置：$RC （标记：$PROJECT_ID ）"
fi

# 确保 rc 存在
[ -f "$RC" ] || : > "$RC"

# 先移除旧块（仅匹配整行唯一标记），再在尾部追加新块；用 mktemp 原子替换（兼容 GNU/BSD）
TMP_RC="$(mktemp 2>/dev/null || mktemp -t llmi-tools)"
awk -v begin="$BEGIN_MARK" -v end="$END_MARK" '
  BEGIN { skip=0 }
  $0 == begin { skip=1; next }
  $0 == end   { skip=0; next }
  skip==0 { print }
' "$RC" > "$TMP_RC"

{
  printf "%s\n" "$BEGIN_MARK"
  if [ "$SHELL_NAME" = "bash" ]; then
    printf '%s\n' 'source "$HOME/.llmi/init.bash"'
  else
    printf '%s\n' 'source "$HOME/.llmi/init.zsh"'
  fi
  printf "%s\n" "$END_MARK"
} >> "$TMP_RC"

# 末尾确保换行
LC_ALL=C tail -c 1 "$TMP_RC" >/dev/null 2>&1 || printf '\n' >>"$TMP_RC"

# 原子替换
mv "$TMP_RC" "$RC"

# ===== Step 6. 确保 ~/.local/bin 在 PATH 中 =====
LOCAL_BIN_LINE='export PATH="$HOME/.local/bin:$PATH"'
if [ -f "$HOME/.zshrc" ]; then
  if ! grep -qs "\.local/bin" "$HOME/.zshrc" 2>/dev/null; then
    printf "\n" >> "$HOME/.zshrc" 2>/dev/null || true
    echo "$LOCAL_BIN_LINE" >> "$HOME/.zshrc"
    echo "ℹ️  已将 ~/.local/bin 写入 ~/.zshrc"
  fi
fi
if [ -f "$HOME/.bashrc" ]; then
  if ! grep -qs "\.local/bin" "$HOME/.bashrc" 2>/dev/null; then
    printf "\n" >> "$HOME/.bashrc" 2>/dev/null || true
    echo "$LOCAL_BIN_LINE" >> "$HOME/.bashrc"
    echo "ℹ️  已将 ~/.local/bin 写入 ~/.bashrc"
  fi
fi

# 创建 ~/.local/bin 符号链接（如果不存在）
LOCAL_BIN_DIR="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN_DIR"
if [ ! -L "$LOCAL_BIN_DIR/llmi" ]; then
  ln -sf "$BIN_DIR/llmi" "$LOCAL_BIN_DIR/llmi"
fi

# ===== Step 7. 完成提示 =====
echo
echo ">>> 安装完成 🎉"
echo "安装目录：$INSTALL_ROOT"
echo "技能目录：$SKILLS_DIR"
echo "可执行文件：$BIN_DIR/llmi"
echo
echo "请执行： source \"$RC\""
echo "然后运行： llmi \"如何查看当前目录？\""
echo "         llmi list"
echo "         llmi install https://..."
