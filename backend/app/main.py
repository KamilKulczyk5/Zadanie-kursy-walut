from datetime import datetime, date
import requests
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .db import Base, engine
from .deps import get_db
from .schemas import FetchResponse, RatesByDateResponse, RateOut
from .nbp_client import fetch_table_a_for_date
from .services import (
    upsert_rates,
    get_rates_for_date,
    get_distinct_currencies,
    get_rates_for_range,
)

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


# 1) Lista walut dostępnych w bazie
@app.get("/currencies")
def currencies(db: Session = Depends(get_db)):
    return {"currencies": get_distinct_currencies(db)}


# 2) Kursy dla konkretnej daty
@app.get("/currencies/{date_str}", response_model=RatesByDateResponse)
def currencies_by_date(date_str: str, db: Session = Depends(get_db)):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    rows = get_rates_for_date(db, d)
    rates = [RateOut(code=r.currency_code, mid=float(r.mid)) for r in rows]
    return RatesByDateResponse(date=date_str, rates=rates)


# 3) Kursy z bazy w zakresie dat (NOWE)
@app.get("/rates")
def rates_range(
    from_: date = Query(..., alias="from", description="YYYY-MM-DD"),
    to: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    if from_ > to:
        raise HTTPException(status_code=400, detail="'from' must be <= 'to'")

    rows = get_rates_for_range(db, from_, to)

    # UWAGA: w modelu masz rate_date, nie date
    return [
        {"date": r.rate_date.isoformat(), "currency": r.currency_code, "mid": float(r.mid)}
        for r in rows
    ]


# 4) Pobierz z NBP i zapisz do bazy
@app.post("/currencies/fetch", response_model=FetchResponse)
def fetch_and_save(
    date_str: str = Query(..., alias="date", description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        rates = fetch_table_a_for_date(date_str)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status == 404:
            raise HTTPException(
                status_code=404,
                detail="Brak danych NBP dla wybranej daty (weekend/święto lub dzień bez publikacji tabeli).",
            )
        raise HTTPException(status_code=502, detail=f"NBP fetch failed: {e}")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"NBP request failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"NBP fetch failed: {e}")

    inserted, updated = upsert_rates(db, d, rates)

    return FetchResponse(
        date=date_str,
        inserted=inserted,
        updated=updated,
        total=len(rates),
    )
