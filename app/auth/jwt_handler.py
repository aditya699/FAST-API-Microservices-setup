from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from fastapi import Request, Depends

# Load environment variables
load_dotenv()

# Get JWT settings from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

# Verify we have all required settings
if not all([SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES]):
    raise ValueError("Missing required JWT configuration in environment variables")

def create_access_token(user_data: dict):
    """
    Create a JWT access token
    Args:
        user_data (dict): User data to encode in token
    Returns:
        str: JWT token
    """
    try:
        # Create a copy of data to avoid modifying original
        payload = user_data.copy()
        
        # Add token expiration time
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload.update({
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow()  # Token creation time
        })
        
        # Create JWT token
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating access token: {str(e)}"
        )
    
def verify_access_token(token: str):
    """
    Verify the JWT access token
    Args:
        token (str): JWT token to verify
    Returns:
        dict: Decoded token payload if valid
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp")):
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
            
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate token"
        )
    
async def get_current_user(request: Request):
    """
    Dependency to get current user from JWT token in cookie
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated - No token found"
        )
    
    # Verify the token and return user data
    user_data = verify_access_token(token)
    return user_data
