from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/test/")
def test_database_connection(db: Session = Depends(get_db)):
    try:
        # Use text() to properly format the SQL query
        result = db.execute(text("SELECT 1"))
        return {"message": "Successfully connected to database"}
    except Exception as e:
        return {"error": str(e)}