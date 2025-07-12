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
from controllers.reportController import router as report_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="DataIntel Hub API",
    description="A FastAPI backend for DataIntel Hub",
    version="1.0.0",
    docs_url="/swagger",         # Change Swagger UI path
    redoc_url="/redoc",          # Change Redoc path
    openapi_url="/openapi.json"  # Change OpenAPI schema path
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://dataintel-hub-frontend.onrender.com"],  # Allow frontend origin for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(report_router, prefix="/api/users", tags=["reports"])

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

# Get port from environment variable or default to 8091
port = int(os.getenv("PORT", 8090))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    ) 
