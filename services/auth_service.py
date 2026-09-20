import re
import hashlib
import os
import secrets
from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session
from database.models import User

try:
    import bcrypt
    USE_BCRYPT = True
except ImportError:
    USE_BCRYPT = False


def hash_password(password: str) -> str:
    """Secure password hashing using bcrypt or salted SHA-256 fallback."""
    if USE_BCRYPT:
        # bcrypt has 72 byte limit for secret
        pwd_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')
    else:
        salt = secrets.token_hex(16)
        salted_pwd = (password + salt).encode('utf-8')
        pwd_hash = hashlib.sha256(salted_pwd).hexdigest()
        return f"pbkdf2_sha256${salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    if not plain_password or not hashed_password:
        return False
    if USE_BCRYPT and hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        try:
            pwd_bytes = plain_password.encode('utf-8')[:72]
            hash_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            _, salt, pwd_hash = hashed_password.split("$")
            salted_pwd = (plain_password + salt).encode('utf-8')
            check_hash = hashlib.sha256(salted_pwd).hexdigest()
            return secrets.compare_digest(check_hash, pwd_hash)
        except Exception:
            return False
    return False



def validate_email(email: str) -> bool:
    """Check if email matches standard pattern."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password strength criteria."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, "Valid password"


def register_user(db: Session, name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[User]]:
    """Register a new user account with complete validation."""
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    confirm_password = confirm_password or ""

    if not name:
        return False, "Full Name is required.", None
    if not email:
        return False, "Email address is required.", None
    if not validate_email(email):
        return False, "Invalid email address format.", None
    if not password:
        return False, "Password is required.", None
    if password != confirm_password:
        return False, "Passwords do not match.", None

    is_strong, msg = validate_password_strength(password)
    if not is_strong:
        return False, msg, None

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return False, "An account with this email already exists.", None

    pwd_hash = hash_password(password)
    new_user = User(
        name=name,
        email=email,
        password_hash=pwd_hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return True, "Registration successful! You can now log in.", new_user


def authenticate_user(db: Session, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """Authenticate user credentials."""
    email = (email or "").strip().lower()
    password = password or ""

    if not email or not password:
        return False, "Email and password are required.", None

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False, "Invalid email or password.", None

    if not verify_password(password, user.password_hash):
        return False, "Invalid email or password.", None

    return True, "Authentication successful.", user
