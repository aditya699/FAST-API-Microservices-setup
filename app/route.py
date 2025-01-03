from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app import models
from .auth.session_handler import verify_session

from app import models, schemas
router = APIRouter()

    
@router.get("/test-session")
async def test_session(session: models.Session = Depends(verify_session)):
    return {
        "message": "Valid session",
        "session_id": str(session.session_id),
        "created_at": session.created_at,
        "expires_at": session.expires_at
    }


@router.post("/chat/")
async def create_chat_message(
    message_input: schemas.MessageInput,
    session: models.Session = Depends(verify_session),
    db: Session = Depends(get_db)
):
    """
    Create a new chat message and get assistant's response
    """
    # Create new message
    db_message = models.Message(
        session_id=session.session_id,
        user_message=message_input.message,
        # Echo the message back for now
        assistant_message=f"Echo: {message_input.message}"
    )
    
    try:
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        return {
            "message_id": str(db_message.message_id),
            "user_message": db_message.user_message,
            "assistant_message": db_message.assistant_message,
            "created_at": db_message.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/")
async def get_chat_history(
    session: models.Session = Depends(verify_session),
    db: Session = Depends(get_db)
):
    """Get all messages for the current session"""
    messages = db.query(models.Message).filter(
        models.Message.session_id == session.session_id
    ).order_by(models.Message.created_at.asc()).all()
    
    return [{
        "message_id": str(msg.message_id),
        "user_message": msg.user_message,
        "assistant_message": msg.assistant_message,
        "created_at": msg.created_at
    } for msg in messages]
