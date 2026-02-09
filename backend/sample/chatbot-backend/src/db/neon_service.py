import os
import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class NeonDBService:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            # Raise an error immediately if configuration is missing
            raise ValueError("DATABASE_URL environment variable is not set")
        self.pool = None

    # Renamed from init_pool to initialize_pool to match main.py's assumed call
    async def initialize_pool(self):
        """Initialize pool with a retry for the serverless wake-up delay"""
        import asyncio
    
    # Use the connection string from .env
        dsn = self.connection_string
    
        for attempt in range(3):
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=dsn,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
            
                # Give Neon a moment to stabilize the session
                await asyncio.sleep(1) 
            
                # Test the connection before running heavy CREATE TABLE commands
                async with self.pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                
                # Now run the table creation
                await self.create_tables()
                print("NeonDB connection pool initialized successfully")
                return
            
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if self.pool:
                    await self.pool.close()
                if attempt < 2:
                    await asyncio.sleep(2) # Wait 2 seconds before retrying
                else:
                    raise e

    async def close_pool(self):
        """Close the connection pool gracefully"""
        if self.pool:
            await self.pool.close()
            print("NeonDB connection pool closed.")

    async def create_tables(self):
        """Create required tables for chat sessions, user credentials, and refresh tokens"""
        # CRITICAL CHECK: Ensure pool exists before acquiring a connection
        if not self.pool:
            raise RuntimeError("Database pool not initialized before table creation.")

        async with self.pool.acquire() as conn:
            # 1. Create users table (Assuming full_name, disabled were optional fields in Pydantic models)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    full_name VARCHAR(255),  
                    disabled BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Create refresh_tokens table (CRITICAL FOR AUTH)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    token_hash CHAR(64) PRIMARY KEY, -- SHA-256 hash of the token
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_revoked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Create chat_sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    session_title VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Create chat_messages table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for better performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)")


    # --- User Methods ---

# src/db/neon_service.py

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
    # Emergency check: if pool is None, try to initialize it now
        if self.pool is None:
            await self.initialize_pool()

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, username, password_hash, email, created_at FROM users WHERE username = $1",
                username
            )
            return dict(row) if row else None

    async def create_user(self, username: str, password_hash: str, email: Optional[str] = None, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user with safety check"""
        if not self.pool:
            await self.initialize_pool()

        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO users (username, password_hash, email, full_name)
                VALUES ($1, $2, $3, $4)
                RETURNING id, username, email, full_name, created_at, updated_at
                """,
                username, password_hash, email, full_name
            )
            return dict(result)

    async def update_user_password(self, username: str, new_password_hash: str):
        """Update user's password"""
        async with self.pool.acquire() as conn:
            # Returns 'UPDATE 1' on success
            return await conn.execute(
                """
                UPDATE users
                SET password_hash = $1, updated_at = CURRENT_TIMESTAMP
                WHERE username = $2
                """,
                new_password_hash, username
            )

    # --- Refresh Token Methods (CRITICAL NEW METHODS) ---

    async def store_refresh_token(self, token_hash: str, user_id: int, expires_at: datetime):
        """Store the hash of the refresh token in the database."""
        async with self.pool.acquire() as conn:
            # Use ON CONFLICT DO UPDATE to handle potential hash collisions or token replacement
            await conn.execute(
                """
                INSERT INTO refresh_tokens (token_hash, user_id, expires_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (token_hash) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    expires_at = EXCLUDED.expires_at,
                    is_revoked = FALSE,
                    created_at = CURRENT_TIMESTAMP
                """,
                token_hash, user_id, expires_at
            )

    async def get_valid_refresh_token(self, token_hash: str) -> Optional[Dict[str, Any]]:
        """Check if the refresh token hash exists, is not revoked, and is not expired."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT token_hash, user_id, expires_at
                FROM refresh_tokens
                WHERE token_hash = $1 
                  AND is_revoked = FALSE
                  AND expires_at > CURRENT_TIMESTAMP
                """,
                token_hash
            )
            return dict(row) if row else None

    async def revoke_refresh_token(self, token_hash: str) -> bool:
        """Mark a refresh token hash as revoked."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE refresh_tokens
                SET is_revoked = TRUE
                WHERE token_hash = $1 AND is_revoked = FALSE
                """,
                token_hash
            )
            # The result string will be 'UPDATE 1' if a row was updated, 'UPDATE 0' otherwise
            return result == 'UPDATE 1'

    # --- Chat Session Methods (Remaining methods unchanged, except for adding self before self.pool) ---

    async def create_chat_session(self, user_id: int, session_title: str = None) -> Dict[str, Any]:
        """Create a new chat session"""
        async with self.pool.acquire() as conn:
            # ... (SQL unchanged)
            result = await conn.fetchrow(
                """
                INSERT INTO chat_sessions (user_id, session_title)
                VALUES ($1, $2)
                RETURNING id, user_id, session_title, created_at
                """,
                user_id, session_title
            )
            return dict(result)

    async def add_chat_message(self, session_id: int, user_id: int, role: str, content: str) -> Dict[str, Any]:
        """Add a chat message to a session"""
        async with self.pool.acquire() as conn:
            # ... (SQL unchanged)
            result = await conn.fetchrow(
                """
                INSERT INTO chat_messages (session_id, user_id, role, content)
                VALUES ($1, $2, $3, $4)
                RETURNING id, session_id, user_id, role, content, timestamp
                """,
                session_id, user_id, role, content
            )
            return dict(result)

    async def get_chat_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a chat session by ID"""
        async with self.pool.acquire() as conn:
            # ... (SQL unchanged)
            row = await conn.fetchrow(
                "SELECT id, user_id, session_title, created_at FROM chat_sessions WHERE id = $1",
                session_id
            )
            return dict(row) if row else None

    async def get_chat_messages_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """Get all messages for a chat session"""
        async with self.pool.acquire() as conn:
            # ... (SQL unchanged)
            rows = await conn.fetch(
                """
                SELECT id, session_id, user_id, role, content, timestamp
                FROM chat_messages
                WHERE session_id = $1
                ORDER BY timestamp ASC
                """,
                session_id
            )
            return [dict(row) for row in rows]


    async def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user"""
        async with self.pool.acquire() as conn:
            # ... (SQL unchanged)
            rows = await conn.fetch(
                """
                SELECT id, user_id, session_title, created_at, updated_at
                FROM chat_sessions
                WHERE user_id = $1
                ORDER BY updated_at DESC
                """,
                user_id
            )
            return [dict(row) for row in rows]

    async def update_session_title(self, session_id: int, title: str):
        """Update the title of a chat session"""
        async with self.pool.acquire() as conn:
            # ... (SQL unchanged)
            await conn.execute(
                """
                UPDATE chat_sessions
                SET session_title = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
                """,
                title, session_id
            )

    async def update_user_email(self, username: str, new_email: str):
        """Update user's email"""
        async with self.pool.acquire() as conn:
            # ... (SQL unchanged)
            await conn.execute(
                """
                UPDATE users
                SET email = $1, updated_at = CURRENT_TIMESTAMP
                WHERE username = $2
                """,
                new_email, username
            )

# Global instance
neon_db_service = NeonDBService()