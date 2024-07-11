from src.schemas import UserModel
from src.repository.auth import Hash, create_access_token
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.configuration.models import User
from typing import Optional,Union,Dict
from fastapi import UploadFile
from src.utils.cloudinary import upload_file_to_cloudinary

hash_handler = Hash()


class UsernameToken(Exception):
    """Exception raised when the username is already taken."""
    pass

class Wrongpassword(Exception):
    """Exception raised when the password is incorrect."""
    pass

class LoginFailed(Exception):
    """Exception raised when login fails."""
    pass 


class UserService:
    """
    Service class for handling user-related operations.
    """

    @staticmethod
    def get_user(username: str, db: Session) -> Optional[User]:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user.
            db (Session): The database session.

        Returns:
            Optional[User]: The user object if found, else None.
        """
        user = db.query(User).filter(User.email == username).first()
        return user


    @staticmethod
    def check_user_available(username: str, db: Session):
        """
        Check if a user with the given username already exists.

        Args:
            username (str): The username to check.
            db (Session): The database session.

        Raises:
            UsernameToken: If a user with the given username already exists.
        """
        exist_user = UserService.get_user(username,db)
        if exist_user:
            raise UsernameToken
        
    @staticmethod
    def create_new_user(body:UserModel, db: Session) -> Optional[Dict]:
        """
        Create a new user.

        Args:
            body (UserModel): The user data.
            db (Session): The database session.

        Returns:
            Optional[Dict]: The newly created user object.
        """
        UserService.check_user_available(username=body.email, db=db)
        new_user = User(username=body.username,email=body.email,password=hash_handler.get_password_hash(body.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    
    @staticmethod
    def check_password(entered_password: str, database_password: str):
        """
        Check if the entered password matches the database password.

        Args:
            entered_password (str): The entered password.
            database_password (str): The password stored in the database.

        Raises:
            Wrongpassword: If the passwords do not match.
        """
        if not hash_handler.verify_password(entered_password, database_password):
            raise Wrongpassword
        
    @staticmethod
    def login_user(body: OAuth2PasswordRequestForm, db: Session):
        """
        Authenticate a user and generate an access token.

        Args:
            body (OAuth2PasswordRequestForm): The login form data.
            db (Session): The database session.

        Returns:
            str: The access token.

        Raises:
            LoginFailed: If login fails.
        """
        user = UserService.get_user(body.username ,db = db)
        if user is None or not hash_handler.verify_password(body.password, user.password):
            raise LoginFailed
        
        access_token = create_access_token(data={"sub": user.email})
        return access_token
    
    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User:
        """
        Retrieve a user by their email.

        Args:
            email (str): The email of the user.
            db (Session): The database session.

        Returns:
            User: The user object.
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def confirmed_email(email: str, db: Session) -> None:
        """
        Confirm the email of a user.

        Args:
            email (str): The email to confirm.
            db (Session): The database session.
        """
        user = UserService.get_user_by_email(email, db)
        user.confirmed = True
        db.commit()

    def update_token(user: User, token: Union[str, None], db: Session) -> None:
        """
        Update the refresh token of a user.

        Args:
            user (User): The user object.
            token (Union[str, None]): The new refresh token.
            db (Session): The database session.
        """
        user.refresh_token = token
        db.commit()

    @staticmethod
    def save_user(user_to_save: User, db: Session) -> User:
        """
        Save the user to the database.

        Args:
            user_to_save (User): The user object to save.
            db (Session): The database session.

        Returns:
            User: The saved user object.
        """
        db.add(user_to_save)
        db.commit()
        db.refresh(user_to_save)
        return user_to_save

    @staticmethod
    def update_avatar(user: User, file: UploadFile,db: Session):
        """
        Update the avatar of a user.

        Args:
            user (User): The user object.
            file (UploadFile): The uploaded file object.
            db (Session): The database session.

        Returns:
            User: The updated user object with the new avatar.
        """
        user.avatar = upload_file_to_cloudinary(file.file, f'user_avatar{user.id}')
        UserService.save_user(user,db)
        return user



    


