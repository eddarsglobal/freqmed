#!/bin/bash
# GEN-R66: synchronize a complete source candidate into an isolated Git worktree.
# This script NEVER modifies the owner's original worktree/main branch.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
BRANCH="candidate/gen-r66-sequence-audit-20261123"
TARGET="generator/candidates/GEN-R66"

if [ "$(uname -s)" != "Darwin" ]; then echo "GEN_R66_MACOS_REQUIRED" >&2; exit 2; fi
for cmd in git python3 shasum rsync; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "MISSING_COMMAND:$cmd" >&2; exit 3; }
done

# Validate the complete candidate before touching Git.
( cd "$HERE" && shasum -a 256 -c SHA256SUMS.txt )
( cd "$HERE" && python3 -B tools/run_tests_r66.py )

REPO=""
for d in "$HOME/Documents/App_py/freqmed" "$HOME/Documents/App_py/freqmed/Github"; do
  if git -C "$d" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    found="$(git -C "$d" rev-parse --show-toplevel)"
    if [ -n "$REPO" ] && [ "$REPO" != "$found" ]; then
      echo "MULTIPLE_GIT_REPOS_FOUND_REQUIRES_EXPLICIT_CHOICE" >&2; exit 4
    fi
    REPO="$found"
  fi
done
[ -n "$REPO" ] || { echo "FREQMED_LOCAL_GIT_REPO_NOT_FOUND" >&2; exit 4; }
ORIGIN="$(git -C "$REPO" remote get-url origin)"
case "$ORIGIN" in
  https://github.com/eddarsglobal/freqmed|https://github.com/eddarsglobal/freqmed.git|git@github.com:eddarsglobal/freqmed|git@github.com:eddarsglobal/freqmed.git) ;;
  *) echo "GIT_ORIGIN_MISMATCH:$ORIGIN" >&2; exit 5;;
esac

printf 'ORIGINAL_GIT_ROOT=%s\n' "$REPO"
printf 'ORIGINAL_WORKTREE_STATUS_BEFORE\n'
git -C "$REPO" status --short

# No checkout, reset, commit or staging in the original repository.
git -C "$REPO" fetch --no-tags origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R66_SYNC_XXXXXX")"
rmdir "$WORK"
git -C "$REPO" worktree add --detach "$WORK" "refs/remotes/origin/$BRANCH"

case "$WORK" in "$HOME/Downloads/FREQMED_GEN_R66_SYNC_"*) ;; *) echo "INVALID_TEMP_WORKTREE" >&2; exit 6;; esac
mkdir -p "$WORK/$TARGET"
rsync -a --delete --exclude='__pycache__/' --exclude='*.pyc' \
  "$HERE/" "$WORK/$TARGET/"

git -C "$WORK" add -A -- "$TARGET"
if git -C "$WORK" diff --cached --quiet; then
  echo "GEN_R66_GIT_NO_SOURCE_CHANGES"
else
  git -C "$WORK" commit -m "GEN-R66: native sequence audit, adversarial tests and Mac Intel runner"
fi
# Fast-forward ONLY. Never force push; fail rather than overwrite others' work.
git -C "$WORK" push origin "HEAD:refs/heads/$BRANCH"
printf 'GEN_R66_REMOTE_BRANCH=%s\n' "$BRANCH"
printf 'GEN_R66_REMOTE_COMMIT=%s\n' "$(git -C "$WORK" rev-parse HEAD)"
printf 'GEN_R66_SOURCE_WORKTREE=%s\n' "$WORK"
printf 'GEN_R66_PR=https://github.com/eddarsglobal/freqmed/pull/25\n'
printf 'ORIGINAL_WORKTREE_STATUS_AFTER\n'
git -C "$REPO" status --short
printf 'GEN_R66_MAIN_WORKTREE_PRESERVED=YES\n'
printf 'GEN_R66_NO_MERGE=YES\n'
