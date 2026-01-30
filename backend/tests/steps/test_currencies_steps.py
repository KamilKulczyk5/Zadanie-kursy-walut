from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../features/currencies.feature")


@given("NBP returns rates")
def nbp_returns_rates(mock_nbp):
    assert mock_nbp is True


@when(parsers.parse('I fetch and save rates for "{date_str}"'))
def fetch_for_date(client, date_str):
    r = client.post("/currencies/fetch", params={"date": date_str})
    assert r.status_code == 200


@then(parsers.parse('reading rates for "{date_str}" returns 3 items'))
def read_by_date(client, date_str):
    r = client.get(f"/currencies/{date_str}")
    assert r.status_code == 200
    assert len(r.json()["rates"]) == 3


@then(parsers.parse('reading range from "{from_date}" to "{to_date}" returns {n:d} items'))
def read_range(client, from_date, to_date, n):
    r = client.get("/rates", params={"from": from_date, "to": to_date})
    assert r.status_code == 200
    assert len(r.json()) == n
