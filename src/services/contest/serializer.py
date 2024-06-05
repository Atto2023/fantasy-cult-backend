from datetime import datetime
from typing import (
    List, 
    Optional
)
from pydantic import (
    UUID4, 
    BaseModel, 
    confloat, 
    conint, 
    constr, 
    validator
)

from src.db.models import DraftForEnum

class MaxMinPlayerResponseSerializer(BaseModel):
    player_count: conint(ge=0)
    invitation_code: constr()
    min_member_allowed: conint(ge=2) = 2
    max_member_allowed: conint(gt=2)

class WinnerCompensationResponseSerializer(BaseModel):
    winner_amount: conint(ge=0)
    number_of_winners: conint(ge=0)
    winner_list: List
    winnner_json: dict

class PlayerChoiceResponseSerializer(BaseModel):
    each_member_player: Optional[conint()]
    min_bat_count: Optional[conint()]
    max_bat_count: Optional[conint()]
    min_bowl_count: Optional[conint()]
    max_bowl_count: Optional[conint()]
    min_all_count: Optional[conint()]
    max_all_count: Optional[conint()]
    min_wk_count: Optional[conint()]
    max_wk_count: Optional[conint()]

class PlayChoiceDraftRequestSerializer(BaseModel):
    each_member_player: conint()
    bat: conint()
    bowl: conint()
    all: conint()
    wk: conint()


class CreateDraftRequestSerializer(BaseModel):
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
    is_public: bool = False

class InvitationCodeResponseSerializer(BaseModel):
    user_draft_id: UUID4
    winners_price: dict
    entry_amount: confloat(ge=0)
    max_playing_user: conint(gt=0)
    joined_player: Optional[conint(ge=0)]
    draft_match_series_id: Optional[UUID4]
    draft_for: Optional[DraftForEnum]
    draft_starting_time: Optional[datetime]


class ListDraftResponseSerializer(BaseModel):
    series_name: Optional[constr()]
    series_start_date: Optional[datetime]
    series_start_day: Optional[constr()]
    match_start_time: Optional[datetime]
    match_start_day: Optional[constr()]
    cricket_team_id_a: Optional[UUID4]
    team_short_name_a: Optional[constr()]
    team_logo_url_a: Optional[constr()]
    cricket_team_id_b: Optional[UUID4]
    team_short_name_b: Optional[constr()]
    team_logo_url_b: Optional[constr()]
    draft_for: Optional[DraftForEnum]
    draft_data: Optional[List[InvitationCodeResponseSerializer]]


class PlayersResponseSerializer(BaseModel):
    player_id: Optional[UUID4]
    name: Optional[constr()]
    role: Optional[constr()]
    logo: Optional[constr()]
    team: Optional[constr()]
    is_selected: bool = False

class PlayersScoreResponseSerializer(BaseModel):
    player_id: Optional[UUID4]
    name: Optional[constr()]
    role: Optional[constr()]
    logo: Optional[constr()]
    score: Optional[confloat()] = 0.0
    is_captain: Optional[bool] = False
    is_vice_captain: Optional[bool] = False

class MemberResponseSerializer(BaseModel):
    user_id: UUID4
    name: Optional[constr()]
    position: Optional[conint()]
    profile_image: Optional[constr()]
    total_player: conint() = 0
    bat: conint() = 0
    bowl: conint() = 0
    all: conint() = 0
    wk: conint() = 0
    your_turn: bool = False

class PlayerDetailResponseSerializer(BaseModel):
    player_id: Optional[UUID4]
    name: Optional[constr()]
    role: Optional[constr()]
    logo: Optional[constr()]
    team: Optional[constr()]
    batting_style: Optional[constr()]
    bowling_style: Optional[constr()]
    batting_stats: dict
    bowling_stats: dict


class SquadResponseSerializer(BaseModel):
    user_id: UUID4
    name: Optional[constr()]
    players: List[PlayersResponseSerializer] = []

class MySquadResponseSerializer(SquadResponseSerializer):
    player_choice: dict = {
        "wk": 0,
        "all": 0,
        "bat": 0,
        "bowl": 0,
        "each_member_player": 0
    }

class CaptainRequestSerializer(BaseModel):
    captain: UUID4
    vice_captain: UUID4

class MyContestResponseSerializer(BaseModel):
    draft_for: Optional[DraftForEnum]
    draft_match_series_id: Optional[UUID4]
    series_name: Optional[constr()]
    series_start_date: Optional[datetime]
    series_start_day: Optional[constr()]
    match_format: Optional[constr()]
    match_start_time: Optional[datetime]
    match_start_day: Optional[constr()]
    cricket_team_id_a: Optional[UUID4]
    team_short_name_a: Optional[constr()]
    team_logo_url_a: Optional[constr()]
    cricket_team_id_b: Optional[UUID4]
    team_short_name_b: Optional[constr()]
    team_logo_url_b: Optional[constr()]


class IndividualContestResponseSerializer(BaseModel):
    user_draft_id: UUID4
    created_by_me: bool = False
    is_draft_completed: Optional[bool] = False
    is_result_announce: Optional[bool] = False
    draft_starting_time: Optional[datetime]
    amount: confloat() = 0.0
    max_playing_user: conint(gt=0)
    joined_player: Optional[conint(ge=0)]
    player_selected: Optional[List]
    winners_price: dict
    entry_amount: confloat(ge=0)
    league_name: Optional[constr()]
    is_draft_cancelled: Optional[bool] = False


class MyMatchContestResponseSerializer(BaseModel):
    series_name: Optional[constr()]
    series_start_date: Optional[datetime]
    series_start_day: Optional[constr()]
    match_start_time: Optional[datetime]
    match_start_day: Optional[constr()]
    cricket_team_id_a: Optional[UUID4]
    team_short_name_a: Optional[constr()]
    team_logo_url_a: Optional[constr()]
    cricket_team_id_b: Optional[UUID4]
    team_short_name_b: Optional[constr()]
    team_logo_url_b: Optional[constr()]
    draft_for: Optional[DraftForEnum]
    draft_data: Optional[List[IndividualContestResponseSerializer]] = []

class MemberLeaderboardResponseSerializer(BaseModel):
    user_id: Optional[UUID4]
    name: Optional[constr()]
    profile_image: Optional[constr()]
    amount: Optional[confloat()]
    points: Optional[confloat()]
    position: Optional[conint()]

class LeaderboardResponseSerializer(BaseModel):
    series_name: Optional[constr()]
    series_start_date: Optional[datetime]
    series_start_day: Optional[constr()]
    match_start_time: Optional[datetime]
    match_start_day: Optional[constr()]
    cricket_team_id_a: Optional[UUID4]
    team_short_name_a: Optional[constr()]
    team_logo_url_a: Optional[constr()]
    cricket_team_id_b: Optional[UUID4]
    team_short_name_b: Optional[constr()]
    team_logo_url_b: Optional[constr()]
    draft_for: Optional[DraftForEnum]
    top_picks: Optional[conint()]
    number_of_round: Optional[conint()]
    show_captain_change: Optional[bool] = False
    logged_in_user_captain: Optional[UUID4] = None
    logged_in_user_vice_captain: Optional[UUID4] = None
    member_data: Optional[List[MemberLeaderboardResponseSerializer]] = []
    text_show: Optional[constr()] = ""

class DraftDetailResponseSerializer(BaseModel):
    entry_amount: confloat(ge = 0)
    account_deduct: confloat() = 0.0
    winning_deduct: confloat() = 0.0
    bonus_deduct: confloat() = 0.0
    number_of_round: conint(ge=1)
    top_picks: conint(ge=1)
    player_choice: PlayChoiceDraftRequestSerializer

class WinningDistributionRequestSerializer(BaseModel):
    user_draft_ids: List[UUID4] = []
