from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from src.configuration.database import get_db
from src.configuration.models import User
from src.repository.auth import Hash
from src.schemas import UserModel
from src.repository.users import UserService,UsernameToken,LoginFailed


router = APIRouter(prefix='/users',tags = ['users'])
hash_handler = Hash()
user_service = UserService()



@router.post("/signup",status_code=201)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    try:
        user_service.check_user_available(body.email,db)
    except UsernameToken:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    new_user = User(email=body.email, password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"new_user": new_user.email}


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        access_token = user_service.login_user(body,db)
    except LoginFailed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed")
    return {"access_token": access_token, "token_type": "bearer"}

