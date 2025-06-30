from fastapi import Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.models.user import User
from src.core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(request: Request, db: Session):
    token = await oauth2_scheme(request)
    user = verify_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

async def role_required(role: str):
    def role_checker(current_user: User):
        if role not in current_user.roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
    return role_checker