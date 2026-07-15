#!/usr/bin/env bash
set -euo pipefail

PAPER_DIR="${PAPER_DIR:-/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga}"
REMOTE_NAME="${REMOTE_NAME:-overleaf}"
LOCAL_BRANCH="${LOCAL_BRANCH:-${BRANCH:-main}}"
REMOTE_BRANCH="${REMOTE_BRANCH:-master}"
OVERLEAF_GIT_URL="${OVERLEAF_GIT_URL:-}"
OVERLEAF_GIT_TOKEN="${OVERLEAF_GIT_TOKEN:-}"
COMMIT_MSG="${1:-Update paper draft}"

cd "$PAPER_DIR"

if [[ ! -d .git ]]; then
  git init
  git branch -M "$LOCAL_BRANCH" 2>/dev/null || true
fi

if [[ -n "$OVERLEAF_GIT_URL" ]]; then
  if git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
    git remote set-url "$REMOTE_NAME" "$OVERLEAF_GIT_URL"
  else
    git remote add "$REMOTE_NAME" "$OVERLEAF_GIT_URL"
  fi
fi

if ! git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  echo "Missing $REMOTE_NAME remote. Set OVERLEAF_GIT_URL=https://git.overleaf.com/<project-id> and rerun." >&2
  exit 2
fi

remote_url="$(git remote get-url "$REMOTE_NAME")"
if [[ -n "$OVERLEAF_GIT_TOKEN" && "$remote_url" == https://git.overleaf.com/* ]]; then
  auth_url="https://git:${OVERLEAF_GIT_TOKEN}@${remote_url#https://}"
else
  auth_url="$remote_url"
fi

# Compile before pushing if latexmk is available.
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null
elif [[ -x /Users/fanta/Library/TinyTeX/bin/universal-darwin/latexmk ]]; then
  PATH="/Users/fanta/Library/TinyTeX/bin/universal-darwin:$PATH" latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null
fi

if [[ -f .overleaf_files ]]; then
  git add --pathspec-from-file=.overleaf_files
else
  git add .gitignore README.md main.tex references.bib drafts figures
fi
if git diff --cached --quiet; then
  echo "No staged paper changes."
else
  git commit -m "$COMMIT_MSG"
fi

# Rebase if remote already has content. Do not auto-resolve conflicts.
git pull --rebase "$auth_url" "$REMOTE_BRANCH"
git push "$auth_url" "$LOCAL_BRANCH:$REMOTE_BRANCH"
