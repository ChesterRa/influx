# T000003: Auth-Unblock for M1 Automation Paths

**Owner**: PeerB (implementation) + External (Composio team/admin)
**Status**: PENDING (M1 week 1, BLOCKING)
**Created**: 2025-11-13
**Target**: M1 day 1-3 (≤72h from M1 start)

## Objective

Resolve two credential blockers preventing automation paths (GitHub-seed + following-graph) required for M1 scale (2k-3k authors):

1. **GitHub OAuth**: Enable GITHUB_LIST_ORGANIZATION_MEMBERS + GITHUB_GET_A_USER for org member discovery
2. **Twitter v2 Enrollment**: Fix TWITTER_FOLLOWING_BY_USER_ID "client-not-enrolled" error for following-graph expansion

## Background

**M0 Evidence** (manual CSV approach validated):
- 2 consecutive auth blockers in 24h triggered M0 pivot to manual CSV (docs/por/POR.md Decision Log 2025-11-13 13:05)
- GitHub OAuth: Failed during T000002 initial automation attempt
- Twitter v2: Following probe (Foreman#000028) failed with "client-not-enrolled" (0/5 API calls succeeded)
- Impact: Bet 1 FALSIFIED for M0 - "80-90% authors discoverable via GitHub-seed + following-graph" invalidated
- Mitigation: Manual CSV proven across 4 milestones (48→66→121→151 authors, 100% validation maintained)

**M1 Requirements**:
- Scale target: 2k-3k authors (13-20× current scale)
- Manual CSV approach: Not sustainable at 2k+ scale (curation time, diversity limits)
- Automation paths: REQUIRED for M1 execution within ≤6 weeks timeline

## Blockers Detail

### Blocker 1: GitHub OAuth (org:read scope)

**Required APIs**:
- `GITHUB_LIST_ORGANIZATION_MEMBERS`: Fetch org members with twitter_username field
- `GITHUB_GET_A_USER`: Verify user profiles and extract twitter_username

**Current State**: RUBE MCP `github` toolkit lacks valid OAuth token with org:read scope

**Resolution Steps**:
1. **Verify Composio GitHub connection** (PeerB, 30min):
   - Check existing connections: `composio connections list --toolkit github`
   - Identify connection ID and current scopes
2. **Request org:read scope** (PeerB + Composio team, 2-4h):
   - If connection exists: Upgrade scopes via Composio dashboard or API
   - If no connection: Create new GitHub OAuth app with org:read + user:read scopes
   - Contact: Composio support team (support@composio.dev or dashboard support chat)
3. **Test org member discovery** (PeerB, 30min):
   - Retry: `GITHUB_LIST_ORGANIZATION_MEMBERS` with target orgs (openai, anthropic, google, meta)
   - Validate: Extract twitter_username fields from ≥3 orgs with ≥10 members each
   - Expected: ≥30 handles extracted

**Owner**: PeerB (orchestration) + External Composio integration team (scope approval)
**ETA**: M1 day 1-2 (~4-8h total, includes Composio support response time)
**Contacts**:
- Composio support: support@composio.dev
- RUBE MCP GitHub: https://github.com/ComposioHQ/composio

### Blocker 2: Twitter v2 Enrollment

**Required API**:
- `TWITTER_FOLLOWING_BY_USER_ID`: Fetch following list for network expansion (who a user follows)

**Current State**: Composio Twitter credentials lack v2 Project attachment, causing "client-not-enrolled" error

**Error Message**:
```
"client-not-enrolled" - App keys not attached to Project with v2 access
```

**Resolution Steps**:
1. **Identify Twitter App credentials** (PeerB, 15min):
   - Check Composio connections: `composio connections list --toolkit twitter`
   - Note: Connection ID, app keys (consumer key/secret visible in Composio dashboard)
2. **Attach credentials to v2 Project** (External admin, 1-2h):
   - Navigate to Twitter Developer Portal (developer.twitter.com)
   - Locate existing App OR create new App with v2 Project access
   - Attach app keys to v2-enabled Project (requires Elevated or higher access tier)
   - Note: Free tier may have v2 restrictions - verify TWITTER_FOLLOWING endpoint availability
3. **Update Composio connection** (PeerB + External admin, 30min):
   - If new app created: Re-authenticate Composio Twitter connection with new credentials
   - If existing app upgraded: Verify connection automatically picks up v2 access
4. **Retry following probe** (PeerB, 15min):
   - Re-run following slice-1 probe (tools/influx-harvest following, 5 seeds × 1 page)
   - Validate: ≥50 following records extracted after entry filters
   - Expected: 100% pass rate (5/5 API calls succeed)

**Owner**: External Composio/user account admin (Twitter Developer Portal access) + PeerB (Composio connection management)
**ETA**: M1 day 1-3 (dependent on Composio support response + Twitter Developer Portal access)
**Contacts**:
- Twitter Developer Portal: developer.twitter.com
- Composio support: support@composio.dev (for v2 Project guidance)

## Validation Probe

**Acceptance Criteria**:
1. **GitHub OAuth validated**:
   - `GITHUB_LIST_ORGANIZATION_MEMBERS` succeeds for ≥3 target orgs
   - Extracts ≥30 handles with twitter_username field
   - Handles pass entry filter ((verified+30k) OR 50k): ≥20 handles retained
2. **Twitter v2 validated**:
   - `TWITTER_FOLLOWING_BY_USER_ID` succeeds for ≥5 seed authors
   - Extracts ≥50 following records after entry filters (1 page per seed)
   - Error rate: 0% (5/5 API calls succeed)
3. **Following slice-1 probe PASSES**:
   - Command: `tools/influx-harvest following --seeds <5-seeds.jsonl> --pages 1 --out following.jsonl`
   - Output: .cccc/work/validation/following.jsonl with ≥50 records
   - Validation: 100% schema-compliant (tools/influx-validate)

**Probe Timeline**: M1 day 3 (after both blockers resolved)
**Execution Time**: ≤30min
**Acceptance**: All 3 criteria met → M1 automation paths UNBLOCKED

## Dependencies

- **Composio support response time**: 2-24h (varies, weekday vs weekend)
- **Twitter Developer Portal access**: User must have admin access to Twitter App or ability to create new App
- **GitHub org access**: Target orgs (openai, anthropic, google, etc.) must have public members OR user must have org member access
- **M1 start date**: Auth-unblock MUST complete within first 3 days of M1 to avoid timeline slip

## Risk & Mitigations

**R1**: Composio support delays >3 days → **Mitigation**: Escalate via GitHub issues + direct email; consider alternative RUBE MCP toolkit if available

**R2**: Twitter v2 access unavailable on free tier → **Mitigation**: Evaluate paid tier upgrade ROI (cost vs manual CSV curation labor) OR defer following-graph to M2, continue manual CSV + x-lists for M1

**R3**: GitHub org:read scope denied (privacy concerns) → **Mitigation**: Use public member lists only (GITHUB_GET_USER + search), lower coverage expectations from 80-90% to 40-50%

**R4**: Both blockers unresolved >3 days → **Fallback**: M1 continues manual CSV approach (proven at 150 scale), target 2k via bulk curation + x-lists (no following-graph), extend M1 timeline by +2 weeks

## Deliverables

1. **Auth status report** (M1 day 1): Composio connections reviewed, support tickets opened (if needed)
2. **GitHub OAuth validated** (M1 day 1-2): ≥30 handles extracted from ≥3 orgs
3. **Twitter v2 validated** (M1 day 2-3): Following probe succeeds (≥50 records, 5/5 API calls)
4. **Validation probe complete** (M1 day 3): Following slice-1 probe PASSES, evidence committed to .cccc/work/validation/
5. **SUBPOR updated** (M1 day 3): Status → COMPLETE, evidence logged, acceptance criteria met

## Estimated Duration

- **GitHub OAuth**: 4-8h (includes Composio support response)
- **Twitter v2 Enrollment**: 8-24h (includes Developer Portal access + potential tier upgrade evaluation)
- **Validation Probe**: 30min (after both blockers resolved)
- **Total**: 1-3 days from M1 start (ETA: M1 day 1-3)

## Success Criteria

- [ ] GitHub OAuth: org:read scope enabled, GITHUB_LIST_ORGANIZATION_MEMBERS operational
- [ ] Twitter v2: "client-not-enrolled" error resolved, TWITTER_FOLLOWING_BY_USER_ID operational
- [ ] Validation probe: Following slice-1 probe produces ≥50 records with 100% schema compliance
- [ ] M1 automation paths: UNBLOCKED for GitHub-seed + following-graph collection at 2k-3k scale

## References

- POR Risk Radar: docs/por/POR.md#R1a (API auth blockers)
- M0 Pivot Evidence: docs/por/POR.md Decision Log 2025-11-13 13:05
- Following Probe Failure: PeerB message 000040 (2025-11-13)
- D2 Pipeline Contract: docs/por/d2-pipeline-contract.md (Following Slice-1 acceptance criteria)
- Bet 1 FALSIFIED: docs/por/POR.md Bets & Assumptions (M0 finding)

---

## REV Log

- 2025-11-13 14:15 | Initial SUBPOR draft | Status: PENDING | Created per Foreman#000042 directive
