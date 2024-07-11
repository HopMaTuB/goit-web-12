from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from starlette import status
from settings import SECRET_KEY,ALGORITHM

from src.configuration.database import get_db
from src.configuration.models import User
from settings import oauth2_scheme


class Hash:
    """
    A class for handling password hashing.

    Attributes
    ----------
    pwd_context : CryptContext
        The context for hashing passwords, using bcrypt.

    Methods
    -------
    verify_password(plain_password, hashed_password):
        Verifies if the provided password matches the hashed password.
    get_password_hash(password):
        Returns the hashed version of the provided password.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the provided password matches the hashed password.

        Parameters
        ----------
        plain_password : str
            The password provided by the user.
        hashed_password : str
            The hashed password stored in the database.

        Returns
        -------
        bool
            True if the passwords match, otherwise False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Returns the hashed version of the provided password.

        Parameters
        ----------
        password : str
            The password provided by the user.

        Returns
        -------
        str
            The hashed password.
        """
        return self.pwd_context.hash(password)



# define a function to generate a new access token
def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Generates a new JWT token.

    Parameters
    ----------
    data : dict
        The data to be encoded in the token.
    expires_delta : Optional[float]
        The time in seconds until the token expires.

    Returns
    -------
    str
        The generated JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current user from the token.

    Parameters
    ----------
    token : str
        The JWT token.
    db : Session
        The database session.

    Returns
    -------
    User
        The current user.

    Raises
    ------
    HTTPException
        If the token is invalid or the user is not found.
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        if email is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
