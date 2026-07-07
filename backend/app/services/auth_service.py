from app.core.security import hash_password, verify_password
from app.repositories.users import create_user, get_user_by_username


def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def register_user(username: str, password: str):
    return create_user(username, hash_password(password))
