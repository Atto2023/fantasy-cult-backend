from datetime import datetime, timedelta, date
from fastapi import status, File, Response
from pydantic import UUID4, EmailStr
import uuid
import time
from src.db.models import DraftForEnum
from src.config.config import Config
from fastapi.responses import FileResponse
from src.services.admin.serializer import(
    AdminCreateDraftRequestSerializer,
    AdminDraftDetailResponseSerializer, 
    DraftResponseSerialzier, 
    GstIndividualCalculationResponseSerializer, 
    GstRequestResponseSerializer,
    HomeScreeenUpdateSerializer,
    MemberDetailResponseSerialzier, 
    GstRequestResponseSerializer, 
    GstListResponseSerializer, 
    TdsIndividualCalculationResponseSerializer, 
    TdsRequestResponseSerializer, 
    TdsListResponseSerializer, 
    DiscountRequestResponseSerializer, 
    CricketSeriesResponseSerializer, 
    CricketTeamResponseSerializer, 
    CricketSeriesRequestSerialzier, 
    CricketTeamRequestSerialzier, 
    HomeScreenResponseSerializer, 
    HomeScreeenRequestSerializer,
    AdminAddAmountRequestSerializer
)
from src.services.contest.schema import DraftSchema
from src.services.notification.schema import NotificationSchema
from src.services.user.controller import UserController, UserProfileController
from src.services.user.schema import UserProfileSchema, UserSchema
from src.services.user.serializer import (
    BalanceResponseSerializer,
    BankResponseSerializer,
    OTPRequestSerializer,
    PanVerificationResponseSerializer,
    TransactionResponseSerializer,
    UserLoginRegisterRequestSerializer,
    UserLoginRegisterResponseSerializer,
    UserProfileResponseSerializer,
    TransactionAllResponseSerializer
)
import csv

#Local Imports
from src.utils.constant import (
    NotificationConstant, 
    UserConstant
)
from src.utils.entity_sports import EntitySportsLive
from src.utils.helper_functions import (
    send_email_with_attachment, 
    send_mail_notification, 
    send_notification
)
from src.utils.jwt import auth_check
from src.utils.response import (
    SuccessResponseSerializer,
    ErrorResponseSerializer,
    response_structure,
)
from src.services.admin.schema import (
    AdminSchema,
)
from src.services.cricket.schema import (
    CricketMatchSchema
)
from src.services.cricket.serializer import (
    MatchListResponseSerializer,
    SeriesListResponseSerializer,
)
from src.services.contest.serializer import PlayersResponseSerializer
from src.utils.common_html import money_won_html, money_lost_html, money_deposited_html, money_bonus_html

class AdminController():

    @classmethod
    async def login(cls, request: UserLoginRegisterRequestSerializer):
        user_data = await UserProfileSchema.get_user_data(
            mobile = request.mobile,
            with_base = True
        )

        if user_data and user_data.is_admin:
            data = await UserSchema.update_email_mobile_otp_data(
                mobile = request.mobile
            )
            data = UserLoginRegisterResponseSerializer(
                mobile = request.mobile,
                mobile_otp_id = data["mobile_otp_id"]
            )
            serializer = SuccessResponseSerializer(
                message = UserConstant.SUCCESS_EMAIL_PHONE_STORE,
                status_code = status.HTTP_200_OK,
                data = data
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = f"You have no access to admin"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )

    @classmethod
    async def verify_otp(cls, request:OTPRequestSerializer, authorize):
        return await UserController.verify_otp(
            request = request,
            authorize = authorize
        )
    
    @classmethod
    async def refresh_token(cls, authorize):
        return await UserController.refresh_token(
            authorize = authorize
        )

    @classmethod
    async def user_list(cls, token, authorize, limit, offset, email: EmailStr = None, search_text:str=None,  is_export: bool = True):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        if is_export:  
            csv_data = await ExportCSVController.user_list_csv(
                email = email,
                search_text = search_text
            )
            return FileResponse(path=csv_data.data)

        user_list = await AdminSchema.user_list(
            limit = limit,
            offset = offset,
            search_text=search_text
        )

        data = [UserProfileResponseSerializer(**(i._asdict())) for i in user_list]
        serializer = SuccessResponseSerializer(
            message = "User List",
            data = data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def get_profile(cls, user_id, token, authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

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
    async def pan_get(cls, user_id, token, authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()
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
    async def bank_get(cls, user_id, token, authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

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
    async def get_amount(cls, user_id, token, authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

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
    async def get_transaction(cls, user_id, token, authorize, limit, offset, search_text:str=None):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        user_transaction = await UserProfileSchema.get_user_transaction(
            user_id = user_id,
            limit = limit,
            offset = offset,
            search_text=search_text
        )
        data = [TransactionResponseSerializer(**i._asdict()) for i in user_transaction] if user_transaction else []
        serializer = SuccessResponseSerializer(
            message=UserConstant.FETCH_ALL_TRANSACTION,
            status_code=status.HTTP_200_OK,
            data=data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def pan_status(cls,token,user_id, pan_status ,authorize):
        await auth_check(token=token,authorize=authorize)
        pan_user = authorize.get_jwt_subject()
        user_pan_data = await UserProfileSchema.pan_get(user_id=user_id)
        if user_pan_data:
            update_value = {
                'status' : pan_status
            }
            user_pan_data = await UserProfileSchema.pan_update(
                user_id=user_id,
                update_value=update_value
            )

            serializer = SuccessResponseSerializer(
                message = "User Pan Status Update!",
                data = True
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            serializer = ErrorResponseSerializer(
                message="Not able to find Pan Details",
                status_code=status.HTTP_404_NOT_FOUND
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )

    @classmethod
    async def bank_status(cls,token, user_id, bank_status, authorize):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()
        user_bank_data = await UserProfileSchema.bank_get(user_id=user_id)
        if user_bank_data:
            update_value = {
                'status' : bank_status
            }
            user_bank_data = await UserProfileSchema.bank_update(
                user_id=user_id,
                update_value=update_value
            )

            serializer = SuccessResponseSerializer(
                message="User Bank Status Update!",
                data = True
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            serializer = ErrorResponseSerializer(
                message="Not able to find Bank Details",
                status_code=status.HTTP_404_NOT_FOUND
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )
        
    @classmethod
    async def get_matches(cls, match_id, series_id, token, authorize, limit, offset,search_text:str=None):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()
        matches = await CricketMatchSchema.get_matches(
            series_id = series_id,
            match_id = match_id,
            limit = limit,
            offset = offset,
            search_text=search_text
        )
        if match_id:
            match_serializer = MatchListResponseSerializer(**(matches._asdict()))
            match_serializer.series_start_day = match_serializer.series_start_date.strftime('%A') if match_serializer.series_start_date else None
            match_serializer.match_start_day = match_serializer.match_start_time.strftime('%A') if match_serializer.match_start_time else None
        else:
            match_serializer = []
            for i in matches:
                data  = MatchListResponseSerializer(**(i._asdict()))
                data.series_start_day = data.series_start_date.strftime('%A') if data.series_start_date else None
                data.match_start_day = data.match_start_time.strftime('%A') if data.match_start_time else None
                match_serializer.append(data)
        serializer = SuccessResponseSerializer(
            message = "Match List",
            data = match_serializer
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )
    
    @classmethod
    async def get_series(cls, series_id, token, authorize, limit, offset,search_text:str=None):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()
        series = await CricketMatchSchema.get_series(
            series_id = series_id,
            limit = limit,
            offset = offset,
            search_text=search_text
        )
        if series_id:
            series_serializer = SeriesListResponseSerializer(**(series._asdict()))
            series_serializer.series_start_day = series_serializer.series_start_date.strftime('%A') if series_serializer.series_start_date else None
        else:
            series_serializer = []
            for i in series:
                data  = SeriesListResponseSerializer(**(i._asdict()))
                data.series_start_day = data.series_start_date.strftime('%A') if data.series_start_date else None
                series_serializer.append(data)
        serializer = SuccessResponseSerializer(
            message = "series List",
            data = series_serializer
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def draft_list(cls, token, authorize, draft_match_series_id, draft_for, limit, offset,search_text:str=None):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()
        draft_data = await DraftSchema.get_draft_data(
            is_list = True,
            draft_for = draft_for,
            draft_match_series_id = draft_match_series_id,
            limit = limit,
            offset = offset,
            search_text=search_text
        )
        if draft_data:
            data = [DraftResponseSerialzier(**(i._asdict())) for i in draft_data]
            serializer = SuccessResponseSerializer(
                message = "All draft",
                data = data
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        else:
            serializer = ErrorResponseSerializer(
                message = "No draft found",
                data = []
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )


    @classmethod
    async def create_draft(cls, token, authorize, request: AdminCreateDraftRequestSerializer):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if request.top_picks > request.number_of_round:
            serializer = ErrorResponseSerializer(
                message = f"Top Picks must be less than  number of rounds"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )

        total_choice_member = request.player_choice.bat + request.player_choice.bowl + request.player_choice.wk + request.player_choice.all
        if total_choice_member > request.player_choice.each_member_player:
            serializer = ErrorResponseSerializer(
                message = f"Please check the Player Choice"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )

        if request.draft_for == DraftForEnum.MATCH:
            match_data = await DraftSchema.match_series_team(
                cricket_match_id = request.draft_match_series_id
            )
            if not match_data:
                serializer = ErrorResponseSerializer(
                    message = f"This match id does not exist"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )
        if request.draft_for == DraftForEnum.SERIES:
            series_data = await DraftSchema.check_series_with_id(
                series_id = request.draft_match_series_id
            )
            if not series_data:
                serializer = ErrorResponseSerializer(
                    message = f"This series id does not exist"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )

        user_draft = await DraftSchema.get_draft_data(
            invitation_code = request.invitation_code
        )
        if user_draft:
            serializer = ErrorResponseSerializer(
                message = f"This draft is already created"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )

        draft = await AdminSchema.admin_create_draft(
            request = request,
            user_id = admin_user
        )
        serializer = SuccessResponseSerializer(
            message = f"Draft Initialized",
            data = {
                "draft_id": draft.user_draft_id
            }
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def create_gst(cls, token, authorize, request:GstRequestResponseSerializer):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if request.gst_id:
            await AdminSchema.update_gst(
                request = request
            )
        else:
            await AdminSchema.create_gst(
                request= request
            )
        serializer = SuccessResponseSerializer(
            message="GST Value Added",
            status_code=status.HTTP_200_OK,
            data={}
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def get_gst(cls, token, authorize):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        gst_data = await AdminSchema.get_gst()
        gst_data = [GstRequestResponseSerializer(**(i._asdict())) for i in gst_data]
        serializer = SuccessResponseSerializer(
            message="get gst data",
            status=status.HTTP_200_OK,
            data=gst_data
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )

    @classmethod
    async def gst_calculation_list(cls, token, authorize, year):
        await auth_check(token=token, authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        gst_list_data = await AdminSchema.gst_calculation_list(
            year = year
        )
        gst_list_data = [GstListResponseSerializer(**(i._asdict())) for i in gst_list_data]

        serializer = SuccessResponseSerializer(
            message = "GST Calculation List",
            status = status.HTTP_200_OK,
            data = gst_list_data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def draft_detail(cls, token, authorize, user_draft_id):
        await auth_check(token=token, authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        user_draft = await AdminSchema.get_draft_detail(user_draft_id)
        if not user_draft:
            serializer = ErrorResponseSerializer(
                message = f"Draft with this draft id not found",
                status_code = status.HTTP_404_NOT_FOUND
            )
            return response_structure(
                serializer=serializer,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        data = AdminDraftDetailResponseSerializer(**(user_draft._asdict()))
        if user_draft.draft_for == DraftForEnum.SERIES:
            players_info = await AdminSchema.get_series_player_id_list(
                series_id = user_draft.draft_match_series_id
            )
            for player_info in players_info:
                player_id = player_info.player_id
                player = await AdminSchema.get_player_data_in_list(
                    player_id = player_id
                )
                player_data = [PlayersResponseSerializer(**(i._asdict())) for i in player]
                data.player_list = player_data
        else: # this is for match
            march_info = await DraftSchema.match_series_team(
                cricket_match_id = user_draft.draft_match_series_id
            )
            player_a = await DraftSchema.match_series_team_player(
                series_id = march_info.series_id,
                team_id = march_info.team_a
            )
            player_b = await DraftSchema.match_series_team_player(
                series_id = march_info.series_id,
                team_id = march_info.team_b
            )
            for player in player_a.player_id:
                player_data = await DraftSchema.get_player_data(
                    player_id = player
                )
                player_response = PlayersResponseSerializer(
                    **(player_data._asdict())
                )
                data.player_list.append(player_response)
            for player in player_b.player_id:
                player_data = await DraftSchema.get_player_data(
                    player_id = player
                )
                player_response = PlayersResponseSerializer(
                    **(player_data._asdict())
                )
                data.player_list.append(player_response)

        serializer = SuccessResponseSerializer(
            message = UserConstant.FETCH_ALL_SUCCESS,
            status_code = status.HTTP_200_OK,
            data = data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def member_detail(cls, token, authorize, user_draft_id):
        await auth_check(token=token,authorize=authorize)

        draft_data = await AdminSchema.member_detail(
            user_draft_id = user_draft_id
        )
        data = []
        for member in draft_data:
            member_detail = MemberDetailResponseSerialzier(**(member._asdict()))
            if member.captain:
                captain_detail = await AdminSchema.get_player_data_individual(
                    player_id = member.captain
                )
                member_detail.captain_detail = PlayersResponseSerializer(**(captain_detail._asdict()))
            if member.vice_captain:
                vice_captain_detail = await AdminSchema.get_player_data_individual(
                    player_id = member.vice_captain
                )
                member_detail.vice_captain_detail = PlayersResponseSerializer(**(vice_captain_detail._asdict()))
            if member.player_selected:
                player_list = await AdminSchema.get_player_data_in_list(
                    player_id = member.player_selected
                )
                member_detail.player_list = [PlayersResponseSerializer(**(i._asdict())) for i in player_list]
            data.append(member_detail)
        serializer = SuccessResponseSerializer(
            message = "Member Detail",
            data = data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )


    @classmethod
    async def change_match_status(cls, token, authorize, match_id, is_live):
        await auth_check(token=token, authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        match = await CricketMatchSchema.get_matches(
            match_id = match_id,
            limit = 10,
            offset = 1
        )

        if not match:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = f"Unable to find match with this status"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )
        await CricketMatchSchema.update_cricket_match_status(
            match_id = match_id,
            is_live = is_live
        )

        serializer = SuccessResponseSerializer(
            status_code = status.HTTP_200_OK,
            message = "Status Updated for the match"
        )
        return response_structure(
            status_code = status.HTTP_200_OK,
            serializer = serializer
        )

    @classmethod
    async def change_series_status(cls, token, authorize, series_id, is_live):
        await auth_check(token=token, authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        series = await CricketMatchSchema.get_series(
            series_id = series_id,
            limit = 10,
            offset = 1
        )

        if not series:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = f"Unable to find series with this status"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )
        await CricketMatchSchema.update_cricket_series_status(
            series_id = series_id,
            is_live = is_live
        )

        serializer = SuccessResponseSerializer(
            status_code = status.HTTP_200_OK,
            message = "Status Updated for the series"
        )
        return response_structure(
            status_code = status.HTTP_200_OK,
            serializer = serializer
        )

    @classmethod
    async def get_gst_individual(cls, token, authorize, month, year, email: EmailStr = None, is_export: bool = True ):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if is_export:  
            csv_data = await ExportCSVController.export_gst_list(
                year = year,
                month = month,
                email = email
            )
            return FileResponse(path=csv_data.data)

        gst_data = await AdminSchema.gst_calculation_individual_list(
            month = month,
            year = year
        )
        gst_data = [GstIndividualCalculationResponseSerializer(**(i._asdict())) for i in gst_data]
        serializer = SuccessResponseSerializer(
            message = "Gst Individual List",
            status = status.HTTP_200_OK,
            data = gst_data
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )

    @classmethod
    async def get_gst_year(cls, token, authorize):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        gst_year = await AdminSchema.get_gst_year()
        gst_year = [i.year for i in gst_year]
        serializer = SuccessResponseSerializer(
            message = "GST Year",
            data = gst_year
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )

    @classmethod
    async def gst_pay(cls, token, authorize, gst_calculation_id, year, month):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if not gst_calculation_id and not year and not month:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                message = f"Either pass gst_calculation_id or (year and month) in request parameter"
            )
            return response_structure(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                serializer = serializer
            )

        if gst_calculation_id and year and month:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                message = f"You can not pass gst_calculation_id, year and month together"
            )
            return response_structure(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                serializer = serializer
            )

        if (year and not month) or (not year and month):
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                message = f"year and month should be together"
            )
            return response_structure(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                serializer = serializer
            )

        if year and month:
            await AdminSchema.gst_pay(
                year = year,
                month = month
            )
            serializer = SuccessResponseSerializer(
                message = f"Paid GST for entire month"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )

        if gst_calculation_id:
            await AdminSchema.gst_pay(
                gst_calculation_id = gst_calculation_id
            )
            serializer = SuccessResponseSerializer(
                message = f"Paid GST for this user"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )

        serializer = ErrorResponseSerializer(
            message = f"There is some error"
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_400_BAD_REQUEST
        )

    @classmethod
    async def get_all_transaction(cls, token, authorize, limit, offset, search_text:str=None, start_date=None, end_date=None, email: EmailStr = None, is_export: bool = True):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        if is_export:  
            csv_data = await ExportCSVController.export_transaction_list(
                search_text = search_text,
                start_date = start_date,
                end_date = end_date,
                email = email
            )
            return FileResponse(path=csv_data.data)

        user_transaction = await UserProfileSchema.get_all_transaction(
            limit = limit,
            offset = offset,
            search_text = search_text,
            start_date = start_date,
            end_date = end_date
        )
        data = [TransactionAllResponseSerializer(**i._asdict()) for i in user_transaction] if user_transaction else []
        serializer = SuccessResponseSerializer(
            message = "All Transactions",
            status_code = status.HTTP_200_OK,
            data = data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )
    
    @classmethod
    async def get_home_screen(cls, token, authorize,homescreen_id:UUID4=None,limit:int=10,offset:int=1):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        get_home_screen = await AdminSchema.get_home_screen(
            homescreen_id = homescreen_id,
            limit = limit,
            offset = offset
        )
        if homescreen_id:
            serializer = SuccessResponseSerializer(
                message =  UserConstant.HOME_SCREEN_DETAIL,
                data = HomeScreenResponseSerializer.from_orm(get_home_screen),
                status_code=status.HTTP_200_OK
            )
        else:
            serializer = SuccessResponseSerializer(
                message=UserConstant.HOME_SCREEN_LIST,
                data = [HomeScreenResponseSerializer.from_orm(i) for i in get_home_screen],
                status_code=status.HTTP_200_OK
            )
        return response_structure(
            serializer = serializer,
            status_code= serializer.status_code
        )

    @classmethod
    async def home_screen(cls, token, request: HomeScreeenRequestSerializer, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        if user_id:
            home_screen_data = await AdminSchema.add_home_screen(
                request = request,
            )
            if home_screen_data:
                serializer = SuccessResponseSerializer(
                    status_code=status.HTTP_200_OK,
                    message=UserConstant.HOME_SCREEN_ADDED,
                    data= HomeScreenResponseSerializer.from_orm(home_screen_data)
                )
            else:
                serializer = ErrorResponseSerializer(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    message=UserConstant.HOME_SCREEN_ERROR,
                    data = None
                )
        else:
            serializer = ErrorResponseSerializer(
                message=UserConstant.NOT_ADMIN,
                data = None,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        return response_structure(
            serializer = serializer,
            status_code= serializer.status_code
        )
    
    @classmethod
    async def update_home_screen(cls, token, request: HomeScreeenUpdateSerializer, authorize, homescreen_id:UUID4):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        await AdminSchema.update_home_screen(
            homescreen_id = homescreen_id,
            value_dict = request.dict(
                exclude_none = True,
                exclude_defaults = True,
                exclude_unset = True
            )
        )
        return response_structure(
            serializer = SuccessResponseSerializer(),
            status_code= status.HTTP_200_OK
        )

    @classmethod
    async def delete_home_screen(cls,token,homescreen_id,authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        await AdminSchema.delete_home_screen(
            homescreen_id=homescreen_id
        )
        return response_structure(
            serializer=SuccessResponseSerializer(),
            status_code=status.HTTP_200_OK
        )
    @classmethod
    async def create_tds(cls, token, authorize, request:TdsRequestResponseSerializer):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if request.tds_id:
            await AdminSchema.update_tds(
                request = request
            )
        else:
            await AdminSchema.create_tds(
                request= request
            )
        serializer = SuccessResponseSerializer(
            message="TDS Value Added",
            status_code=status.HTTP_200_OK,
            data={}
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )

    @classmethod
    async def get_tds(cls, token, authorize):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        tds_data = await AdminSchema.get_tds()
        tds_data = [TdsRequestResponseSerializer(**(i._asdict())) for i in tds_data]
        serializer = SuccessResponseSerializer(
            message="TDS Data",
            status=status.HTTP_200_OK,
            data=tds_data
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )

    @classmethod
    async def get_tds_year(cls, token, authorize):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        tds_year = await AdminSchema.get_tds_year()
        tds_year = [i.year for i in tds_year]
        serializer = SuccessResponseSerializer(
            message = "tds Year",
            data = tds_year
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )

    @classmethod
    async def tds_calculation_list(cls, token, authorize, year):
        await auth_check(token=token, authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        tds_list_data = await AdminSchema.tds_calculation_list(
            year = year
        )
        tds_list_data = [TdsListResponseSerializer(**(i._asdict())) for i in tds_list_data]

        serializer = SuccessResponseSerializer(
            message = "TDS Calculation List",
            status = status.HTTP_200_OK,
            data = tds_list_data
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )
    
    @classmethod
    async def get_tds_individual(cls, token, authorize, month, year, email: EmailStr = None, is_export: bool = True ):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if is_export:  
            csv_data = await ExportCSVController.export_tds_list(
                year = year,
                month = month,
                email = email
            )
            return FileResponse(path=csv_data.data)

        tds_data = await AdminSchema.tds_calculation_individual_list(
            month = month,
            year = year
        )
        tds_data = [TdsIndividualCalculationResponseSerializer(**(i._asdict())) for i in tds_data]
        serializer = SuccessResponseSerializer(
            message = "TDS Individual List",
            status = status.HTTP_200_OK,
            data = tds_data
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )
    
    @classmethod
    async def tds_pay(cls, token, authorize, tds_calculation_id, year, month):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if not tds_calculation_id and not year and not month:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                message = f"Either pass tds_calculation_id or (year and month) in request parameter"
            )
            return response_structure(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                serializer = serializer
            )

        if tds_calculation_id and year and month:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                message = f"You can not pass tds_calculation_id, year and month together"
            )
            return response_structure(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                serializer = serializer
            )

        if (year and not month) or (not year and month):
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                message = f"year and month should be together"
            )
            return response_structure(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                serializer = serializer
            )

        if year and month:
            await AdminSchema.tds_pay(
                year = year,
                month = month
            )
            serializer = SuccessResponseSerializer(
                message = f"Paid TDS for entire month"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )

        if tds_calculation_id:
            await AdminSchema.tds_pay(
                tds_calculation_id = tds_calculation_id
            )
            serializer = SuccessResponseSerializer(
                message = f"Paid TDS for this user"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )

        serializer = ErrorResponseSerializer(
            message = f"There is some error"
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_400_BAD_REQUEST
        )
    
    @classmethod
    async def add_cash_bonus_discount(cls, token, authorize, request:DiscountRequestResponseSerializer):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        if request.cash_bonus_discount_id:
            await AdminSchema.update_discount(
                request = request
            )
        else:
            await AdminSchema.create_discount(
                request= request
            )
        serializer = SuccessResponseSerializer(
            message="Cash Bouns Dicount Data Added",
            status_code=status.HTTP_200_OK,
            data={}
        )
        return response_structure(
            serializer=serializer,
            status_code=status.HTTP_200_OK
        )
    
    @classmethod
    async def get_cash_bonus_discount(cls, token, authorize):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        cash_bonus_data = await AdminSchema.get_discount()
        cash_bonus_data = [DiscountRequestResponseSerializer(**(i._asdict())) for i in cash_bonus_data]
        serializer = SuccessResponseSerializer(
            message = "Cash Bouns Dicount Data",
            status = status.HTTP_200_OK,
            data = cash_bonus_data
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )
    
    @classmethod
    async def get_all_draft_list(cls, token, authorize , limit, offset, search_text:str=None, start_date=None, end_date=None):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        draft_list = await DraftSchema.get_draft_data(
            is_list = True,
            limit = limit,
            offset = offset,
            search_text=search_text,
            start_date = start_date,
            end_date = end_date
        )
        result = []
        for i in draft_list:
            draft_data = DraftResponseSerialzier(**(i._asdict()))
            if draft_data.draft_for == DraftForEnum.MATCH:
                data = await CricketMatchSchema.get_matches(
                    match_id = draft_data.draft_match_series_id,
                    limit=10,
                    offset=1
                )
            else: # this is for series
                data = await CricketMatchSchema.get_series(
                    series_id = draft_data.draft_match_series_id
                )
            if not data.series_use_name:
                draft_data.series_name = data.series_fc_name
            else:
                draft_data.series_name = data.series_name
            if draft_data.draft_for == DraftForEnum.MATCH:
                if not data.use_short_name_a:
                    draft_data.team_short_name_a = data.fc_short_name_a
                else:
                    draft_data.team_short_name_a = data.team_short_name_a
                if not data.use_short_name_b:
                    draft_data.team_short_name_b = data.fc_short_name_b
                else:
                    draft_data.team_short_name_b = data.team_short_name_b
            result.append(draft_data)
        serializer = SuccessResponseSerializer(
            message = "Draft List",
            data = result
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def winning_distribution_for_draft(cls, user_draft_ids):
        for user_draft_id in user_draft_ids:
            draft_data = await DraftSchema.get_draft_data(
                user_draft_id = user_draft_id
            )
            if draft_data.draft_for == DraftForEnum.MATCH:
                data = await DraftSchema.get_completed_match(
                    user_draft_id = user_draft_id
                )
            else: # this is for series
                data = await DraftSchema.get_completed_series(
                    user_draft_id = user_draft_id
                )
            if len(data) > 0:
                unique_draft_ids = []
                for i in data:
                    if i.user_draft_id not in unique_draft_ids:
                        unique_draft_ids.append(i.user_draft_id)
                        user_draft = await DraftSchema.get_draft_data(
                            user_draft_id = i.user_draft_id
                        )
                        contest_member = await DraftSchema.get_contest_member(
                            draft_id = i.user_draft_id,
                            is_list = True,
                            by_points = True
                        )
                        price = user_draft.winners_price
                        new_price = {}
                        for p,q in price.items():
                            if len(p) > 1:
                                var = p.split("-")
                                for i in range(int(var[0]), int(var[1]) + 1):
                                    new_price[int(i)] = q
                            else:
                                new_price[int(p)] = q

                        for member in range(len(contest_member)):
                            if member+1 in new_price:
                                await DraftSchema.update_contest_member(
                                    draft_id = contest_member[member].draft_id,
                                    user_id = contest_member[member].user_id,
                                    value_dict = {"amount": new_price[member + 1], "position": member + 1}
                                )

                                await UserProfileSchema.add_update_amount(
                                    user_id = contest_member[member].user_id,
                                    winning_amount = int(new_price[member + 1]),
                                    meta_data = {
                                        "user_draft_id": str(contest_member[member].draft_id)
                                    }
                                )

                                ########### Notification and Mail for Won Money
                                user_data = await UserProfileSchema.get_user_data(
                                    user_id = contest_member[member].user_id,
                                    with_base = True
                                )
                                notification_data = {
                                    "title": "Money Won",
                                    "body": NotificationConstant.MONEY_WON.format(new_price[member + 1], i.league_name)
                                }
                                notification = await NotificationSchema.add_notification(
                                    user_id = contest_member[member].user_id,
                                    message = notification_data["body"]
                                )
                                await send_notification(
                                    user_id = contest_member[member].user_id,
                                    data = notification_data,
                                    notification_id = notification.notification_id
                                )
                                notification_data["body"] = money_won_html.format(
                                    amount = new_price[member + 1],
                                    draft_name = i.league_name,
                                    android_link = "#",
                                    ios_link = "#"
                                )
                                await send_mail_notification(
                                    notification_data = notification_data,
                                    email = user_data.email
                                )
                                ##########
                            else:
                                await DraftSchema.update_contest_member(
                                    draft_id = contest_member[member].draft_id,
                                    user_id = contest_member[member].user_id,
                                    value_dict = {"amount": 0, "position": member + 1}
                                )
                                ########### Notification and Mail for Loss Money
                                user_data = await UserProfileSchema.get_user_data(
                                    user_id = contest_member[member].user_id,
                                    with_base = True
                                )
                                notification_data = {
                                    "title": "Money Loss",
                                    "body": NotificationConstant.MONEY_LOSS
                                }
                                notification = await NotificationSchema.add_notification(
                                    user_id = contest_member[member].user_id,
                                    message = notification_data["body"]
                                )
                                await send_notification(
                                    user_id = contest_member[member].user_id,
                                    data = notification_data,
                                    notification_id = notification.notification_id
                                )
                                notification_data["body"] = money_lost_html.format(
                                    android_link = "#",
                                    ios_link = "#"
                                )
                                await send_mail_notification(
                                    notification_data = notification_data,
                                    email = user_data.email
                                )
                                ##########
                        await DraftSchema.update_draft_data(
                            user_draft_id = i.user_draft_id,
                            value_dict = {"is_result_announce": True}
                        )
        return response_structure(
            status_code = status.HTTP_200_OK,
            serializer = SuccessResponseSerializer(
               data = {}
            )
        )

    @classmethod
    async def is_winner_available(cls, draft_match_series_id, draft_for):
        user_draft_ids = []
        if draft_for == DraftForEnum.MATCH:
            data = await CricketMatchSchema.get_match_with_cricket_match_id(
                cricket_match_id = draft_match_series_id
            )
            if data:
                # match_status = await EntitySportsLive.entity_match_status(
                #     match_id = data.match_id
                # )
                #if match_status["status"] == 2: # completed
                ist_time = datetime.now() + timedelta(hours=5, minutes=30)
                if data.match_start_time <= ist_time:
                    drafts = await DraftSchema.get_draft_data(
                        is_list = True,
                        draft_for = draft_for,
                        is_draft_completed = True,
                        draft_match_series_id = draft_match_series_id
                    )
                    for draft in drafts:
                        if draft.is_draft_completed and not draft.is_result_announce:
                            user_draft_ids.append(draft.user_draft_id)
                    if user_draft_ids:
                        serializer = SuccessResponseSerializer(
                            data = {
                                "show": True,
                                "user_draft_ids": user_draft_ids
                            }
                        )
                    else:
                        serializer = SuccessResponseSerializer(
                            data = {
                                "show": False,
                                "user_draft_ids": user_draft_ids
                            }
                        )
                else:
                    serializer = SuccessResponseSerializer(
                        data = {
                            "show": False,
                            "user_draft_ids": user_draft_ids
                        }
                    )
            else:
                serializer = SuccessResponseSerializer(
                    data = {
                        "show": False,
                        "user_draft_ids": user_draft_ids
                    }
                )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )

        else: # for series
            data = await CricketMatchSchema.get_series(
                series_id = draft_match_series_id
            )
            if data:
                series_status = await EntitySportsLive.entity_series_status(
                    series_id = data.series_id
                )
                if series_status["status"] == "result": # completed
                    drafts = await DraftSchema.get_draft_data(
                        is_list = True,
                        draft_for = draft_for,
                        is_draft_completed = True,
                        draft_match_series_id = draft_match_series_id
                    )
                    for draft in drafts:
                        if draft.is_draft_completed and not draft.is_result_announce:
                            user_draft_ids.append(draft.user_draft_id)
                    if user_draft_ids:
                        serializer = SuccessResponseSerializer(
                            data = {
                                "show": True,
                                "user_draft_ids": user_draft_ids
                            }
                        )
                    else:
                        serializer = SuccessResponseSerializer(
                            data = {
                                "show": False,
                                "user_draft_ids": user_draft_ids
                            }
                        )
                else:
                    serializer = SuccessResponseSerializer(
                        data = {
                            "show": False,
                            "user_draft_ids": user_draft_ids
                        }
                    )
            else:
                serializer = SuccessResponseSerializer(
                    data = {
                        "show": False,
                        "user_draft_ids": user_draft_ids
                    }
                )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )
        
    @classmethod
    async def add_amount(cls, request: AdminAddAmountRequestSerializer):

        if request.token != "d1yt0o8h0l":
            serializer = ErrorResponseSerializer(
                message = "Token Not Valid"
            )
            return response_structure(
                serializer = serializer,
                status_code = serializer.status_code
            )

        user_data = await UserProfileSchema.get_user_data(
            mobile = request.mobile,
            with_base = True
        )
    
        if not user_data:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = "User not found"
            )
            return response_structure(
                serializer=serializer,
                status_code=status.HTTP_404_NOT_FOUND
            )

        user_id = user_data.user_id
            

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
        notification_data["body"] = money_deposited_html.format(
            amount = added_amount,
            android_link = "#",
            ios_link = "#"
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
        notification_data["body"] = money_bonus_html.format(
            bonus_amount = cash_bonus_amount,
            android_link = "#",
            ios_link = "#"
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
    async def cancel_draft(cls, token: str ,invitation_code):
        
        if token != "d1yt0o8h0l":
            serializer = ErrorResponseSerializer(
                message = "Token Not Valid"
            )
            return response_structure(
                serializer = serializer,
                status_code = serializer.status_code
            )

        user_draft = await DraftSchema.get_draft_data(
            invitation_code = invitation_code
        )

        if user_draft and not user_draft.is_draft_cancelled:
            if not user_draft.is_result_announce:
                await AdminSchema.update_draft_status(user_draft.user_draft_id)

                serializer = SuccessResponseSerializer(
                    status_code = status.HTTP_200_OK,
                    message = f"Draft cancelled successful"
                )
                return response_structure(
                    status_code = status.HTTP_404_NOT_FOUND,
                    serializer = serializer
                )
            else:
                serializer = ErrorResponseSerializer(
                message = f"Result is announced, so you can't cancel this draft"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )
        else:
            serializer = ErrorResponseSerializer(
                message = f"Draft not found"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )



class ExportCSVController():

    @classmethod
    async def export_tds_list(cls, month, year,email):
        tds_list = await AdminSchema.tds_calculation_individual_list(
            month = month,
            year = year
        )

        csv_filename = f'src/files/Tds_List_{uuid.uuid4()}.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = [
                'name', 
                'mobile', 
                'tds_value', 
                'is_paid', 
                'total', 
                'tds_calculation_id', 
                'email', 
                'user_id', 
                'year', 
                'amount', 
                'month'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for tds_data in tds_list:
                writer.writerow(tds_data._asdict())

        subject = 'Tds List CSV'
        sender_email = 'afsanamemon13.py@gmail.com'  
        receiver_email = email
        body = 'Please find attached the user list CSV file.'
        send_email_with_attachment(subject, sender_email, receiver_email, body, csv_filename,
                                'Tds_list.csv', Config.MAIL_FROM, Config.MAIL_PASSWORD)
        serializer = SuccessResponseSerializer(
            message = "CSV Export Successfully",
            data = csv_filename
        )
        return serializer

    @classmethod
    async def export_gst_list(cls,month, year, email):
        gst_list = await AdminSchema.gst_calculation_individual_list(
            month = month,
            year = year
        )

        csv_filename = f'src/files/Gst_List_{uuid.uuid4()}.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = [
                'is_paid', 
                'name',
                'mobile', 
                'gst_value', 
                'total', 
                'gst_calculation_id', 
                'email', 
                'user_id', 
                'year', 
                'amount', 
                'month'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for gst_data in gst_list:
                writer.writerow(gst_data._asdict())

        subject = 'Gst List CSV'
        sender_email = 'afsanamemon13.py@gmail.com'  
        receiver_email = email
        body = 'Please find attached the user list CSV file.'
        send_email_with_attachment(subject, sender_email, receiver_email, body, csv_filename,
                                'Gst_list.csv', Config.MAIL_FROM, Config.MAIL_PASSWORD)
        serializer = SuccessResponseSerializer(
            message = "CSV Export Successfully",
            data = csv_filename
        )
        return serializer

    @classmethod
    async def export_transaction_list(cls, email, search_text:str=None, start_date: date = None, end_date: date = None):
        transaction_list = await UserProfileSchema.get_all_transaction(
            search_text = search_text,
            start_date = start_date,
            end_date = end_date
        )

        csv_filename = f'src/files/Transaction_list_{uuid.uuid4()}.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = [
                'transaction_id',
                'name', 
                'user_id', 
                'email',
                'mobile', 
                'amount', 
                'transaction_status', 
                'transaction_type', 
                'created_at',
                'updated_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for transaction in transaction_list:
                transaction_dict = dict(transaction._asdict())
                if transaction_dict["transaction_type"]:
                    transaction_dict["transaction_type"] = transaction_dict["transaction_type"].value
                if transaction_dict["transaction_status"]:
                    transaction_dict["transaction_status"] = transaction_dict["transaction_status"].value
                writer.writerow(transaction_dict)

        subject = 'Transaction list csv'
        sender_email = 'afsanamemon13.py@gmail.com'  
        receiver_email = email
        body = 'Please find attached the user list CSV file.'
        send_email_with_attachment(subject, sender_email, receiver_email, body, csv_filename,
                                'Transaction_list.csv', Config.MAIL_FROM, Config.MAIL_PASSWORD)
        serializer = SuccessResponseSerializer(
            message = "CSV Export Successfully",
            data = csv_filename
        )
        return serializer
    
    @classmethod
    async def user_list_csv(cls, email, search_text:str=None):
        user_list = await AdminSchema.user_list(
            search_text = search_text
        )
        # Create CSV file
        csv_filename = f'src/files/User_List_{uuid.uuid4()}.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames =  [
                'user_id',
                'name',
                'dob',
                'gender',
                'profile_image', 
                'email',
                'mobile', 
                'address', 
                'is_email_verified', 
                'is_admin',
                'city', 
                'state',
                'country',
                'pan_number',
                'is_pan_verified',
                'account_number',
                'is_bank_account_verified',
                'pin_code',
                'team_name'
                'team_id',
                'team_code',
                'team_leader_id',
                'referral_code'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for user in user_list:
                user_dict = dict(user._asdict())
                if user_dict["is_pan_verified"]:
                    user_dict["is_pan_verified"] = user_dict["is_pan_verified"].value
                if user_dict["is_bank_account_verified"]:
                    user_dict["is_bank_account_verified"] = user_dict["is_bank_account_verified"].value
                user_dict.pop('city_id', None)
                user_dict.pop('state_id', None)
                user_dict.pop('country_id', None)
                user_dict.pop('team_name', None)
                writer.writerow(user_dict)
            
        # Send email with the CSV file attached
        subject = 'User List CSV'
        sender_email = 'afsanamemon13.py@gmail.com'  
        receiver_email = email
        body = 'Please find attached the user list CSV file.'
        send_email_with_attachment(subject, sender_email, receiver_email, body, csv_filename,
                                'user_list.csv', Config.MAIL_FROM, Config.MAIL_PASSWORD)
        serializer = SuccessResponseSerializer(
            message = "CSV Export Successfully",
            data = csv_filename
        )
        return serializer

    @classmethod
    async def download_csv_and_send_email(cls, token, authorize, csv_type, limit, offset, email):  
        # await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()
        
        if csv_type == 1:
            csv_data =await cls.user_list_csv(
                email=email,
                limit = limit,
                offset = offset
            )
            serializer  = FileResponse(path=csv_data.data)

            
        elif csv_type == 2:
            csv_data =await cls.export_tds_list(
                email=email
            )
            serializer  = FileResponse(path=csv_data.data)
        
        elif csv_type == 3:
            csv_data =await cls.export_gst_list(
                email=email
            )
            serializer  = FileResponse(path=csv_data.data)

        elif csv_type == 4:
            csv_data =await cls.export_transaction_list(
                email=email
            )
            serializer  = FileResponse(path=csv_data.data)
    
        else:
            serializer = ErrorResponseSerializer(
            message = f"Invalid csv_type parameter. Use 1 for user, 2 for tds, and 3 for gst, 4 for transaction"
        )
        return FileResponse(path=csv_data.data)

class CricketSeries():
    
    @classmethod
    async def list_series(cls, token, authorize, limit, offset, search_text:str=None):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        cricket_series = await AdminSchema.list_series(
            limit = limit,
            offset = offset,
            search_text = search_text
        )
        data = [CricketSeriesResponseSerializer(**(i._asdict())) for i in cricket_series]
        serializer = SuccessResponseSerializer(
            message = "cricket series list",
            data = data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )
    
    @classmethod
    async def update_series(cls, token, request: CricketSeriesRequestSerialzier, authorize, cricket_series_id):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        await AdminSchema.update_series(
            cricket_series_id,
            request.dict(exclude_none=True, exclude_unset=True)
        )

        return response_structure(
            serializer = SuccessResponseSerializer(),
            status_code = status.HTTP_200_OK
        )
        
    @classmethod
    async def get_series_individual(cls, token, authorize, cricket_series_id):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        cricket_series = await AdminSchema.get_series_individual(
            cricket_series_id
        )
        serializer = SuccessResponseSerializer(
            message = "cricket_series Individual List",
            status = status.HTTP_200_OK,
            data = CricketSeriesResponseSerializer(**(cricket_series._asdict()))
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )
    
class CricketTeam():

    @classmethod
    async def list_team(cls, token, authorize, limit, offset, search_text:str=None):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        cricket_team = await AdminSchema.list_team(
            limit = limit,
            offset = offset,
            search_text = search_text
        )
        data = [CricketTeamResponseSerializer(**(i._asdict())) for i in cricket_team]
        serializer = SuccessResponseSerializer(
            message = "cricket team list",
            data = data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )
    
    @classmethod
    async def update_team(cls, token, request: CricketTeamRequestSerialzier, authorize, cricket_team_id):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        await AdminSchema.update_team(
            cricket_team_id,
            request.dict(exclude_none=True, exclude_unset=True),
            user_id = admin_user_id
        )

        return response_structure(
            serializer = SuccessResponseSerializer(),
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def get_team_individual(cls, token, authorize, cricket_team_id):
        await auth_check(token=token,authorize=authorize)
        admin_user = authorize.get_jwt_subject()

        cricket_team = await AdminSchema.get_team_individual(
            cricket_team_id
        )
        serializer = SuccessResponseSerializer(
            message = "cricket_team Individual List",
            status = status.HTTP_200_OK,
            data = CricketTeamResponseSerializer(**(cricket_team._asdict()))
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )
    
class SearchFunctionality():

    @classmethod
    async def user_search(cls, token, search_data ,authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        Search_data = await SearchFunctionalitySchema.user_search(
            search_data= search_data
        )
        serializer = SuccessResponseSerializer(
            message = "search data",
            status = status.HTTP_200_OK,
            data = [UserSearchResult(**(i._asdict())) for i in Search_data]
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )
    
    @classmethod
    async def all_draft_search(cls, token, search_data ,authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        Search_data = await SearchFunctionalitySchema.all_draft_search(
            search_data= search_data
        )
        serializer = SuccessResponseSerializer(
            message = "search data",
            status = status.HTTP_200_OK,
            data = [AllDraftSearchResult(**(i._asdict())) for i in Search_data]
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )
    
    @classmethod
    async def match_search(cls, token, search_data ,authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        Search_data = await SearchFunctionalitySchema.match_search(
            search_data= search_data
        )
        serializer = SuccessResponseSerializer(
            message = "search data",
            status = status.HTTP_200_OK,
            data = [MatchSearchResult(**(i._asdict())) for i in Search_data]
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )
    
    @classmethod
    async def series_search(cls, token, search_data ,authorize):
        await auth_check(authorize=authorize, token=token)
        admin_user_id = authorize.get_jwt_subject()

        Search_data = await SearchFunctionalitySchema.series_search(
            search_data= search_data
        )
        serializer = SuccessResponseSerializer(
            message = "search data",
            status = status.HTTP_200_OK,
            data = [SeriesSearchResult(**(i._asdict())) for i in Search_data]
        )
        return response_structure(
            serializer = serializer,
            status_code= status.HTTP_200_OK
        )