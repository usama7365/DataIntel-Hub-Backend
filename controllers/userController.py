from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import hashlib
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from models.userModel import User
from utils.jwtToken import create_access_token
from utils.sendEmail import send_email
from middleware.error import ErrorHandler

load_dotenv()

class UserController:
    def __init__(self):
        pass
    
    async def register_user(self, user_data: Dict[str, Any]) -> JSONResponse:
        """
        Register a new user
        """
        try:
            # Create user
            user = await User.create(**user_data)
            
            # Generate JWT token
            token = create_access_token(data={"id": str(user.id)})
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "User registered successfully",
                    "user": user.to_dict(),
                    "token": token
                }
            )
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def verify_email(self, token: str) -> JSONResponse:
        """
        Verify user email with token
        """
        try:
            verify_email_token = hashlib.sha256(token.encode()).hexdigest()
            
            # Find user with verification token
            user = await User.find_one({
                "verify_email_token": verify_email_token,
                "verify_email_expire": {"$gt": datetime.utcnow()}
            })
            
            if not user:
                raise ErrorHandler("Invalid or expired email verification token", 400)
            
            # Update user verification status
            user.is_verified = True
            user.verify_email_token = None
            user.verify_email_expire = None
            await user.save()
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Email verified successfully"
                }
            )
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def resend_verification_email(self, email_data: Dict[str, Any]) -> JSONResponse:
        """
        Resend verification email
        """
        try:
            email = email_data.get("email")
            if not email:
                raise ErrorHandler("Email is required", 400)
            
            # Find user
            user = await User.find_one({"email": email})
            if not user:
                raise ErrorHandler("User not found", 404)
            
            if user.is_verified:
                raise ErrorHandler("User has already been verified", 400)
            
            # Generate new verification token
            verify_token = user.get_verify_email()
            await user.save()
            
            # Send verification email
            verify_email_url = f"{os.getenv('FRONTEND_URL')}/EmailVerification/{verify_token}"
            message = f"Your email verification token is: \n\n {verify_email_url} \n\n If you have not requested this email then, please ignore it"
            
            try:
                await send_email({
                    "email": user.email,
                    "subject": "Data Intel Hub Email verification",
                    "message": message
                })
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": f"Verification email sent to {user.email} successfully"
                    }
                )
            except Exception as error:
                user.verify_email_token = None
                user.verify_email_expire = None
                await user.save()
                raise ErrorHandler(str(error), 500)
                
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def login_user(self, login_data: Dict[str, Any]) -> JSONResponse:
        """
        Login user
        """
        try:
            email = login_data.get("email")
            password = login_data.get("password")
            
            if not email or not password:
                raise ErrorHandler("Please Enter Email and Password", 400)
            
            # Find user with password
            user = await User.find_one({"email": email})
            if not user:
                raise ErrorHandler("Invalid Email or Password", 401)
            
            # Check password
            if not await user.compare_password(password):
                raise ErrorHandler("Invalid Email or Password", 401)
            
            # Generate token
            token = create_access_token(data={"id": str(user.id)})
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Login success",
                    "user": user.to_dict(),
                    "token": token
                }
            )
            
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def logout(self) -> JSONResponse:
        """
        Logout user
        """
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Logged out successfully"
            }
        )
    
    async def forgot_password(self, email_data: Dict[str, Any]) -> JSONResponse:
        """
        Send forgot password email
        """
        try:
            email = email_data.get("email")
            if not email:
                raise ErrorHandler("Email is required", 400)
            
            user = await User.find_one({"email": email})
            if not user:
                raise ErrorHandler("User not found", 404)
            
            # Generate reset token
            reset_token = user.get_reset_password_token()
            await user.save()
            
            # Send reset email
            reset_password_url = f"{os.getenv('FRONTEND_URL')}/reset-password/{reset_token}"
            message = f"Your password reset token is: \n\n {reset_password_url} \n\n If you have not requested this email then, please ignore it"
            
            try:
                await send_email({
                    "email": user.email,
                    "subject": "DataIntel Hub Password Recovery",
                    "message": message
                })
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": f"Email sent to {user.email} successfully"
                    }
                )
            except Exception as error:
                user.reset_password_token = None
                user.reset_password_expire = None
                await user.save()
                raise ErrorHandler(str(error), 500)
                
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def reset_password(self, token: str, password_data: Dict[str, Any]) -> JSONResponse:
        """
        Reset password with token
        """
        try:
            reset_password_token = hashlib.sha256(token.encode()).hexdigest()
            
            user = await User.find_one({
                "reset_password_token": reset_password_token,
                "reset_password_expire": {"$gt": datetime.utcnow()}
            })
            
            if not user:
                raise ErrorHandler("Reset Password Token is invalid or has been expired", 400)
            
            # Update password
            new_password = password_data.get("password")
            if not new_password:
                raise ErrorHandler("New password is required", 400)
            
            user.password = new_password
            user.reset_password_token = None
            user.reset_password_expire = None
            await user.save()
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Password updated successfully"
                }
            )
            
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_user_details(self, user_id: str) -> JSONResponse:
        """
        Get user details
        """
        try:
            user = await User.find_one({"_id": user_id})
            if not user:
                raise ErrorHandler("User not found", 404)
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "user": user.to_dict()
                }
            )
            
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> JSONResponse:
        """
        Update user profile
        """
        try:
            user = await User.find_one({"_id": user_id})
            if not user:
                raise ErrorHandler("User not found", 404)
            
            # Update user fields
            for field, value in user_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            await user.save()
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "User updated successfully",
                    "user": user.to_dict()
                }
            )
            
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_password(self, user_id: str, password_data: Dict[str, Any]) -> JSONResponse:
        """
        Update user password
        """
        try:
            user = await User.find_one({"_id": user_id})
            if not user:
                raise ErrorHandler("User not found", 404)
            
            old_password = password_data.get("oldPassword")
            new_password = password_data.get("newPassword")
            
            if not old_password or not new_password:
                raise ErrorHandler("Old and new passwords are required", 400)
            
            # Check old password
            if not await user.compare_password(old_password):
                raise ErrorHandler("Old password is incorrect", 400)
            
            # Update password
            user.password = new_password
            await user.save()
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Password updated successfully"
                }
            )
            
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_all_users(self, admin_id: str) -> JSONResponse:
        """
        Get all users (admin only)
        """
        try:
            # Check if user is admin (you can implement admin check logic here)
            admin_user = await User.find_one({"_id": admin_id})
            if not admin_user or not admin_user.is_admin:
                raise ErrorHandler("Access denied. Admin privileges required.", 403)
            
            users = await User.find_all()
            users_list = [user.to_dict() for user in users]
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "users": users_list
                }
            )
            
        except Exception as e:
            if isinstance(e, ErrorHandler):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            raise HTTPException(status_code=500, detail=str(e)) 