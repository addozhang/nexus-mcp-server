#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Ralph Wiggum Loop for Nexus MCP Server (tmux version)
# =============================================================================
# Project: Sonatype Nexus Pro 3 MCP Server (Python + FastMCP)
# Mode: BOTH (Planning → Building)
# CLI: opencode (running in tmux for TTY)
# Max Iterations: 15 (5 for planning, 10 for building)
# =============================================================================

# Configuration
MAX_PLANNING_ITERS=5
MAX_BUILDING_ITERS=10
PLAN_SENTINEL='STATUS: PLANNING_COMPLETE'
BUILD_SENTINEL='STATUS: COMPLETE'
LOG_FILE=".ralph/ralph.log"
BACKPRESSURE_CMD="pytest tests/ -v && mypy src/ && ruff check src/ tests/"
OPENCODE_BIN="/home/addo/.opencode/bin/opencode"
MODEL="github-copilot/claude-opus-4.5"

# tmux setup
SOCKET="/tmp/openclaw-tmux-sockets/opencode-ralph.sock"
SESSION="opencode-ralph-$$"
mkdir -p /tmp/openclaw-tmux-sockets

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log() { echo -e "${BLUE}[Ralph]${NC} $*" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}✅ $*${NC}" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}❌ $*${NC}" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}" | tee -a "$LOG_FILE"; }

# Cleanup function
cleanup() {
  log "Cleaning up tmux session..."
  tmux -S "$SOCKET" kill-session -t "$SESSION" 2>/dev/null || true
}
trap cleanup EXIT

# =============================================================================
# Pre-flight checks
# =============================================================================

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  error "Not inside a git repository. Run this inside ~/nexus-mcp-server/"
  exit 1
fi

if ! [ -f "$OPENCODE_BIN" ]; then
  error "opencode CLI not found at $OPENCODE_BIN"
  exit 1
fi

if ! command -v tmux &> /dev/null; then
  error "tmux not found. Install it first: sudo apt install tmux"
  exit 1
fi

# Create log directory
mkdir -p .ralph

# Create tmux session
tmux -S "$SOCKET" new -d -s "$SESSION" -n ralph
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 "cd $(pwd)" Enter
sleep 1

success "Ralph loop initialized (tmux session: $SESSION)"
log "Project: $(pwd)"
log "Max iterations: Planning=$MAX_PLANNING_ITERS, Building=$MAX_BUILDING_ITERS"
log "Monitor with: tmux -S '$SOCKET' attach -t '$SESSION'"

# =============================================================================
# Phase 1: PLANNING
# =============================================================================

log "\n=========================================="
log "Phase 1: PLANNING"
log "=========================================="

# Copy planning prompt
cp PROMPT_PLANNING.md PROMPT.md
success "Switched to PLANNING mode"

for i in $(seq 1 "$MAX_PLANNING_ITERS"); do
  log "\n--- PLANNING iteration $i/$MAX_PLANNING_ITERS ---"
  
  # Send opencode command to tmux
  CMD="$OPENCODE_BIN run --model $MODEL \"\$(cat PROMPT.md)\""
  tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 "$CMD" Enter
  
  # Wait for prompt to return (indicating completion)
  log "Waiting for OpenCode to complete..."
  TIMEOUT=300  # 5 minutes max per iteration
  ELAPSED=0
  while [ $ELAPSED -lt $TIMEOUT ]; do
    OUTPUT=$(tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -5)
    if echo "$OUTPUT" | grep -q "addo@.*\$"; then
      success "Planning iteration $i completed"
      break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
  done
  
  if [ $ELAPSED -ge $TIMEOUT ]; then
    error "Planning iteration $i timed out after $TIMEOUT seconds"
    tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 C-c
    exit 1
  fi
  
  # Capture output to log
  tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200 >> "$LOG_FILE"
  
  # Check if planning is complete
  if grep -Fq "$PLAN_SENTINEL" IMPLEMENTATION_PLAN.md; then
    success "Planning phase complete! Moving to BUILDING..."
    break
  fi
  
  # Safety check
  if [ "$i" -eq "$MAX_PLANNING_ITERS" ]; then
    error "Planning phase reached max iterations without completion"
    warn "Review IMPLEMENTATION_PLAN.md manually"
    exit 1
  fi
done

# =============================================================================
# Phase 2: BUILDING
# =============================================================================

log "\n=========================================="
log "Phase 2: BUILDING"
log "=========================================="

# Copy building prompt
cp PROMPT_BUILDING.md PROMPT.md
success "Switched to BUILDING mode"

for i in $(seq 1 "$MAX_BUILDING_ITERS"); do
  log "\n--- BUILDING iteration $i/$MAX_BUILDING_ITERS ---"
  
  # Send opencode command to tmux
  CMD="$OPENCODE_BIN run --model $MODEL \"\$(cat PROMPT.md)\""
  tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 "$CMD" Enter
  
  # Wait for prompt to return
  log "Waiting for OpenCode to complete..."
  TIMEOUT=600  # 10 minutes max per iteration (building takes longer)
  ELAPSED=0
  while [ $ELAPSED -lt $TIMEOUT ]; do
    OUTPUT=$(tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -5)
    if echo "$OUTPUT" | grep -q "addo@.*\$"; then
      success "Building iteration $i completed"
      break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
  done
  
  if [ $ELAPSED -ge $TIMEOUT ]; then
    warn "Building iteration $i timed out - may need manual intervention"
    tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 C-c
  fi
  
  # Capture output to log
  tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -500 >> "$LOG_FILE"
  
  # Run backpressure (tests) if venv exists
  if [ -n "$BACKPRESSURE_CMD" ] && [ -f "venv/bin/activate" ]; then
    log "Running backpressure: $BACKPRESSURE_CMD"
    tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 "source venv/bin/activate && $BACKPRESSURE_CMD" Enter
    sleep 10
  fi
  
  # Check if building is complete
  if grep -Fq "$BUILD_SENTINEL" IMPLEMENTATION_PLAN.md; then
    success "Building phase complete! 🎉"
    log "\nFinal status:"
    log "- Implementation plan: IMPLEMENTATION_PLAN.md"
    log "- Logs: $LOG_FILE"
    log "- Git history: git log --oneline"
    log "- tmux session: tmux -S '$SOCKET' attach -t '$SESSION'"
    exit 0
  fi
  
  # Safety check
  if [ "$i" -eq "$MAX_BUILDING_ITERS" ]; then
    error "Building phase reached max iterations without completion"
    warn "Review IMPLEMENTATION_PLAN.md for remaining tasks"
    warn "tmux session still active: tmux -S '$SOCKET' attach -t '$SESSION'"
    exit 1
  fi
done

# Should not reach here
error "Loop ended unexpectedly"
exit 1
