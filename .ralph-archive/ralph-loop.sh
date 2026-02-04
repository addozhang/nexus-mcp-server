#!/usr/bin/env bash
set -euo pipefail

# ========== Configuration ==========
CLI_CMD="/home/addo/.opencode/bin/opencode run"
MODEL="github-copilot/claude-sonnet-4.5"
MODE="BOTH"  # PLANNING | BUILDING | BOTH
MAX_PLANNING_ITERS=5
MAX_BUILDING_ITERS=10
WORKDIR="$HOME/nexus-mcp-server"
PLAN_SENTINEL='STATUS:\s*(PLANNING_)?COMPLETE'
ITER_TIMEOUT=1800  # 30 minutes per iteration

echo "🚀 Ralph Loop - Nexus MCP Server Streamable-HTTP Support"
echo "============================================"
echo "CLI: $CLI_CMD"
echo "Model: $MODEL"
echo "Mode: $MODE"
echo "Workdir: $WORKDIR"
echo "============================================"

# ========== Validation ==========
cd "$WORKDIR" || exit 1

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Not a git repository: $WORKDIR"
  exit 1
fi

mkdir -p .ralph

# ========== Helper: Run Iteration ==========
run_iteration() {
  local iter=$1 phase=$2 max_iters=$3
  
  echo ""
  echo "╔═══════════════════════════════════════════════╗"
  echo "║  $phase ITERATION $iter/$max_iters"
  echo "╚═══════════════════════════════════════════════╝"
  
  # Select prompt
  local prompt_file
  if [[ "$phase" == "PLANNING" ]]; then
    prompt_file="PROMPT_PLANNING.md"
  else
    prompt_file="PROMPT_BUILDING.md"
  fi
  
  if [[ ! -f "$prompt_file" ]]; then
    echo "❌ Prompt file not found: $prompt_file"
    return 1
  fi
  
  # Log file
  local log_file=".ralph/${phase}-iter-${iter}.log"
  
  echo "⏳ Running OpenCode..."
  echo "📝 Logging to: $log_file"
  
  # Run OpenCode directly with timeout
  if timeout $ITER_TIMEOUT $CLI_CMD --model "$MODEL" "$(cat "$prompt_file")" &> "$log_file"; then
    echo "✅ OpenCode completed successfully"
  else
    local exit_code=$?
    if [[ $exit_code -eq 124 ]]; then
      echo "⏱️  OpenCode timed out after ${ITER_TIMEOUT}s"
    else
      echo "⚠️  OpenCode exited with code $exit_code"
    fi
  fi
  
  # Show last lines of output
  echo ""
  echo "--- Last 15 lines of output ---"
  tail -n 15 "$log_file" || true
  echo "--- End of output ---"
  echo ""
  
  # Check completion sentinel
  if grep -Eq "$PLAN_SENTINEL" IMPLEMENTATION_PLAN.md 2>/dev/null; then
    echo "✨ COMPLETION DETECTED! ✨"
    return 0
  fi
  
  echo "⏭️  Completion not detected, continuing..."
  return 1
}

# ========== Main Loop ==========
case "$MODE" in
  PLANNING)
    echo "🧠 Running PLANNING mode only"
    for i in $(seq 1 $MAX_PLANNING_ITERS); do
      if run_iteration $i "PLANNING" $MAX_PLANNING_ITERS; then
        echo ""
        echo "🎉 Planning complete!"
        exit 0
      fi
    done
    echo "❌ Max planning iterations reached without completion"
    exit 1
    ;;
    
  BUILDING)
    echo "🔨 Running BUILDING mode only"
    for i in $(seq 1 $MAX_BUILDING_ITERS); do
      if run_iteration $i "BUILDING" $MAX_BUILDING_ITERS; then
        echo ""
        echo "🎉 Building complete!"
        exit 0
      fi
    done
    echo "❌ Max building iterations reached without completion"
    exit 1
    ;;
    
  BOTH)
    echo "🧠 Starting PLANNING phase..."
    for i in $(seq 1 $MAX_PLANNING_ITERS); do
      if run_iteration $i "PLANNING" $MAX_PLANNING_ITERS; then
        echo "✅ Planning phase complete"
        break
      fi
      
      if [[ $i -eq $MAX_PLANNING_ITERS ]]; then
        echo "⚠️  Planning incomplete, proceeding to building anyway..."
      fi
    done
    
    echo ""
    echo "🔨 Starting BUILDING phase..."
    
    # Clear planning completion marker
    sed -i '/STATUS:.*PLANNING_COMPLETE/d' IMPLEMENTATION_PLAN.md 2>/dev/null || true
    
    for i in $(seq 1 $MAX_BUILDING_ITERS); do
      if run_iteration $i "BUILDING" $MAX_BUILDING_ITERS; then
        echo ""
        echo "🎉 PROJECT COMPLETE! 🎉"
        exit 0
      fi
    done
    
    echo "❌ Max building iterations reached without completion"
    exit 1
    ;;
    
  *)
    echo "❌ Invalid MODE: $MODE (must be PLANNING, BUILDING, or BOTH)"
    exit 1
    ;;
esac
