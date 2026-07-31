-- Rollback removes only additive v2 tables. Legacy tables remain untouched.
DROP TABLE IF EXISTS publication_decisions_v2;
DROP TABLE IF EXISTS assessments_v2;
DROP TABLE IF EXISTS review_tasks_v2;
DROP TABLE IF EXISTS claims_v2;
DROP TABLE IF EXISTS evidence_assertions_v2;
DROP TABLE IF EXISTS impact_observations_v2;
DROP TABLE IF EXISTS evidence_records_v2;
DROP TABLE IF EXISTS factor_versions;
DROP TABLE IF EXISTS impact_indicator_definitions_v2;
DROP TABLE IF EXISTS methodology_versions;
