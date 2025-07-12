from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import os

# Import your existing modules
from models.userModel import User
from controllers.userController import UserController
from middleware.authentication import verify_token
from middleware.error import error_handler
from routes.userRoutes import user_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="DataIntel Hub API",
    description="A FastAPI backend for DataIntel Hub",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(user_router, prefix="/api/users", tags=["users"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "DataIntel Hub API is running!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DataIntel Hub API"}

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return error_handler(request, exc)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 