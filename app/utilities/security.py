from pwdlib import PasswordHash
from datetime import timedelta, datetime, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated, TYPE_CHECKING
from fastapi import Depends, HTTPException, status, Request

if TYPE_CHECKING:
    from app.dependencies.session import SessionDep

from app.config import get_settings
from app.models.user import User
from sqlmodel import select
from fastapi.security import OAuth2PasswordBearer


password_hash = PasswordHash.recommended()

def encrypt_password(password:str):
    return password_hash.hash(password)

def verify_password(plaintext_password:str, encrypted_password):
    print("\n\n\n\n\n\n\n\n")
    print(len(password_hash.hashers))
    print(password_hash.hashers)
    print("\n\n\n\n\n\n\n\n")
    return password_hash.verify(password=plaintext_password, hash=encrypted_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=get_settings().jwt_access_token_expires)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().secret_key, algorithm=get_settings().jwt_algorithm)
    return encoded_jwt

async def get_current_user(request:Request, db:"SessionDep")->User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth_header = request.headers.get("Authorization")
    auth_cookie = request.cookies.get("access_token")

    token = None
    if auth_header and auth_header.startswith("Bearer "): # Regular auth
        token = auth_header.split(" ")[1]
    elif auth_cookie: # Web auth
        token = auth_cookie.split(" ")[1]
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[get_settings().jwt_algorithm])
        user_id = int(payload.get("sub",None))
    except InvalidTokenError:
        raise credentials_exception
    user = db.get(User,user_id)

    if user is None:
        raise credentials_exception
    return user

async def is_logged_in(request: Request, db:"SessionDep"):
    try:
        await get_current_user(request, db)
        return True
    except Exception as e:
        print(e)
        return False

IsUserLoggedIn = Annotated[bool, Depends(is_logged_in)]
AuthDep = Annotated[User, Depends(get_current_user)]

async def is_admin(user: User):
    return user.role == "admin"

async def is_admin_dep(user: AuthDep):
    if not await is_admin(user):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to access this page",
            )
    return user

AdminDep = Annotated[User, Depends(is_admin_dep)]