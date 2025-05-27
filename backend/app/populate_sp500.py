import os
from datetime import datetime, timedelta, date
import yfinance as yf
import pandas as pd
import time

from app.database import SessionLocal
from app.models.snp500 import Company, StockData

ASSETS = [
    {
        'symbol': '^GSPC',
        'name': 'S&P 500 Index',
        'sector': 'Index',
        'industry': 'Market Index'
    },
    {
        'symbol': 'GC=F',
        'name': 'Gold Futures',
        'sector': 'Commodity',
        'industry': 'Precious Metals'
    },
    {
        'symbol': '^TNX',
        'name': '10-Year Treasury Yield',
        'sector': 'Fixed Income',
        'industry': 'Government Bonds'
    },
    {
        'symbol': 'BTC-USD',
        'name': 'Bitcoin USD',
        'sector': 'Cryptocurrency',
        'industry': 'Digital Assets'
    },
    {
        'symbol': 'EURUSD=X',
        'name': 'EUR/USD Exchange Rate',
        'sector': 'Forex',
        'industry': 'Currency Pairs'
    }
]

def populate_data():
    # Get DB session
    session = SessionLocal()

    try:
        # Download 1 year of data for each asset
        end_date = date(2024, 5, 14)
        start_date = end_date - timedelta(days=365 * 5)  # Changed to 5 years
        
        for asset in ASSETS:
            print(f"\nProcessing {asset['name']}...")
            
            # Check if company exists
            company = session.query(Company).filter(Company.symbol == asset['symbol']).first()
            if not company:
                company = Company(
                    symbol=asset['symbol'],
                    name=asset['name'],
                    sector=asset['sector'],
                    industry=asset['industry']
                )
                session.add(company)
                session.commit()
                session.refresh(company)
            
            print(f"Downloading data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Add retry logic
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    df = yf.download(asset['symbol'], 
                                   start=start_date.strftime("%Y-%m-%d"), 
                                   end=end_date.strftime("%Y-%m-%d"),
                                   progress=False)
                    
                    if df.empty:
                        print(f"No data downloaded for {asset['name']} on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            continue
                        break
                    
                    # Reset index to make Date a column
                    df = df.reset_index()
                    
                    # Delete existing data for this company
                    session.query(StockData).filter(StockData.company_id == company.id).delete()
                    session.commit()
                    
                    # Insert stock data
                    for _, row in df.iterrows():
                        date_value = row['Date']
                        # If date_value is a Series, get the first value
                        if isinstance(date_value, pd.Series):
                            date_value = date_value.iloc[0]
                        # If it's a Timestamp, get the date
                        if hasattr(date_value, 'date'):
                            date_value = date_value.date()
                        stock_data = StockData(
                            company_id=company.id,
                            date=date_value,
                            open_price=float(row['Open']),
                            high_price=float(row['High']),
                            low_price=float(row['Low']),
                            close_price=float(row['Close']),
                            volume=int(row['Volume'])
                        )
                        session.add(stock_data)
                    
                    session.commit()
                    print(f"Successfully populated {len(df)} data points for {asset['name']}")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    print(f"Error downloading {asset['name']} on attempt {attempt + 1}: {str(e)}")
                    session.rollback()  # Rollback on error
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"Failed to download data for {asset['name']} after {max_retries} attempts")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    populate_data()
