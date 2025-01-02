from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app import models
from .auth.session_handler import verify_session


router = APIRouter()

@router.get("/test/")
def test_database_connection(db: Session = Depends(get_db)):
    try:
        # Use text() to properly format the SQL query
        result = db.execute(text("SELECT 1"))
        return {"message": "Successfully connected to database"}
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/test-session")
async def test_session(session: models.Session = Depends(verify_session)):
    return {
        "message": "Valid session",
        "session_id": str(session.session_id),
        "created_at": session.created_at,
        "expires_at": session.expires_at
    }