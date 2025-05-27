from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class StockDataBase(BaseModel):
    date: date
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[int] = None
    dtcai: Optional[float] = None

class StockDataCreate(StockDataBase):
    company_id: int

class StockData(StockDataBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

class CompanyBase(BaseModel):
    symbol: str
    name: str
    sector: str
    industry: str

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    stock_data: List[StockData] = []

    class Config:
        from_attributes = True 