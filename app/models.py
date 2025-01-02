from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship  # Add this import



class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    google_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationship with User
    user = relationship("User", back_populates="sessions")
    
    # Relationship with Messages
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    session_id = Column(UNIQUEIDENTIFIER, ForeignKey('sessions.session_id'), nullable=False)
    user_message = Column(String(length=None), nullable=False)  # NVARCHAR(MAX)
    assistant_message = Column(String(length=None))  # NVARCHAR(MAX)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with Session
    session = relationship("Session", back_populates="messages")