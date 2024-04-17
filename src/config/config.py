import os
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT


# from decouple import config
load_dotenv()
class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    SMS_91_URL = "https://control.msg91.com/api/v5/flow/"#os.getenv("SMS_91_URL", "")
    SMS_91_Template = "65639546d6fc05099a1278e2"#os.getenv("SMS_91_Template", "")
    SMS_91_AUTHKEY = "275109AN6j4BLdCwVF5ccd28c1"#os.getenv("SMS_91_AUTHKEY", "")
    OTP_SEND = "False" #os.getenv("OTP_SEND", "False")
    # RAZORPAY_KEY = "rzp_live_DpW6y2pUUDkdwF"
    # RAZORPAY_SECRET = "q77Vj9wCq58q1c0ihXtt3RAC"
    RAZORPAY_KEY = "rzp_test_C87xjgg0jqrh4M"
    RAZORPAY_SECRET = 'NnWJgAkURwQa0qjYGwDxeAiH'
    ACCESS_KEY = os.getenv("ACCESS_KEY", '')
    SECRET_KEY = os.getenv("SECRET_KEY")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    RAZORPAYX_URL = "https://api.razorpay.com/v1/payouts"
    ACCOUNT_NUMBER = "2323230029052161"
    FCM_API_URL = "https://fcm.googleapis.com/fcm/send"
    FCM_SERVER_KEY = "AAAAEzc69SY:APA91bFhJXvS7JQu-N7XhKes0yRVADOW3srS4lZnzPxT9aAr3liyQ99uJwo21haYqqxwT5QpK1nlQ7LneSsQbud0fjTdSZ1VXGNzHr5MBz7uuAGuuMxcnyjl5C-6kgr50x0KRncpC-UV"

conf = ConnectionConfig(
   MAIL_USERNAME = os.getenv("EMAIL", ''),
   MAIL_PASSWORD = os.getenv("PASSWORD", ''),
   MAIL_PORT = 587,
   MAIL_SERVER = "smtp.gmail.com",
   MAIL_STARTTLS = True,
   MAIL_SSL_TLS = False,
   USE_CREDENTIALS = True,
   VALIDATE_CERTS = True,
   MAIL_FROM = os.getenv("EMAIL", ''),
)

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

@AuthJWT.load_config
def get_config():
    return Settings()
