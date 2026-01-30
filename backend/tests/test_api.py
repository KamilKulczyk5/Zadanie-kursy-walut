def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_fetch_and_get_by_date(client, mock_nbp):
    r = client.post("/currencies/fetch", params={"date": "2025-10-09"})
    assert r.status_code == 200
    data = r.json()

    assert data["total"] == 3
    assert data["inserted"] == 3

    r2 = client.get("/currencies/2025-10-09")
    assert r2.status_code == 200
    payload = r2.json()

    assert payload["date"] == "2025-10-09"
    assert len(payload["rates"]) == 3


def test_rates_range(client, mock_nbp):
    client.post("/currencies/fetch", params={"date": "2025-10-09"})
    client.post("/currencies/fetch", params={"date": "2025-10-10"})

    r = client.get("/rates", params={"from": "2025-10-09", "to": "2025-10-10"})
    assert r.status_code == 200
    assert len(r.json()) == 6
