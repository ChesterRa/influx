<!-- Generated on 2025-11-23T12:51:18+00:00 by por_subpor.py 0.1.1 -->

# T000001 - Creator Economy Seed List Development - Owner: peerB - Stage: proposed - Timebox: 1d

- Goal/Scope (<=3 lines):
- Research and create curated seed list of 50-100 creator economy influencers with 50K+ followers
- Focus on YouTube/TikTok creators, newsletter writers, podcasters in tech/business niches
- Provide proper URL evidence for each handle to avoid @handle format violations

- Non-Goals (<=2 lines):
- No brand/media accounts or official company channels
- No recycled handles from existing processed seed lists

- Deliverable & Interface (path/format/user-visible change):
- lists/seeds/creator-economy-fresh.csv with columns: handle,category,source,note,evidence
- Ready for MCP processing with proper URL evidence from creation

- Acceptance (3-5 observable items):
[ ] 50-100 unique handles with verified 50K+ follower counts (or verified+30K)
[ ] All entries have proper URL evidence (tweet/github/profile links)
[ ] Zero brand/official accounts included
[ ] CSV format matches existing seed list structure
[ ] No duplicates with current dataset (282 authors)

- Probe (cheapest decisive): Research top 10 creator economy handles, verify follower counts, create sample CSV with proper evidence
- Kill Criteria (when to stop/pivot): If <30% of researched handles meet 50K threshold after 2 hours
- Implementation Approach (<=3 bullets):
  - Domain research: Identify top creators in tech/business niches via YouTube/TikTok/newsletter platforms
  - Verification: Use MCP to verify follower counts and account status before inclusion
  - Quality gates: Apply entry thresholds and evidence requirements from start

- Evidence (minimal refs): cmd:TWITTER_USER_LOOKUP_BY_USERNAME::OK; log:climate tech verification#leahstokes(99K),billmckibben(359K),KHayhoe(221K)
- Risks/Dependencies (1 line each): Creator platform API limitations; Follower count verification accuracy
- Next (single, decidable, <=30 minutes): Process verified climate handles (leahstokes, billmckibben, KHayhoe) via influx-harvest to reach 300 target

## REV (append-only)
- YYYY-MM-DD HH:MM | author | delta (short) | refs

## Aux (tactical, when used)
- Offloaded micro-task(s): <one-liners> | why | how to verify

- Maintenance note: update this sheet before major steps; keep REV concise.

<!-- Generated on {{generated_on}} by {{tool}} {{tool_version}} ; template_sha1=9ead40e3dc96f80aa7cddce3ac0062ac8329f48d -->
