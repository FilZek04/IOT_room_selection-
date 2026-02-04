from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class Token(BaseModel):
    """
    JWT token response model.
    
    Returned after successful authentication.
    """
    access_token: str = Field(..., description="JWT access token string")
    token_type: str = Field(default="bearer", description="Token type, typically 'bearer'")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """
    Token payload data extracted from JWT.
    
    Used for decoding and validating access tokens.
    """
    username: Optional[str] = Field(None, description="Username from token payload")
    scopes: Optional[list] = Field(None, description="List of permission scopes")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "scopes": ["read:rooms", "write:bookings"]
            }
        }


class UserBase(BaseModel):
    """
    Base user model with common fields.
    
    Contains fields shared across all user-related models.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., description="User email address")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    created_at: Optional[datetime] = Field(default=None, description="Account creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "is_active": True,
                "created_at": "2024-12-22T14:30:00Z"
            }
        }


class UserCreate(UserBase):
    """
    User registration model with password.
    
    Extends UserBase with password field and validation.
    """
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength requirements.
        
        Password must:
        - Be at least 8 characters
        - Contain at least one uppercase letter
        - Contain at least one lowercase letter
        - Contain at least one digit
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "is_active": True,
                "created_at": "2024-12-22T14:30:00Z",
                "password": "SecurePass123"
            }
        }


class UserInDB(UserBase):
    """
    User model as stored in database.
    
    Includes hashed password and MongoDB-specific fields.
    """
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    id: Optional[str] = Field(default=None, description="MongoDB ObjectId as string")

    def to_mongo_dict(self) -> dict:
        """
        Convert model to MongoDB-compatible dictionary.
        
        - Excludes the 'id' field (MongoDB uses '_id')
        - Converts datetime objects to ISO format strings
        - Handles ObjectId if present
        
        Returns:
            Dictionary ready for MongoDB insertion
        """
        data = self.model_dump(exclude={'id'})
        
        # Convert datetime to ISO format string for MongoDB
        if data.get('created_at'):
            if isinstance(data['created_at'], datetime):
                data['created_at'] = data['created_at'].isoformat()
        
        # Convert id to ObjectId if present
        if self.id:
            data['_id'] = ObjectId(self.id)
        
        return data

    @classmethod
    def from_mongo(cls, doc: dict) -> "UserInDB":
        """
        Create UserInDB instance from MongoDB document.
        
        Args:
            doc: MongoDB document dictionary
            
        Returns:
            UserInDB instance with id converted to string
        """
        if not doc:
            raise ValueError("Document cannot be None")
        
        data = dict(doc)
        
        # Convert _id to id
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        
        # Parse datetime strings back to datetime objects
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        return cls(**data)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "username": "john_doe",
                "email": "john.doe@example.com",
                "is_active": True,
                "created_at": "2024-12-22T14:30:00Z",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G"
            }
        }


class UserResponse(BaseModel):
    """
    Safe user response model without password.
    
    Returned in API responses to avoid exposing sensitive data.
    """
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="User email address")
    is_active: bool = Field(..., description="Whether the user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "is_active": True,
                "created_at": "2024-12-22T14:30:00Z"
            }
        }
    }


class UserLogin(BaseModel):
    """
    User login credentials.
    
    Used for authentication requests.
    """
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "SecurePass123"
            }
        }
