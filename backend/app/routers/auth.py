from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.auth import authenticate_user, create_access_token, get_current_user, get_current_active_user
from app.database import db
from app.models.user import UserCreate, UserResponse, UserInDB, Token

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and get access token",
    description="Authenticate a user with username and password, returning a JWT access token for subsequent authenticated requests.",
    tags=["Authentication"]
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user with username/password and return JWT access token.
    
    Args:
        form_data: OAuth2PasswordRequestForm containing username and password
        
    Raises:
        HTTPException: 401 if credentials are invalid
        
    Returns:
        Token: JWT access token with bearer type
    """
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    
    logger.info(f"User '{form_data.username}' logged in successfully")
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (Admin only)",
    description="Create a new user account. Only existing authenticated users can register new users.",
    tags=["Authentication"]
)
async def register(
    user_data: UserCreate,
    current_user = Depends(get_current_user)
):
    """
    Create a new user account.
    
    Args:
        user_data: UserCreate model containing user details and password
        current_user: The currently authenticated user (from token)
        
    Raises:
        HTTPException: 409 if username or email already exists
        
    Returns:
        UserResponse: The created user data (without password)
    """
    users_collection = db.get_collection("users")
    
    # Check if username already exists
    existing_user = await users_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_data.username}' already exists"
        )
    
    # Check if email already exists
    existing_email = await users_collection.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_data.email}' already registered"
        )
    
    # Hash the password
    from app.auth import get_password_hash
    hashed_password = get_password_hash(user_data.password)
    
    # Create user document
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    
    # Insert into database
    result = await users_collection.insert_one(user_dict)
    
    logger.info(f"New user '{user_data.username}' registered by '{current_user.get('username')}'")
    
    # Return user response without password
    return UserResponse(
        username=user_data.username,
        email=user_data.email,
        is_active=user_data.is_active,
        created_at=user_dict["created_at"]
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve the profile information of the currently authenticated user.",
    tags=["Authentication"]
)
async def get_me(current_user = Depends(get_current_active_user)):
    """
    Get current authenticated user profile.
    
    Args:
        current_user: The currently authenticated active user (from token)
        
    Returns:
        UserResponse: The current user's profile data
    """
    created_at = current_user.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    
    return UserResponse(
        username=current_user["username"],
        email=current_user["email"],
        is_active=current_user.get("is_active", True),
        created_at=created_at or datetime.utcnow()
    )
