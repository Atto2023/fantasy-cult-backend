#Third Party Imports
from pydantic import (
    BaseModel, 
    constr, 
    UUID4,
    EmailStr
)
from pydantic.types import (
    constr, 
    conint, 
    confloat
)
from typing import (
    List, 
    Optional
)
from datetime import datetime

from src.db.models import DraftForEnum
from src.services.contest.serializer import (
    PlayChoiceDraftRequestSerializer, 
    PlayersResponseSerializer
)

class DraftResponseSerialzier(BaseModel):
    user_draft_id: UUID4
    league_name: Optional[constr(min_length=1)]
    invitation_code: Optional[constr(min_length=1)]
    max_playing_user: Optional[conint(ge=2)]
    entry_amount: Optional[confloat(ge=0.0)]
    total_amount: Optional[confloat(ge=0.0)]
    fantasy_commission: Optional[confloat(ge=0.0)]
    winners_price: Optional[dict]
    player_choice: Optional[dict]
    draft_for: Optional[DraftForEnum]
    draft_match_series_id: Optional[UUID4]
    is_draft_completed: Optional[bool]
    is_result_announce: Optional[bool]
    is_public: Optional[bool]
    draft_starting_time: Optional[datetime]
    created_at: Optional[datetime]
    series_name: Optional[constr()] = ''
    team_short_name_a: Optional[constr()] = ''
    team_short_name_b: Optional[constr()] = ''


class AdminDraftDetailResponseSerializer(DraftResponseSerialzier):
    player_list: List[PlayersResponseSerializer] = []

class AdminCreateDraftRequestSerializer(BaseModel):
    league_name: constr(min_length=1)
    invitation_code: constr(min_length=1, max_length=6)
    max_playing_user: conint(gt=0)
    entry_amount: confloat(ge=0)
    winners_price: dict
    player_choice: PlayChoiceDraftRequestSerializer
    draft_for: DraftForEnum
    draft_match_series_id: UUID4
    draft_starting_time: datetime
    number_of_round: conint(ge=1)
    top_picks: conint(ge=1)
    is_captain_allowed: bool = True
    is_public: bool = True

class GstRequestResponseSerializer(BaseModel):
    gst_id: Optional[UUID4]
    percentage: confloat(ge = 0.0, le = 100.0)
    name: Optional[constr(min_length=1)] = "India"

class MemberDetailResponseSerialzier(BaseModel):
    user_id : UUID4
    name: Optional[constr()]
    email: Optional[EmailStr]
    mobile: Optional[constr()]
    profile_image: Optional[constr()]
    amount: Optional[confloat()] = 0.0
    points: Optional[confloat()] = 0.0
    captain_detail: Optional[PlayersResponseSerializer]
    vice_captain_detail: Optional[PlayersResponseSerializer]
    player_list: List[PlayersResponseSerializer] = []

class GstListResponseSerializer(BaseModel):
    amount: confloat(gt = 0.0) = 0.0
    gst_value: confloat(gt = 0.0) = 0.0
    total: confloat(gt=0.0)
    year: conint(ge=0)
    month: conint(ge=1,le=12)
    
class GstIndividualCalculationResponseSerializer(BaseModel):
    gst_calculation_id: Optional[UUID4]
    amount: Optional[confloat(gt=0.0)]
    gst_value: Optional[confloat(gt=0.0)]
    total: Optional[confloat(gt=0.0)]
    is_paid: Optional[bool]
    month: Optional[conint(ge=1,le=12)]
    year: Optional[conint(ge=0)]
    user_id: UUID4
    name: Optional[constr()]
    email: Optional[EmailStr]
    mobile: Optional[constr(min_length=1)]

class GstPaidRequestSerializer(BaseModel):
    gst_calculation_id: Optional[UUID4]
    month: Optional[conint(ge=1,le=12)]
    year: Optional[conint(ge=0)]

class TdsRequestResponseSerializer(BaseModel):
    tds_id: Optional[UUID4]
    percentage: confloat(ge = 0.0, le = 100.0)
    name: Optional[constr(min_length=1)] = "India"

class TdsListResponseSerializer(BaseModel):
    amount: confloat(gt = 0.0) = 0.0
    tds_value: confloat(gt = 0.0) = 0.0
    total: confloat(gt=0.0)
    year: conint(ge=0)
    month: conint(ge=1,le=12)

class TdsIndividualCalculationResponseSerializer(BaseModel):
    tds_calculation_id: Optional[UUID4]
    amount: Optional[confloat(gt=0.0)]
    tds_value: Optional[confloat(gt=0.0)]
    total: Optional[confloat(gt=0.0)]
    is_paid: Optional[bool]
    month: Optional[conint(ge=1,le=12)]
    year: Optional[conint(ge=0)]
    user_id: UUID4
    name: Optional[constr()]
    email: Optional[EmailStr]
    mobile: Optional[constr(min_length=1)]

class TdsPaidRequestSerializer(BaseModel):
    tds_calculation_id: Optional[UUID4]
    month: Optional[conint(ge=1,le=12)]
    year: Optional[conint(ge=0)]

class DiscountRequestResponseSerializer(BaseModel):
    cash_bonus_discount_id: Optional[UUID4]
    percentage: confloat(ge = 0.0, le = 100.0)
    name: Optional[constr(min_length=1)] = "India"

class CricketSeriesResponseSerializer(BaseModel):
    cricket_series_id: UUID4
    name: Optional[constr()]
    fc_name: Optional[constr()]
    use_name: Optional[bool] = False
    created_at: datetime

class CricketSeriesRequestSerialzier(BaseModel):
    fc_name: Optional[constr(min_length = 1)]
    use_name: Optional[bool]

class CricketTeamResponseSerializer(BaseModel):
    cricket_team_id: UUID4
    short_name: Optional[constr()]
    fc_short_name: Optional[constr()]
    logo_url: Optional[constr()]
    use_short_name: Optional[bool] = False
    use_logo_url: Optional[bool] = False
    fc_logo_url: Optional[constr()]
    created_at: datetime

class CricketTeamRequestSerialzier(BaseModel):
    fc_short_name: Optional[constr(min_length = 1)]
    fc_logo_url: Optional[constr(min_length = 1)]
    use_short_name: Optional[bool]
    use_logo_url: Optional[bool]

class HomeScreeenRequestSerializer(BaseModel):
    image: constr()
    title: Optional[constr()] = None
    is_active: bool = True

class HomeScreeenUpdateSerializer(BaseModel):
    image: Optional[constr()] = None
    title: Optional[constr()] = None
    is_active: Optional[bool]

class HomeScreenResponseSerializer(BaseModel):
    homescreen_id : Optional[UUID4] = None
    image : Optional[constr()] = None
    title : Optional[constr()] = None
    is_active : Optional[bool] = None
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None

    class Config:
        orm_mode = True

class AdminAddAmountRequestSerializer(BaseModel):
    mobile: constr(min_length=1, max_length=10)
    amount: confloat()
    token: constr(min_length=1)
