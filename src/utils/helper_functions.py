import base64,os,boto3,uuid
from passlib.context import CryptContext
from fastapi import HTTPException,status
import smtplib, json, requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from src.config.config import conf
from fastapi_mail import FastMail, MessageSchema,MessageType
from src.services.notification.schema import NotificationSchema
from src.utils.common_html import send_email_html
from src.config.config import Config

async def convert_password(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash_password = pwd_context.hash(password)
    return hash_password

async def check_password(db_password,request_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    verify_pwd = pwd_context.verify(secret=request_password,hash=db_password)
    return verify_pwd

async def jwt_requiered(Authorize):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Token')
    
async def send_verification_mail(email, link):
    try:
        verification_message_template = send_email_html.format(
            link = link
        )

        message = MessageSchema(
            subject="Verify Your Email Address",
            recipients=[email],  # List of recipients, as many as you can pass
            body=verification_message_template,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return True
    except Exception as e:
        print(e)
        return False

async def send_mail_notification(notification_data, email):
    try:
        message = MessageSchema(
            subject=notification_data["title"],
            recipients=[email],  # List of recipients, as many as you can pass  
            body=notification_data["body"],
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return True
    except Exception as e:
        print(e)
        return False
   
async def send_otp(mobile, otp):
    url = Config.SMS_91_URL

    payload = {
        "template_id": Config.SMS_91_Template,
        "short_url": "0",
        "recipients": [
            {
                "mobiles": "91" + mobile,
                "var1": otp
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": Config.SMS_91_AUTHKEY
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False

def send_email_with_attachment( subject, sender_email, receiver_email, body, attachment_filename, attachment_name, smtp_username, smtp_password):
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        with open(attachment_filename, 'rb') as attachment:
            part = MIMEApplication(attachment.read(), Name=attachment_name)
            part['Content-Disposition'] = f'attachment; filename={attachment_name}'
            message.attach(part)

        # Connect to the SMTP server and send the email
        smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server
        smtp_port = 587  # Replace with your SMTP port

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, str(smtp_password))
            server.sendmail(sender_email, receiver_email, message.as_string())
            print('Email sent successfully!')

class S3Config:

    def upload_file(file_obj, object_name=None):
        """Upload a file to an S3 bucket

        :param s3_client: S3 Client
        :param file_obj: File to upload
        :param bucket: Bucket to upload to
        :param folder: Folder to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        ACCESS_KEY = Config.ACCESS_KEY
        SECRET_KEY = Config.SECRET_KEY
        S3_BUCKET_NAME = Config.S3_BUCKET_NAME
        # region_name=config('AWS_DEFAULT_REGION'), 

        s3_client = boto3.client("s3", 
                    aws_access_key_id=ACCESS_KEY, 
                    aws_secret_access_key=SECRET_KEY)
        # If S3 object_name was not specified, use file_name

        if object_name is None:
            object_name = file_obj
        try:
            s3_client.upload_file(file_obj, S3_BUCKET_NAME, f"media/{object_name}",ExtraArgs = {
                "ContentType": 'image/jpeg',
                'ACL':'public-read'
            })
        except Exception as e:
            print("printing exception")
            print(e)
            return False
        return True
    
    def img_conversion(img_data,object_name=None,file_path:str=None):
        decode_data = base64.b64decode(img_data)
        img_file = open('./image.jpeg','wb')
        img_file.write(decode_data)
        img_file.close()
        if object_name is None:
            object_name=f'{uuid.uuid4()}.jpg'
        if file_path:
            file_location = f"{file_path}/{object_name}"
        else:
            file_location = object_name
        S3Config.upload_file(file_obj='./image.jpeg',object_name=file_location)
        os.remove('./image.jpeg')

async def razorpay_payout(amount, user_data):
    if user_data.is_bank_account_verified:
        url = Config.RAZORPAYX_URL

        payload = json.dumps({
            "account_number": Config.ACCOUNT_NUMBER,
            "amount": int(amount * 100), # in paise
            "currency": "INR",
            "mode": "IMPS",
            "purpose": "payout",
            "fund_account": {
                "account_type": "bank_account",
                "bank_account": {
                    "name": user_data.bank_name,
                    "ifsc": user_data.ifsc_code,
                    "account_number": user_data.account_number
                },
                "contact": {
                    "name": user_data.name,
                    "email": user_data.email,
                    "contact": user_data.mobile,
                    "type": "employee",
                    "notes": {
                        "user_id": str(user_data.user_id)
                    }
                }
            },
            "queue_if_low_balance": True
        })
        print(payload)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic cnpwX3Rlc3RfQzg3eGpnZzBqcXJoNE06Tm5XSmdBa1VSd1FhMHFqWUd3RHhlQWlI'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response)
        if response.status_code == 200:
            return True
        else:
            return False
    else:
        return False

async def send_notification(user_id, data, notification_id):

    user_device = await NotificationSchema.get_device_token_of_user(
        user_id=user_id
    )
    headers = {
        "Authorization": f"key={Config.FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }

    for token in user_device:
        payload = {
            "to": token[0],
            "notification": {
                "title": data["title"],
                "body": data["body"],
                "click_action": "FLUTTER_NOTIFICATION_CLICK",  # Adjust for your client application
            }
        }

        try:
            response = requests.post(Config.FCM_API_URL, json=payload, headers=headers, timeout=1.5)
            if response.status_code == 200:
                data = response.json()
                if data["success"] == 0 and data["failure"] == 1:
                    print("Unable to send notification")
                else:
                    print("Notification sended successfully")
                    await NotificationSchema.update_notification(notification_id=notification_id)
            else:
                print("Unable to send notification")
        except:
            print("Not able to call firebase")
    return True
