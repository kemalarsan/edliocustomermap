# Development Plan - Safe Feature Implementation

## Lessons Learned from Failed Implementation

### What Broke
1. **Google SSO Changes** - Modified initialization broke authentication
2. **Complex State Management** - Too many global variables caused conflicts
3. **Large Single Commits** - Made it hard to identify breaking changes
4. **No Incremental Testing** - Deployed multiple features at once

### New Development Approach

## Phase 1: Fix Google SSO Loading (feature/sso-loading-fix)
**Goal**: Show loading state for Google Sign-In without breaking auth

**Approach**:
1. Add minimal loading indicator
2. Don't modify initialization logic
3. Test authentication thoroughly
4. Small, focused changes only

## Phase 2: Simple Navigation Tabs (feature/simple-navigation)
**Goal**: Add tab navigation without complex state

**Approach**:
1. Start with just 2 tabs (Map, Table)
2. No keyboard shortcuts initially
3. Simple show/hide logic
4. Test state persistence

## Phase 3: Basic Table View (feature/basic-table)
**Goal**: Simple customer table without advanced features

**Approach**:
1. Basic HTML table
2. No pagination initially (show all)
3. Simple sorting on name/state
4. Minimal filtering

## Phase 4: Incremental Table Enhancements
Split into multiple small features:
- feature/table-pagination (add pagination)
- feature/table-search (add search)
- feature/table-export (add export)
- feature/table-health (add health scores)

## Testing Protocol

### Before Each Merge
1. **Local Testing**
   - Login and refresh 5 times
   - Test all existing features
   - Check console for errors
   - Test in different browsers

2. **Staging Testing**
   - Deploy to feature branch URL
   - Test for 24 hours
   - Get team feedback

3. **Rollback Plan**
   - Always tag before merge
   - Document rollback steps
   - Keep changes small enough to revert

## Implementation Rules

1. **One Feature Per Branch**
   - Single responsibility
   - Easy to test
   - Easy to revert

2. **Minimal Global State**
   - Use function parameters
   - Avoid global variables
   - Document any new globals

3. **Progressive Enhancement**
   - Features should degrade gracefully
   - Don't break existing functionality
   - Add, don't modify

4. **Code Review Required**
   - Another person tests the feature
   - Document what was tested
   - Confirm no regressions

## Priority Order

1. 🔴 **Critical**: Fix any authentication issues
2. 🟡 **High**: Basic navigation between views
3. 🟢 **Medium**: Table view with basic features
4. 🔵 **Low**: Advanced features (health scores, etc.)

## Success Criteria

Each feature is successful when:
- ✅ Existing features still work
- ✅ New feature works as intended
- ✅ No performance degradation
- ✅ Code is maintainable
- ✅ Can be reverted cleanly