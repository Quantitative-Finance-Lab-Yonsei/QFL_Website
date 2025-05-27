from sqlalchemy import create_engine, BigInteger
from sqlalchemy.sql import text
from ..database import SQLALCHEMY_DATABASE_URL

def update_volume_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Update the volume column type to BigInteger
    with engine.connect() as connection:
        connection.execute(text("""
            ALTER TABLE stock_data 
            ALTER COLUMN volume TYPE BIGINT 
            USING volume::BIGINT
        """))
        connection.commit()

if __name__ == "__main__":
    update_volume_column()
    print("Volume column updated to BigInteger successfully.") 