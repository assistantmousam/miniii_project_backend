from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine


app = FastAPI(
    title="DSA Arcade API",
    description="Backend API for the DSA Arcade gamified DSA learning platform",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to DSA Arcade API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected",
    }