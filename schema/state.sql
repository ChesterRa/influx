-- influx State Database Schema (SQLite)
-- Version: 1.0.0
-- Purpose: Persistent state for incremental updates, metrics history, and governance
-- Enables: trend analysis, anomaly detection, adaptive scoring (M1/M2)

-- Enable WAL mode for better concurrent read performance
-- Run after DB creation: PRAGMA journal_mode=WAL;

-- Main authors table (current state snapshot)
CREATE TABLE IF NOT EXISTS authors (
    id TEXT PRIMARY KEY NOT NULL,                -- Twitter author_id
    handle TEXT NOT NULL UNIQUE,                 -- Twitter username (lowercase for case-insensitive unique)
    name TEXT NOT NULL,
    verified TEXT NOT NULL CHECK(verified IN ('none', 'blue', 'org', 'legacy')),
    followers_count INTEGER NOT NULL CHECK(followers_count >= 0),
    lang_primary TEXT NOT NULL CHECK(length(lang_primary) = 2),
    topic_tags TEXT NOT NULL,                    -- JSON array as TEXT (e.g., '["ai","ml"]')

    -- 30-day metrics (current window)
    posts_original INTEGER CHECK(posts_original >= 0),
    median_likes INTEGER CHECK(median_likes >= 0),
    p90_likes INTEGER CHECK(p90_likes >= 0),
    median_replies INTEGER CHECK(median_replies >= 0),
    median_retweets INTEGER CHECK(median_retweets >= 0),

    -- Metadata
    score REAL CHECK(score >= 0 AND score <= 100),
    rank_global INTEGER CHECK(rank_global >= 1),
    last_active_at TEXT,                         -- ISO 8601
    last_refresh_at TEXT NOT NULL,               -- ISO 8601
    provenance_hash TEXT CHECK(length(provenance_hash) = 64),  -- SHA-256 hex

    -- Extension fields (JSON as TEXT)
    ext TEXT,                                    -- JSON object '{"key":"value"}'

    -- Governance
    banned INTEGER NOT NULL DEFAULT 0 CHECK(banned IN (0, 1)),
    ban_reason TEXT,

    -- Indexes for common queries
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_authors_handle ON authors(handle);
CREATE INDEX IF NOT EXISTS idx_authors_score ON authors(score DESC);
CREATE INDEX IF NOT EXISTS idx_authors_followers ON authors(followers_count DESC);
CREATE INDEX IF NOT EXISTS idx_authors_lang_primary ON authors(lang_primary);
CREATE INDEX IF NOT EXISTS idx_authors_last_active ON authors(last_active_at DESC);
CREATE INDEX IF NOT EXISTS idx_authors_banned ON authors(banned) WHERE banned = 0;

-- Historical metrics snapshots (for trend analysis, anomaly detection)
CREATE TABLE IF NOT EXISTS metrics_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    snapshot_at TEXT NOT NULL,                   -- ISO 8601 timestamp of snapshot

    -- Snapshot metrics (same as authors.metrics_30d)
    posts_original INTEGER,
    median_likes INTEGER,
    p90_likes INTEGER,
    median_replies INTEGER,
    median_retweets INTEGER,

    -- Follower count at snapshot time (for growth tracking)
    followers_count INTEGER,

    -- Computed deltas (optional, can compute on read)
    delta_followers INTEGER,                     -- vs previous snapshot
    delta_score REAL,                            -- vs previous snapshot

    UNIQUE(author_id, snapshot_at)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_author ON metrics_snapshots(author_id, snapshot_at DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_time ON metrics_snapshots(snapshot_at DESC);

-- Provenance sources (normalized from JSON sources array)
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    method TEXT NOT NULL CHECK(method IN ('github_seed', 'following_expansion', 'x_list', 'manual', 'keyword_search')),
    fetched_at TEXT NOT NULL,                    -- ISO 8601
    evidence TEXT NOT NULL,                      -- Freeform description
    seed_handle TEXT,                            -- If method=following_expansion, the seed's handle

    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sources_author ON sources(author_id);
CREATE INDEX IF NOT EXISTS idx_sources_method ON sources(method);
CREATE INDEX IF NOT EXISTS idx_sources_seed ON sources(seed_handle) WHERE seed_handle IS NOT NULL;

-- Banned authors (governance tracking with audit trail)
-- Note: banned flag is also in authors table for query efficiency
CREATE TABLE IF NOT EXISTS ban_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK(action IN ('ban', 'unban')),
    reason TEXT NOT NULL,
    actioned_by TEXT NOT NULL,                   -- Who made the decision (e.g., 'manual', 'heuristic:brand', 'user_request')
    actioned_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ban_history_author ON ban_history(author_id, actioned_at DESC);

-- Following graph cache (for network analysis, clustering)
-- Stores "who follows whom" relationships discovered during following_expansion
CREATE TABLE IF NOT EXISTS following_graph (
    follower_id TEXT NOT NULL,                   -- Author in our DB who follows someone
    following_id TEXT NOT NULL,                  -- Author being followed (may or may not be in DB)
    discovered_at TEXT NOT NULL,                 -- ISO 8601

    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_following_follower ON following_graph(follower_id);
CREATE INDEX IF NOT EXISTS idx_following_following ON following_graph(following_id);

-- Metadata table (for schema versioning, last global operations)
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Insert schema version
INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', '1.0.0');
INSERT OR REPLACE INTO metadata (key, value) VALUES ('last_full_recalc', datetime('now'));

-- Trigger to update authors.updated_at on any change
CREATE TRIGGER IF NOT EXISTS update_authors_timestamp
AFTER UPDATE ON authors
FOR EACH ROW
BEGIN
    UPDATE authors SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- View for active (non-banned) authors with rank
CREATE VIEW IF NOT EXISTS active_authors AS
SELECT
    id, handle, name, verified, followers_count, lang_primary, topic_tags,
    posts_original, median_likes, p90_likes, median_replies, median_retweets,
    score, rank_global, last_active_at, last_refresh_at, provenance_hash
FROM authors
WHERE banned = 0
ORDER BY score DESC, followers_count DESC, handle ASC;

-- View for recent activity (last 24h updates)
CREATE VIEW IF NOT EXISTS recent_updates AS
SELECT
    id, handle, name, score, rank_global, last_refresh_at
FROM authors
WHERE datetime(last_refresh_at) >= datetime('now', '-1 day')
ORDER BY last_refresh_at DESC;

-- Example queries for M1/M2 features:

-- Anomaly detection: sudden follower spike (>50% increase in 7 days)
-- SELECT a.handle, ms1.followers_count as current, ms2.followers_count as week_ago,
--        (ms1.followers_count - ms2.followers_count) * 100.0 / ms2.followers_count as growth_pct
-- FROM authors a
-- JOIN metrics_snapshots ms1 ON a.id = ms1.author_id AND ms1.snapshot_at = (SELECT MAX(snapshot_at) FROM metrics_snapshots WHERE author_id = a.id)
-- JOIN metrics_snapshots ms2 ON a.id = ms2.author_id AND ms2.snapshot_at = (SELECT MAX(snapshot_at) FROM metrics_snapshots WHERE author_id = a.id AND snapshot_at <= datetime('now', '-7 days'))
-- WHERE growth_pct > 50;

-- Network clustering: find authors who share many followings (collaborative filtering)
-- SELECT f1.follower_id, f2.follower_id, COUNT(*) as shared_followings
-- FROM following_graph f1
-- JOIN following_graph f2 ON f1.following_id = f2.following_id AND f1.follower_id < f2.follower_id
-- GROUP BY f1.follower_id, f2.follower_id
-- HAVING shared_followings >= 10
-- ORDER BY shared_followings DESC;

-- Trend analysis: score delta over last 30 days
-- SELECT author_id,
--        AVG(delta_score) as avg_score_change,
--        COUNT(*) as snapshots
-- FROM metrics_snapshots
-- WHERE snapshot_at >= datetime('now', '-30 days')
-- GROUP BY author_id
-- HAVING AVG(delta_score) < -5  -- declining authors
-- ORDER BY avg_score_change ASC;
