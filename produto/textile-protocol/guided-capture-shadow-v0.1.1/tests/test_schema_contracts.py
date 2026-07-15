import json
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from db import init_db
from capture_service import start_session
from id_service import resolve_mapping

SCHEMAS = [
    "capture_session.schema.json",
    "capture_item.schema.json",
    "sample_id_mapping.schema.json",
    "evidence_record.schema.json",
    "verification_task.schema.json",
    "shadow_resolution.schema.json"
]

class SchemaContractTests(unittest.TestCase):
    def test_all_schemas_are_valid_draft_2020_12(self):
        for name in SCHEMAS:
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)

    def test_mapping_object_validates(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "test.db"
            init_db(db)
            mapping = resolve_mapping(db, "OPS-TX-001")
            obj = {
                key: mapping[key] for key in [
                    "mapping_id", "ops_id", "service_sample_id",
                    "textile_sample_node_id", "record_kind",
                    "operations_status", "physical_sample_received",
                    "capture_allowed", "source_package", "notes"
                ]
            }
            schema = json.loads(
                (ROOT / "schemas" / "sample_id_mapping.schema.json").read_text(encoding="utf-8")
            )
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(obj)

    def test_session_object_validates(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "test.db"
            init_db(db)
            session = start_session(db, "OPS-SYN-001", "operator:test")
            obj = {
                key: session.get(key) for key in [
                    "session_id", "mapping_id", "ops_id", "service_sample_id",
                    "textile_sample_node_id", "protocol_version", "status",
                    "operator_id", "device_id", "created_at", "completed_at",
                    "ready_for_baseline", "supersedes_session_id",
                    "superseded_by_session_id", "supersession_reason",
                    "metadata", "items", "completion"
                ]
            }
            schema = json.loads(
                (ROOT / "schemas" / "capture_session.schema.json").read_text(encoding="utf-8")
            )
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(obj)
