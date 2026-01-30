from __future__ import annotations
import requests

BASE_URL = "https://api.nbp.pl/api"


def fetch_table_a_for_date(date_str: str) -> list[dict]:
    """
    Zwraca liste kursow z tabeli A dla konkretnego dnia.
    Output: [{"code": "USD", "mid": 4.1234}, ...]
    """
    url = f"{BASE_URL}/exchangerates/tables/A/{date_str}/?format=json"
    r = requests.get(url, timeout=15)
    r.raise_for_status()

    data = r.json()
    # API zwraca liste z jednym elementem
    rates = data[0]["rates"]
    return [{"code": x["code"], "mid": x["mid"]} for x in rates]
