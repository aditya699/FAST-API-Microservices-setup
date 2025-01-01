from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    google_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)