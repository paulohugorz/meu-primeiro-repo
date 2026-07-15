from __future__ import annotations
import csv
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
MAPPING_SEED_PATH = ROOT / "data" / "integration" / "sample_id_mappings.csv"

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()

def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, factory=ClosingConnection, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn

def seed_mappings(conn: sqlite3.Connection) -> None:
    if not MAPPING_SEED_PATH.exists():
        return
    with MAPPING_SEED_PATH.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    now = utcnow()
    for row in rows:
        conn.execute(
            """INSERT OR IGNORE INTO sample_id_mappings(
                mapping_id,ops_id,service_sample_id,textile_sample_node_id,
                record_kind,operations_status,physical_sample_received,
                capture_allowed,source_package,notes,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                row["mapping_id"], row["ops_id"], row["service_sample_id"],
                row["textile_sample_node_id"], row["record_kind"],
                row["operations_status"],
                1 if row["physical_sample_received"].lower() == "true" else 0,
                1 if row["capture_allowed"].lower() == "true" else 0,
                row["source_package"], row["notes"], now
            )
        )

def init_db(db_path: str | Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        seed_mappings(conn)
        conn.execute(
            "INSERT OR REPLACE INTO system_state(key,value) VALUES(?,?)",
            ("shadow_mode_policy_version", "0.1.1")
        )
        conn.execute(
            "INSERT OR REPLACE INTO system_state(key,value) VALUES(?,?)",
            ("capture_protocol_version", "0.1.1")
        )
        conn.execute(
            "INSERT OR REPLACE INTO system_state(key,value) VALUES(?,?)",
            ("operations_state", "prepared_not_sent")
        )

@contextmanager
def transaction(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
