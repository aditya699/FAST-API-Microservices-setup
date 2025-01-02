from fastapi import HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
import app.models as models
from ..auth.jwt_handler import get_current_user

async def verify_session(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifies if the user has a valid session
    Returns the session if valid, raises HTTPException if not
    """
    session_id = current_user.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="No session found in token")
    
    # Query the session
    session = db.query(models.Session).filter(
        models.Session.session_id == session_id,
        models.Session.user_id == current_user["user_id"]
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Session not found")
        
    # Check if session has expired
    if session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Session has expired")
        
    return session