import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import User
from services.auth_service import register_user, authenticate_user, hash_password, verify_password

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_password_hashing():
    pwd = "SecretPassword123!"
    h1 = hash_password(pwd)
    assert h1 != pwd
    assert verify_password(pwd, h1) is True
    assert verify_password("WrongPwd", h1) is False


def test_user_registration(db_session):
    success, msg, user = register_user(db_session, "Alice Legal", "alice@example.com", "Password123", "Password123")
    assert success is True
    assert user is not None
    assert user.email == "alice@example.com"
    assert user.name == "Alice Legal"


def test_duplicate_registration(db_session):
    register_user(db_session, "Alice Legal", "alice@example.com", "Password123", "Password123")
    success, msg, user = register_user(db_session, "Alice Copy", "alice@example.com", "Password123", "Password123")
    assert success is False
    assert "already exists" in msg


def test_password_mismatch(db_session):
    success, msg, user = register_user(db_session, "Bob Legal", "bob@example.com", "Password123", "DifferentPwd")
    assert success is False
    assert "do not match" in msg


def test_authentication(db_session):
    register_user(db_session, "Charlie", "charlie@example.com", "MySecret123", "MySecret123")
    
    # Valid auth
    success, msg, user = authenticate_user(db_session, "charlie@example.com", "MySecret123")
    assert success is True
    assert user.email == "charlie@example.com"

    # Invalid auth
    success, msg, user = authenticate_user(db_session, "charlie@example.com", "BadPassword")
    assert success is False
    assert user is None
