-- State Database Schema v1.0.0
-- SQLite database for influx persistent state
-- Purpose: Enable incremental updates, history tracking, and efficient queries
-- Location: state/influx.db

-- Database configuration (set at connection time)
-- PRAGMA journal_mode=WAL;
-- PRAGMA foreign_keys=ON;
-- PRAGMA synchronous=NORMAL;

-- =============================================================================
-- Authors Table (core identity and current state)
-- =============================================================================
CREATE TABLE IF NOT EXISTS authors (
    -- Primary keys
    id TEXT PRIMARY KEY,                    -- Twitter author_id (immutable)
    handle TEXT NOT NULL UNIQUE COLLATE NOCASE,  -- Twitter username (case-insensitive unique)

    -- Core identity
    name TEXT NOT NULL,                     -- Display name
    verified TEXT NOT NULL CHECK(verified IN ('none', 'blue', 'org', 'legacy')),
    followers_count INTEGER NOT NULL CHECK(followers_count >= 0),

    -- Metadata
    lang_primary TEXT NOT NULL CHECK(length(lang_primary) = 2),  -- ISO 639-1
    topic_tags TEXT NOT NULL DEFAULT '[]',  -- JSON array of topic strings

    -- Current metrics (30-day window, updated on refresh)
    posts_original INTEGER CHECK(posts_original >= 0),
    median_likes INTEGER CHECK(median_likes >= 0),
    p90_likes INTEGER CHECK(p90_likes >= 0),
    median_replies INTEGER CHECK(median_replies >= 0),
    median_retweets INTEGER CHECK(median_retweets >= 0),

    -- Scoring and ranking (updated on refresh)
    score REAL CHECK(score >= 0 AND score <= 100),
    rank_global INTEGER CHECK(rank_global >= 1),

    -- Timestamps
    last_active_at TEXT,                    -- ISO 8601 timestamp of most recent tweet (NULL if unknown)
    last_refresh_at TEXT NOT NULL DEFAULT (datetime('now')),  -- ISO 8601 timestamp of last metrics update
    first_seen_at TEXT NOT NULL DEFAULT (datetime('now')),    -- ISO 8601 timestamp when author was first added

    -- Provenance
    provenance_hash TEXT CHECK(length(provenance_hash) = 64),  -- SHA-256 hex

    -- Flags
    banned INTEGER NOT NULL DEFAULT 0,      -- Boolean: 0=active, 1=banned
    ban_reason TEXT,                         -- Human-readable reason if banned=1

    -- Audit
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_authors_handle ON authors(handle COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_authors_verified ON authors(verified);
CREATE INDEX IF NOT EXISTS idx_authors_followers ON authors(followers_count DESC);
CREATE INDEX IF NOT EXISTS idx_authors_score ON authors(score DESC);
CREATE INDEX IF NOT EXISTS idx_authors_rank ON authors(rank_global);
CREATE INDEX IF NOT EXISTS idx_authors_last_active ON authors(last_active_at DESC);
CREATE INDEX IF NOT EXISTS idx_authors_lang ON authors(lang_primary);
CREATE INDEX IF NOT EXISTS idx_authors_banned ON authors(banned) WHERE banned = 1;

-- =============================================================================
-- Sources Table (provenance tracking)
-- =============================================================================
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL,                -- FK to authors.id
    method TEXT NOT NULL,                   -- Discovery method: github_seed, following_expansion, x_list, manual, keyword_search
    fetched_at TEXT NOT NULL,               -- ISO 8601 timestamp
    evidence TEXT,                          -- Freeform evidence string
    seed_handle TEXT,                       -- If method=following_expansion, the seed author's handle

    -- Audit
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sources_author ON sources(author_id);
CREATE INDEX IF NOT EXISTS idx_sources_method ON sources(method);
CREATE INDEX IF NOT EXISTS idx_sources_fetched ON sources(fetched_at DESC);

-- =============================================================================
-- Metrics History (time-series tracking for trend analysis)
-- =============================================================================
CREATE TABLE IF NOT EXISTS metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL,                -- FK to authors.id
    snapshot_at TEXT NOT NULL,              -- ISO 8601 timestamp

    -- Snapshot values
    followers_count INTEGER NOT NULL,
    posts_original INTEGER,
    median_likes INTEGER,
    p90_likes INTEGER,
    median_replies INTEGER,
    median_retweets INTEGER,
    score REAL,
    rank_global INTEGER,

    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_metrics_author ON metrics_history(author_id, snapshot_at DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_snapshot ON metrics_history(snapshot_at DESC);

-- =============================================================================
-- Following Graph (network expansion tracking)
-- =============================================================================
CREATE TABLE IF NOT EXISTS following (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seed_author_id TEXT NOT NULL,           -- Author who follows
    target_author_id TEXT NOT NULL,         -- Author being followed
    discovered_at TEXT NOT NULL,            -- ISO 8601 timestamp when relationship was discovered

    -- Deduplication
    UNIQUE(seed_author_id, target_author_id),

    -- Only FK on seed_author_id (allows storing edges to not-yet-materialized targets)
    FOREIGN KEY (seed_author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_following_seed ON following(seed_author_id);
CREATE INDEX IF NOT EXISTS idx_following_target ON following(target_author_id);

-- =============================================================================
-- Collection Runs (batch job tracking)
-- =============================================================================
CREATE TABLE IF NOT EXISTS collection_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,               -- ISO 8601 timestamp
    completed_at TEXT,                      -- ISO 8601 timestamp (NULL if in progress)
    method TEXT NOT NULL,                   -- Collection method: github_seed, following_expansion, full_refresh
    status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'failed')),

    -- Statistics
    authors_discovered INTEGER DEFAULT 0,
    authors_updated INTEGER DEFAULT 0,
    api_calls_made INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,

    -- Parameters (JSON)
    params TEXT,                            -- JSON object with run parameters

    -- Results
    notes TEXT                              -- Freeform notes or error messages
);

CREATE INDEX IF NOT EXISTS idx_runs_started ON collection_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status ON collection_runs(status);

-- =============================================================================
-- Banned Authors (permanent record even if removed from authors table)
-- =============================================================================
CREATE TABLE IF NOT EXISTS banned_authors (
    id TEXT PRIMARY KEY,                    -- Twitter author_id
    handle TEXT NOT NULL,                   -- Handle at time of ban
    name TEXT NOT NULL,                     -- Name at time of ban
    banned_at TEXT NOT NULL,                -- ISO 8601 timestamp
    reason TEXT NOT NULL,                   -- Human-readable reason
    requested_by TEXT,                      -- Source of ban request (e.g., "user_email@example.com", "manual_review")

    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_banned_at ON banned_authors(banned_at DESC);

-- =============================================================================
-- Views for Common Queries
-- =============================================================================

-- Active authors (not banned, sorted by score)
CREATE VIEW IF NOT EXISTS v_active_authors AS
SELECT
    id, handle, name, verified, followers_count,
    lang_primary, topic_tags,
    posts_original, median_likes, p90_likes, median_replies, median_retweets,
    score, rank_global,
    last_active_at, last_refresh_at, first_seen_at,
    provenance_hash
FROM authors
WHERE banned = 0
ORDER BY score DESC, followers_count DESC, handle;

-- Top authors by topic (requires JSON parsing, simplified view)
CREATE VIEW IF NOT EXISTS v_top_authors AS
SELECT
    id, handle, name, verified, followers_count,
    lang_primary, topic_tags,
    score, rank_global,
    last_active_at
FROM authors
WHERE banned = 0
  AND score IS NOT NULL
ORDER BY score DESC
LIMIT 1000;

-- Recent activity (authors active in last 7 days)
CREATE VIEW IF NOT EXISTS v_recent_active AS
SELECT
    id, handle, name, verified, followers_count,
    lang_primary, score, rank_global,
    last_active_at
FROM authors
WHERE banned = 0
  AND julianday('now') - julianday(last_active_at) <= 7
ORDER BY last_active_at DESC;

-- Authors needing refresh (stale metrics, >24 hours since last refresh)
CREATE VIEW IF NOT EXISTS v_stale_authors AS
SELECT
    id, handle, name, followers_count,
    last_active_at, last_refresh_at,
    CAST((julianday('now') - julianday(last_refresh_at)) * 24 AS INTEGER) AS hours_since_refresh
FROM authors
WHERE banned = 0
  AND julianday('now') - julianday(last_refresh_at) > 1
ORDER BY last_refresh_at ASC
LIMIT 500;

-- Network overlap (authors followed by multiple seeds, high-signal candidates)
CREATE VIEW IF NOT EXISTS v_network_overlap AS
SELECT
    target_author_id,
    COUNT(DISTINCT seed_author_id) AS follower_count,
    GROUP_CONCAT(DISTINCT seed_author_id) AS seed_ids
FROM following
GROUP BY target_author_id
HAVING follower_count >= 2
ORDER BY follower_count DESC;

-- =============================================================================
-- Triggers for Audit Trail
-- =============================================================================

-- Update authors.updated_at on any change
CREATE TRIGGER IF NOT EXISTS trg_authors_updated
AFTER UPDATE ON authors
FOR EACH ROW
BEGIN
    UPDATE authors SET updated_at = datetime('now')
    WHERE id = NEW.id;
END;

-- Auto-sync banned authors to banned_authors table
CREATE TRIGGER IF NOT EXISTS trg_authors_banned
AFTER UPDATE OF banned ON authors
FOR EACH ROW
WHEN NEW.banned = 1 AND OLD.banned = 0
BEGIN
    INSERT OR REPLACE INTO banned_authors (id, handle, name, banned_at, reason)
    VALUES (NEW.id, NEW.handle, NEW.name, datetime('now'), NEW.ban_reason);
END;

-- =============================================================================
-- Initial Data / Metadata
-- =============================================================================

-- Schema version table
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    notes TEXT
);

INSERT OR IGNORE INTO schema_version (version, notes)
VALUES ('1.0.0', 'Initial schema for influx state DB');
