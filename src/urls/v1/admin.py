from fastapi import (
    APIRouter,
    Depends, 
    Request
)
from typing import Optional
from fastapi_jwt_auth import AuthJWT
from pydantic import (
    UUID4, 
    conint,
    EmailStr,
    constr
)
from src.db.models import (
    BankVerificationEnum, 
    DraftForEnum, 
    VerificationEnum
)
from datetime import datetime, date
from fastapi import Query
from src.services.admin.serializer import (
    AdminCreateDraftRequestSerializer, 
    GstRequestResponseSerializer, 
    HomeScreeenRequestSerializer, 
    HomeScreeenUpdateSerializer, 
    TdsRequestResponseSerializer, 
    DiscountRequestResponseSerializer, 
    CricketSeriesRequestSerialzier, 
    CricketTeamRequestSerialzier,
    AdminAddAmountRequestSerializer
)
from src.services.contest.serializer import WinningDistributionRequestSerializer

# )#################### user ######################
from src.services.user.serializer import (
    OTPRequestSerializer,
    UserLoginRegisterRequestSerializer
)
#################### Admin #######################
from src.services.admin.controller import (
    AdminController,
    ExportCSVController,
    CricketSeries,
    CricketTeam
)

router = APIRouter(prefix="/v1/admin")

@router.post("/login")
async def login(request:UserLoginRegisterRequestSerializer):
    return await AdminController.login(
        request = request
    )

@router.post("/verify_otp")
async def verify_otp(request:OTPRequestSerializer, authorize:AuthJWT=Depends()):
    return await AdminController.verify_otp(
        request = request,
        authorize = authorize
    )

@router.post("/refresh_token")
async def refresh_token(authorize: AuthJWT = Depends()):
    return await AdminController.refresh_token(authorize=authorize)

####################################### User Data #########################################################

@router.get("/user_list")
async def user_list(token:Request, authorize:AuthJWT=Depends(), limit: conint(ge=1) = 10, offset: conint(ge=1) = 1,search_text:str=None, email: Optional[EmailStr] = None, is_export: Optional[bool] = None):
    return await AdminController.user_list(
        token = token,
        authorize = authorize,
        limit = limit,
        offset = offset,
        search_text = search_text,
        email = email,
        is_export = is_export
    )


@router.get("/profile")
async def get_profile(user_id: UUID4, token:Request, authorize:AuthJWT=Depends()):
    return await AdminController.get_profile(
        user_id = user_id,
        token = token,
        authorize = authorize
    )

@router.get('/pan')
async def pan_get(user_id: UUID4, token:Request,authorize:AuthJWT=Depends()):
    return await AdminController.pan_get(
        user_id = user_id,
        token = token,
        authorize = authorize
    )

@router.get('/bank')
async def bank_get(user_id: UUID4, token:Request, authorize:AuthJWT=Depends()):
    return await AdminController.bank_get(
        user_id = user_id,
        token=token,
        authorize=authorize
    )

######################################## Amount #############################################################

@router.post("/amount")
async def add_amount(request: AdminAddAmountRequestSerializer):
    return await AdminController.add_amount(
        request = request
    )

@router.get("/amount")
async def get_amount(user_id: UUID4, token:Request, authorize:AuthJWT=Depends()):
    return await AdminController.get_amount(
        user_id = user_id,
        token = token,
        authorize = authorize
    )

@router.get("/transaction")
async def get_transaction(user_id: UUID4, token:Request, authorize:AuthJWT=Depends(), limit: conint(ge=1) = 10, offset: conint(ge=1) = 1, search_text:str=None,):
    return await AdminController.get_transaction(
        user_id = user_id,
        token = token,
        authorize=authorize,
        limit = limit,
        offset = offset,
        search_text=search_text,
    )


@router.get('/pan_status')
async def pan_status(token:Request, user_id : UUID4, pan_status : VerificationEnum ,authorize:AuthJWT=Depends(), ):
    return await AdminController.pan_status(
        token=token,
        authorize=authorize,
        user_id = user_id,
        pan_status = pan_status
    )

@router.get('/bank_status')
async def bank_status(token:Request, user_id : UUID4, bank_status : BankVerificationEnum ,authorize:AuthJWT=Depends(), ):
    return await AdminController.bank_status(
        token=token,
        authorize=authorize,
        user_id = user_id,
        bank_status = bank_status
    )

######################################### Matches #####################################################################################

@router.get('/matches')
async def get_matches(token:Request, authorize:AuthJWT=Depends(), series_id: Optional[UUID4] = None, match_id: Optional[UUID4] = None, limit: conint(ge=1) = 10, offset: conint(ge=1) = 1,search_text:str=None):
    return await AdminController.get_matches(
        match_id = match_id,
        series_id = series_id,
        token = token,
        authorize = authorize,
        limit=limit,
        offset=offset,
        search_text = search_text
    )

@router.get('/series')
async def get_series(token:Request, authorize:AuthJWT=Depends(), series_id: Optional[UUID4] = None, limit: conint(ge=1) = 10, offset: conint(ge=1) = 1,search_text:str=None):
    return await AdminController.get_series(
        series_id = series_id,
        token = token,
        authorize = authorize,
        limit=limit,
        offset=offset,
        search_text=search_text
    )

@router.get('/draft')
async def draft_list(token:Request, draft_match_series_id: Optional[UUID4], draft_for: DraftForEnum, authorize:AuthJWT=Depends(),limit: conint(ge=1) = 10, offset: conint(ge=1) = 1,search_text:str=None):
    return await AdminController.draft_list(
        token = token,
        authorize = authorize,
        draft_match_series_id = draft_match_series_id,
        draft_for = draft_for,
        limit = limit,
        offset = offset,
        search_text=search_text
    )

@router.post("/draft")
async def create_draft(token: Request, request: AdminCreateDraftRequestSerializer, authorize:AuthJWT=Depends()):
    return await AdminController.create_draft(
        token = token,
        authorize = authorize,
        request = request
    )

@router.get("/draft_detail")
async def draft_detail(token: Request, user_draft_id: UUID4, authorize:AuthJWT=Depends()):
    return await AdminController.draft_detail(
        token = token,
        authorize = authorize,
        user_draft_id = user_draft_id
    )

@router.post("/gst")
async def create_gst(token: Request, request: GstRequestResponseSerializer, authorize:AuthJWT=Depends()):
    return await AdminController.create_gst(
        token = token,
        authorize = authorize,
        request = request
    )

@router.get("/gst")
async def get_gst(token: Request, authorize:AuthJWT=Depends()):
    return await AdminController.get_gst(
        token = token,
        authorize = authorize
    )

@router.get("/gst_year")
async def get_gst_year(token: Request, authorize:AuthJWT=Depends()):
    return await AdminController.get_gst_year(
        token = token,
        authorize = authorize
    )

@router.get("/gst_calculation_list")
async def gst_calculation_list(token: Request, year:conint(), authorize:AuthJWT=Depends()):
    return await AdminController.gst_calculation_list(
        token = token,
        authorize = authorize,
        year = year
    )
    
@router.get("/get_gst_individual")
async def gst_list(token: Request, year:conint(), month:conint(), authorize:AuthJWT=Depends(), email: Optional[EmailStr] = None, is_export: Optional[bool] = None):
    return await AdminController.get_gst_individual(
        token = token,
        authorize = authorize,
        year = year,
        month = month,
        email = email,
        is_export = is_export
    )
    
@router.get("/gst_pay")
async def gst_pay(token: Request, gst_calculation_id: Optional[UUID4] = None, year:Optional[conint(ge=0)] = None, month:Optional[conint(ge=1,le=12)] = None, authorize:AuthJWT=Depends()):
    return await AdminController.gst_pay(
        token = token,
        authorize = authorize,
        gst_calculation_id = gst_calculation_id,
        year = year,
        month = month
    )

@router.get("/member_detail")
async def member_detail(token: Request, user_draft_id: UUID4, authorize:AuthJWT=Depends()):
    return await AdminController.member_detail(
        token = token,
        authorize = authorize,
        user_draft_id = user_draft_id
    )

@router.get("/change_match_status")
async def change_match_status(token: Request, is_live: Optional[bool], authorize: AuthJWT=Depends(), match_id: Optional[UUID4] = None):
    return await AdminController.change_match_status(
        token = token,
        authorize = authorize,
        match_id = match_id,
        is_live = is_live
    )

@router.get("/change_series_status")
async def change_series_status(token: Request, is_live: Optional[bool], authorize: AuthJWT=Depends(), series_id: Optional[UUID4] = None):
    return await AdminController.change_series_status(
        token = token,
        authorize = authorize,
        series_id = series_id,
        is_live = is_live
    )

@router.get("/all_transaction")
async def get_transaction(token:Request, authorize:AuthJWT=Depends(), limit: conint(ge=1) = 10, offset: conint(ge=1) = 1, search_text:str=None, start_date: date = None, end_date: date = None, email: Optional[EmailStr] = None, is_export: Optional[bool] = None):
    return await AdminController.get_all_transaction(
        token = token,
        authorize=authorize,
        limit = limit,
        offset = offset,
        search_text = search_text,
        start_date = start_date,
        end_date = end_date,
        email = email,
        is_export = is_export
    )

@router.get("/user_list_csv")
async def create_csv_and_send_email(limit: conint(ge=1)=10 ,offset: conint(ge=1)=1):
    return await ExportCSVController.user_list_csv(
        limit = limit,
        offset = offset
    )

@router.get("/tds_list_csv")
async def create_csv_and_send_email():
    return await ExportCSVController.export_tds_list()

@router.get("/gst_list_csv")
async def create_csv_and_send_email():
    return await ExportCSVController.export_gst_list()

@router.get("/transaction_list_csv")
async def create_csv_and_send_email():
    return await ExportCSVController.export_transaction_list()
    
@router.get("/download_csv")
async def download_csv_and_send_email(token: Request,email:EmailStr, csv_type:Optional[conint(ge=0)] = None, limit: conint(ge=1)=10 ,offset: conint(ge=1)=1, authorize: AuthJWT=Depends()):
    return await ExportCSVController.download_csv_and_send_email(
        token = token,
        authorize = authorize,
        csv_type = csv_type,
        email = email,
        limit = limit,
        offset = offset
    )   

@router.post("/tds")
async def create_tds(token: Request, request: TdsRequestResponseSerializer, authorize:AuthJWT=Depends()):
    return await AdminController.create_tds(
        token = token,
        authorize = authorize,
        request = request
    )

@router.get("/tds")
async def get_tds(token: Request, authorize:AuthJWT=Depends()):
    return await AdminController.get_tds(
        token = token,
        authorize = authorize
    )

@router.get("/tds_year")
async def get_tds_year(token: Request, authorize:AuthJWT=Depends()):
    return await AdminController.get_tds_year(
        token = token,
        authorize = authorize
    )

@router.get("/tds_calculation_list")
async def tds_calculation_list(token: Request, year:conint(), authorize:AuthJWT=Depends()):
    return await AdminController.tds_calculation_list(
        token = token,
        authorize = authorize,
        year = year
    )
    
@router.get("/tds_gst_individual")
async def tds_list(token: Request, year:conint(), month:conint(), authorize:AuthJWT=Depends(), email: Optional[EmailStr] = None, is_export: Optional[bool] = None):
    return await AdminController.get_tds_individual(
        token = token,
        authorize = authorize,
        year = year,
        month = month,
        email = email,
        is_export = is_export
    )

@router.get("/tds_pay")
async def tds_pay(token: Request, tds_calculation_id: Optional[UUID4] = None, year:Optional[conint(ge=0)] = None, month:Optional[conint(ge=1,le=12)] = None, authorize:AuthJWT=Depends()):
    return await AdminController.tds_pay(
        token = token,
        authorize = authorize,
        tds_calculation_id = tds_calculation_id,
        year = year,
        month = month
    )

@router.post("/cash_bonus_discount")
async def add_cash_bonus_discount(token: Request, request: DiscountRequestResponseSerializer, authorize:AuthJWT=Depends()):
    return await AdminController.add_cash_bonus_discount(
        token = token,
        authorize = authorize,
        request = request
    )

@router.get("/cash_bonus_discount")
async def get_cash_bonus_discount(token: Request, authorize:AuthJWT=Depends()):
    return await AdminController.get_cash_bonus_discount(
        token = token,
        authorize = authorize
    )

@router.get("/get_all_draft_list")
async def get_all_draft_list(token:Request, authorize:AuthJWT=Depends(), limit: conint(ge=1) = 10, offset: conint(ge=1) = 1,search_text:str=None, start_date: date = None, end_date: date = None):
    return await AdminController.get_all_draft_list(
        token = token,
        authorize = authorize,
        limit = limit,
        offset = offset,
        search_text=search_text,
        start_date=start_date,
        end_date=end_date,
    )

@router.post("/winning_distribution")
async def winning_distribution(request: WinningDistributionRequestSerializer):
    return await AdminController.winning_distribution_for_draft(
        user_draft_ids = request.user_draft_ids
    )

@router.get("/is_winner_available")
async def is_winner_available(draft_match_series_id: UUID4, draft_for: DraftForEnum):
    return await AdminController.is_winner_available(
        draft_match_series_id = draft_match_series_id,
        draft_for = draft_for
    )

######################## cricket series ##################

@router.get("/list_series")
async def list_series(token:Request, authorize:AuthJWT=Depends(), limit: conint(ge=1) = 10, offset: conint(ge=1) = 1, search_text:str=None):
    return await CricketSeries.list_series(
        token = token,
        authorize = authorize,
        limit = limit,
        offset = offset,
        search_text=search_text
    )

@router.get("/get_series_individual")
async def get_series_individual(token: Request, cricket_series_id:UUID4, authorize:AuthJWT=Depends()):
    return await CricketSeries.get_series_individual(
        token = token,
        authorize = authorize,
        cricket_series_id = cricket_series_id
    )

@router.post("/update_series")
async def update_series(token:Request, request:CricketSeriesRequestSerialzier, cricket_series_id: UUID4, authorize:AuthJWT=Depends()):
    return await CricketSeries.update_series(
        authorize = authorize,
        token = token,
        request = request,
        cricket_series_id = cricket_series_id
    )
####################### cricket team ####################


@router.get("/list_team")
async def list_team(token:Request, authorize:AuthJWT=Depends(), limit: conint(ge=1) = 10, offset: conint(ge=1) = 1, search_text:str=None):
    return await CricketTeam.list_team(
        token = token,
        authorize = authorize,
        limit = limit,
        offset = offset,
        search_text=search_text
    )

@router.post("/update_team")
async def update_team(token:Request, request:CricketTeamRequestSerialzier, cricket_team_id: UUID4, authorize:AuthJWT=Depends()):
    return await CricketTeam.update_team(
        authorize = authorize,
        token = token,
        request = request,
        cricket_team_id = cricket_team_id
    )

@router.get("/get_team_individual")
async def get_team_individual(token: Request, cricket_team_id:UUID4, authorize:AuthJWT=Depends()):
    return await CricketTeam.get_team_individual(
        token = token,
        authorize = authorize,
        cricket_team_id = cricket_team_id
    )

@router.get("/home_screen")
async def get_home_screen(token: Request,homescreen_id:UUID4=None,limit:int=10,offset:int=1, authorize:AuthJWT=Depends()):
    return await AdminController.get_home_screen(
        token = token,
        authorize = authorize,
        limit=limit,
        offset=offset,
        homescreen_id=homescreen_id
    )

@router.post("/home_screen")
async def home_screen(token: Request, request: HomeScreeenRequestSerializer, authorize:AuthJWT=Depends()):
    return await AdminController.home_screen(
        token = token,
        authorize = authorize,
        request = request
    )

@router.post("/update_home_screen")
async def update_home_screen(token:Request, request:HomeScreeenUpdateSerializer, homescreen_id: UUID4, authorize:AuthJWT=Depends()):
    return await AdminController.update_home_screen(
        authorize = authorize,
        token = token,
        request = request,
        homescreen_id = homescreen_id
    )

@router.delete("/delete_home_screen")
async def delete_home_screen(token:Request,homescreen_id:UUID4,authorize:AuthJWT=Depends()):
    return await AdminController.delete_home_screen(
        token=token,
        authorize=authorize,
        homescreen_id = homescreen_id
    )

@router.get("/cancel_draft")
async def cancel_draft(token: str,invitation_code: constr()):
    return await AdminController.cancel_draft(
        token = token,
        invitation_code = invitation_code
    )