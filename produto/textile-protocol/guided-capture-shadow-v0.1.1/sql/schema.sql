PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sample_id_mappings (
    mapping_id TEXT PRIMARY KEY,
    ops_id TEXT NOT NULL UNIQUE,
    service_sample_id TEXT NOT NULL UNIQUE,
    textile_sample_node_id TEXT NOT NULL UNIQUE,
    record_kind TEXT NOT NULL CHECK(record_kind IN ('operations_candidate','synthetic_fixture')),
    operations_status TEXT NOT NULL,
    physical_sample_received INTEGER NOT NULL CHECK(physical_sample_received IN (0,1)),
    capture_allowed INTEGER NOT NULL CHECK(capture_allowed IN (0,1)),
    source_package TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS capture_sessions (
    session_id TEXT PRIMARY KEY,
    mapping_id TEXT NOT NULL REFERENCES sample_id_mappings(mapping_id),
    ops_id TEXT NOT NULL,
    service_sample_id TEXT NOT NULL,
    textile_sample_node_id TEXT NOT NULL,
    protocol_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN (
        'draft','in_progress','quality_review','complete','superseded','cancelled'
    )),
    operator_id TEXT NOT NULL,
    device_id TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    ready_for_baseline INTEGER NOT NULL DEFAULT 0 CHECK(ready_for_baseline IN (0,1)),
    supersedes_session_id TEXT REFERENCES capture_sessions(session_id),
    superseded_by_session_id TEXT REFERENCES capture_sessions(session_id),
    supersession_reason TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_supersession
ON capture_sessions(supersedes_session_id)
WHERE supersedes_session_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS capture_items (
    item_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES capture_sessions(session_id) ON DELETE CASCADE,
    shot_type TEXT NOT NULL,
    sequence_no INTEGER NOT NULL,
    artifact_path TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL,
    claimed_mime_type TEXT NOT NULL,
    actual_mime_type TEXT NOT NULL,
    image_format TEXT NOT NULL,
    width_px INTEGER NOT NULL CHECK(width_px > 0),
    height_px INTEGER NOT NULL CHECK(height_px > 0),
    bytes_size INTEGER NOT NULL CHECK(bytes_size > 0),
    captured_at TEXT NOT NULL,
    focus_ok INTEGER NOT NULL CHECK(focus_ok IN (0,1)),
    lighting_ok INTEGER NOT NULL CHECK(lighting_ok IN (0,1)),
    sample_fills_frame INTEGER NOT NULL CHECK(sample_fills_frame IN (0,1)),
    no_label_leak INTEGER NOT NULL CHECK(no_label_leak IN (0,1)),
    quality_confirmed_by_actor_id TEXT NOT NULL,
    quality_confirmed_at TEXT NOT NULL,
    accepted INTEGER NOT NULL CHECK(accepted IN (0,1)),
    rejection_reasons_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE(session_id, sequence_no)
);

CREATE INDEX IF NOT EXISTS idx_capture_items_session
ON capture_items(session_id);

CREATE INDEX IF NOT EXISTS idx_capture_items_shot
ON capture_items(session_id, shot_type, accepted);

CREATE TABLE IF NOT EXISTS evidence_records (
    evidence_id TEXT PRIMARY KEY,
    mapping_id TEXT NOT NULL REFERENCES sample_id_mappings(mapping_id),
    ops_id TEXT NOT NULL,
    service_sample_id TEXT NOT NULL,
    textile_sample_node_id TEXT NOT NULL,
    capture_session_id TEXT NOT NULL REFERENCES capture_sessions(session_id),
    capture_item_id TEXT NOT NULL UNIQUE REFERENCES capture_items(item_id),
    evidence_type TEXT NOT NULL CHECK(evidence_type='photograph'),
    artifact_path TEXT NOT NULL,
    artifact_hash_sha256 TEXT NOT NULL,
    artifact_integrity TEXT NOT NULL CHECK(artifact_integrity='sha256_recorded'),
    source_authenticity TEXT NOT NULL CHECK(source_authenticity='unreviewed'),
    evidentiary_relevance TEXT NOT NULL CHECK(evidentiary_relevance='unreviewed'),
    review_status TEXT NOT NULL CHECK(review_status IN (
        'captured_unreviewed_shadow','superseded_capture'
    )),
    record_kind TEXT NOT NULL CHECK(record_kind IN ('operations_candidate','synthetic_fixture')),
    created_by_actor_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    supersedes_evidence_id TEXT REFERENCES evidence_records(evidence_id),
    superseded_by_evidence_id TEXT REFERENCES evidence_records(evidence_id)
);

CREATE TABLE IF NOT EXISTS recognition_runs (
    recognition_run_id TEXT PRIMARY KEY,
    capture_session_id TEXT NOT NULL REFERENCES capture_sessions(session_id),
    mode TEXT NOT NULL CHECK(mode='shadow'),
    status TEXT NOT NULL CHECK(status IN ('running','completed','failed')),
    stage TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    result_json TEXT,
    error TEXT,
    schema_version TEXT NOT NULL,
    official_mutation_applied INTEGER NOT NULL DEFAULT 0 CHECK(official_mutation_applied=0),
    publication_decision_created INTEGER NOT NULL DEFAULT 0 CHECK(publication_decision_created=0)
);

CREATE TABLE IF NOT EXISTS official_decision_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    source_decision_id TEXT NOT NULL,
    decision_hash TEXT NOT NULL,
    decision_json TEXT NOT NULL,
    benchmark_projection_hash TEXT NOT NULL,
    benchmark_projection_json TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    UNIQUE(sample_id, source_decision_id, decision_hash)
);

CREATE TABLE IF NOT EXISTS verification_tasks (
    task_id TEXT PRIMARY KEY,
    task_key TEXT NOT NULL UNIQUE,
    sample_id TEXT NOT NULL,
    source_decision_id TEXT NOT NULL,
    source_ruleset_version TEXT NOT NULL,
    source_benchmark_version_id TEXT NOT NULL,
    source_snapshot_id TEXT NOT NULL REFERENCES official_decision_snapshots(snapshot_id),
    task_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open','assigned','resolved','cancelled')),
    priority TEXT NOT NULL CHECK(priority IN ('high','medium','low')),
    mode TEXT NOT NULL DEFAULT 'shadow' CHECK(mode = 'shadow'),
    trigger_reason TEXT NOT NULL,
    requested_evidence_json TEXT NOT NULL,
    assigned_actor_id TEXT,
    resolution_json TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    affects_official_decision INTEGER NOT NULL DEFAULT 0 CHECK(affects_official_decision = 0),
    user_notification_sent INTEGER NOT NULL DEFAULT 0 CHECK(user_notification_sent = 0)
);

CREATE INDEX IF NOT EXISTS idx_verification_tasks_status
ON verification_tasks(status, priority);

CREATE INDEX IF NOT EXISTS idx_verification_tasks_sample
ON verification_tasks(sample_id);

CREATE TABLE IF NOT EXISTS task_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES verification_tasks(task_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shadow_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES verification_tasks(task_id) ON DELETE CASCADE,
    compared_to_projection_hash TEXT NOT NULL,
    proposed_projection_json TEXT NOT NULL,
    proposed_projection_hash TEXT NOT NULL,
    would_change INTEGER NOT NULL CHECK(would_change IN (0,1)),
    comparison_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS trg_official_snapshot_no_update
BEFORE UPDATE ON official_decision_snapshots
BEGIN
    SELECT RAISE(ABORT, 'official_decision_snapshot_is_immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_official_snapshot_no_delete
BEFORE DELETE ON official_decision_snapshots
BEGIN
    SELECT RAISE(ABORT, 'official_decision_snapshot_is_immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_task_events_no_update
BEFORE UPDATE ON task_events
BEGIN
    SELECT RAISE(ABORT, 'task_events_are_append_only');
END;

CREATE TRIGGER IF NOT EXISTS trg_task_events_no_delete
BEFORE DELETE ON task_events
BEGIN
    SELECT RAISE(ABORT, 'task_events_are_append_only');
END;
