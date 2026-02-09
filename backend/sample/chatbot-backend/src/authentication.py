from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

# Assuming your imports are correct
from .db.neon_service import neon_db_service

load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer()

# JWT configuration from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# --- Pydantic Models ---

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    password_hash: str
    created_at: datetime = None
    updated_at: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

# --- Utility Functions ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt"""
    # Use the context to hash. passlib handles the 72-char limit, 
    # but ensure we are passing a string, not an object.
    return pwd_context.hash(password)

def hash_token(token: str) -> str:
    """Hashes a token using SHA-256 for secure database storage."""
    # We hash the token before storing it to protect against token leakage
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

# --- Database Interaction (Uses neon_db_service) ---

async def get_user_by_username(username: str) -> Optional[UserInDB]:
    """Get a user from the Neon database by username"""

    user_record = await neon_db_service.get_user_by_username(username)
    if user_record:
        return UserInDB(
            id=user_record['id'],
            username=user_record['username'],
            email=user_record['email'],
            # Use .get() and defaults for optional/boolean fields
            full_name=user_record.get('full_name'), 
            disabled=user_record.get('disabled', False),
            password_hash=user_record['password_hash'],
            created_at=user_record['created_at'],
            updated_at=user_record.get('updated_at')
        )
    return None

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password using Neon DB"""
    user_in_db = await get_user_by_username(username)
    if not user_in_db:
        return None

    # CRITICAL FIX: Use the password verification function
    if not verify_password(password, user_in_db.password_hash):
        return None

    return User(
        id=user_in_db.id,
        username=user_in_db.username,
        email=user_in_db.email,
        full_name=user_in_db.full_name,
        disabled=user_in_db.disabled
    )

# --- JWT Token Generation ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a refresh token (also a JWT)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Token Verification and Dependency Injection ---

def verify_token(token: str) -> Optional[TokenData]:
    """Verify a JWT access token and return the token data"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception
            
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    return token_data

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get the current user from the JWT access token"""
    token_data = verify_token(credentials.credentials)
    
    user = await get_user_by_username(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
        
    # Return the Pydantic User model
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user (checks if disabled)"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- Refresh Token Management (Database Backed) ---

async def create_user_token(username: str,) -> Token:
    """Create access/refresh tokens, storing the refresh token HASH in Neon DB."""

    
    # 1. Get User ID
    user = await get_user_by_username(username)
    if not user or user.id is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_id = user.id

    # 2. Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "user_id": user_id}, expires_delta=access_token_expires
    )

    # 3. Create refresh token
    refresh_token = create_refresh_token(data={"sub": username, "user_id": user_id})
    token_hash = hash_token(refresh_token)
    
    # 4. Calculate expiration time for storage
    refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # 5. Store refresh token HASH in the Neon DB
    try:
        await neon_db_service.store_refresh_token(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=refresh_token_expires_at
        )
    except Exception as e:
        print(f"Error storing refresh token in DB: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not store token securely.")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

async def refresh_access_token(refresh_token: str) -> Optional[Token]:
    """Refresh an access token using a refresh token by checking DB validity."""
    
    token_hash = hash_token(refresh_token)
    
    # 1. Check if refresh token exists, is not revoked, and is not expired in the DB
    try:
        # This method in neon_db_service should ensure the token is active and unexpired
        token_record = await neon_db_service.get_valid_refresh_token(token_hash)
    except Exception as e:
        print(f"DB Error during token refresh: {e}")
        return None

    if not token_record:
        return None

    # 2. Immediately revoke the old token in the DB to prevent reuse (One-time use)
    await neon_db_service.revoke_refresh_token(token_hash)

    # 3. Decode the original JWT to get user data for the new tokens
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None or payload.get("type") != "refresh":
            return None 
    except JWTError:
        return None # Invalid JWT signature/format

    # 4. Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": username, "user_id": user_id}, expires_delta=access_token_expires
    )

    # 5. Create new refresh token and hash
    new_refresh_token = create_refresh_token(data={"sub": username, "user_id": user_id})
    new_token_hash = hash_token(new_refresh_token)

    # 6. Calculate new expiration and store new token HASH
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    await neon_db_service.store_refresh_token(
        token_hash=new_token_hash,
        user_id=user_id,
        expires_at=new_expires_at
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

async def revoke_refresh_token(refresh_token: str) -> bool:
    """Revoke a refresh token in the Neon DB."""
    token_hash = hash_token(refresh_token)
    
    try:
        success = await neon_db_service.revoke_refresh_token(token_hash)
        return success 
    except Exception as e:
        print(f"Error revoking refresh token in DB: {e}")
        return False

# For backward compatibility with existing code
async def get_current_user_legacy(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Legacy function for backward compatibility. Uses get_current_user logic."""
    return await get_current_user(credentials)