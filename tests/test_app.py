import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app, db, init_db


@pytest.fixture(autouse=True)
def use_tmp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    app.config.update({"TESTING": True, "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"]})

    with app.app_context():
        db.engine.dispose()
        init_db()
    yield
    with app.app_context():
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client():
    return app.test_client()


def test_create_and_list_event(client):
    payload = {
        "title": "会議",
        "start_time": "2024-01-01T10:00:00",
        "end_time": "2024-01-01T11:00:00",
        "description": "新年の計画",
    }

    create_res = client.post(
        "/api/events",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert create_res.status_code == 201
    created = create_res.get_json()
    assert created["title"] == payload["title"]

    list_res = client.get("/api/events")
    assert list_res.status_code == 200
    events = list_res.get_json()
    assert len(events) == 1
    assert events[0]["id"] == created["id"]


def test_update_and_delete_event(client):
    start = datetime(2024, 1, 1, 9, 0)
    end = start + timedelta(hours=1)
    payload = {
        "title": "ミーティング",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "description": "初回",
    }

    create_res = client.post(
        "/api/events",
        data=json.dumps(payload),
        content_type="application/json",
    )
    event_id = create_res.get_json()["id"]

    update_res = client.put(
        f"/api/events/{event_id}",
        data=json.dumps({**payload, "title": "更新済み"}),
        content_type="application/json",
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["title"] == "更新済み"

    delete_res = client.delete(f"/api/events/{event_id}")
    assert delete_res.status_code == 204

    list_res = client.get("/api/events")
    assert list_res.get_json() == []


def test_validation_errors(client):
    res_missing = client.post("/api/events", data=json.dumps({}), content_type="application/json")
    assert res_missing.status_code == 400

    bad_end = {
        "title": "逆転",
        "start_time": "2024-01-01T12:00:00",
        "end_time": "2024-01-01T11:00:00",
    }
    res_bad = client.post(
        "/api/events",
        data=json.dumps(bad_end),
        content_type="application/json",
    )
    assert res_bad.status_code == 400
