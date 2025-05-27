import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal  # Absolute import for SessionLocal
from app.models.snp500 import StockData, Company  # Import StockData and Company
import os
import csv
from app.database import get_db

def populate_lppl_ai_data():
    db = SessionLocal()  # Create a database session
    try:
        # Read the CSV file
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend', 'LPPL_AI_SNP.csv')
        df = pd.read_csv(csv_path)  # Load the CSV into a DataFrame
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Get or create the ^GSPC company
        company = db.query(Company).filter(Company.symbol == "^GSPC").first()
        if not company:
            company = Company(
                symbol="^GSPC",
                name="S&P 500 Index",
                sector="Index",
                industry="Market Index"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        
        # Insert data into database
        for _, row in df.iterrows():
            # Check if data for this date already exists
            existing_data = db.query(StockData).filter(
                StockData.date == row['Date'].date(),
                StockData.company_id == company.id
            ).first()
            
            if not existing_data:
                # Create a new record if not already present
                stock_data = StockData(
                    company_id=company.id,
                    date=row['Date'].date(),
                    close_price=float(row['Close']),
                    dtcai=float(row['dtcai'])
                )
                db.add(stock_data)  # Add the record to the session
        
        db.commit()  # Commit the transaction to the database
        print("LPPL AI data populated successfully.")
    
    except Exception as e:
        print(f"Error populating LPPL AI data: {e}")
        db.rollback()  # Rollback the transaction if any error occurs
    finally:
        db.close()  # Close the session

def populate_dtcai():
    db = next(get_db())
    with open('LPPL_AI_SNP.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stock_data = db.query(StockData).filter(StockData.date == row['Date']).first()
            if stock_data:
                stock_data.dtcai = float(row['dtcai'])
    db.commit()

if __name__ == "__main__":
    populate_lppl_ai_data()  # Run the function to populate the data
    populate_dtcai()
