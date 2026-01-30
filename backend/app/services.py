from __future__ import annotations

from datetime import date as dt_date
from sqlalchemy.orm import Session

from .models import CurrencyRate


def upsert_rates(db: Session, rate_date: dt_date, rates: list[dict]) -> tuple[int, int]:
    """
    Upsert po (currency_code, rate_date).
    Zwraca (inserted, updated).
    """
    inserted = 0
    updated = 0

    for r in rates:
        code = r["code"]
        mid = r["mid"]

        existing = (
            db.query(CurrencyRate)
            .filter(
                CurrencyRate.currency_code == code,
                CurrencyRate.rate_date == rate_date,
            )
            .one_or_none()
        )

        if existing is None:
            db.add(CurrencyRate(currency_code=code, rate_date=rate_date, mid=mid))
            inserted += 1
        else:
            # aktualizuj tylko jeśli się różni
            if float(existing.mid) != float(mid):
                existing.mid = mid
                updated += 1

    db.commit()
    return inserted, updated


def get_rates_for_date(db: Session, rate_date: dt_date) -> list[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .filter(CurrencyRate.rate_date == rate_date)
        .order_by(CurrencyRate.currency_code.asc())
        .all()
    )


def get_rates_for_range(db: Session, from_: dt_date, to: dt_date) -> list[CurrencyRate]:
    """
    Zwraca rekordy z bazy dla zakresu dat [from_, to].
    Sort: data rosnąco, waluta rosnąco.
    """
    return (
        db.query(CurrencyRate)
        .filter(CurrencyRate.rate_date >= from_)
        .filter(CurrencyRate.rate_date <= to)
        .order_by(CurrencyRate.rate_date.asc(), CurrencyRate.currency_code.asc())
        .all()
    )


def get_distinct_currencies(db: Session) -> list[str]:
    rows = (
        db.query(CurrencyRate.currency_code)
        .distinct()
        .order_by(CurrencyRate.currency_code.asc())
        .all()
    )
    return [r[0] for r in rows]
