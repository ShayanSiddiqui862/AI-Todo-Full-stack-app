from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict
import uuid

from db import get_session
from models import User as UserModel
from .service import REFRESH_TOKEN_EXPIRE_DAYS, UserCreate, UserLogin, Token
from .service import get_password_hash, verify_password, create_access_token, create_refresh_token, hash_token
from .service import get_user_by_username, authenticate_user
from .service import create_user_token, verify_jwt

router = APIRouter()

@router.post("/register", response_model=Dict[str, str])
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    # Check if user already exists by username
    existing_user_by_username = await get_user_by_username(session, user_data.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists"
        )

    # Check if user already exists by email
    from .service import get_user_by_email
    existing_user_by_email = await get_user_by_email(session, user_data.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_id = str(uuid.uuid4())
    user = UserModel(
        id=user_id,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=True  # Regular registration is verified
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Create tokens
    token = await create_user_token(user.username, session)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "token_type": token.token_type
    }


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, session: AsyncSession = Depends(get_session)):
    # Find user by username
    user = await authenticate_user(session, login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    token = await create_user_token(login_data.username, session)

    return token


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(refresh_data: Dict[str, str], session: AsyncSession = Depends(get_session)):
    from .service import get_valid_refresh_token, revoke_refresh_token, create_access_token, create_refresh_token, hash_token
    from jose import jwt
    from .service import SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS
    from datetime import timedelta
    import uuid

    refresh_token_str = refresh_data.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )

    token_hash = hash_token(refresh_token_str)

    # 1. Check if refresh token exists, is not revoked, and is not expired in the DB
    token_record = await get_valid_refresh_token(session, token_hash)

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # 2. Immediately revoke the old token in the DB to prevent reuse (One-time use)
    await revoke_refresh_token(session, token_hash)

    # 3. Decode the original JWT to get user data for the new tokens
    try:
        payload = jwt.decode(refresh_token_str, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")

        if username is None or user_id is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # 4. Create new access token
    access_token = create_access_token(
        data={"sub": username, "user_id": user_id},
        expires_delta=timedelta(minutes=1440)  # 24 hours
    )

    # 5. Create new refresh token and hash
    new_refresh_token = create_refresh_token(data={"sub": username, "user_id": user_id})
    new_token_hash = hash_token(new_refresh_token)

    # 6. Calculate new expiration and store new token HASH
    from datetime import datetime, timezone
    from .service import REFRESH_TOKEN_EXPIRE_DAYS
    # Use naive UTC to match your DB schema and avoid 'offset-aware' errors
    new_expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # Store new refresh token in DB
    from .service import store_refresh_token
    await store_refresh_token(session, new_token_hash, user_id, new_expires_at)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=1440 * 60  # 24 hours in seconds
    )


@router.post("/logout")
async def logout(refresh_request: Dict[str, str], session: AsyncSession = Depends(get_session)):
    """
    Revoke refresh token (logout).
    Expected payload: {"refresh_token": "your_refresh_token"}
    """
    from .service import hash_token, revoke_refresh_token

    refresh_token = refresh_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )

    # Revoke the refresh token
    success = await revoke_refresh_token(session, hash_token(refresh_token))

    if not success:
        # This can happen if the token is already revoked or doesn't exist.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already revoked refresh token"
        )

    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_profile(
    current_user_id: str = Depends(verify_jwt),
    session: AsyncSession = Depends(get_session)
):
    from .service import get_user_by_id
    user = await get_user_by_id(session, current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "id": user.id,
        "email": user.email,
        "name": user.full_name or user.username
    }


@router.get("/google")
async def google_auth_redirect():
    """Initiate Google OAuth flow"""
    from auth.service import get_google_oauth_url
    auth_url = get_google_oauth_url()
    return {"auth_url": auth_url}


@router.post("/google/callback")
async def google_auth_callback(request_data: dict, session: AsyncSession = Depends(get_session)):
    """Handle Google OAuth callback"""
    from auth.service import verify_google_token
    code = request_data.get("code")

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )

    try:
        user_info = await verify_google_token(code)

        # Check if user already exists by email
        from .service import get_user_by_email
        existing_user = await get_user_by_email(session, user_info['email'])

        if existing_user:
            # Check if the existing user has a NULL hashed_password in the database and update it
            # This is necessary to satisfy the database NOT NULL constraint
            from sqlmodel import select
            # Use the UserModel already imported at the top of the file
            raw_user = (await session.execute(select(UserModel).where(UserModel.email == user_info['email']))).scalar_one_or_none()
            if raw_user and raw_user.hashed_password is None:
                raw_user.hashed_password = ""
                session.add(raw_user)
                await session.commit()

            # Return tokens
            token = await create_user_token(existing_user.username, session)
            return {
                "message": "Login successful",
                "user_id": existing_user.id,
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_type": token.token_type
            }
        else:
            # Create new user from Google profile
            user_id = str(uuid.uuid4())
            user = UserModel(
                id=user_id,
                email=user_info['email'],
                username=user_info['email'].split('@')[0].lower(),  # Use part of email as username
                hashed_password="",  # Empty string for OAuth-only users
                full_name=user_info['name'],
                is_active=True,
                is_verified=True,  # Google verified email
                avatar_url=user_info.get('picture'),  # Store avatar if available
                oauth_provider='google'  # Mark as Google OAuth user
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            # Create tokens
            token = await create_user_token(user.username, session)
            return {
                "message": "Account created successfully",
                "user_id": user.id,
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_type": token.token_type
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )