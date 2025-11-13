# SUBPOR: T000003-auth-unblock

**Owner**: PeerB
**Status**: ✅ CLOSED - Resolved-Infeasible
**Created**: 2025-11-13
**Closed**: 2025-11-13
**Timebox**: 0.5d (investigation phase) - COMPLETED

## Goal

Unblock automated data collection by resolving API authentication and authorization issues for GitHub and Twitter toolkits.

## Scope

**IN**: Connection validation, OAuth completion, scope verification, support ticket creation, validation probe execution

**OUT**: Full M1 implementation (deferred until auth completes)

## Acceptance Criteria

- [x] **AC1**: GitHub connection status documented (.cccc/work/validation/connections.github.txt exists)
- [x] **AC2**: Twitter connection status documented (.cccc/work/validation/connections.twitter.txt exists)
- [x] **AC3**: ❌ **INFEASIBLE** - GitHub automation path determined structurally infeasible (RUBE MCP GitHub OAuth does not support `read:org` scope, not solvable within platform)
- [x] **AC4**: ⏸️ **DEFERRED to M2** - Twitter v2 following-graph has low standalone value without GitHub seed layer (opportunistic, not M1-critical)
- [x] **AC5**: ⏸️ **DEFERRED to M2** - Validation probe unnecessary (automation paths unavailable)
- [x] **AC6**: ✅ **COMPLETE** - Investigation findings documented in Deliverables + `.cccc/work/validation/github_scope_infeasibility.md`

## Closure Summary

**Outcome**: Investigation COMPLETE - GitHub automation path determined **STRUCTURALLY INFEASIBLE** within RUBE MCP free tier constraints.

**Key Finding**: RUBE MCP GitHub OAuth integration uses fixed default scopes (`['user']` only) and does not offer `read:org` scope option required for GITHUB_LIST_ORGANIZATION_MEMBERS API. This is a platform architectural constraint, not a temporary blocker.

**Evidence Chain**:
1. User #000077 (2025-11-13T06:40): Investigated RUBE MCP GitHub connection settings, confirmed `read:org` scope unavailable
2. PeerB #000076 (2025-11-13T06:46): Technical verification via RUBE_MANAGE_CONNECTIONS, documented in `.cccc/work/validation/github_scope_infeasibility.md`
3. Independent convergence: PeerA strategic analysis + PeerB technical validation reached identical conclusion

**Impact on M1**:
- ❌ GitHub-seed automation (Path B): **ABANDONED** - permanently infeasible
- ✅ Manual CSV + X Lists (Path A): **PROMOTED to M1 PRIMARY** - proven M0 method (151/151 success, 100% precision)
- ⏸️ Twitter v2 following-graph: **DEFERRED to M2** - low standalone value without GitHub seed layer
- 📊 M1 targets revised: 1.5k-2k authors (was 2k-3k), 4-5 weeks (was 2-3 weeks)

**Strategic Pivot**: M1 commits to manual collection approach. Bet 1 FALSIFIED permanently. POR updated (2025-11-13T15:50).

**Lessons Learned**: Validate tooling OAuth capabilities and architectural constraints BEFORE planning workflows dependent on specific API scopes.

## Current State (FINAL)

### GitHub Toolkit (Status: PARTIAL SUCCESS → INFEASIBLE)

**Final Finding**: RUBE MCP architectural limitation - `read:org` scope permanently unavailable
- OAuth Status: ACTIVE (User #000069 completed authorization)
- Granted Scopes: `['user']` only
- Missing Scope: `read:org` (required for GITHUB_LIST_ORGANIZATION_MEMBERS)
- Platform Constraint: RUBE MCP GitHub integration uses fixed default OAuth scopes, no customization option
- Impact: GitHub-seed automation path (Path B) **STRUCTURALLY INFEASIBLE**, not just temporarily blocked

**Evidence**:
1. User verification (User #000077): RUBE MCP GitHub connection settings lack `read:org` option
2. PeerB technical validation (PeerB #000071, #000076): GITHUB_GET_THE_AUTHENTICATED_USER ✅, org query ❌ INSUFFICIENT_SCOPES
3. Root cause analysis: `.cccc/work/validation/github_scope_infeasibility.md`

**Resolution**: GitHub automation abandoned. M1 pivots to manual CSV extraction from GitHub org pages (no API required).

### Twitter Toolkit (Status: ACTIVE with v2 blocker → DEFERRED)

**Finding**: Connection active but v2 endpoints return "client-not-enrolled"
- Connection ID: ca_osBqL0e0ZLgZ
- Connection Status: ACTIVE
- User: KaireiY9921 (ID: 1950833677333942272)
- Issue: App credentials not enrolled in Twitter Developer Project with v2 access
- Impact: Following-graph expansion (TWITTER_FOLLOWING_BY_USER_ID) unavailable

**Evidence**:
- Background task 2871a5 (following-graph probe): 0/5 API calls succeeded
- Error message: "client-not-enrolled"
- Output file: .cccc/work/foreman/probe-20251113/following.sample.jsonl (empty, 0 records)

**Resolution**: DEFERRED to M2 (opportunistic, not M1-critical)
- Following-graph has low standalone value without GitHub seed layer (which is now infeasible)
- M1 manual CSV+Lists method does not require Twitter v2 following APIs
- Support ticket submission deferred pending user decision (preserves future option if valuable for M2)

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
- **2025-11-13T15:50:00Z**: CLOSED - Resolved-Infeasible - User #000077 confirmed RUBE MCP GitHub OAuth lacks `read:org` scope option (platform architectural constraint); PeerB technical validation via RUBE_MANAGE_CONNECTIONS + root cause analysis (`.cccc/work/validation/github_scope_infeasibility.md`); GitHub automation path ABANDONED (Path B infeasible permanently); M1 pivots to manual CSV+Lists (Path A PRIMARY); Twitter v2 DEFERRED to M2 (low standalone value without GitHub seed); Bet 1 FALSIFIED permanently; POR updated with strategic pivot (2025-11-13T15:50)
