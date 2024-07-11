from datetime import datetime, timedelta
from jose import  jwt
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from settings import SECRET_KEY,ALGORITHM, oauth2_scheme


from src.configuration.database import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = SECRET_KEY
    ALGORITHM = ALGORITHM
    

    def verify_password(self, plain_password, hashed_password):
        """
        Verify if the provided plain password matches the hashed password.

        Args:
            plain_password (str): The plain text password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash the provided password.

        Args:
            password (str): The plain text password.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a new access token.

        Args:
            data (dict): The data to encode in the token.
            expires_delta (Optional[float]): The expiration time of the token in seconds.

        Returns:
            str: The encoded JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=150)
        to_encode.update({"iat": datetime.now(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a new refresh token.

        Args:
            data (dict): The data to encode in the token.
            expires_delta (Optional[float]): The expiration time of the token in seconds.

        Returns:
            str: The encoded JWT refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(days=7)
        to_encode.update({"iat": datetime.now(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode the provided refresh token.

        Args:
            refresh_token (str): The refresh token to decode.

        Returns:
            str: The email from the token's payload.

        Raises:
            HTTPException: If the token is invalid or has an incorrect scope.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Get the current user from the provided token.

        Args:
            token (str): The JWT access token.
            db (Session): The database session.

        Returns:
            User: The authenticated user.

        Raises:
            HTTPException: If the token is invalid or the user does not exist.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = repository_users.UserService.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        Create a token for email verification.

        Args:
            data (dict): The data to encode in the token.

        Returns:
            str: The encoded email token.
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=7)
        to_encode.update({"iat": datetime.now(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
      """
        Get the email from the provided token.

        Args:
            token (str): The email verification token.

        Returns:
            str: The email from the token's payload.

        Raises:
            HTTPException: If the token is invalid.
        """
      try:
          payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
          email = payload["sub"]
          return email
      except JWTError as e:
          print(e)
          raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                              detail="Invalid token for email verification")
                
auth_service = Auth()
