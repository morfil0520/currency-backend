from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base

class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True)
    char_code = Column(String, index=True)
    name = Column(String)
    nominal = Column(Integer)
    value = Column(Float)
    date = Column(String)
