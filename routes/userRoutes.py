from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import subprocess
import os
from tempfile import NamedTemporaryFile

from controllers.userController import UserController
from middleware.authentication import is_authenticated_user
from utils.s3upload import upload_csv_to_local

user_router = APIRouter()

# Initialize user controller
user_controller = UserController()

@user_router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload CSV file and process with Python crew
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Save uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Call the Python crew function with the uploaded file path
        python_result = await call_python_crew(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Uploaded successfully",
                "filePath": temp_file_path,
                "crewResult": python_result
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def call_python_crew(file_path: str):
    """
    Call Python crew function with file path
    """
    try:
        # Run the crew.py script with the file path
        result = subprocess.run(
            ['python', 'crew.py', '--file-path', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Python crew process failed: {e.stderr}"
        )

# User registration and login routes
@user_router.post("/register")
async def register_user(user_data: dict):
    """
    Register a new user
    """
    return await user_controller.register_user(user_data)

@user_router.get("/verify/{token}")
async def verify_email(token: str):
    """
    Verify user email with token
    """
    return await user_controller.verify_email(token)

@user_router.post("/email/resend")
async def resend_verification_email(email_data: dict):
    """
    Resend verification email
    """
    return await user_controller.resend_verification_email(email_data)

@user_router.post("/login")
async def login_user(login_data: dict):
    """
    Login user
    """
    return await user_controller.login_user(login_data)

@user_router.post("/password/forgot")
async def forgot_password(email_data: dict):
    """
    Send forgot password email
    """
    return await user_controller.forgot_password(email_data)

@user_router.put("/password/reset/{token}")
async def reset_password(token: str, password_data: dict):
    """
    Reset password with token
    """
    return await user_controller.reset_password(token, password_data)

@user_router.get("/logout")
async def logout():
    """
    Logout user
    """
    return await user_controller.logout()

@user_router.get("/me")
async def get_user_details(user_id: str = Depends(is_authenticated_user)):
    """
    Get current user details
    """
    return await user_controller.get_user_details(user_id)

@user_router.put("/me/update")
async def update_user(user_data: dict, user_id: str = Depends(is_authenticated_user)):
    """
    Update user profile
    """
    return await user_controller.update_user(user_id, user_data)

@user_router.put("/password/update")
async def update_password(password_data: dict, user_id: str = Depends(is_authenticated_user)):
    """
    Update user password
    """
    return await user_controller.update_password(user_id, password_data)

# Admin routes
@user_router.get("/admin/users")
async def get_all_users(user_id: str = Depends(is_authenticated_user)):
    """
    Get all users (admin only)
    """
    return await user_controller.get_all_users(user_id) 