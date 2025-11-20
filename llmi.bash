#!/usr/bin/env bash
# llmi bash integration: Press Tab on empty prompt to insert last llmi suggestion

__llmi_cache_file() {
  local dir
  dir=${LLMI_CACHE_DIR:-"$HOME/.cache/llmi"}
  echo "$dir/last_command"
}

__llmi_insert_or_tab() {
  # Only handle when line is empty; otherwise fall back to default by inserting a literal tab
  if [[ -z "${READLINE_LINE:-}" ]]; then
    local f
    f="$(__llmi_cache_file)"
    if [[ -r "$f" ]]; then
      # Read and strip trailing newlines
      local cmd
      cmd=$(tr -d '\r' < "$f" | sed -e :a -e '/^\n*$/{$d;N;ba' -e '}' )
      READLINE_LINE="$cmd"
      READLINE_POINT=${#READLINE_LINE}
      return
    fi
  fi
  # Fallback: insert a literal tab (lets user keep existing behavior when non-empty)
  READLINE_LINE+=$'\t'
  READLINE_POINT=${#READLINE_LINE}
}

# Bind Tab to our function
bind -x '"\C-i":__llmi_insert_or_tab'

# One-time hint
# if [[ -z "$LLMI_BASH_HINT_SHOWN" ]]; then
#   export LLMI_BASH_HINT_SHOWN=1
#   echo "llmi: 已启用 Tab 快捷粘贴（空行按 Tab 自动插入上次建议命令）"
# fi
