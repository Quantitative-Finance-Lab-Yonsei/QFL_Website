from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from typing import List, Optional
from ..models.snp500 import Company, StockData
from ..schemas.snp500 import CompanyCreate, StockDataCreate

def get_company(db: Session, company_id: int):
    return db.query(Company).filter(Company.id == company_id).first()

def get_company_by_symbol(db: Session, symbol: str):
    return db.query(Company).filter(Company.symbol == symbol).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Company).offset(skip).limit(limit).all()

def create_company(db: Session, company: CompanyCreate):
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_stock_data(
    db: Session,
    company_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100
):
    query = db.query(StockData).filter(StockData.company_id == company_id)
    
    if start_date:
        query = query.filter(StockData.date >= start_date)
    if end_date:
        query = query.filter(StockData.date <= end_date)
    
    return query.order_by(desc(StockData.date)).limit(limit).all()

def create_stock_data(db: Session, stock_data: StockDataCreate):
    db_stock_data = StockData(**stock_data.dict())
    db.add(db_stock_data)
    db.commit()
    db.refresh(db_stock_data)
    return db_stock_data

def get_latest_stock_data(db: Session, company_id: int):
    return db.query(StockData)\
        .filter(StockData.company_id == company_id)\
        .order_by(desc(StockData.date))\
        .first() 