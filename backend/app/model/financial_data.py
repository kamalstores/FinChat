from sqlalchemy import Column, Integer, String, Float

from app.shared.db import Base


class FinancialData(Base):
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, index=True)
    ticker = Column(String, index=True)
    sector = Column(String, index=True)
    year = Column(Integer, index=True)
    revenue = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    operating_income = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)