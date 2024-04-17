from fastapi import status
from src.services.payment.serializer import (
    ResponseMakePaymentSerializer, 
    UserBasicDetailsSerializer
)
from src.services.user.schema import UserProfileSchema
from src.services.user.serializer import AddAmountRequestSerializer
from src.utils.jwt import auth_check
from src.config.config import Config
import razorpay

from src.utils.response import (
    SuccessResponseSerializer, 
    response_structure
)


class PaymentController:

    @classmethod
    async def make_payment(cls, token, authorize, request: AddAmountRequestSerializer):
        await auth_check(authorize=authorize, token=token)
        user_id = authorize.get_jwt_subject()

        client = razorpay.Client(
            auth=(Config.RAZORPAY_KEY,Config.RAZORPAY_SECRET)
        )

        user_data = await UserProfileSchema.get_user_data(
            user_id = user_id,
            with_base = True
        )
        prefill = UserBasicDetailsSerializer(**(user_data._asdict()))
        razorpay_amount = request.amount * 100 # Here it takes in paise
        razorpay_dict = {}
        razorpay_dict["amount"] = razorpay_amount
        razorpay_dict["currency"] = "INR"
        razorpay_dict["notes"] = prefill.dict()

        order = client.order.create(data=razorpay_dict)
        result = ResponseMakePaymentSerializer(
            key = Config.RAZORPAY_KEY,
            price = razorpay_amount,
            amount = request.amount,
            order_id = order["id"],
            prefill = prefill
        )

        serializer = SuccessResponseSerializer(
            message="Payment Initiated",
            data=result
        )       
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )
