import random
import string
import uuid
from typing import List
from sqlalchemy import (
    func, 
    cast, 
    TEXT
)
from fastapi import Depends
from sqlalchemy import (
    select, 
    outerjoin,
    join, 
    or_
)
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import update
from fastapi_mail import (
    FastMail, 
    MessageSchema,
    MessageType
)
from datetime import datetime, timedelta, date
#Local Imports
from src.config.config import Config
from src.services.admin.schema import AdminSchema
from src.utils.helper_functions import (
    S3Config, 
    send_otp
)
from src.config.config import conf
from src.db.database import db
from src.db.models import (
    TdsCalculation,
    TransactionStatusEnum,
    TransactionTypeEnum,
    User,
    EmailOTP,
    BankVerification,
    MobileOTP,
    PanVerification,
    UserBalance,
    UserTransaction,
    MasterCity,MasterState,
    MasterCountry,
    GstCalculation
)
from src.utils.constant import UserConstant
from src.utils.helper_functions import S3Config
from src.services.user.serializer import (
    PanRequestSerializer,
    BankRequestSerializer
)

class UserSchema():
    
    @classmethod
    async def create_update_email_otp(cls, email, email_otp):
        email_data = await db.execute(
            select(
                EmailOTP
            ).where(
                EmailOTP.email==email
            )
        )
        email_data = email_data.scalars().one_or_none()
        if email_data:
            await db.execute(
                update(
                    EmailOTP
                ).where(
                    EmailOTP.email==email
                ).values({
                    'otp':email_otp
                }).execution_options(
                    synchronize_session="fetch"
                )
            )
        else:
            email_data = EmailOTP(
                email = email,
                otp = email_otp
            )
            db.add(email_data)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
        return email_data
    
    @classmethod
    async def create_update_mobile_otp(cls, mobile, mobile_otp):
        mobile_data = await db.execute(
            select(
                MobileOTP
            ).where(
                MobileOTP.mobile==mobile
            )
        )
        mobile_data = mobile_data.scalars().one_or_none()
        if mobile_data:
            await db.execute(
                update(
                    MobileOTP
                ).where(
                    MobileOTP.mobile==mobile
                ).values({
                    "otp":mobile_otp
                }).execution_options(
                    synchronize_session="fetch"
                )
            )
        else:
            mobile_data = MobileOTP(
                mobile = mobile,
                otp = mobile_otp
            )
            db.add(mobile_data)
        try:
            await db.commit()
        except Exception as e:
            print(e)
            await db.rollback()
        return mobile_data
    
    @classmethod
    async def update_email_mobile_otp_data(cls, email=None, mobile=None):

        email_otp = '123456'
        mobile_otp = '123456'
        if Config.OTP_SEND == "True":
            mobile_otp = str(random.randint(100000,999999))
            await send_otp(mobile=mobile, otp=mobile_otp)

        data = {}
        if email:
            email_data = await cls.create_update_email_otp(
                email=email,
                email_otp=email_otp
            )
            data["email_otp_id"] = email_data.email_otp_id
        
        if mobile:
            mobile_data = await cls.create_update_mobile_otp(
                mobile=mobile,
                mobile_otp=mobile_otp
            )
            data["mobile_otp_id"] = mobile_data.mobile_otp_id
        
        return data

    @classmethod
    async def get_mobile_otp_verify(cls,mobile_otp_id, otp):
        mobile_data = await db.execute(
            select(
                MobileOTP
            ).where(
                MobileOTP.mobile_otp_id == mobile_otp_id
            )
        )
        mobile_data = mobile_data.scalars().one_or_none()
        if mobile_data and mobile_data.otp == otp:
            return mobile_data
        else:
            return None
    
    @classmethod
    async def check_email(cls, email):
        user = select(
            User
        ).where(
            User.email == email
        )
        user = await db.execute(user)
        user = user.scalars().one_or_none()
        return user

class UserProfileSchema():

    @classmethod
    async def get_country(cls):
        country_data = select(
            MasterCountry
        )

        country_data = await db.execute(country_data)
        return country_data.scalars().all()


    @classmethod
    async def get_state(cls, country: List):
        state_data = select(
            MasterState.state_id,
            MasterState.state
        ).where(
            MasterState.country.in_(country)
        )
        state_data = await db.execute(state_data)
        return state_data.all()


    @classmethod
    async def get_city(cls, state: List):
        city_data = select(
            MasterCity.city_id,
            MasterCity.city
        ).where(
            MasterCity.state.in_(state)
        )
        city_data = await db.execute(city_data)
        return city_data.all()


    @classmethod
    async def create_user(cls, mobile):
        user_data = User(
            mobile=mobile,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(user_data)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return user_data

    @classmethod
    async def get_user_data(cls, user_id = None, email = None, mobile = None, is_active = None, with_base = False):
        if with_base:
            user_data = select(
                User.user_id,
                User.name,
                User.dob,
                User.gender,
                User.profile_image,
                User.email,
                User.mobile,
                User.address,
                User.is_email_verified,
                User.is_admin,
                MasterCity.city_id,
                MasterCity.city,
                MasterState.state_id,
                MasterState.state,
                MasterCountry.country_id,
                MasterCountry.name.label("country"),
                PanVerification.pan_number,
                PanVerification.status.label("is_pan_verified"),
                BankVerification.ifsc_code,
                BankVerification.account_number,
                BankVerification.bank_name,
                BankVerification.status.label("is_bank_account_verified"),
                User.pin_code,
                User.team_name,
                User.referral_code
            ).join(
                MasterCity,
                MasterCity.city_id == User.city,
                isouter=True
            ).join(
                MasterState,
                MasterState.state_id == User.state,
                isouter = True
            ).join(
                PanVerification,
                PanVerification.user_id == user_id,
                isouter = True
            ).join(
                BankVerification,
                BankVerification.user_id == user_id,
                isouter = True
            )
        else:
            user_data = select(
                User
            )
        
        if is_active is not None:
            user_data = user_data.where(
                User.is_active == is_active
            )

        if user_id:
            user_data = user_data.where(
                User.user_id == user_id
            )
        
        if email:
            user_data = user_data.where(
                User.email == email
            )
        
        if mobile:
            user_data = user_data.where(
                User.mobile == mobile
            )

        user_data = await db.execute(user_data)
        if with_base:
            return user_data.one_or_none()
        else:
            return user_data.scalars().one_or_none()

    @classmethod
    async def update_user_data(cls, user_id, update_data: dict):
        if "profile_image" in update_data:
            obj_name = f'{uuid.uuid4()}.jpg'
            S3Config.img_conversion(img_data=update_data['profile_image'],object_name=obj_name,file_path=f'{user_id}/profile')
            obj_name = f'{user_id}/profile/{obj_name}'
            update_data['profile_image'] = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"

        # TODO : Email verification link has to be sended

        update_data["updated_at"] = datetime.now()

        await db.execute(
            update(
                User
            ).where(
                User.user_id == user_id
            ).values(
                update_data
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        try:
            await db.commit()
        except:
            await db.rollback()
        return True


    @classmethod
    async def pan_register(cls,request:PanRequestSerializer,user_id):
        obj_name = f'{uuid.uuid4()}.jpg'
        S3Config.img_conversion(img_data=request.pan_s3_url,object_name=obj_name,file_path=f'{user_id}/pan_docs')
        obj_name = f'{user_id}/pan_docs/{obj_name}'
        pan_s3_url = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"

        user_pan_data = PanVerification(
            user_id = user_id,
            pan_name = request.pan_name,
            pan_number = request.pan_number,
            date_of_birth = request.date_of_birth,
            pan_s3_url = pan_s3_url,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )   
        db.add(user_pan_data)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return True
    
    @classmethod
    async def pan_update(cls, user_id, update_value: dict):
        if "pan_s3_url" in update_value:
            obj_name = f'{uuid.uuid4()}.jpg'
            S3Config.img_conversion(img_data=update_value["pan_s3_url"], object_name=obj_name,file_path=f'{user_id}/pan_docs')
            obj_name = f'{user_id}/pan_docs/{obj_name}'
            update_value["pan_s3_url"] = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"

        update_value['updated_at'] = datetime.now()

        update_pan = update(
            PanVerification
        ).where(
            PanVerification.user_id == user_id
        ).values(
            update_value
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(update_pan)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return True
    
    @classmethod
    async def pan_get(cls, user_id):
        user_pan = select(
            PanVerification
        ).where(
            PanVerification.user_id == user_id
        )
        user_pan = await db.execute(user_pan)
        return user_pan.scalars().one_or_none()

    @classmethod
    async def bank_register(cls,request:BankRequestSerializer,user_id):
        obj_name = f'{uuid.uuid4()}.jpg'
        S3Config.img_conversion(img_data=request.bank_s3_url,object_name=obj_name,file_path=f'{user_id}/bank_docs')
        obj_name = f'{user_id}/bank_docs/{obj_name}'
        bank_s3_url = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"

        user_bank_data = BankVerification(
            user_id = user_id,
            name = request.name,
            bank_name = request.bank_name,
            branch_name = request.branch_name,
            account_number = request.account_number,
            ifsc_code = request.ifsc_code,
            state = request.state,
            bank_s3_url = bank_s3_url,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )   
        db.add(user_bank_data)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return True

    @classmethod
    async def bank_update(cls, user_id, update_value: dict):
        if "bank_s3_url" in update_value:
            obj_name = f'{uuid.uuid4()}.jpg'
            S3Config.img_conversion(img_data=update_value["bank_s3_url"], object_name=obj_name,file_path=f'{user_id}/bank_docs')
            obj_name = f'{user_id}/bank_docs/{obj_name}'
            update_value["bank_s3_url"] = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"

        update_value['updated_at'] = datetime.now()

        update_pan = update(
            BankVerification
        ).where(
            BankVerification.user_id == user_id
        ).values(
            update_value
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(update_pan)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return True

    @classmethod
    async def bank_get(cls, user_id):
        user_bank = select(
            BankVerification
        ).where(
            BankVerification.user_id == user_id
        )
        user_bank = await db.execute(user_bank)
        return user_bank.scalars().one_or_none()


    @classmethod
    async def get_user_balance(cls, user_id):
        user_balance = select(
            UserBalance.added_amount,
            UserBalance.winning_amount,
            UserBalance.cash_bonus_amount,
            UserBalance.amount
        ).where(
            UserBalance.user_id == user_id
        )

        user_balance = await db.execute(user_balance)
        return user_balance.one_or_none()

    @classmethod
    async def add_update_amount(cls, user_id, added_amount = None, winning_amount = None, cash_bonus_amount = None, meta_data = {}):
        user_balance = await cls.get_user_balance(user_id = user_id)
        if user_balance:
            update_value = {}
            amount = user_balance.amount
            if added_amount and added_amount != 0:
                update_value["added_amount"] = user_balance.added_amount + added_amount
                amount = amount + added_amount
                await cls.add_user_transaction(
                    user_id = user_id,
                    amount = added_amount,
                    transaction_type = TransactionTypeEnum.DEPOSIT_MONEY,
                    transaction_status = TransactionStatusEnum.COMPLETED,
                )
            if winning_amount and winning_amount != 0:
                update_value["winning_amount"] = user_balance.winning_amount + winning_amount
                await cls.add_user_transaction(
                    user_id = user_id,
                    amount = winning_amount,
                    transaction_type = TransactionTypeEnum.WON_MONEY,
                    transaction_status = TransactionStatusEnum.COMPLETED,
                    meta_data = meta_data
                )
                amount = amount + winning_amount
            if cash_bonus_amount and cash_bonus_amount != 0:
                update_value["cash_bonus_amount"] = user_balance.cash_bonus_amount + cash_bonus_amount
                await cls.add_user_transaction(
                    user_id = user_id,
                    amount = cash_bonus_amount,
                    transaction_type = TransactionTypeEnum.CASH_BONUS,
                    transaction_status = TransactionStatusEnum.COMPLETED
                )
                amount = amount + cash_bonus_amount
            update_value["amount"] = amount
            await db.execute(
                update(
                    UserBalance
                ).where(
                    UserBalance.user_id == user_id
                ).values(
                    update_value
                ).execution_options(
                    synchronize_session="fetch"
                )
            )
            try:
                await db.commit()
            except Exception:
                await db.rollback()
        else:
            user_balance = UserBalance(
                user_id = user_id,
                added_amount = added_amount,
                winning_amount = 0.00,
                cash_bonus_amount = cash_bonus_amount,
                amount = added_amount + cash_bonus_amount,
                created_at = datetime.now()
            )
            db.add(user_balance)
            try:
                await db.commit()
            except Exception:
                await db.rollback()

            await cls.add_user_transaction(
                user_id = user_id,
                amount = added_amount,
                transaction_type = TransactionTypeEnum.DEPOSIT_MONEY,
                transaction_status = TransactionStatusEnum.COMPLETED
            )
            await cls.add_user_transaction(
                user_id = user_id,
                amount = cash_bonus_amount,
                transaction_type = TransactionTypeEnum.CASH_BONUS,
                transaction_status = TransactionStatusEnum.COMPLETED
            )
        return user_balance

    @classmethod
    async def add_gst_amount(cls, user_id, added_amount, cash_bonus_amount, received_amount):
        now = datetime.now() + timedelta(hours=5, minutes=30)
        gst_calculation = GstCalculation(
            user_id = user_id,
            amount = added_amount,
            gst_value = cash_bonus_amount,
            total = received_amount,
            month = now.month,
            year = now.year,
            is_paid = False
        )
        db.add(gst_calculation)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return True

    @classmethod
    async def update_amount(cls, user_id, joining_amount):
        user_balance = await cls.get_user_balance(
            user_id = user_id
        )
        added_amount = user_balance.added_amount
        winning_amount = user_balance.winning_amount
        cash_bonus_amount = user_balance.cash_bonus_amount
        amount = user_balance.amount
        amount = amount - joining_amount

        deduct_add = 0
        deduct_win = 0
        deduct_cash = 0

        x = await AdminSchema.get_discount()
        for i in x:
            cash_bonus_percentage = i.percentage
            break

        cash_bonus_deduct = round(joining_amount * cash_bonus_percentage / 100)
        if cash_bonus_amount >= cash_bonus_deduct:
            cash_bonus_amount = cash_bonus_amount - cash_bonus_deduct
            deduct_cash = cash_bonus_deduct
            joining_amount = joining_amount - cash_bonus_deduct
        else:
            joining_amount = joining_amount - cash_bonus_amount
            deduct_cash = cash_bonus_amount
            cash_bonus_amount = 0


        if added_amount > 0 and added_amount >= joining_amount:
            added_amount = added_amount - joining_amount
            deduct_add = joining_amount
        else:
            joining_amount = joining_amount - added_amount
            deduct_add = added_amount
            added_amount = 0
            if winning_amount >= joining_amount:
                winning_amount = winning_amount - joining_amount
                deduct_win = joining_amount
            else:
                joining_amount = joining_amount - winning_amount
                deduct_win = winning_amount
                winning_amount = 0

        update_value = {
            'added_amount': added_amount,
            'winning_amount': winning_amount,
            'cash_bonus_amount': cash_bonus_amount,
            'amount': amount
        }
        await db.execute(
            update(
                UserBalance
            ).where(
                UserBalance.user_id == user_id
            ).values(
                update_value
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return deduct_add, deduct_win, deduct_cash

    @classmethod
    async def add_user_transaction(cls,user_id, amount, transaction_type, transaction_status, meta_data = {}, deduct_add = 0, deduct_win = 0, deduct_cash = 0):
        user_transaction = UserTransaction(
            user_id = user_id,
            transaction_type = transaction_type,
            transaction_status = transaction_status,
            amount = amount,
            meta_data = meta_data,
            deduct_add = deduct_add,
            deduct_win = deduct_win,
            deduct_cash = deduct_cash
        )
        db.add(user_transaction)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return True


    @classmethod
    async def get_user_transaction(cls, user_id, limit, offset, search_text:str=None):
        user_data = select(
            UserTransaction.transaction_id,
            UserTransaction.amount,
            UserTransaction.transaction_type,
            UserTransaction.transaction_status,
            UserTransaction.created_at,
            UserTransaction.meta_data,
        ).where(
            UserTransaction.user_id == user_id
        ).order_by(
            UserTransaction.created_at.desc()
        ).limit(limit).offset(offset-1)

        if search_text:
            if search_text.isdigit():
                user_data = user_data.where(
                    UserTransaction.amount == float(search_text), 
                )
            else:
                user_data = user_data.where(
                    or_(
                        cast(UserTransaction.transaction_type, TEXT).ilike(f'%{search_text}%'),
                        cast(UserTransaction.transaction_status, TEXT).ilike(f'%{search_text}%'),
                        cast(UserTransaction.amount, float).ilike(f'%{search_text}%')
                    )
                )

        user = await db.execute(user_data)
        return user.all()
    
    @classmethod
    async def get_user_transaction_with_user_draft_id(cls, user_id, user_draft_id):
        user_data = select(
            UserTransaction.transaction_id,
            UserTransaction.user_id,
            UserTransaction.amount,
            UserTransaction.transaction_type,
            UserTransaction.transaction_status,
            UserTransaction.created_at,
            UserTransaction.meta_data,
            UserTransaction.deduct_add,
            UserTransaction.deduct_win,
            UserTransaction.deduct_cash
        ).where(
            UserTransaction.user_id == user_id,
            UserTransaction.transaction_type == TransactionTypeEnum.JOIN_CONTEST,
            UserTransaction.meta_data == {"user_draft_id": str(user_draft_id)}
        ).order_by(
            UserTransaction.created_at.desc()
        )
        user = await db.execute(user_data)
        return user.one_or_none()

    @classmethod
    async def refund_amount(cls, user_id, actual_amount, deduct_add = None, deduct_win = None, deduct_cash = None, meta_data = {}):
        user_balance = await cls.get_user_balance(user_id = user_id)
        update_value = {}
        amount = user_balance.amount
        if deduct_add and deduct_add != 0:
            update_value["added_amount"] = user_balance.added_amount + deduct_add
            amount = amount + deduct_add
        if deduct_win and deduct_win != 0:
            update_value["winning_amount"] = user_balance.winning_amount + deduct_win
            amount = amount + deduct_win
        if deduct_cash and deduct_cash != 0:
            update_value["cash_bonus_amount"] = user_balance.cash_bonus_amount + deduct_cash
            amount = amount + deduct_cash
        update_value["amount"] = amount
        await db.execute(
            update(
                UserBalance
            ).where(
                UserBalance.user_id == user_id
            ).values(
                update_value
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        try:
            await db.commit()
        except Exception:
            await db.rollback()

        await cls.add_user_transaction(
            user_id = user_id,
            amount = actual_amount,
            transaction_type = TransactionTypeEnum.CANCELLED_CONTEST,
            transaction_status = TransactionStatusEnum.COMPLETED,
            meta_data = meta_data
        )

        return True

    @classmethod
    async def get_all_transaction(cls, limit = None, offset = None, search_text:str=None, start_date: date = None, end_date: date = None):
        user_data = select(
            UserTransaction.transaction_id,
            UserTransaction.amount,
            UserTransaction.transaction_type,
            UserTransaction.transaction_status,
            UserTransaction.created_at,
            UserTransaction.updated_at,
            User.user_id,
            User.name,
            User.email,
            User.mobile
        ).join(
            User,
            UserTransaction.user_id == User.user_id
        ).order_by(
            UserTransaction.created_at.desc()
        )

        if limit and offset:
            user_data = user_data.limit(
                limit
            ).offset(
                offset-1
            )

        if search_text:
            user_data = user_data.where(
                or_(
                    cast(UserTransaction.transaction_type, TEXT).ilike(f'%{search_text}%'),
                    cast(UserTransaction.transaction_status, TEXT).ilike(f'%{search_text}%'),
                    cast(User.name, TEXT).ilike(f'%{search_text}%'),
                    cast(User.email, TEXT).ilike(f'%{search_text}%'),
                    cast(User.mobile, TEXT).ilike(f'%{search_text}%'),
                )
            )
        
        if start_date:
            user_data = user_data.where(
                UserTransaction.created_at >= start_date
            )

        if end_date:
            user_data = user_data.where(
                UserTransaction.created_at <= (end_date + timedelta(days=1))
            )
        
        user_data = await db.execute(user_data)
        return user_data.all()

    @classmethod
    async def winning_payout(cls, user_id, winning_amount, amount):
        update_value = {}
        update_value["winning_amount"] = winning_amount
        update_value["amount"] = amount
        await db.execute(
            update(
                UserBalance
            ).where(
                UserBalance.user_id == user_id
            ).values(
                update_value
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        try:
            await db.commit()
        except Exception:
            await db.rollback()

    @classmethod
    async def add_tds_amount(cls, user_id, amount, tds_value, total):
        now = datetime.now() + timedelta(hours=5, minutes=30)
        tds_calculation = TdsCalculation(
            user_id = user_id,
            amount = amount,
            tds_value = tds_value,
            total = total,
            month = now.month,
            year = now.year,
            is_paid = False
        )
        db.add(tds_calculation)
        try:
            await db.commit()
        except Exception:
            await db.rollback()

    @classmethod
    async def get_last_withdraw_transaction(cls, user_id):
        user_data = select(
            UserTransaction.transaction_id,
            UserTransaction.user_id,
            UserTransaction.transaction_type,
            UserTransaction.created_at
        ).where(
            UserTransaction.user_id == user_id,
            UserTransaction.transaction_type == TransactionTypeEnum.WITHDRAW_MONEY
        ).order_by(
            UserTransaction.created_at.desc()
        ).limit(1).offset(0)

        user_data = await db.execute(user_data)
        return user_data.one_or_none()
