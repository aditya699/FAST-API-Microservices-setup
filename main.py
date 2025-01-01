from fastapi import FastAPI
from app.route import router
from dotenv import load_dotenv
import os
from app.auth.auth import auth_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Add this line after your existing router inclusion
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Include our router
app.include_router(router, prefix="/api")

# Optional: Add a root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI SQL App"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)