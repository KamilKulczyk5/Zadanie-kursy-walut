from sqlalchemy import Column, Integer, String, Date, Numeric, UniqueConstraint
from .db import Base


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    currency_code = Column(String(3), nullable=False, index=True)
    rate_date = Column(Date, nullable=False, index=True)
    mid = Column(Numeric(12, 6), nullable=False)

    __table_args__ = (
        UniqueConstraint("currency_code", "rate_date", name="uix_currency_date"),
    )
