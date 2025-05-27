from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from ..database import get_db
from ..crud import snp500 as crud
from ..schemas.snp500 import Company, CompanyCreate, StockData, StockDataCreate
import yfinance as yf

router = APIRouter(prefix="/api/v1")

@router.get("/companies/", response_model=List[Company])
def read_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    companies = crud.get_companies(db, skip=skip, limit=limit)
    return companies

@router.get("/companies/{company_id}", response_model=Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = crud.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.get("/companies/symbol/{symbol}", response_model=Company)
def read_company_by_symbol(symbol: str, db: Session = Depends(get_db)):
    db_company = crud.get_company_by_symbol(db, symbol=symbol)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.post("/companies/", response_model=Company)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = crud.get_company_by_symbol(db, symbol=company.symbol)
    if db_company:
        raise HTTPException(status_code=400, detail="Company already exists")
    return crud.create_company(db=db, company=company)

@router.get("/stock-data/{company_id}", response_model=List[StockData])
def read_stock_data(
    company_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    stock_data = crud.get_stock_data(
        db,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return stock_data

@router.post("/stock-data/", response_model=StockData)
def create_stock_data(stock_data: StockDataCreate, db: Session = Depends(get_db)):
    return crud.create_stock_data(db=db, stock_data=stock_data)

@router.get("/stock-data/{company_id}/latest", response_model=StockData)
def read_latest_stock_data(company_id: int, db: Session = Depends(get_db)):
    stock_data = crud.get_latest_stock_data(db, company_id=company_id)
    if stock_data is None:
        raise HTTPException(status_code=404, detail="Stock data not found")
    return stock_data

@router.get("/stock-data/symbol/{symbol}", response_model=List[StockData])
def read_stock_data_by_symbol(
    symbol: str,
    db: Session = Depends(get_db)
):
    company = crud.get_company_by_symbol(db, symbol=symbol)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return crud.get_stock_data(db, company_id=company.id)

@router.get("/sp500-index/", response_model=List[StockData])
def read_sp500_index(
    days: int = Query(default=365, ge=1, le=3650),
    db: Session = Depends(get_db)
):
    """Get S&P 500 index data for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    company = crud.get_company_by_symbol(db, symbol="^GSPC")
    if not company:
        raise HTTPException(status_code=404, detail="S&P 500 index data not found")
    
    stock_data = crud.get_stock_data(
        db,
        company_id=company.id,
        start_date=start_date.date(),
        end_date=end_date.date(),
        limit=days
    )
    
    return stock_data

@router.post("/update-sp500-data/")
def update_sp500_data(db: Session = Depends(get_db)):
    """
    Updates the database with 10 years of S&P 500 index data.
    """
    try:
        # Get 10 years of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*10)
        
        # Download S&P 500 data
        df = yf.download("^GSPC", 
                        start=start_date.strftime("%Y-%m-%d"), 
                        end=end_date.strftime("%Y-%m-%d"))
        
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Create or get S&P 500 company entry
        sp500_company = crud.get_company_by_symbol(db, symbol="^GSPC")
        if not sp500_company:
            sp500_company = crud.create_company(db, CompanyCreate(
                symbol="^GSPC",
                name="S&P 500 Index",
                sector="Index",
                industry="Market Index"
            ))
        
        # Create stock data entries
        for _, row in df.iterrows():
            stock_data = StockDataCreate(
                company_id=sp500_company.id,
                date=row["Date"].date(),
                open_price=float(row["Open"]),
                high_price=float(row["High"]),
                low_price=float(row["Low"]),
                close_price=float(row["Close"]),
                volume=int(row["Volume"])
            )
            crud.create_stock_data(db, stock_data)
        
        return {"message": "S&P 500 data updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gold-index/", response_model=List[StockData])
def read_gold_index(
    days: int = Query(default=3650, ge=1, le=3650),
    db: Session = Depends(get_db)
):
    """Get Gold index data for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    company = crud.get_company_by_symbol(db, symbol="GC=F")  # Gold futures symbol
    if not company:
        raise HTTPException(status_code=404, detail="Gold index data not found")
    
    stock_data = crud.get_stock_data(
        db,
        company_id=company.id,
        start_date=start_date.date(),
        end_date=end_date.date(),
        limit=days
    )
    
    return stock_data

@router.get("/interest-rate/", response_model=List[StockData])
def read_interest_rate(
    days: int = Query(default=3650, ge=1, le=3650),
    db: Session = Depends(get_db)
):
    """Get Interest Rate data for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    company = crud.get_company_by_symbol(db, symbol="^TNX")  # 10-Year Treasury Yield
    if not company:
        raise HTTPException(status_code=404, detail="Interest rate data not found")
    
    stock_data = crud.get_stock_data(
        db,
        company_id=company.id,
        start_date=start_date.date(),
        end_date=end_date.date(),
        limit=days
    )
    
    return stock_data

@router.get("/bitcoin-index/", response_model=List[StockData])
def read_bitcoin_index(
    days: int = Query(default=3650, ge=1, le=3650),
    db: Session = Depends(get_db)
):
    """Get Bitcoin index data for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    company = crud.get_company_by_symbol(db, symbol="BTC-USD")  # Bitcoin USD
    if not company:
        raise HTTPException(status_code=404, detail="Bitcoin index data not found")
    
    stock_data = crud.get_stock_data(
        db,
        company_id=company.id,
        start_date=start_date.date(),
        end_date=end_date.date(),
        limit=days
    )
    
    return stock_data

@router.get("/fx-rate/", response_model=List[StockData])
def read_fx_rate(
    days: int = Query(default=3650, ge=1, le=3650),
    db: Session = Depends(get_db)
):
    """Get FX Rate data for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    company = crud.get_company_by_symbol(db, symbol="EURUSD=X")  # EUR/USD exchange rate
    if not company:
        raise HTTPException(status_code=404, detail="FX rate data not found")
    
    stock_data = crud.get_stock_data(
        db,
        company_id=company.id,
        start_date=start_date.date(),
        end_date=end_date.date(),
        limit=days
    )
    
    return stock_data

@router.post("/update-all-assets/")
def update_all_assets(db: Session = Depends(get_db)):
    """
    Updates the database with 10 years of data for all assets.
    """
    try:
        # Get 10 years of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*10)
        
        # Define assets to update
        assets = [
            {"symbol": "^GSPC", "name": "S&P 500 Index", "sector": "Index", "industry": "Market Index"},
            {"symbol": "GC=F", "name": "Gold Futures", "sector": "Commodity", "industry": "Precious Metals"},
            {"symbol": "^TNX", "name": "10-Year Treasury Yield", "sector": "Bond", "industry": "Government Bonds"},
            {"symbol": "BTC-USD", "name": "Bitcoin USD", "sector": "Crypto", "industry": "Cryptocurrency"},
            {"symbol": "EURUSD=X", "name": "EUR/USD Exchange Rate", "sector": "Forex", "industry": "Currency"}
        ]
        
        results = []
        for asset in assets:
            try:
                # Download data
                df = yf.download(asset["symbol"], 
                               start=start_date.strftime("%Y-%m-%d"), 
                               end=end_date.strftime("%Y-%m-%d"))
                
                if df.empty:
                    results.append(f"No data found for {asset['symbol']}")
                    continue
                
                # Reset index to make Date a column
                df = df.reset_index()
                
                # Create or get company entry
                company = crud.get_company_by_symbol(db, symbol=asset["symbol"])
                if not company:
                    company = crud.create_company(db, CompanyCreate(
                        symbol=asset["symbol"],
                        name=asset["name"],
                        sector=asset["sector"],
                        industry=asset["industry"]
                    ))
                
                # Delete existing data for this company
                db.query(StockData).filter(StockData.company_id == company.id).delete()
                db.commit()
                
                # Create stock data entries
                for _, row in df.iterrows():
                    try:
                        stock_data = StockDataCreate(
                            company_id=company.id,
                            date=row["Date"].date(),
                            open_price=float(row["Open"]),
                            high_price=float(row["High"]),
                            low_price=float(row["Low"]),
                            close_price=float(row["Close"]),
                            volume=int(row["Volume"])
                        )
                        crud.create_stock_data(db, stock_data)
                    except Exception as e:
                        print(f"Error creating stock data for {asset['symbol']} on {row['Date']}: {str(e)}")
                        continue
                
                results.append(f"Successfully updated {asset['symbol']} with {len(df)} records")
                
            except Exception as e:
                results.append(f"Error updating {asset['symbol']}: {str(e)}")
                continue
        
        return {"message": "Asset update completed", "results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 