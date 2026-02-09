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
from db import get_session
from models import User as UserModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import bcrypt
# Fix for passlib compatibility with bcrypt 4.0+
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (), {"__version__": bcrypt.__version__})
load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer()

# JWT configuration from environment variables
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-super-secret-jwt-key-change-in-production")
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
    user_id: Optional[str] = None

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    password_hash: Optional[str] = None
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
    """Hash a plain password using bcrypt with a safety check for length"""
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
        
    # Bcrypt limit is 72 bytes. We truncate or reject. 
    # For a Todo app, rejecting is safer than silent truncation.
    if len(password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=400, 
            detail="Password is too long. Maximum length is 72 characters."
        )
        
    return pwd_context.hash(password)
def hash_token(token: str) -> str:
    """Hashes a token using SHA-256 for secure database storage."""
    # We hash the token before storing it to protect against token leakage
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

# --- Database Interaction ---

async def get_user_by_username(session: AsyncSession, username: str) -> Optional[UserInDB]:
    """Get a user from the database by username"""
    statement = select(UserModel).where(UserModel.username == username)


    result = await session.execute(statement)
    user_record = result.scalars().first()

    if user_record:
        return UserInDB(
            id=user_record.id,
            username=user_record.username,
            email=user_record.email,
            full_name=user_record.full_name,
            disabled=user_record.is_active is False,  # Inverted logic: is_active=False means disabled
            password_hash=user_record.hashed_password,
            created_at=user_record.created_at,
            updated_at=user_record.updated_at
        )
    return None

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UserInDB]:
    """Get a user from the database by email"""
    statement = select(UserModel).where(UserModel.email == email)
    result = await session.execute(statement)
    user_record = result.scalars().first()

    if user_record:
        return UserInDB(
            id=user_record.id,
            username=user_record.username,
            email=user_record.email,
            full_name=user_record.full_name,
            disabled=user_record.is_active is False,
            password_hash=user_record.hashed_password,
            created_at=user_record.created_at,
            updated_at=user_record.updated_at
        )
    return None

async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[UserInDB]:
    """Get a user from the database by ID"""
    statement = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(statement)
    user_record = result.scalars().first()

    if user_record:
        return UserInDB(
            id=user_record.id,
            username=user_record.username,
            email=user_record.email,
            full_name=user_record.full_name,
            disabled=user_record.is_active is False,
            password_hash=user_record.hashed_password,
            created_at=user_record.created_at,
            updated_at=user_record.updated_at
        )
    return None

async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password"""
    user_in_db = await get_user_by_username(session, username)
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

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify JWT token and extract user_id
    Returns the user_id from the token
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Token contains: sub=username, user_id=actual_user_id
        # We need the user_id for database lookups
        user_id: str = payload.get("user_id") or payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: AsyncSession = Depends(get_session)) -> User:
    """Get the current user from the JWT access token"""
    token_data = verify_token(credentials.credentials)

    user = await get_user_by_username(session, token_data.username)
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

async def store_refresh_token(session: AsyncSession, token_hash: str, user_id: str, expires_at: datetime):
    """Store the hash of the refresh token in the database."""
    from models import RefreshToken as RefreshTokenModel
    if expires_at.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=None)
    
    refresh_token = RefreshTokenModel(
        token_hash=token_hash,
        user_id=user_id,
        expires_at=expires_at,
        created_at=datetime.utcnow() # Use naive UTC
    )
    session.add(refresh_token)
    await session.commit()


async def get_valid_refresh_token(session: AsyncSession, token_hash: str):
    """Check if the refresh token hash exists, is not revoked, and is not expired."""
    from models import RefreshToken as RefreshTokenModel
    from sqlmodel import select

    statement = select(RefreshTokenModel).where(
        RefreshTokenModel.token_hash == token_hash,
        RefreshTokenModel.is_revoked == False,
        RefreshTokenModel.expires_at > datetime.utcnow()
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def revoke_refresh_token(session: AsyncSession, token_hash: str) -> bool:
    """Mark a refresh token hash as revoked."""
    from models import RefreshToken as RefreshTokenModel
    from sqlmodel import select

    statement = select(RefreshTokenModel).where(
        RefreshTokenModel.token_hash == token_hash,
        RefreshTokenModel.is_revoked == False
    )
    result = await session.execute(statement)
    token = result.scalars().first()

    if token:
        token.is_revoked = True
        await session.commit()
        return True
    return False


async def create_user_token(username: str, session: AsyncSession = Depends(get_session)) -> Token:
    """Create access/refresh tokens, storing the refresh token HASH in database."""

    # 1. Get User ID
    user = await get_user_by_username(session, username)
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

    # 5. Store refresh token HASH in the database
    try:
        await store_refresh_token(session, token_hash, user_id, refresh_token_expires_at)
    except Exception as e:
        print(f"Error storing refresh token in DB: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not store token securely.")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# --- Google OAuth Functions ---

def get_google_oauth_url():
    """Generate Google OAuth authorization URL"""
    import urllib.parse

    # Get Google OAuth credentials from environment
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/google/callback")

    if not google_client_id:
        raise ValueError("GOOGLE_CLIENT_ID not configured in environment")

    # Google OAuth URL
    params = {
        "client_id": google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return auth_url


async def verify_google_token(code: str):
    """Exchange Google OAuth code for user info"""
    import httpx
    import urllib.parse

    # Get Google OAuth credentials from environment
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/google/callback")

    if not google_client_id or not google_client_secret:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be configured in environment")

    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()

        # Get user info using the access token
        access_token = token_info.get("access_token")
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        return user_info