# app/auth.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from app.database import get_db
import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .. import models
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from .jwt_handler import get_current_user
from jose import JWTError, jwt

from .jwt_handler import create_access_token,verify_access_token
auth_router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

@auth_router.get("/google/login")
async def google_login(request: Request):
    try:
        # First check if user has valid token
        token = request.cookies.get("access_token")
        if token:
            # Verify token
            user_data = verify_access_token(token)
            # If token is valid, redirect to home/dashboard
            return RedirectResponse(url="/auth/test-auth")
            
    except (JWTError, HTTPException):
        # If token invalid or expired, proceed with Google login
        pass
        
    # If no token or invalid token, proceed with Google login
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
    }
    
    from urllib.parse import urlencode
    authorization_url = f"{auth_url}?{urlencode(params)}"
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
        
        current_time = datetime.now(timezone.utc)
        
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

        token_data = {
            "user_id": str(user.user_id),
            "email": user.email
        }
        access_token = create_access_token(token_data)
        
        # For now, just return the token
         
        # Create response object
        response = JSONResponse(
            content={
                "message": "Successfully authenticated",
                "user": {
                    "email": user.email,
                    "username": user.username
                }
            }
        )
        
        # Set JWT in secure cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,     # JavaScript can't access cookie
            secure=True,       # Only sent over HTTPS
            samesite="lax",    # CSRF protection
            max_age=86400      # 24 hours in seconds
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@auth_router.get("/test-auth")
async def test_protected_route(current_user: dict = Depends(get_current_user)):
    """
    Protected route that requires valid JWT token
    """
    return {
        "message": "You are authenticated!",
        "your_details": {
            "user_id": current_user["user_id"],
            "email": current_user["email"]
        }
    }


@auth_router.get("/logout")
async def logout():
    # Create response
    response = JSONResponse(content={"message": "Successfully logged out"})
    
    # Delete the JWT cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return response