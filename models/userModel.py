from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import bcrypt
import os
import uuid
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

load_dotenv()

# MongoDB connection
MONGO_URI = "mongodb+srv://shuaib:shuaib123@cluster0.3ka8vsg.mongodb.net/data-intel-hub"
client = AsyncIOMotorClient(MONGO_URI)
db = client.data_intel_hub
users_collection = db.users

class UserBase(BaseModel):
    """Base user model"""
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    role: str = Field(default="user", description="User's role")

class UserCreate(UserBase):
    """Model for creating a new user"""
    pass

class UserUpdate(BaseModel):
    """Model for updating user information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    """Model for user response"""
    id: str
    first_name: str
    last_name: str
    email: str
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User:
    """
    User model with authentication methods using MongoDB
    """
    
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id')
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')
        self.role = kwargs.get('role', 'user')
        self.is_verified = kwargs.get('is_verified', False)
        self.reset_password_token = kwargs.get('reset_password_token')
        self.reset_password_expire = kwargs.get('reset_password_expire')
        self.verify_email_token = kwargs.get('verify_email_token')
        self.verify_email_expire = kwargs.get('verify_email_expire')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.is_admin = kwargs.get('is_admin', False)
    
    @classmethod
    async def create(cls, **kwargs):
        """Create a new user"""
        # Generate UUID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        # Hash password
        if 'password' in kwargs:
            kwargs['password'] = cls._hash_password(kwargs['password'])
        
        # Set timestamps
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        
        # Create user instance
        user = cls(**kwargs)
        
        # Prepare data for MongoDB (keep datetime objects for MongoDB)
        user_dict = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "password": user.password,
            "role": user.role,
            "is_verified": user.is_verified,
            "is_admin": user.is_admin,
            "reset_password_token": user.reset_password_token,
            "reset_password_expire": user.reset_password_expire,
            "verify_email_token": user.verify_email_token,
            "verify_email_expire": user.verify_email_expire,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
        # Save to MongoDB
        result = await users_collection.insert_one(user_dict)
        user._id = result.inserted_id
        
        return user
    
    @classmethod
    async def find_one(cls, query: Dict[str, Any]):
        """Find a user by query"""
        # Convert string ID to ObjectId if needed
        if '_id' in query and isinstance(query['_id'], str):
            try:
                query['_id'] = ObjectId(query['_id'])
            except:
                pass
        
        user_data = await users_collection.find_one(query)
        if user_data:
            return cls(**user_data)
        return None
    
    @classmethod
    async def find_all(cls):
        """Find all users"""
        users = []
        cursor = users_collection.find({})
        async for user_data in cursor:
            users.append(cls(**user_data))
        return users
    
    async def save(self):
        """Save user to database"""
        self.updated_at = datetime.utcnow()
        
        # Convert to dict and remove _id for update
        user_dict = self.to_dict()
        user_dict['updated_at'] = self.updated_at
        
        # Update in MongoDB
        await users_collection.update_one(
            {"_id": self._id},
            {"$set": user_dict}
        )
        return self
    
    def get_jwt_token(self) -> str:
        """Generate JWT token for user"""
        from utils.jwtToken import create_access_token
        return create_access_token(data={"id": str(self.id)})
    
    async def compare_password(self, entered_password: str) -> bool:
        """Compare entered password with stored password"""
        return bcrypt.checkpw(
            entered_password.encode('utf-8'),
            self.password.encode('utf-8')
        )
    
    def get_reset_password_token(self) -> str:
        """Generate password reset token"""
        # Generate token
        reset_token = secrets.token_hex(20)
        
        # Hash token
        self.reset_password_token = hashlib.sha256(
            reset_token.encode()
        ).hexdigest()
        
        # Set expiration (15 minutes)
        self.reset_password_expire = datetime.utcnow() + timedelta(minutes=15)
        
        return reset_token
    
    def get_verify_email(self) -> str:
        """Generate email verification token"""
        # Generate token
        verify_token = secrets.token_hex(20)
        
        # Hash token
        self.verify_email_token = hashlib.sha256(
            verify_token.encode()
        ).hexdigest()
        
        # Set expiration (24 hours)
        self.verify_email_expire = datetime.utcnow() + timedelta(hours=24)
        
        return verify_token
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON response"""
        return {
            "id": str(self.id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "reset_password_token": self.reset_password_token,
            "reset_password_expire": self.reset_password_expire.isoformat() if self.reset_password_expire else None,
            "verify_email_token": self.verify_email_token,
            "verify_email_expire": self.verify_email_expire.isoformat() if self.verify_email_expire else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8') 