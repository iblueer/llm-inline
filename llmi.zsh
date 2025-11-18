#!/usr/bin/env zsh
# llmi zsh integration: Press Tab on empty prompt to insert last llmi suggestion

# Only for interactive shells
[[ -o interactive ]] || return 0

typeset -g LLMI_CACHE_DIR
LLMI_CACHE_DIR=${LLMI_CACHE_DIR:-$HOME/.cache/llmi}
typeset -g LLMI_LAST_CMD
LLMI_LAST_CMD="$LLMI_CACHE_DIR/last_command"

function llmi-insert-or-complete() {
  # If line buffer is empty and we have a cached command, insert it; otherwise, do normal completion
  if [[ -z "$BUFFER" && -r "$LLMI_LAST_CMD" ]]; then
    LBUFFER="$(< "$LLMI_LAST_CMD")"
  else
    zle expand-or-complete
  fi
}
zle -N llmi-insert-or-complete

_llmi_bind_tab() {
  bindkey -M emacs '^I' llmi-insert-or-complete 2>/dev/null || true
  bindkey -M viins '^I' llmi-insert-or-complete 2>/dev/null || true
}

# Initial bind and also re-assert on each prompt (some plugins reset bindings)
_llmi_bind_tab
autoload -Uz add-zsh-hook 2>/dev/null || true
typeset -f add-zsh-hook >/dev/null 2>&1 && add-zsh-hook precmd _llmi_bind_tab

# Optional: print a hint once per shell session
if [[ -z "$LLMI_ZSH_HINT_SHOWN" ]]; then
  export LLMI_ZSH_HINT_SHOWN=1
  echo "llmi: 已启用 Tab 快捷粘贴（空行按 Tab 自动插入上次建议命令）"
fi
fi
