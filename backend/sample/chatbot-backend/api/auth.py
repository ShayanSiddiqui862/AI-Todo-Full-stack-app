from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from datetime import datetime, timezone
import hashlib


from backend.src.authentication import (
    UserCreate,
    UserLogin,
    Token,
    User,
    create_user_token,
    refresh_access_token,
    revoke_refresh_token,
    get_current_active_user,
    authenticate_user,
    get_password_hash, # <-- NEW: Import the hash function
    verify_password,   # <-- NEW: Import verify password (if needed elsewhere)
    get_user_by_username # <-- NEW: Import for user checks
)
from src.db.neon_service import neon_db_service

router = APIRouter()

# --- Authentication Endpoints ---

@router.post("/auth/register", response_model=Token)
async def register_user(user_data: UserCreate):
    """
    Register a new user with username, email, and password.
    """
    try:
        # Check if user already exists in database using the dedicated service function
        existing_user = await get_user_by_username(user_data.username) 
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # 1. HASH the password before storing it
        password_hash = get_password_hash(user_data.password)

        # 2. Create the user in the database
        # NOTE: Your neon_db_service.create_user MUST accept password_hash
        created_user = await neon_db_service.create_user(
            username=user_data.username,
            password_hash=password_hash,
            email=user_data.email,
            full_name=user_data.full_name # Pass optional full_name
        )
        
        # Check if DB creation was successful and returned data with username
        if not created_user or 'username' not in created_user:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed in database"
            )

        # 3. Create and return token (will now store refresh token in DB)
        token = await create_user_token(created_user['username'])
        return token

    except HTTPException:
        raise
    except Exception as e:
        # Log the exception for debugging
        print(f"Registration Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error."
        )


@router.post("/auth/sign-in/username", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """
    Authenticate user and return access and refresh tokens.
    """
    try:
        # CRITICAL FIX: Use the authenticate_user function which handles password hashing check
        user = await authenticate_user(user_credentials.username, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user.disabled:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create and return token (will now store refresh token in DB)
        token = await create_user_token(user.username)
        return token

    except HTTPException:
        raise
    except Exception as e:
        # Log the exception for debugging
        print(f"Login Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error."
        )


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(refresh_request: dict):
    """
    Refresh access token using refresh token.
    Expected payload: {"refresh_token": "your_refresh_token"}
    """
    refresh_token = refresh_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )

    # NOTE: refresh_access_token is now async
    new_token = await refresh_access_token(refresh_token) 
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    return new_token


@router.post("/auth/logout")
async def logout_user(refresh_request: dict, current_user: User = Depends(get_current_active_user)):
    """
    Revoke refresh token (logout).
    Expected payload: {"refresh_token": "your_refresh_token"}
    """
    refresh_token = refresh_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )

    # NOTE: revoke_refresh_token is now async
    success = await revoke_refresh_token(refresh_token) 
    
    if not success:
        # This can happen if the token is already revoked or doesn't exist.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already revoked refresh token"
        )

    return {"message": "Successfully logged out"}


# api/auth.py

@router.get("/auth/get-session", response_model=User)
async def get_session(current_user: User = Depends(get_current_active_user)):
    """
    Better-Auth calls this endpoint to check if the user is still logged in.
    'get_current_active_user' will automatically look for the JWT in the 
    'Authorization: Bearer <token>' header.
    """
    return current_user


@router.post("/auth/change-password")
async def change_password(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Change user password.
    Expected payload: {"current_password": "old_password", "new_password": "new_password"}
    """
    try:
        # Get the request body
        body = await request.json()
        current_password = body.get("current_password")
        new_password = body.get("new_password")

        if not current_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both current_password and new_password are required"
            )

        # 1. Verify current password by attempting to authenticate the user
        user = await authenticate_user(current_user.username, current_password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # 2. HASH the new password before updating
        new_password_hash = get_password_hash(new_password)
        
        # 3. Update password in the database (assuming this method exists in your service)
        await neon_db_service.update_user_password(current_user.username, new_password_hash)

        return {"message": "Password updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        # Log the exception for debugging
        print(f"Password Change Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed due to server error."
        )