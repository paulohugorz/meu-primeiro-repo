#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from db import init_db
from id_service import resolve_mapping
from capture_service import (
    add_capture_base64, finalize_session, get_session, load_protocol, start_session
)
from task_service import (
    compare_shadow_decision, get_task, list_tasks, resolve_task, shadow_report
)

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"
MAX_JSON_BYTES = 36 * 1024 * 1024

class Handler(SimpleHTTPRequestHandler):
    db_path: str
    artifacts_root: str

    def translate_path(self, path: str) -> str:
        local = urlparse(path).path.lstrip("/") or "index.html"
        candidate = (WEB_ROOT / local).resolve()
        if WEB_ROOT.resolve() not in candidate.parents and candidate != WEB_ROOT.resolve():
            return str(WEB_ROOT / "index.html")
        return str(candidate)

    def _json(self, status: int, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_JSON_BYTES:
            raise ValueError("invalid request size")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/health":
                return self._json(200, {
                    "status": "ok", "mode": "shadow",
                    "operations_state": "prepared_not_sent",
                    "physical_samples_received": 0,
                    "field_test_enabled": False,
                    "promotion_enabled": False
                })
            if path == "/api/protocol":
                return self._json(200, load_protocol())
            if path == "/api/tasks":
                status = parse_qs(parsed.query).get("status", [None])[0]
                return self._json(200, list_tasks(self.db_path, status))
            if path == "/api/shadow-report":
                return self._json(200, shadow_report(self.db_path))
            if path == "/api/resolve-id":
                ref = parse_qs(parsed.query).get("sample_ref", [None])[0]
                return self._json(200, resolve_mapping(self.db_path, ref))
            m = re.fullmatch(r"/api/sessions/([^/]+)", path)
            if m:
                return self._json(200, get_session(self.db_path, m.group(1)))
            m = re.fullmatch(r"/api/tasks/([^/]+)", path)
            if m:
                return self._json(200, get_task(self.db_path, m.group(1)))
            return super().do_GET()
        except KeyError as exc:
            return self._json(404, {"error": str(exc)})
        except Exception as exc:
            return self._json(400, {"error": str(exc)})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/sessions":
                return self._json(201, start_session(
                    self.db_path, payload["sample_ref"], payload["operator_id"],
                    payload.get("device_id"), payload.get("metadata"),
                    payload.get("supersedes_session_id"),
                    payload.get("supersession_reason")
                ))
            m = re.fullmatch(r"/api/sessions/([^/]+)/captures", path)
            if m:
                return self._json(201, add_capture_base64(
                    self.db_path, self.artifacts_root, m.group(1), payload
                ))
            m = re.fullmatch(r"/api/sessions/([^/]+)/finalize", path)
            if m:
                return self._json(200, finalize_session(self.db_path, m.group(1)))
            m = re.fullmatch(r"/api/tasks/([^/]+)/resolve", path)
            if m:
                return self._json(200, resolve_task(
                    self.db_path, m.group(1), payload["outcome"],
                    payload["performed_by_actor_id"], payload.get("notes", ""),
                    payload.get("evidence_ids"), payload.get("proposed_decision")
                ))
            m = re.fullmatch(r"/api/tasks/([^/]+)/compare", path)
            if m:
                return self._json(200, compare_shadow_decision(
                    self.db_path, m.group(1), payload["proposed_decision"]
                ))
            return self._json(404, {"error": "endpoint not found"})
        except KeyError as exc:
            return self._json(404, {"error": str(exc)})
        except Exception as exc:
            return self._json(400, {"error": str(exc)})

def run(db_path: str, artifacts_root: str, host: str = "127.0.0.1", port: int = 8765):
    init_db(db_path)
    Handler.db_path = db_path
    Handler.artifacts_root = artifacts_root
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"PHYLLOS guided capture: http://{host}:{port}")
    print("Shadow mode active. Real 70-candidate capture remains blocked.")
    server.serve_forever()

if __name__ == "__main__":
    run(
        str(ROOT / "runtime" / "phyllos_shadow.db"),
        str(ROOT / "runtime" / "artifacts")
    )
