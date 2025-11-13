# SUBPOR: T000003-auth-unblock

**Owner**: PeerB
**Status**: 🔴 BLOCKED
**Created**: 2025-11-13
**Timebox**: 0.5d (investigation phase)

## Goal

Unblock automated data collection by resolving API authentication and authorization issues for GitHub and Twitter toolkits.

## Scope

**IN**: Connection validation, OAuth completion, scope verification, support ticket creation, validation probe execution

**OUT**: Full M1 implementation (deferred until auth completes)

## Acceptance Criteria

- [x] **AC1**: GitHub connection status documented (.cccc/work/validation/connections.github.txt exists)
- [x] **AC2**: Twitter connection status documented (.cccc/work/validation/connections.twitter.txt exists)
- [ ] **AC3**: GitHub OAuth completed OR support ticket filed with ticket number
- [ ] **AC4**: Twitter v2 access enabled OR support ticket filed with ticket number
- [ ] **AC5**: Validation probe (5 seeds × 1 page following) executes successfully with ≥1 filtered result
- [ ] **AC6**: GitHub and Twitter ticket numbers and ETAs recorded in Deliverables section (per Foreman #000070)

## Current State

### GitHub Toolkit (Status: INITIATED)

**Finding**: OAuth authorization not completed
- Status: INITIATED (requires user authorization)
- Redirect URL: https://connect.composio.dev/link/lk_MDk4vBjk2D4F
- Issue: Cannot perform automated org member discovery
- Impact: Blocks GitHub-based seed expansion (GITHUB_SEARCH_USERS, GITHUB_GET_A_USER)

**Action Required**:
1. User authorizes GitHub via redirect URL
2. Verify org:read scope included in authorization
3. Test with GITHUB_GET_A_USER after completion

**Ticket**: TBD (pending user decision on OAuth timing)

### Twitter Toolkit (Status: ACTIVE with v2 blocker)

**Finding**: Connection active but v2 endpoints return "client-not-enrolled"
- Connection ID: ca_osBqL0e0ZLgZ
- Connection Status: ACTIVE
- User: KaireiY9921 (ID: 1950833677333942272)
- Issue: App credentials not enrolled in Twitter Developer Project with v2 access
- Impact: BLOCKER for following-graph expansion (TWITTER_FOLLOWING_BY_USER_ID fails)

**Evidence**:
- Background task 2871a5 (following-graph probe): 0/5 API calls succeeded
- Error message: "client-not-enrolled"
- Output file: .cccc/work/foreman/probe-20251113/following.sample.jsonl (empty, 0 records)

**Action Required**:
1. File support ticket with Composio/Twitter Developer Portal
2. Request: Enroll app credentials in Project with Twitter API v2 access
3. Priority: HIGH (blocks M1 automated collection)

**Ticket**: TBD (awaiting ticket creation)

## Evidence

- Connection validation: .cccc/work/validation/connections.{github,twitter}.txt
- Twitter v2 error proof: Background task 2871a5 output (exit code 0, 0 records generated)
- RUBE_MANAGE_CONNECTIONS output: 1 active (twitter), 1 initiated (github)

## Next Steps

1. **Immediate** (≤24h): File Twitter v2 support ticket, document ticket number in Deliverables(1)
2. **Short-term** (≤3d): Complete GitHub OAuth (user action), verify org:read scope
3. **Validation** (post-unblock): Execute 5-seed × 1-page following probe, expect ≥1 filtered result per seed

## Deliverables

1. Support Tickets & Timeline:
   - **GitHub OAuth**:
     * Ticket: User completed OAuth (User #000069, 2025-11-13T06:23)
     * Status: ⚠️ **PARTIAL SUCCESS** - Connection ACTIVE but missing `read:org` scope (only `['user']` granted)
     * Validation: PeerB #000071 (2025-11-13T06:30) - GITHUB_GET_THE_AUTHENTICATED_USER ✅, org query ❌ INSUFFICIENT_SCOPES
     * Action Required: User re-authorization with `read:org` scope (instructions sent)
     * ETA: ≤24h re-authorization OR T+72h commit to Fallback Path A
   - **Twitter v2 Access**:
     * Ticket: TBD (needs filing per Foreman #000070)
     * Status: Awaiting ticket submission
     * ETA: TBD (dependent on Composio/Twitter support response, est. 3-7d)

2. Validation Probe:
   - Execution window: Post-unblock
   - Target: 5 seeds (AlecRad, DarioAmodei, DrJimFan, EMostaque, jackclarkSF)
   - Expected: ≥1 filtered following per seed (filter: verified AND followers≥30k OR followers≥50k)

## Trade-offs

### Pro
- ✓ Identified exact blockers (GitHub: incomplete OAuth, Twitter: v2 enrollment)
- ✓ Documented evidence with connection IDs and error messages
- ✓ Clear action paths (OAuth URL for GitHub, support ticket for Twitter)

### Con
- External dependencies (user action for GitHub, provider support for Twitter)
- Timeline uncertainty (OAuth: hours-days, support ticket: days-weeks)
- M1 automated collection blocked until resolution

## References

- Foreman directive: Message 000054 (2025-11-13T14:26:32Z)
- Connection validation: .cccc/work/validation/connections.{github,twitter}.txt
- Twitter v2 error: Background task 2871a5

## REV

- **2025-11-13T14:30:00Z**: INVESTIGATION COMPLETE - GitHub initiated (needs OAuth), Twitter active but v2-blocked ("client-not-enrolled"); connections documented; support tickets TBD
