# Dashboard Web Application

A full-stack web application for displaying and managing dashboards with daily updated data.

## Project Structure
```
csv_dashboard/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── routes/    # API routes
│   │   └── database.py
│   └── main.py
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   └── package.json
└── requirements.txt
```

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the backend directory with:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/dashboard_db
   ```

4. Run the backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the frontend:
   ```bash
   npm start
   ```

## Features
- Multiple dashboard views
- Daily data updates
- Interactive charts and visualizations
- Data management interface 