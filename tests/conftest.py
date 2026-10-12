from fastapi.testclient import TestClient
import pytest

from app import database, main


@pytest.fixture
def database_path(tmp_path):
    path = tmp_path / "unit-integration.db"
    database.initialize(path)
    return path


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "api.db"
    database.initialize(db_path)
    monkeypatch.setattr(main, "DB_PATH", db_path)
    return TestClient(main.app)
