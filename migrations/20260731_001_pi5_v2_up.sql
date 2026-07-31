-- PI5 v2 additive migration. PostgreSQL. No legacy row is rewritten.
CREATE TABLE IF NOT EXISTS methodology_versions (
  id TEXT PRIMARY KEY, version TEXT NOT NULL, status TEXT NOT NULL,
  definition JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(id, version)
);
CREATE TABLE IF NOT EXISTS impact_indicator_definitions_v2 (
  id TEXT PRIMARY KEY, version TEXT NOT NULL, dimension TEXT NOT NULL, unit TEXT NOT NULL,
  direction TEXT NOT NULL, scope TEXT NOT NULL, formula JSONB, thresholds JSONB,
  minimum_coverage NUMERIC, methodology_id TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS factor_versions (
  id TEXT PRIMARY KEY, factor_code TEXT NOT NULL, version TEXT NOT NULL, unit TEXT NOT NULL,
  value NUMERIC, source TEXT NOT NULL, evidence_id TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS evidence_records_v2 (
  id TEXT PRIMARY KEY, kind TEXT NOT NULL, issuer TEXT NOT NULL, subject TEXT NOT NULL,
  content_hash TEXT NOT NULL, location TEXT NOT NULL, rights TEXT NOT NULL,
  verification_status TEXT NOT NULL, confidentiality TEXT NOT NULL,
  expires_at TIMESTAMPTZ, public_url TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS impact_observations_v2 (
  id TEXT PRIMARY KEY, indicator_id TEXT NOT NULL, piece_id TEXT, lot_id TEXT NOT NULL,
  supplier_id TEXT NOT NULL, facility_id TEXT NOT NULL, production_stage TEXT NOT NULL,
  period_start TIMESTAMPTZ NOT NULL, period_end TIMESTAMPTZ NOT NULL,
  value NUMERIC, unit TEXT, origin TEXT NOT NULL, method_id TEXT NOT NULL,
  factor_version_id TEXT REFERENCES factor_versions(id), uncertainty JSONB,
  evidence_ids JSONB NOT NULL DEFAULT '[]', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS evidence_assertions_v2 (
  id TEXT PRIMARY KEY, field_name TEXT NOT NULL, value JSONB NOT NULL, mode TEXT NOT NULL,
  confidence NUMERIC, evidence_id TEXT NOT NULL REFERENCES evidence_records_v2(id),
  actor_id TEXT NOT NULL, review_status TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS claims_v2 (
  id TEXT PRIMARY KEY, claim_type TEXT NOT NULL, subject TEXT NOT NULL, value JSONB,
  mode TEXT NOT NULL, strength TEXT NOT NULL, evidence_ids JSONB NOT NULL DEFAULT '[]',
  allowed_status TEXT NOT NULL, reasons JSONB NOT NULL DEFAULT '[]',
  submitted_by TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS review_tasks_v2 (
  id TEXT PRIMARY KEY, task_type TEXT NOT NULL, target_type TEXT NOT NULL, target_id TEXT NOT NULL,
  status TEXT NOT NULL, submitted_by TEXT NOT NULL, reviewer_id TEXT,
  due_at TIMESTAMPTZ, justification TEXT, evidence_ids JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), decided_at TIMESTAMPTZ,
  CHECK (reviewer_id IS NULL OR reviewer_id <> submitted_by)
);
CREATE TABLE IF NOT EXISTS assessments_v2 (
  id TEXT PRIMARY KEY, assessment_type TEXT NOT NULL, target_id TEXT NOT NULL,
  method_version TEXT NOT NULL, result JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS publication_decisions_v2 (
  id TEXT PRIMARY KEY, target TEXT NOT NULL, policy_version TEXT NOT NULL,
  allowed_fields JSONB NOT NULL, blocked_fields JSONB NOT NULL, reasons JSONB NOT NULL,
  reviewer_id TEXT NOT NULL, submitted_by TEXT NOT NULL, manifest_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), CHECK (reviewer_id <> submitted_by)
);
