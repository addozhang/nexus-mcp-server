#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Ralph Wiggum Loop for Nexus MCP Server
# =============================================================================
# Project: Sonatype Nexus Pro 3 MCP Server (Python + FastMCP)
# Mode: BOTH (Planning → Building)
# CLI: opencode
# Max Iterations: 15 (5 for planning, 10 for building)
# Sandbox: Docker (recommended for safety)
# =============================================================================

# Configuration
MAX_PLANNING_ITERS=5
MAX_BUILDING_ITERS=10
PLAN_SENTINEL='STATUS: PLANNING_COMPLETE'
BUILD_SENTINEL='STATUS: COMPLETE'
LOG_FILE=".ralph/ralph.log"
BACKPRESSURE_CMD="pytest tests/ -v && mypy src/ && ruff check src/ tests/"

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

# =============================================================================
# Pre-flight checks
# =============================================================================

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  error "Not inside a git repository. Run this inside ~/nexus-mcp-server/"
  exit 1
fi

if ! command -v opencode &> /dev/null; then
  error "opencode CLI not found. Install it first."
  exit 1
fi

# Create log directory
mkdir -p .ralph

success "Ralph loop initialized"
log "Project: $(pwd)"
log "Max iterations: Planning=$MAX_PLANNING_ITERS, Building=$MAX_BUILDING_ITERS"

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
  
  # Run opencode (auto-approve for planning phase)
  if opencode run "$(cat PROMPT.md)" 2>&1 | tee -a "$LOG_FILE"; then
    success "Planning iteration $i completed"
  else
    error "Planning iteration $i failed"
    exit 1
  fi
  
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
  
  # Run opencode (auto-approve for building phase)
  if opencode run "$(cat PROMPT.md)" 2>&1 | tee -a "$LOG_FILE"; then
    success "Building iteration $i completed"
  else
    warn "Building iteration $i had errors, continuing..."
  fi
  
  # Run backpressure (tests)
  if [ -n "$BACKPRESSURE_CMD" ] && [ -f "venv/bin/activate" ]; then
    log "Running backpressure: $BACKPRESSURE_CMD"
    if bash -c "source venv/bin/activate && $BACKPRESSURE_CMD" 2>&1 | tee -a "$LOG_FILE"; then
      success "Tests passed"
    else
      warn "Tests failed - agent should fix in next iteration"
    fi
  fi
  
  # Check if building is complete
  if grep -Fq "$BUILD_SENTINEL" IMPLEMENTATION_PLAN.md; then
    success "Building phase complete! 🎉"
    log "\nFinal status:"
    log "- Implementation plan: IMPLEMENTATION_PLAN.md"
    log "- Logs: $LOG_FILE"
    log "- Git history: git log --oneline"
    exit 0
  fi
  
  # Safety check
  if [ "$i" -eq "$MAX_BUILDING_ITERS" ]; then
    error "Building phase reached max iterations without completion"
    warn "Review IMPLEMENTATION_PLAN.md for remaining tasks"
    exit 1
  fi
done

# Should not reach here
error "Loop ended unexpectedly"
exit 1
