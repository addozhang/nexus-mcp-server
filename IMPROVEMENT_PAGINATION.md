# Pagination Output Size Optimization

## Problem
When querying packages with hundreds of versions (e.g., popular libraries), the `get_maven_versions` and `get_python_versions` tools return too much data, causing "output exceeds maximum character limit of 10000" errors in MCP clients.

## Current Implementation
- ✅ Pagination is implemented with `page_size` and `continuation_token`
- ✅ Default `page_size` = 50
- ❌ Each version includes full `assets` array with `downloadUrl` and `path`
- ❌ Even with pagination, 50 versions × detailed assets = often > 10KB output

## Solution

### 1. Reduce Default Page Size
**Change**: `page_size` default from 50 → 20

**Reasoning**:
- 20 versions with assets ≈ 3-5KB (safe for 10KB limit)
- Users can still increase via parameter if needed
- Better user experience (less scrolling in chat)

### 2. Add `simple` Parameter (Optional Enhancement)
**New parameter**: `simple: bool = False`

When `simple=True`:
- Return only version numbers (no assets, no downloadUrl)
- Output: `["3.2.1", "3.2.0", "3.1.5", ...]`
- ~95% size reduction

**Use cases**:
- Quick version check: "What are the latest versions?"
- Version list for selection
- Follow-up query for specific version details

### 3. Optimize Output Format
**Current**:
```json
{
  "versions": [
    {
      "version": "3.2.1",
      "repository": "maven-central",
      "assets": [
        {"downloadUrl": "https://...", "path": "..."},
        {"downloadUrl": "https://...", "path": "..."}
      ]
    }
  ]
}
```

**Optimized** (for normal mode):
```json
{
  "versions": [
    {
      "version": "3.2.1",
      "repository": "maven-central",
      "assetCount": 2
    }
  ]
}
```
- Remove `assets` array from list view
- Add `assetCount` summary
- ~60% size reduction while keeping useful info

## Implementation Plan

### Phase 1: Quick Fix (Immediate)
1. Change default `page_size`: 50 → 20
2. Update tool descriptions to mention pagination

**Files**:
- `src/nexus_mcp/server.py` (2 tools)
- `src/nexus_mcp/tools/implementations.py` (2 implementations)
- Tests: verify page_size=20 default

### Phase 2: Simple Mode (Optional)
1. Add `simple: bool = False` parameter
2. Implement simplified output
3. Update tool descriptions
4. Add tests for simple mode

### Phase 3: Optimize Full Mode (Future)
1. Remove detailed `assets` from list view
2. Add `assetCount` summary
3. Consider new tool: `get_artifact_details(version)` for full info

## Testing
```bash
# Before: 50 versions = ~8-12KB (may exceed limit)
get_maven_versions(group_id="org.springframework", artifact_id="spring-core")

# After: 20 versions = ~3-5KB (safe)
get_maven_versions(group_id="org.springframework", artifact_id="spring-core")

# Simple mode: 100 versions = ~1KB (very safe)
get_maven_versions(group_id="org.springframework", artifact_id="spring-core", simple=True, page_size=100)
```

## Rollout Strategy
1. ✅ **Phase 1** (This PR): Change default page_size to 20
2. ⏳ **Phase 2** (Optional): Add simple mode if users request it
3. ⏳ **Phase 3** (Future): Full output format optimization

---

**Decision**: Start with Phase 1 (minimal change, immediate fix)
