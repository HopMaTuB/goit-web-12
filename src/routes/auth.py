from fastapi import (
    APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request,UploadFile, File
)
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from fastapi_mail import MessageSchema,FastMail,MessageType

from src.configuration.models import User
from src.configuration.database import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail,UserDb,UserDisplayModel
from src.repository.users import UserService 
from src.services.auth import auth_service
from src.services.email import send_email
from settings import limiter,conf

import cloudinary
import cloudinary.uploader

from src.repository import users as repository_users



router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse,response_model_include={'email','detail'}, status_code=status.HTTP_201_CREATED)
@limiter.limit('1/minute')
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = UserService.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = UserService.create_new_user(body, db)
    background_tasks.add_task(send_email, new_user.email,new_user.username, request.base_url)
    return new_user


@router.post("/login", response_model=TokenModel)
@limiter.limit('1/minute')
async def login(request: Request, body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = UserService.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    UserService.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = auth_service.decode_refresh_token(token)
    user = UserService.get_user_by_email(email, db)
    if user.refresh_token != token:
        UserService.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = auth_service.create_access_token(data={"sub": email})
    refresh_token = auth_service.create_refresh_token(data={"sub": email})
    UserService.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = UserService.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    UserService.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = UserService.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    

@router.post("/send_test_email")
@limiter.limit('1/minute')
async def send_test_email(request : Request ,email_to_send: str, background_tasks: BackgroundTasks):
    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=[email_to_send],
        template_body={"fullname": "Billy Jones"},
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message,template_name='example_template.html')
    return {"message": "email has been sent"}

@router.patch('/avatar', response_model=UserDisplayModel)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    user = UserService.update_avatar(current_user,file,db)
    return user