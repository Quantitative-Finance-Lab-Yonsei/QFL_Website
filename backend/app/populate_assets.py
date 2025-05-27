import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import snp500 as crud
from app.schemas.snp500 import CompanyCreate, StockDataCreate
import pandas as pd

def populate_assets():
    db = SessionLocal()
    try:
        # Define assets and their symbols
        assets = [
            {"symbol": "GC=F", "name": "Gold Futures", "sector": "Commodity", "industry": "Precious Metals"},
            {"symbol": "^TNX", "name": "10-Year Treasury Yield", "sector": "Bond", "industry": "Government"},
            {"symbol": "BTC-USD", "name": "Bitcoin USD", "sector": "Cryptocurrency", "industry": "Digital Currency"},
            {"symbol": "EURUSD=X", "name": "EUR/USD Exchange Rate", "sector": "Forex", "industry": "Currency"}
        ]

        # Get 10 years of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*10)

        for asset in assets:
            # Download data
            df = yf.download(asset["symbol"], 
                            start=start_date.strftime("%Y-%m-%d"), 
                            end=end_date.strftime("%Y-%m-%d"))
            
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
            
            # Create stock data entries
            for _, row in df.iterrows():
                stock_data = StockDataCreate(
                    company_id=company.id,
                    date=pd.to_datetime(row["Date"]).iloc[0].date(),
                    open_price=float(row["Open"]),
                    high_price=float(row["High"]),
                    low_price=float(row["Low"]),
                    close_price=float(row["Close"]),
                    volume=int(row["Volume"])
                )
                crud.create_stock_data(db, stock_data)
            
            print(f"{asset['name']} data populated successfully.")
    
    except Exception as e:
        print(f"Error populating assets: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_assets() 