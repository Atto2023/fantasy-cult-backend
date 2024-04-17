#Third Party Imports
from pydantic import (
    BaseModel, 
    constr,
    EmailStr,
    UUID4,
    AnyUrl,
    validator,
    root_validator
)
from pydantic.types import (
    constr, 
    conint, 
    PastDate, 
    confloat
)
from typing import (
    Optional, 
    List, 
    Any
)
from datetime import datetime, date

from src.db.models import (
    BankVerificationEnum, 
    TransactionStatusEnum, 
    TransactionTypeEnum, 
    VerificationEnum
)

class UserLoginRegisterRequestSerializer(BaseModel):
    mobile: constr(min_length=10, max_length=13)

class UserLoginRegisterResponseSerializer(UserLoginRegisterRequestSerializer):
    mobile_otp_id: UUID4

class OTPRequestSerializer(BaseModel):
    mobile_otp_id: UUID4
    otp: constr(min_length=1, max_length=6)


class OTPResponseSerializer(BaseModel):
    already_user: bool
    user_id: UUID4
    access_token: constr()
    refresh_token: constr()

class CountryResponseSerializer(BaseModel):
    country_id: UUID4
    name: constr()

class StateRequestSerializer(BaseModel):
    country: List[UUID4] = ["31cdcc3f-48ae-4734-a2dd-7c86dd9e4c52"]

class StateResponseSerializer(BaseModel):
    state_id : UUID4
    state : constr()

class CityRequestSerializer(BaseModel):
    state: List[UUID4]

class CityResponseSerializer(BaseModel):
    city_id : UUID4
    city : str

class RequestEmailVerificationSerializer(BaseModel):
    email: EmailStr

class UserProfileRequestSerailizer(BaseModel):
    email: Optional[EmailStr]
    name: Optional[constr(min_length=1)]
    profile_image: Optional[constr(min_length=1)]
    gender: Optional[constr(min_length=1)]
    address: Optional[constr(min_length=1)]
    dob: Optional[date] # MMMM-YY-DD
    city: Optional[UUID4]
    state: Optional[UUID4]
    country: Optional[UUID4]
    pin_code: Optional[constr(min_length=1, max_length=6)]
    team_name: Optional[constr(min_length=1)]
    referral_code: Optional[constr(min_length=1)]

class UserProfileResponseSerializer(BaseModel):
    user_id: UUID4
    name:Optional[constr()]
    email:Optional[EmailStr]
    is_email_verified: Optional[bool]
    mobile:Optional[constr()]
    dob:Optional[date]
    gender:Optional[constr()]
    address:Optional[constr()]
    city_id: Optional[UUID4]
    city: Optional[constr()]
    state_id: Optional[UUID4]
    state: Optional[constr()]
    country_id: Optional[UUID4]
    country: Optional[constr()]
    pin_code:Optional[constr()]
    profile_image: Optional[constr()]
    team_name:Optional[constr()]
    referral_code:Optional[constr()]
    is_mobile_verified : Optional[bool] = True
    pan_number : Optional[constr()]
    is_pan_verified : Optional[VerificationEnum]
    is_admin : Optional[bool]
    account_number : Optional[constr()]
    is_bank_account_verified : Optional[BankVerificationEnum]


#Pan Verification
class PanRequestSerializer(BaseModel):
    pan_name : constr(max_length=240)
    pan_number: constr(max_length=10, min_length=10)
    date_of_birth : date # YYYY-MM-DD
    pan_s3_url : constr()


class PanVerificationResponseSerializer(BaseModel):
    pan_verfication_id : UUID4
    user_id : UUID4
    pan_name : constr(max_length=255)
    pan_number: constr()
    date_of_birth: date
    pan_s3_url: constr()
    status: VerificationEnum


#Bank Verification
class BankRequestSerializer(BaseModel):
    name : constr(max_length=240,min_length=1)
    account_number : constr(min_length=1)
    ifsc_code : constr(min_length=1)
    bank_name : constr(max_length=240)
    branch_name: constr(max_length=240)
    state : constr()
    bank_s3_url: constr()


class BankResponseSerializer(BaseModel):
    bank_verification_id :UUID4
    user_id : UUID4
    name : constr()
    account_number : constr()
    ifsc_code : constr(min_length = 1)
    bank_name : constr()
    branch_name : constr()
    state : constr()
    bank_s3_url : constr()
    status: BankVerificationEnum



class AddAmountRequestSerializer(BaseModel):
    amount: confloat()

class BalanceResponseSerializer(BaseModel):
    added_amount: Optional[confloat()] = 0.0
    winning_amount: Optional[confloat()] = 0.0
    cash_bonus_amount : Optional[confloat()] = 0.0
    amount : Optional[confloat()]= 0.0

class ListAnySerializer(BaseModel):
    data: List[Any]

class TransactionResponseSerializer(BaseModel):
    transaction_id: UUID4
    amount: confloat()
    created_at: datetime
    transaction_type: TransactionTypeEnum
    transaction_status: TransactionStatusEnum
    message: Optional[constr()] = ''

class TransactionAllResponseSerializer(BaseModel):
    transaction_id: UUID4
    amount: confloat()
    transaction_type: TransactionTypeEnum
    transaction_status: TransactionStatusEnum
    user_id: UUID4
    name: Optional[constr()]
    email: Optional[EmailStr]
    mobile: Optional[constr()]
    created_at: datetime
