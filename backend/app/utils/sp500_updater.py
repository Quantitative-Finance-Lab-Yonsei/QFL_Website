import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from ..models.sp500 import SP500Data, SP500Company
from datetime import datetime, timedelta

def get_sp500_symbols():
    """Get list of S&P 500 symbols from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    return df[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry']].rename(
        columns={
            'Symbol': 'symbol',
            'Security': 'name',
            'GICS Sector': 'sector',
            'GICS Sub-Industry': 'industry'
        }
    )

def update_companies(db: Session):
    """Update S&P 500 companies information"""
    companies_df = get_sp500_symbols()
    
    for _, row in companies_df.iterrows():
        company = db.query(SP500Company).filter(SP500Company.symbol == row['symbol']).first()
        if company:
            company.name = row['name']
            company.sector = row['sector']
            company.industry = row['industry']
        else:
            company = SP500Company(
                symbol=row['symbol'],
                name=row['name'],
                sector=row['sector'],
                industry=row['industry']
            )
            db.add(company)
    
    db.commit()

def update_stock_data(db: Session, days_back=30):
    """Update stock data for all S&P 500 companies"""
    companies = db.query(SP500Company).all()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    for company in companies:
        try:
            # Get stock data
            stock = yf.Ticker(company.symbol)
            hist = stock.history(start=start_date, end=end_date)
            
            # Update database
            for date, row in hist.iterrows():
                data = db.query(SP500Data).filter(
                    SP500Data.symbol == company.symbol,
                    SP500Data.date == date.date()
                ).first()
                
                if data:
                    data.open_price = row['Open']
                    data.high_price = row['High']
                    data.low_price = row['Low']
                    data.close_price = row['Close']
                    data.volume = row['Volume']
                else:
                    data = SP500Data(
                        date=date.date(),
                        symbol=company.symbol,
                        open_price=row['Open'],
                        high_price=row['High'],
                        low_price=row['Low'],
                        close_price=row['Close'],
                        volume=row['Volume']
                    )
                    db.add(data)
            
            db.commit()
            print(f"Updated data for {company.symbol}")
            
        except Exception as e:
            print(f"Error updating {company.symbol}: {str(e)}")
            continue 