import pytest
from pydantic import ValidationError

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.schemas.review import ReviewCreate


def test_password_hashing_and_verification():
    hashed = hash_password("DemoPass@123")
    assert hashed != "DemoPass@123"
    assert verify_password("DemoPass@123", hashed)
    assert not verify_password("WrongPass@123", hashed)


def test_jwt_contains_subject_and_role():
    token = create_access_token("42", "customer")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "customer"


def test_review_validation_blocks_invalid_rating_and_empty_comment():
    with pytest.raises(ValidationError):
        ReviewCreate(rating=6, comment="Good service")
    with pytest.raises(ValidationError):
        ReviewCreate(rating=5, comment="")
