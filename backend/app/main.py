from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import snp500

app = FastAPI(title="S&P 500 Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(snp500.router)  # Router already has /api/v1 prefix

@app.get("/")
def read_root():
    return {"message": "Welcome to S&P 500 Dashboard API"} 