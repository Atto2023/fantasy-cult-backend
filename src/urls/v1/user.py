from fastapi import (
    APIRouter,
    Depends, 
    Request,
    Path,
)
from fastapi_jwt_auth import AuthJWT
from pydantic import (
    UUID4,
    EmailStr, 
    conint,
    constr
)
from src.services.user.serializer import (
    #User Login Flow
    AddAmountRequestSerializer,
    CityRequestSerializer,
    PanRequestSerializer,
    StateRequestSerializer,
    UserProfileRequestSerailizer,
    UserLoginRegisterRequestSerializer,
    BankRequestSerializer,
    OTPRequestSerializer,
    RequestEmailVerificationSerializer
)
from src.services.user.controller import (
    UserProfileController,
    UserController
)
# from src.utils.helper import get_current_user

router = APIRouter(prefix="/v1/user")

##### User Login Flow #############################################################
@router.post("/login_register")
async def login_register(request:UserLoginRegisterRequestSerializer):
    return await UserController.login_register(
        request = request
    )

@router.post("/verify_otp")
async def verify_otp(request:OTPRequestSerializer, authorize:AuthJWT=Depends()):
    return await UserController.verify_otp(
        request = request, 
        authorize = authorize
    )

@router.post("/resend_otp")
async def resend_otp(request : UserLoginRegisterRequestSerializer):
    return await UserController.login_register(
        request = request
    )

@router.post("/refresh_token")
async def refresh_token(authorize: AuthJWT = Depends()):
    return await UserController.refresh_token(authorize=authorize)


@router.get("/email_verify/{email}/{user_id}")
async def email_verify(email: EmailStr, user_id: constr() = Path(...)):
    return await UserController.email_verify(
        email = email,
        user_id = user_id
    )

@router.post("/send_verification_mail")
async def send_verification_mail(request: RequestEmailVerificationSerializer, token: Request, authorize:AuthJWT=Depends()):
    return await UserController.send_verification_email(
        token = token,
        request = request,
        authorize = authorize
    )

##### User Profile Flow #############################################################

@router.get("/country")
async def get_country():
    return await UserProfileController.get_country()

@router.get("/state")
async def get_state(request: StateRequestSerializer):
    return await UserProfileController.get_state(
        request = request
    )

@router.get("/city")
async def get_city(request: CityRequestSerializer):
    return await UserProfileController.get_city(
        request = request
    )


@router.put("/profile")
async def update_profile(token : Request,request:UserProfileRequestSerailizer, authorize:AuthJWT=Depends()):
    return await UserProfileController.update_profile(
        token = token,
        request = request,
        authorize = authorize
    )


@router.get("/profile")
async def get_profile(token:Request, authorize:AuthJWT=Depends()):
    return await UserProfileController.get_profile(
        token = token,
        authorize = authorize
    )


@router.post('/pan')
async def pan_register(token:Request,request:PanRequestSerializer,authorize:AuthJWT=Depends()):
    return await UserProfileController.pan_register(
        token = token,
        request = request,
        authorize = authorize
    )

@router.get('/pan')
async def pan_get(token:Request,authorize:AuthJWT=Depends()):
    return await UserProfileController.pan_get(
        token = token,
        authorize = authorize
    )

@router.post('/bank')
async def bank_register(token:Request,request:BankRequestSerializer,authorize:AuthJWT=Depends()):
    return await UserProfileController.bank_register(
        token=token,
        request=request,
        authorize=authorize
    )

@router.get('/bank')
async def bank_get(token:Request,authorize:AuthJWT=Depends()):
    return await UserProfileController.bank_get(
        token=token,
        authorize=authorize
    )

############################################################# User Amount Flow #############################################################

@router.post("/amount")
async def add_amount(token : Request,request:AddAmountRequestSerializer,authorize:AuthJWT=Depends()):
    return await UserProfileController.add_amount(
        token = token,
        request = request,
        authorize = authorize
    )

@router.get("/amount")
async def get_amount(token : Request,authorize:AuthJWT=Depends()):
    return await UserProfileController.get_amount(
        token = token,
        authorize = authorize
    )

@router.get("/transaction")
async def get_transaction(token:Request, authorize:AuthJWT=Depends(), limit: conint(ge=1) = 10, offset: conint(ge=1) = 1):
    return await UserProfileController.get_transaction(
        token = token,
        authorize = authorize,
        limit = limit,
        offset = offset
    )

@router.post("/payout")
async def payout(token:Request, request:AddAmountRequestSerializer, authorize:AuthJWT=Depends()):
    return await UserProfileController.payout(
        token = token,
        request = request,
        authorize = authorize
    )
