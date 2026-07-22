from __future__ import annotations

import base64

from fastapi.testclient import TestClient

from app.main import app


def _authorization(username: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_gate_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PILOT_ACCESS_REQUIRED", raising=False)
    with TestClient(app) as client:
        response = client.get("/pecas")
    assert response.status_code == 200


def test_private_route_requires_authentication(monkeypatch):
    monkeypatch.setenv("PILOT_ACCESS_REQUIRED", "true")
    monkeypatch.setenv("PILOT_ACCESS_USER", "pilot")
    monkeypatch.setenv("PILOT_ACCESS_PASSWORD", "secret")
    with TestClient(app) as client:
        response = client.get("/pecas")
    assert response.status_code == 401


def test_valid_credentials_unlock_private_route(monkeypatch):
    monkeypatch.setenv("PILOT_ACCESS_REQUIRED", "true")
    monkeypatch.setenv("PILOT_ACCESS_USER", "pilot")
    monkeypatch.setenv("PILOT_ACCESS_PASSWORD", "secret")
    with TestClient(app) as client:
        response = client.get("/pecas", headers=_authorization("pilot", "secret"))
    assert response.status_code == 200


def test_health_check_remains_public(monkeypatch):
    monkeypatch.setenv("PILOT_ACCESS_REQUIRED", "true")
    monkeypatch.setenv("PILOT_ACCESS_USER", "pilot")
    monkeypatch.setenv("PILOT_ACCESS_PASSWORD", "secret")
    with TestClient(app) as client:
        response = client.get("/api/status")
    assert response.status_code == 200


def test_public_passport_route_does_not_request_authentication(monkeypatch):
    monkeypatch.setenv("PILOT_ACCESS_REQUIRED", "true")
    monkeypatch.setenv("PILOT_ACCESS_USER", "pilot")
    monkeypatch.setenv("PILOT_ACCESS_PASSWORD", "secret")
    with TestClient(app) as client:
        response = client.get("/p/nonexistent-passport")
    assert response.status_code == 404
    assert "www-authenticate" not in response.headers


def test_required_gate_fails_closed_without_credentials(monkeypatch):
    monkeypatch.setenv("PILOT_ACCESS_REQUIRED", "true")
    monkeypatch.delenv("PILOT_ACCESS_USER", raising=False)
    monkeypatch.delenv("PILOT_ACCESS_PASSWORD", raising=False)
    with TestClient(app) as client:
        response = client.get("/pecas")
    assert response.status_code == 503
