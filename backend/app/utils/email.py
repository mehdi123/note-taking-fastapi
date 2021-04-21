from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List
from fastapi.templating import Jinja2Templates

from app.core.config import (MAIL_USERNAME,
                            MAIL_PASSWORD, 
                            MAIL_FROM, 
                            MAIL_SERVER)


templates = Jinja2Templates("./app/templates")


conf = ConnectionConfig(
    MAIL_USERNAME = str(MAIL_USERNAME),
    MAIL_PASSWORD = str(MAIL_PASSWORD),
    MAIL_FROM = str(MAIL_FROM),
    MAIL_PORT = 587,
    MAIL_SERVER = str(MAIL_SERVER),
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)


async def send_email_task(message: MessageSchema, conf: ConnectionConfig) -> None:
    fm = FastMail(conf)
    await fm.send_message(message)
    
async def send_email(email: List[EmailStr], 
                    verification_link: str, 
                    background_tasks: BackgroundTasks) -> None:

    #TODO remove the print
    # it is printed in case the email credentials has not been sent

    print(verification_link)
    message = MessageSchema(
        subject="Email Verification",
        recipients=email,  # List of recipients
        body=templates.get_template('verification-email.html').render(verification_link=verification_link),
        subtype="html"
    )
    # sending the email is added to the background tasks.
    background_tasks.add_task(send_email_task, message, conf)