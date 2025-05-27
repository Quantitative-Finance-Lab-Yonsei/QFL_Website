from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import sp500
from app.routes.snp500 import router as snp500_router

# Create database tables
sp500.Base.metadata.create_all(bind=engine)

app = FastAPI(title="S&P 500 Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(snp500_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to S&P 500 Dashboard API"} 