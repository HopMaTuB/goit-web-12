from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from settings import conf
from src.services.auth import auth_service


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send an email for email verification.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The recipient's username.
        host (str): The host URL for generating the verification link.

    Returns:
        None
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


