import uuid
from fastapi import Depends
from sqlalchemy import (
    select, 
    update,
    cast,
    Integer,
    func,
    extract,
    and_,
    or_,
    delete,
    cast, 
    TEXT
)
from pydantic import UUID4, BaseModel
from fastapi_jwt_auth import AuthJWT
#Local Imports
from src.db.database import db
from src.db.models import (
    BankVerification,
    MasterCity,
    MasterCountry,
    MasterState,
    PanVerification,
    User,
    GST,
    UserDraft,
    ContestPlayers,
    GstCalculation,
    TdsCalculation,
    TDS,
    CashBonusDiscount,
    CricketSeries,
    CricketTeam,
    HomeScreen,
    CricketMatch,
    UserTransaction
)
from src.services.admin.serializer import (
    AdminCreateDraftRequestSerializer, 
    GstRequestResponseSerializer, 
    TdsRequestResponseSerializer, 
    DiscountRequestResponseSerializer, 
    HomeScreenResponseSerializer,
    HomeScreeenRequestSerializer
)
from src.db.models import ContestPlayers
from src.services.admin.serializer import AdminCreateDraftRequestSerializer
from src.services.contest.schema import DraftSchema
from src.utils.helper_functions import S3Config

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

@AuthJWT.load_config
def get_config():
    return Settings()

Authorize : AuthJWT = Depends()

class AdminSchema():

    @classmethod
    async def user_list(cls, limit, offset,search_text:str=None):
        if search_text:
            sport_team = select(
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
                BankVerification.account_number,
                BankVerification.status.label("is_bank_account_verified"),
                User.pin_code,
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
                PanVerification.user_id == User.user_id,
                isouter = True
            ).join(
                BankVerification,
                BankVerification.user_id == User.user_id,
                isouter = True
            ).where(
                or_(
                    User.name.ilike(f"%{search_text}%"),
                    User.email.ilike(f"%{search_text}%"),
                    User.mobile.ilike(f"%{search_text}%"),
                    User.address.ilike(f"%{search_text}%"),
                )
            ).limit(
                limit
            ).offset(
                offset-1
            )
            sport_team = await db.execute(sport_team)
            return sport_team.all()

        sport_team = select(
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
            BankVerification.account_number,
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
            PanVerification.user_id == User.user_id,
            isouter = True
        ).join(
            BankVerification,
            BankVerification.user_id == User.user_id,
            isouter = True
        ).limit(
            limit
        ).offset(
            offset-1
        )
        sport_team = await db.execute(sport_team)
        return sport_team.all()

    @classmethod
    async def get_draft_detail(cls, user_draft_id):
        return await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )

    @classmethod
    async def get_series_player_id_list(cls, series_id):
        return await DraftSchema.match_series_team_player(
            series_id = series_id
        )

    @classmethod
    async def get_player_data_in_list(cls, player_id):
        return await DraftSchema.get_player_data(
            player_id = player_id,
            is_list = True
        )
    
    @classmethod
    async def get_player_data_individual(cls, player_id):
        return await DraftSchema.get_player_data(
            player_id = player_id,
            is_list = False
        )

    @classmethod
    async def member_detail(cls, user_draft_id):
        member_detail = select(
            ContestPlayers.player_selected,
            ContestPlayers.captain,
            ContestPlayers.vice_captain,
            ContestPlayers.amount,
            ContestPlayers.points,
            User.user_id,
            User.name,
            User.mobile,
            User.email,
            User.profile_image
        ).join(
            User,
            ContestPlayers.user_id == User.user_id,
        ).where(
            ContestPlayers.draft_id == user_draft_id
        )
        member_detail = await db.execute(member_detail)
        return member_detail.all()
    
    @classmethod
    async def admin_create_draft(cls, request: AdminCreateDraftRequestSerializer, user_id):
        add_draft = UserDraft(
            user_id = user_id,
            league_name = request.league_name,
            invitation_code = request.invitation_code,
            max_playing_user = request.max_playing_user,
            entry_amount = request.entry_amount,
            total_amount = request.entry_amount * request.max_playing_user,
            fantasy_commission = (request.entry_amount * request.max_playing_user)*0.1,
            winners_price = request.winners_price,
            player_choice = request.player_choice.dict(),
            draft_for = request.draft_for,
            draft_match_series_id = request.draft_match_series_id,
            is_public = request.is_public,
            draft_starting_time = request.draft_starting_time,
            is_draft_completed = False,
            number_of_round = request.number_of_round,
            top_picks = request.top_picks,
            player_selected = []
        )
        db.add(add_draft)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return add_draft

    @classmethod
    async def create_gst(cls, request: GstRequestResponseSerializer):
        add_percentage = GST(
            percentage = request.percentage,
            name = request.name
        )
        db.add(add_percentage)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return add_percentage
    
    @classmethod
    async def update_gst(cls, request: GstRequestResponseSerializer):
        value_dict = request.dict(
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True
        )
        value_dict.pop("gst_id")
        data = update(
            GST
        ).where(
            GST.gst_id == request.gst_id
        ).values(
            value_dict
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(data)
        try:
            await db.commit()
        except Exception:
            await db.rollback()

    @classmethod
    async def get_gst(cls):
        gst_data = select(
            GST.gst_id,
            GST.name,
            GST.percentage
        )
        gst_data = await db.execute(gst_data)
        return gst_data.all()
    
    @classmethod
    async def get_gst_year(cls):
        gst_year = select(
            GstCalculation.year
        ).distinct(
            GstCalculation.year
        ).order_by(
            GstCalculation.year.desc()
        )
        gst_year = await db.execute(gst_year)
        return gst_year.all()

    @classmethod
    async def gst_calculation_list(cls, year):
        gst_list_data = select(
            func.sum(GstCalculation.amount).label("amount"),
            func.sum(GstCalculation.gst_value).label("gst_value"),
            func.sum(GstCalculation.total).label("total"),
            GstCalculation.month,
            GstCalculation.year
        ).where(
            GstCalculation.year == year
        ).group_by(
            GstCalculation.month,
            GstCalculation.year
        )
        gst_list_data  = await db.execute(gst_list_data)
        return gst_list_data.all()

    @classmethod
    async def gst_calculation_individual_list(cls, month, year):
        gst_data = select(
            GstCalculation.gst_calculation_id,
            GstCalculation.amount,
            GstCalculation.gst_value,
            GstCalculation.total,
            GstCalculation.is_paid,
            GstCalculation.month,
            GstCalculation.year,
            User.user_id,
            User.name,
            User.email,
            User.mobile
        ).join(
            User,
            GstCalculation.user_id == User.user_id
        ).where(
            GstCalculation.month == month,
            GstCalculation.year == year
        )
        gst_data = await db.execute(gst_data)
        return gst_data.all()

    @classmethod
    async def gst_pay(cls, gst_calculation_id = None, year = None, month = None):
        if year and month:
            data = update(
                GstCalculation
            ).where(
                GstCalculation.month == month,
                GstCalculation.year == year
            ).values(
                {"is_paid": True}
            ).execution_options(
                synchronize_session="fetch"
            )
            await db.execute(data)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
        elif gst_calculation_id:
            data = update(
                GstCalculation
            ).where(
                GstCalculation.gst_calculation_id == gst_calculation_id
            ).values(
                {"is_paid": True}
            ).execution_options(
                synchronize_session="fetch"
            )
            await db.execute(data)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
        return True

    @classmethod
    async def create_tds(cls, request: TdsRequestResponseSerializer):
        add_percentage = TDS(
            percentage = request.percentage,
            name = request.name
        )
        db.add(add_percentage)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return add_percentage
    
    @classmethod
    async def update_tds(cls, request: TdsRequestResponseSerializer):
        value_dict = request.dict(
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True
        )
        value_dict.pop("tds_id")
        data = update(
            TDS
        ).where(
            TDS.tds_id == request.tds_id
        ).values(
            value_dict
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(data)
        try:
            await db.commit()
        except Exception:
            await db.rollback()

    @classmethod
    async def get_tds(cls):
        tds_data = select(
            TDS.tds_id,
            TDS.name,
            TDS.percentage
        )
        tds_data = await db.execute(tds_data)
        return tds_data.all()

    @classmethod
    async def get_tds_year(cls):
        tds_year = select(
            TdsCalculation.year
        ).distinct(
            TdsCalculation.year
        ).order_by(
            TdsCalculation.year.desc()
        )
        tds_year = await db.execute(tds_year)
        return tds_year.all()
    
    @classmethod
    async def tds_calculation_list(cls, year):
        tds_list_data = select(
            func.sum(TdsCalculation.amount).label("amount"),
            func.sum(TdsCalculation.tds_value).label("tds_value"),
            func.sum(TdsCalculation.total).label("total"),
            TdsCalculation.month,
            TdsCalculation.year
        ).where(
            TdsCalculation.year == year
        ).group_by(
            TdsCalculation.month,
            TdsCalculation.year
        )
        tds_list_data  = await db.execute(tds_list_data)
        return tds_list_data.all()
    
    @classmethod
    async def tds_calculation_individual_list(cls, month, year):
        tds_data = select(
            TdsCalculation.tds_calculation_id,
            TdsCalculation.amount,
            TdsCalculation.tds_value,
            TdsCalculation.total,
            TdsCalculation.is_paid,
            TdsCalculation.month,
            TdsCalculation.year,
            User.user_id,
            User.name,
            User.email,
            User.mobile
        ).join(
            User,
            TdsCalculation.user_id == User.user_id
        ).where(
            TdsCalculation.month == month,
            TdsCalculation.year == year
        )
        tds_data = await db.execute(tds_data)
        return tds_data.all()
    
    @classmethod
    async def tds_pay(cls, tds_calculation_id = None, year = None, month = None):
        if year and month:
            data = update(
                TdsCalculation
            ).where(
                TdsCalculation.month == month,
                TdsCalculation.year == year
            ).values(
                {"is_paid": True}
            ).execution_options(
                synchronize_session="fetch"
            )
            await db.execute(data)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
        elif tds_calculation_id:
            data = update(
                TdsCalculation
            ).where(
                TdsCalculation.tds_calculation_id == tds_calculation_id
            ).values(
                {"is_paid": True}
            ).execution_options(
                synchronize_session="fetch"
            )
            await db.execute(data)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
        return True
    
    @classmethod
    async def create_discount(cls, request: DiscountRequestResponseSerializer):
        cash_bonus = CashBonusDiscount(
            percentage = request.percentage,
            name = request.name
        )
        db.add(cash_bonus)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return cash_bonus

    @classmethod
    async def update_discount(cls, request: DiscountRequestResponseSerializer):
        value_dict = request.dict(
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True
        )
        value_dict.pop("cash_bonus_discount_id")
        data = update(
            CashBonusDiscount
        ).where(
            CashBonusDiscount.cash_bonus_discount_id == request.cash_bonus_discount_id
        ).values(
            value_dict
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(data)
        try:
            await db.commit()
        except Exception:
            await db.rollback()

    @classmethod
    async def get_discount(cls):
        cash_bonus = select(
            CashBonusDiscount.cash_bonus_discount_id,
            CashBonusDiscount.name,
            CashBonusDiscount.percentage
        )
        cash_bonus = await db.execute(cash_bonus)
        return cash_bonus.all()

    @classmethod
    async def list_series(cls, limit, offset, search_text:str=None):
        cricket_series = select(
            CricketSeries.cricket_series_id,
            CricketSeries.fc_name,
            CricketSeries.name,
            CricketSeries.use_name,
            CricketSeries.created_at
        ).order_by(
            CricketSeries.created_at.desc()
        ).limit(
            limit
        ).offset(
            offset-1
        )

        if search_text:
            cricket_series = cricket_series.where(
                or_(
                    cast(CricketSeries.fc_name, TEXT).ilike(f'%{search_text}%'),
                    cast(CricketSeries.name, TEXT).ilike(f'%{search_text}%'),
                    cast(CricketSeries.use_name, TEXT).ilike(f'%{search_text}%'),
                )
            )

        cricket_series = await db.execute(cricket_series)
        return cricket_series.all()
    
    @classmethod
    async def update_series(cls, cricket_series_id, update_data):
        update_cricket_series = (
            update(
                CricketSeries
            ).where(
                CricketSeries.cricket_series_id == cricket_series_id
            ).values(
                **update_data
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.execute(update_cricket_series)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
    
    @classmethod
    async def get_series_individual(cls, cricket_series_id):
        cricket_series = select(
            CricketSeries.cricket_series_id,
            CricketSeries.fc_name,
            CricketSeries.name,
            CricketSeries.use_name,
            CricketSeries.created_at
        ).where(
            CricketSeries.cricket_series_id == cricket_series_id
        )
        cricket_series = await db.execute(cricket_series)
        return cricket_series.one_or_none()

    @classmethod
    async def list_team(cls, limit, offset, search_text:str=None):
        cricket_team = select(
           CricketTeam.cricket_team_id,
           CricketTeam.short_name,
           CricketTeam.fc_short_name,
           CricketTeam.logo_url,
           CricketTeam.fc_logo_url,
           CricketTeam.use_short_name,
           CricketTeam.use_logo_url,
           CricketTeam.created_at
        ).order_by(
            CricketTeam.created_at.desc()
        ).limit(
            limit
        ).offset(
            offset-1
        )
        if search_text:
            cricket_team = cricket_team.where(
                or_(
                    cast(CricketTeam.short_name, TEXT).ilike(f'%{search_text}%'),
                    cast(CricketTeam.fc_short_name, TEXT).ilike(f'%{search_text}%'),
                    cast(CricketTeam.created_at, TEXT).ilike(f'%{search_text}%'),
                )
            )
        cricket_team = await db.execute(cricket_team)
        return cricket_team.all()
    
    @classmethod
    async def delete_home_screen(cls,homescreen_id:UUID4):
        await db.execute(
            delete(
                HomeScreen
            ).where(
                HomeScreen.homescreen_id == homescreen_id
            )
        )
        try:
            await db.commit()
        except:
            await db.rollback()
        return True

    @classmethod
    async def get_home_screen(cls,homescreen_id:UUID4=None,limit:int=10,offset:int=1):
        if homescreen_id:
            home_screen_query = select(
                HomeScreen
            ).where(
                HomeScreen.homescreen_id == homescreen_id
            )
            home_screen_data = await db.execute(home_screen_query)
            return home_screen_data.scalars().one_or_none()
        
        home_screen_query = select(
            HomeScreen
        ).order_by(
            HomeScreen.created_at.desc()
        ).limit(
            limit
        ).offset(
            offset-1
        )
        home_screen_data = await db.execute(home_screen_query)
        return home_screen_data.scalars().all()
    
    @classmethod
    async def add_home_screen(cls, request: HomeScreeenRequestSerializer):
        obj_name = f'{uuid.uuid4()}.jpg'
        S3Config.img_conversion(img_data=request.image,object_name=obj_name,file_path=f'HomeScreen')
        obj_name = f'HomeScreen/{obj_name}'
        request.image = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"
        home_screen_data = HomeScreen(
            image =request.image,
            title = request.title,
            is_active = request.is_active
        )
        db.add(home_screen_data)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            return None
        return home_screen_data
    
    @classmethod
    async def update_home_screen(cls, value_dict:dict, homescreen_id:UUID4):
        if value_dict.get("image") != None:
            obj_name = f'{uuid.uuid4()}.jpg'
            S3Config.img_conversion(img_data=value_dict['image'],object_name=obj_name,file_path=f'HomeScreen')
            obj_name = f'HomeScreen/{obj_name}'
            value_dict['image'] = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"
            
        update_home_screen = update(
            HomeScreen
        ).where(
            HomeScreen.homescreen_id == homescreen_id
        ).values(
            value_dict
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(update_home_screen)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return True
    
    @classmethod
    async def update_team(cls, cricket_team_id, update_data, user_id):
        if "fc_logo_url" in update_data:
            obj_name = f'{uuid.uuid4()}.jpg'
            S3Config.img_conversion(img_data=update_data['fc_logo_url'],object_name=obj_name,file_path=f'{user_id}/profile')
            obj_name = f'{user_id}/profile/{obj_name}'
            update_data['fc_logo_url'] = f"https://fantasy-staging-bucket.s3.ap-south-1.amazonaws.com/media/{obj_name}"

        update_cricket_team = (
            update(
                CricketTeam
            ).where(
                CricketTeam.cricket_team_id == cricket_team_id
            ).values(
                **update_data
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.execute(update_cricket_team)
        try:
            await db.commit()
        except Exception:
            await db.rollback()

    @classmethod
    async def get_team_individual(cls, cricket_team_id):
        cricket_team = select(
           CricketTeam.cricket_team_id,
           CricketTeam.short_name,
           CricketTeam.logo_url,
           CricketTeam.fc_short_name,
           CricketTeam.use_short_name,
           CricketTeam.fc_logo_url,
           CricketTeam.use_logo_url,
           CricketTeam.created_at
        ).where(
           CricketTeam.cricket_team_id == cricket_team_id
        )
        cricket_team = await db.execute(cricket_team)
        return cricket_team.one_or_none()
    
    @classmethod
    async def get_user_transaction(cls):
        user_data = select(
            UserTransaction.transaction_id,
            UserTransaction.amount,
            UserTransaction.transaction_type,
            UserTransaction.transaction_status,
            UserTransaction.created_at,
            UserTransaction.meta_data
        ).order_by(
            UserTransaction.created_at.desc()
        )

        user = await db.execute(user_data)
        return user.all()
    