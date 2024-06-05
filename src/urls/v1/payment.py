from fastapi import (
    APIRouter, 
    Request, 
    Depends
)
from fastapi_jwt_auth import AuthJWT

from src.services.payment.controller import PaymentController
from src.services.user.serializer import AddAmountRequestSerializer


router = APIRouter(prefix="/v1/payment")

@router.post("")
async def make_payment(token: Request, request: AddAmountRequestSerializer, authorize:AuthJWT=Depends()):
    return await PaymentController.make_payment(
        token=token,
        authorize=authorize,
        request=request
    )
