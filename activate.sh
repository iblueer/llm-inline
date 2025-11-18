#!/usr/bin/env bash
# Activation script for llm-inline
set -euo pipefail

# Resolve project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_DIR="$HOME/.local/bin"
WRAPPER_PATH="$WRAPPER_DIR/llmi"
VENV_DIR="$SCRIPT_DIR/.venv"

mkdir -p "$WRAPPER_DIR"

# Create venv and install deps
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install -U pip setuptools wheel
fi
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

# Create wrapper script with absolute paths
cat > "$WRAPPER_PATH" <<EOF
#!/usr/bin/env bash
VENV_PY="$VENV_DIR/bin/python"
SCRIPT="$SCRIPT_DIR/llmi.py"
exec "\$VENV_PY" "\$SCRIPT" "\$@"
EOF

chmod +x "$WRAPPER_PATH"

echo "✅ 已安装 llmi 命令到: $WRAPPER_PATH"
if ! echo ":$PATH:" | grep -q ":$WRAPPER_DIR:"; then
  echo "ℹ️  请将 $WRAPPER_DIR 加入 PATH，例如:"
  echo "   echo 'export PATH=\"$WRAPPER_DIR:\$PATH\"' >> ~/.bashrc  # 或 ~/.zshrc"
fi

# Install shell integration for Tab insertion
CONF_DIR="$HOME/.config/llmi"
mkdir -p "$CONF_DIR"
cp -f "$SCRIPT_DIR/llmi.zsh" "$CONF_DIR/llmi.zsh"
cp -f "$SCRIPT_DIR/llmi.bash" "$CONF_DIR/llmi.bash"
echo "ℹ️  Zsh 集成: $CONF_DIR/llmi.zsh"
echo "   立即启用: source $CONF_DIR/llmi.zsh"
echo "   或在 ~/.zshrc 添加: source $CONF_DIR/llmi.zsh (建议放在文件末尾，晚于 oh-my-zsh/compinit)"
echo "ℹ️  Bash 集成: $CONF_DIR/llmi.bash"
echo "   立即启用: source $CONF_DIR/llmi.bash"
echo "   或在 ~/.bashrc 添加: source $CONF_DIR/llmi.bash"