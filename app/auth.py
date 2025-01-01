# app/auth.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from app.database import get_db
import os
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from fastapi import HTTPException
auth_router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

@auth_router.get("/google/login")
async def google_login():
    # Google's OAuth2 server URL
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth"
    # Parameters for the request
    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
    }
    
    # Construct the authorization URL with parameters
    from urllib.parse import urlencode
    authorization_url = f"{auth_url}?{urlencode(params)}"
    
    # Redirect to Google's authorization endpoint
    return RedirectResponse(authorization_url)

@auth_router.get("/callback")
async def auth_callback(code: str, db: Session = Depends(get_db)):
    try:
        # Step 1 - Exchange the code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        # Make request to get tokens
        import requests as requests_lib
        token_response = requests_lib.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get token from Google")
            
        token_json = token_response.json()

        # Step 2 - Get user info from token
        idinfo = id_token.verify_oauth2_token(
            token_json['id_token'],
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Step 3 - Check if user exists
        user = db.query(models.User).filter(models.User.google_id == idinfo['sub']).first()
        
        current_time = datetime.utcnow()
        
        if user:
            # Update existing user's last login
            user.last_login = current_time
            if user.username != idinfo.get('name'):  # Update username if changed
                user.username = idinfo.get('name')
        else:
            # Create new user
            user = models.User(
                google_id=idinfo['sub'],
                email=idinfo['email'],
                username=idinfo.get('name'),
                created_at=current_time,
                last_login=current_time
            )
            db.add(user)
        
        db.commit()

        return {
            "message": "Successfully authenticated",
            "user_info": {
                "user_id": str(user.user_id),
                "email": user.email,
                "username": user.username,
                "last_login": user.last_login
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))