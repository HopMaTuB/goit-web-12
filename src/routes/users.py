from typing import List

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session

from src.configuration.database import get_db
from src.configuration.models import User
from src.repository.auth import create_access_token,Hash
from src.schemas import UserModel
from src.repository.users import UserService,UsernameToken


router = APIRouter(prefix='/users',tags = ['users'])
hash_handler = Hash()
user_service = UserService()

@router.post("/signup")
async def signup(body: UserModel, db: Session = Depends(get_db)):
    try:
        user_service.check_user_available(body.username,db)
    except UsernameToken:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    new_user = User(email=body.username, password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"new_user": new_user.email}