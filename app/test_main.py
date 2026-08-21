import os
os.environ["DB_HOST"] = os.environ.get("DB_HOST", "localhost")
os.environ["DB_NAME"] = os.environ.get("DB_NAME", "appdb")
os.environ["DB_USER"] = os.environ.get("DB_USER", "appuser")
os.environ["DB_PASSWORD"] = os.environ.get("DB_PASSWORD", "apppassword")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
client.__enter__()


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] in ["ready", "not ready"]


def test_form_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "3-Tier App Demo" in response.text


def test_submit_message():
    response = client.post("/submit", data={"content": "pytest automated test message"})
    assert response.status_code == 200
    assert "pytest automated test message" in response.text
