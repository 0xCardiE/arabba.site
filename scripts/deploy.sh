#!/usr/bin/env bash
# Pull latest static site files for arabba.hr.
# Triggered manually or by scripts/github-deploy-webhook.js on GitHub push.
set -euo pipefail

ROOT="/var/www/arabba"
LOG_DIR="$ROOT/scripts/logs"
LOG_FILE="$LOG_DIR/deploy.log"
LOCK_FILE="/tmp/arabba-deploy.lock"
BRANCH="${DEPLOY_BRANCH:-main}"

mkdir -p "$LOG_DIR"

log() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" | tee -a "$LOG_FILE"
}

run_locked() {
  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    log "Deploy already running; skipping."
    exit 0
  fi
  "$@"
}

deploy() {
  log "Deploy started (branch=$BRANCH)"

  cd "$ROOT"

  log "Fetching and pulling latest changes"
  git fetch origin "$BRANCH"
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH"

  log "Health check"
  curl -fsS --max-time 15 https://arabba.hr/ >/dev/null

  log "Deploy finished successfully"
}

run_locked deploy
