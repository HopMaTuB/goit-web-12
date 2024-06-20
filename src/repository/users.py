from src.schemas import UserModel
from src.repository.auth import create_access_token,Hash
from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status
from src.configuration.models import User

hash_handler = Hash()


class UsernameToken(Exception):
    pass


class UserService:

    @staticmethod
    def check_user_available(username: str, db: Session):
        exist_user = db.query(User).filter(User.email == username).first()
        if exist_user:
            raise UsernameToken
        
    @staticmethod
    def create_new_user(body:UserModel, db: Session):
        UserService.check_user_available(username=body.username, db=Session)
        new_user = User(email=body.username,password=hash_handler.get_password_hash(body.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


