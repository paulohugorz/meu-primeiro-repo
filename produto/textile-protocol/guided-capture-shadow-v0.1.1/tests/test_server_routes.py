import json
import sys
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from server import Handler
from db import init_db
from http.server import ThreadingHTTPServer


class EncodedRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        Handler.db_path = str(root / "test.db")
        Handler.artifacts_root = str(root / "artifacts")
        init_db(Handler.db_path)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(
            self.base + path, data=data,
            headers={"Content-Type": "application/json"},
            method="POST" if data is not None else "GET"
        )
        with urllib.request.urlopen(req) as response:
            return json.load(response)

    def test_encoded_session_id_resolves(self):
        session = self.request("/api/sessions", {
            "sample_ref": "OPS-SYN-001", "operator_id": "operator:http-test"
        })
        encoded = urllib.parse.quote(session["session_id"], safe="")
        fetched = self.request(f"/api/sessions/{encoded}")
        self.assertEqual(fetched["session_id"], session["session_id"])
