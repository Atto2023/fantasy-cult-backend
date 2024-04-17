from typing import Optional
from pydantic import(
    BaseModel, 
    EmailStr, 
    confloat, 
    conint, 
    constr
)

class UserBasicDetailsSerializer(BaseModel):
    mobile: constr()
    email: Optional[EmailStr]

class ResponseMakePaymentSerializer(BaseModel):
    key: constr()
    price: confloat()
    amount: confloat()
    name: constr() = "Fantasy Cult"
    order_id: constr()
    description: constr() = "Payment to add balance"
    timeout: conint() = 360
    prefill: UserBasicDetailsSerializer
