import os
import sys

# żeby importy "from app..." działały w pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.deps import get_db
from app.main import app
from app.models import CurrencyRate  # <-- DODANE (czyszczenie tabeli)


@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ✅ KLUCZ: czyścimy tabelę przed KAŻDYM testem, żeby inserted było przewidywalne
@pytest.fixture(autouse=True)
def clean_db(db_session):
    db_session.query(CurrencyRate).delete()
    db_session.commit()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def mock_nbp(monkeypatch):
    import app.main

    def fake_fetch_table_a_for_date(date_str: str):
        return [
            {"code": "EUR", "mid": 4.0},
            {"code": "USD", "mid": 3.5},
            {"code": "GBP", "mid": 4.8},
        ]

    monkeypatch.setattr(app.main, "fetch_table_a_for_date", fake_fetch_table_a_for_date)
    return True
