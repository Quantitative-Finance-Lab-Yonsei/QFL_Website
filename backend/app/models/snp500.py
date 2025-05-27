from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from ..database import Base

class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    
    # Relationship with stock data
    stock_data = relationship("StockData", back_populates="company")

class StockData(Base):
    __tablename__ = "stock_data"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    date = Column(Date, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(BigInteger)
    dtcai = Column(Float)  # Adding dtcai column

    # Relationship with company
    company = relationship("Company", back_populates="stock_data") 