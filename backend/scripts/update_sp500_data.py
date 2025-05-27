import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.snp500 import Company, StockData
from app.schemas.snp500 import CompanyCreate, StockDataCreate

def get_sp500_companies():
    """Get list of S&P 500 companies from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    return df[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry']]

def fetch_stock_data(symbol: str, start_date: datetime, end_date: datetime):
    """Fetch stock data for a given symbol using yfinance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        return hist
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def update_database():
    db = SessionLocal()
    try:
        # Get S&P 500 companies
        print("Fetching S&P 500 companies...")
        companies_df = get_sp500_companies()
        
        # Set date range for stock data (last 5 years)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        
        # Process each company
        for _, row in companies_df.iterrows():
            symbol = row['Symbol']
            name = row['Security']
            sector = row['GICS Sector']
            industry = row['GICS Sub-Industry']
            
            # Check if company exists
            company = db.query(Company).filter(Company.symbol == symbol).first()
            if not company:
                # Create new company
                company_data = CompanyCreate(
                    symbol=symbol,
                    name=name,
                    sector=sector,
                    industry=industry
                )
                company = Company(**company_data.dict())
                db.add(company)
                db.commit()
                db.refresh(company)
                print(f"Added new company: {symbol}")
            
            # Fetch and store stock data
            print(f"Fetching stock data for {symbol}...")
            stock_data = fetch_stock_data(symbol, start_date, end_date)
            
            if stock_data is not None:
                for date, row in stock_data.iterrows():
                    # Check if data for this date already exists
                    existing_data = db.query(StockData).filter(
                        StockData.company_id == company.id,
                        StockData.date == date.date()
                    ).first()
                    
                    if not existing_data:
                        # Create new stock data entry
                        stock_data_entry = StockDataCreate(
                            company_id=company.id,
                            date=date.date(),
                            open_price=float(row['Open']),
                            high_price=float(row['High']),
                            low_price=float(row['Low']),
                            close_price=float(row['Close']),
                            volume=int(row['Volume'])
                        )
                        db_stock_data = StockData(**stock_data_entry.dict())
                        db.add(db_stock_data)
                
                db.commit()
                print(f"Updated stock data for {symbol}")
            
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting S&P 500 data update...")
    update_database()
    print("Data update completed!") 