#Third Party Imports
from datetime import datetime, timedelta
import time
import uuid,logging
from fastapi import status
from pydantic import UUID4
from src.db.models import (
    TransactionStatusEnum, 
    TransactionTypeEnum,
)
from src.services.contest.schema import DraftSchema
from src.services.notification.schema import NotificationSchema
#Local Imports
from src.utils.constant import (
    NotificationConstant, 
    UserConstant
)
from src.utils.helper_functions import (
    convert_password, 
    check_password,
    S3Config, 
    razorpay_payout, 
    send_mail_notification, 
    send_notification
)
from src.utils.jwt import auth_check
from fastapi.responses import HTMLResponse
from src.config.config import Config
from src.utils.helper_functions import (
    convert_password,
    check_password,
    S3Config,
    send_verification_mail)

from src.utils.common_html import verify_email_html

from src.utils.response import (
    SuccessResponseSerializer,
    ErrorResponseSerializer,
    response_structure
)
from src.services.user.serializer import (
    AddAmountRequestSerializer,
    CityRequestSerializer,
    CityResponseSerializer,
    CountryResponseSerializer,
    OTPResponseSerializer,
    StateRequestSerializer,
    StateResponseSerializer,
    TransactionResponseSerializer,
    UserLoginRegisterRequestSerializer,
    PanVerificationResponseSerializer,
    UserLoginRegisterResponseSerializer,
    OTPRequestSerializer,
    BankRequestSerializer,
    PanRequestSerializer,
    BankResponseSerializer,
    OTPRequestSerializer,
    UserProfileRequestSerailizer,
    UserProfileResponseSerializer,
    BalanceResponseSerializer,
    ListAnySerializer,
    RequestEmailVerificationSerializer
)
from src.services.user.schema import (
    UserSchema,
    UserProfileSchema
)
from src.services.admin.schema import (
    AdminSchema
)

#Logger Configration
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
# FORMAT = "%(levelname)s:%(message)s"
# logging.basicConfig(format=FORMAT, level=logging.DEBUG)

class UserController:

    @classmethod
    async def login_register(cls, request:UserLoginRegisterRequestSerializer):
        """
        """
        data = await  UserSchema.update_email_mobile_otp_data(
            mobile = request.mobile
        )
        data = UserLoginRegisterResponseSerializer(
            mobile=request.mobile,
            mobile_otp_id=data["mobile_otp_id"]
        )
        serializer = SuccessResponseSerializer(
            message=UserConstant.SUCCESS_EMAIL_PHONE_STORE,
            status_code=status.HTTP_200_OK,
            data=data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def verify_otp(cls, request:OTPRequestSerializer, authorize):
        """
        """
        mobile_data = await UserSchema.get_mobile_otp_verify(
            mobile_otp_id = request.mobile_otp_id,
            otp = request.otp
        )
        if not mobile_data:
            logger.error("Mobile_id otp is not match.Please Check proper!")
            serializer = ErrorResponseSerializer(
                message=UserConstant.ERROR_MOBILE_OTP_NOT_MATCH
            )
            return response_structure(
                serializer=serializer,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user_data = await UserProfileSchema.get_user_data(mobile=mobile_data.mobile)
        
        if user_data:
            already_user = True
        else:
            already_user = False
            user_data = await UserProfileSchema.create_user(
                mobile=mobile_data.mobile
            )
        
        access_token = authorize.create_access_token(subject=str(user_data.user_id),expires_time=3600)
        refresh_token = authorize.create_refresh_token(subject=str(user_data.user_id),expires_time=False)
    
        data = OTPResponseSerializer(
            already_user=already_user,
            user_id=str(user_data.user_id),
            access_token=access_token,
            refresh_token=refresh_token
        )
        serializer = SuccessResponseSerializer(
            message=UserConstant.SUCCESS_USER_REGISTRATION,
            status_code=status.HTTP_201_CREATED,
            data = data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_201_CREATED
        )

    @classmethod
    async def refresh_token(cls, authorize):
        """
        The function `refresh_token` is used to generate a new access token for a user based on their
        refresh token, and returns a success response with the new access token or an error response if
        the token is invalid.
        
        :param cls: The parameter `cls` refers to the class itself. In this case, it is a class method
        :param authorize: The `authorize` parameter is an instance of a class that handles authorization
        and authentication. It provides methods for validating and creating access tokens and refresh
        tokens
        :return: The code is returning either a SuccessResponseSerializer or an ErrorResponseSerializer.
        """
        try:
            authorize.jwt_refresh_token_required()
            raw_jwt = authorize.get_raw_jwt()
            current_user = raw_jwt["sub"]
            new_access_token = authorize.create_access_token(subject=str(current_user))
            serializer =  SuccessResponseSerializer(
                message=UserConstant.NEW_TOKEN_GENERATED,
                data=new_access_token
            )
            return response_structure(
                serializer=serializer,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            serializer = ErrorResponseSerializer(
                message=UserConstant.INVALID_TOKEN,
                data=""
            )
            return response_structure(
                serializer=serializer,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @classmethod
    async def email_verify(cls, user_id, email):
        update_data = {
            "email": email,
            "is_email_verified" : True
        }
        await UserProfileSchema.update_user_data(
            user_id=user_id,
            update_data=update_data
        )
        return HTMLResponse(content=verify_email_html)

    @classmethod
    async def send_verification_email(cls,token, request: RequestEmailVerificationSerializer, authorize):
        await auth_check(authorize=authorize, token=token)
        user_id = authorize.get_jwt_subject()

        email_data = await UserSchema.check_email(
            email = request.email
        )
        if not email_data:
            link = f"{Config.BACKEND_URL}/v1/user/email_verify/{request.email}/{user_id}"

            success = await send_verification_mail(
                email = request.email,
                link = link
            )

            if success:
                serializer = SuccessResponseSerializer(
                    message = "Verification email sended"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_200_OK
                )
            else:
                serializer = ErrorResponseSerializer(
                    message = "Verification email not sended",
                    status_code = status.HTTP_400_BAD_REQUEST
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )
        else:
            serializer = ErrorResponseSerializer(
                message = "Email Already Exist",
                status_code = status.HTTP_207_MULTI_STATUS
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_207_MULTI_STATUS
            )

class UserProfileController:

    @classmethod
    async def get_country(cls):
        country_data = await UserProfileSchema.get_country()
        country_data = [CountryResponseSerializer(**(i.__dict__)) for i in country_data]
        serializer = SuccessResponseSerializer(
            message="Country Data",
            data=country_data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def get_state(cls, request: StateRequestSerializer):
        state_data = await UserProfileSchema.get_state(country = request.country)
        if not state_data:
            serializer = SuccessResponseSerializer(
                message=UserConstant.NO_DATA_FOUND
            )
        else:
            state_data = {"data": [StateResponseSerializer(**(i._asdict())) for i in state_data]}
            data = ListAnySerializer(**state_data).data
            serializer = SuccessResponseSerializer(
                message=UserConstant.ALL_STATE_DATA,
                status_code=status.HTTP_200_OK,
                data=data
            )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )


    @classmethod
    async def get_city(cls, request: CityRequestSerializer):
        city_data = await UserProfileSchema.get_city(state = request.state)
        if not city_data:
            serializer = SuccessResponseSerializer(
                message=UserConstant.NO_DATA_FOUND
            )
        else:
            city_data = {"data": [CityResponseSerializer(**(i._asdict())) for i in city_data]}
            data = ListAnySerializer(**city_data).data
            serializer = SuccessResponseSerializer(
                message=UserConstant.ALL_CITY_DATA,
                status_code=status.HTTP_200_OK,
                data=data
            )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def update_profile(cls,token,request:UserProfileRequestSerailizer,authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        if request and request.gender and request.gender not in ["Male", "Female", "Others"]:
            serializer = ErrorResponseSerializer(
                message = "Gender Can either of Male, Female or Others"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )
        update_data = request.dict(
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True
        )
        await UserProfileSchema.update_user_data(
            user_id=user_id,
            update_data=update_data
        )
        serializer = SuccessResponseSerializer(
            message=UserConstant.UPDATE_SUCCESS,
            status_code=status.HTTP_200_OK
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def get_profile(cls,token,authorize):
        # try:
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        user = await UserProfileSchema.get_user_data(
            user_id = user_id,
            with_base = True
        )
        if user:
            data = UserProfileResponseSerializer(**(user._asdict()))
        else:
            serializer = ErrorResponseSerializer(
                message=UserConstant.USER_NOT_FOUND,
                status_code=status.HTTP_400_BAD_REQUEST,
                data=''
            )
            return response_structure(
                serializer=serializer,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer = SuccessResponseSerializer(
            message=UserConstant.FETCH_ALL_SUCCESS,
            status_code=status.HTTP_200_OK,
            data=data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def pan_register(cls,token,request:PanRequestSerializer,authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        user_pan_data = await UserProfileSchema.pan_get(user_id = user_id)
        if user_pan_data:
            update_value = request.dict(
                exclude_none=True,
                exclude_unset=True,
                exclude_defaults=True
            )
            user_pan_data = await UserProfileSchema.pan_update(
                user_id=user_id,
                update_value=update_value
            )
            serializer = SuccessResponseSerializer(
                message="Pan Data Added",
                data = True
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            user_pan_data = await UserProfileSchema.pan_register(
                request=request,
                user_id=user_id
            )
            serializer = SuccessResponseSerializer(
                message="Pan Data Added",
                data = True
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        
    @classmethod
    async def pan_get(cls,token,authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        user_pan_data = await UserProfileSchema.pan_get(
            user_id = user_id
        )
        if user_pan_data:
            user_pan_data = PanVerificationResponseSerializer(**(user_pan_data.__dict__))
            serializer = SuccessResponseSerializer(
                status_code = status.HTTP_200_OK,
                message = UserConstant.PAN_DATA_GET,
                data = user_pan_data
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            serializer = ErrorResponseSerializer(
                status_code=status.HTTP_404_NOT_FOUND,
                message=UserConstant.PAN_DATA_NOT_EXIST,
                data = None
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )

    @classmethod
    async def bank_register(cls,token, request : BankRequestSerializer, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        user_bank_data = await UserProfileSchema.bank_get(user_id=user_id)
        if user_bank_data:
            update_value = request.dict(
                exclude_none=True,
                exclude_unset=True,
                exclude_defaults=True
            )
            user_bank_data = await UserProfileSchema.bank_update(
                user_id=user_id,
                update_value=update_value
            )

            serializer = SuccessResponseSerializer(
                message="Bank Data Added",
                data = True
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            user_pan_data = await UserProfileSchema.bank_register(
                request=request,
                user_id=user_id
            )
            serializer = SuccessResponseSerializer(
                message="Bank Data Added",
                data = True
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )

    @classmethod
    async def bank_get(cls,token,authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        user_bank_data = await UserProfileSchema.bank_get(
            user_id = user_id
        )
        if user_bank_data:
            user_bank_data = BankResponseSerializer(**(user_bank_data.__dict__))
            serializer = SuccessResponseSerializer(
                status_code = status.HTTP_200_OK,
                message = UserConstant.BANK_DATA_GET,
                data = user_bank_data
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            serializer = ErrorResponseSerializer(
                status_code=status.HTTP_404_NOT_FOUND,
                message=UserConstant.BANK_DATA_NOT_EXIST,
                data = None
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )
        
    @classmethod
    async def add_amount(cls, token, request: AddAmountRequestSerializer, authorize):
        await auth_check(token=token, authorize=authorize)
        user_id = authorize.get_jwt_subject()
        gst_list = await AdminSchema.get_gst()

        received_amount = round(request.amount, 2)
        gst_percentage = (gst_list[0].percentage) / 100
        added_amount = round(received_amount / (1 + gst_percentage), 0)
        cash_bonus_amount = received_amount - added_amount

        time.sleep(1)
        await UserProfileSchema.add_update_amount(
            added_amount=added_amount,
            cash_bonus_amount=cash_bonus_amount,
            user_id=user_id
        )
        ########### Add Money Notification and Mail for added amount
        user_data = await UserProfileSchema.get_user_data(
            user_id = user_id,
            with_base = True
        )
        notification_data = {
            "title": "Money Deposited",
            "body": NotificationConstant.MONEY_DEPOSITED.format(added_amount)
        }
        notification = await NotificationSchema.add_notification(
            user_id = user_id,
            message = notification_data["body"]
        )
        await send_notification(
            user_id = user_id,
            data = notification_data,
            notification_id = notification.notification_id
        )
        await send_mail_notification(
            notification_data = notification_data,
            email = user_data.email
        )
        ##############
        ########### Add Money Notification and Mail for cash bonus amount
        notification_data = {
            "title": "Money Bonus",
            "body": NotificationConstant.MONEY_BONUS.format(cash_bonus_amount)
        }
        notification = await NotificationSchema.add_notification(
            user_id = user_id,
            message = notification_data["body"]
        )
        await send_notification(
            user_id = user_id,
            data = notification_data,
            notification_id = notification.notification_id
        )
        await send_mail_notification(
            notification_data = notification_data,
            email = user_data.email
        )
        ##############
        await UserProfileSchema.add_gst_amount(
            user_id = user_id,
            added_amount= added_amount,
            cash_bonus_amount = cash_bonus_amount,
            received_amount = received_amount
        )

        serializer = SuccessResponseSerializer(
            status_code=status.HTTP_200_OK,
            message=UserConstant.SUCCESS_BALANCE_ADD,
            data=True
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def payout(cls, token, request: AddAmountRequestSerializer, authorize):
        await auth_check(token=token, authorize=authorize)
        user_id = authorize.get_jwt_subject()

        last_transaction = await UserProfileSchema.get_last_withdraw_transaction(
            user_id = user_id
        )

        if last_transaction:
            if datetime.now() - last_transaction.created_at < timedelta(hours = 24):
                serializer = ErrorResponseSerializer(
                    message = f"You can withdraw only once in 24 hours"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )

        user_balance = await UserProfileSchema.get_user_balance(user_id = user_id)
        received_amount = round(request.amount, 2)
        if received_amount > user_balance.winning_amount:
            serializer = ErrorResponseSerializer(
                message = f"Insufficient Balance"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )

        tds_list = await AdminSchema.get_tds()
        new_winning_amount = user_balance.winning_amount - received_amount
        new_amount = user_balance.amount - received_amount
        tds_value = round(received_amount * (tds_list[0].percentage) / 100, 2)
        amount = round(received_amount - tds_value, 2)

        user_data = await UserProfileSchema.get_user_data(
            user_id = user_id,
            with_base = True
        )
        check_payout = await razorpay_payout(
            amount = amount,
            user_data = user_data
        )

        ############
        if check_payout:
            ############ Withdraw Money Notification and Mail
            notification_data = {
                "title": "Money Withdraw",
                "body": NotificationConstant.MONEY_WITHDRAW.format(amount, tds_value)
            }
            notification = await NotificationSchema.add_notification(
                user_id = user_id,
                message = notification_data["body"]
            )
            await send_notification(
                user_id = user_id,
                data = notification_data,
                notification_id = notification.notification_id
            )
            await send_mail_notification(
                notification_data = notification_data,
                email = user_data.email
            )
            await UserProfileSchema.add_tds_amount(
                user_id = user_id,
                amount = amount,
                tds_value = tds_value,
                total = received_amount,
            )

            await UserProfileSchema.add_user_transaction(
                user_id = user_id,
                amount = received_amount,
                transaction_type = TransactionTypeEnum.WITHDRAW_MONEY,
                transaction_status = TransactionStatusEnum.COMPLETED
            )
            await UserProfileSchema.winning_payout(
                amount = new_amount,
                winning_amount = new_winning_amount,
                user_id = user_id
            )

            serializer = SuccessResponseSerializer(
                message = f"Your Payout is successful"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            serializer = ErrorResponseSerializer(
                message = f"In order to proceed with your withdrawal, please ensure that your complete address and bank details are updated in your profile under My Profile"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )

    @classmethod
    async def get_amount(cls,token, authorize):
        # try:
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        user_balance = await UserProfileSchema.get_user_balance(user_id = user_id)
        data = BalanceResponseSerializer(**(user_balance._asdict())) if user_balance else BalanceResponseSerializer()
        serializer = SuccessResponseSerializer(
            message=UserConstant.FETCH_ALL_AMOUNT,
            status_code=status.HTTP_200_OK, 
            data=data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def get_transaction(cls,token, authorize, limit, offset):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        user_transaction = await UserProfileSchema.get_user_transaction(
            user_id = user_id,
            limit=limit,
            offset=offset
        )
        data = []
        if user_transaction:
            for i in user_transaction:
                transaction = TransactionResponseSerializer(**i._asdict())
                transaction.created_at = transaction.created_at + timedelta(hours=5, minutes=30)
                if i.meta_data and "user_draft_id" in i.meta_data:
                    draft_data = await DraftSchema.get_draft_data(
                        user_draft_id = UUID4(i.meta_data["user_draft_id"])
                    )
                    if draft_data:
                        if transaction.transaction_type == TransactionTypeEnum.JOIN_CONTEST:
                            transaction.message = f'Deducted for Draft {draft_data.league_name}'
                        elif transaction.transaction_type == TransactionTypeEnum.WON_MONEY:
                            transaction.message = f'Won for Draft {draft_data.league_name}'
                        elif transaction.transaction_type == TransactionTypeEnum.CANCELLED_CONTEST:
                            transaction.message = f'Refund for Cancelled Draft {draft_data.league_name}'
                        else:
                            transaction.message = ''

                data.append(transaction)
        
        logger.info(" User's Show All Transaction")
        serializer = SuccessResponseSerializer(
            message=UserConstant.FETCH_ALL_TRANSACTION,
            status_code=status.HTTP_200_OK,
            data=data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )