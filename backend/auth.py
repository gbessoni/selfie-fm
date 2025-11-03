"""
Authentication utilities for selfie.fm
Handles password hashing, JWT tokens, and session management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets

from database import get_db
from models import User

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# HTTP Bearer for JWT
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate to 72 bytes for bcrypt, handling UTF-8 properly
    password_bytes = plain_password.encode('utf-8')[:72]
    # Hash is stored as string, need to convert to bytes for bcrypt
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Truncate to 72 bytes for bcrypt, handling UTF-8 properly
    password_bytes = password.encode('utf-8')[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for storage
    return hashed.decode('utf-8')


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for at least one number
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    # Check for at least one letter
    if not any(char.isalpha() for char in password):
        return False, "Password must contain at least one letter"
    
    return True, ""


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    
    if not user.password_hash:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token (optional - returns None if not authenticated)"""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    username: str = payload.get("sub")
    if not username:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user


def get_current_user_required(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token (required - raises exception if not authenticated)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def verify_user_access(current_user: User, username: str) -> None:
    """Verify that the current user has access to the specified username's resources"""
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )


def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from session cookie (optional)"""
    token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    username: str = payload.get("sub")
    if not username:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user


def set_auth_cookie(response: Response, token: str, remember_me: bool = False) -> None:
    """Set authentication cookie in response"""
    max_age = 60 * 60 * 24 * 7 if remember_me else None  # 7 days if remember_me, else session
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=max_age,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )


def clear_auth_cookie(response: Response) -> None:
    """Clear authentication cookie"""
    response.delete_cookie(key="access_token")


# Rate limiting storage (simple in-memory for MVP)
login_attempts = {}


def check_rate_limit(email: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """
    Check if user has exceeded rate limit for login attempts
    Returns True if within limit, False if exceeded
    """
    now = datetime.utcnow()
    
    if email in login_attempts:
        attempts, first_attempt = login_attempts[email]
        
        # Reset if window has passed
        if now - first_attempt > timedelta(minutes=window_minutes):
            login_attempts[email] = (1, now)
            return True
        
        # Check if exceeded
        if attempts >= max_attempts:
            return False
        
        # Increment attempts
        login_attempts[email] = (attempts + 1, first_attempt)
    else:
        login_attempts[email] = (1, now)
    
    return True


def reset_rate_limit(email: str) -> None:
    """Reset rate limit for a user (called on successful login)"""
    if email in login_attempts:
        del login_attempts[email]
