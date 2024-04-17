from datetime import datetime
from fastapi import (
    APIRouter, 
    Depends, 
    Request, 
    WebSocket
)
from fastapi_jwt_auth import AuthJWT
from pydantic import UUID4, conint, constr
from src.db.models import (
    ContestStatusEnum, 
    DraftForEnum
)

from src.services.contest.controller import DraftController
from src.services.contest.serializer import (
    CaptainRequestSerializer, 
    CreateDraftRequestSerializer
)

router = APIRouter(prefix="/v1/contest")

@router.get("/check_balance_kyc")
async def check_balance_kyc(token:Request, authorize:AuthJWT=Depends()):
    return await DraftController.check_balance_kyc(
        token = token,
        authorize = authorize
    )

@router.get("/check_max_min_member")
async def check_max_min_member(draft_match_series_id: UUID4, draft_for: DraftForEnum):
    return await DraftController.check_max_min_member(
        draft_match_series_id = draft_match_series_id,
        draft_for = draft_for
    )

@router.get("/winner_compensation")
async def winner_compensation(amount: conint(ge=0), members: conint(ge=2), number_of_winners: conint(gt=0) = 0):
    return await DraftController.winner_compensation(
        amount = amount,
        members = members,
        number_of_winners = number_of_winners
    )

@router.get("/player_choice")
async def player_choice(total_member: conint(ge=2), player_count: conint(gt=0), draft_match_series_id: UUID4, draft_for: DraftForEnum, number_of_round: conint(ge=1)):
    return await DraftController.player_choice(
        total_member = total_member,
        player_count = player_count,
        draft_match_series_id = draft_match_series_id,
        draft_for = draft_for,
        number_of_round = number_of_round
    )

@router.post("/create_draft")
async def create_draft(token:Request, request: CreateDraftRequestSerializer, authorize:AuthJWT=Depends()):
    return await DraftController.create_draft(
        token = token,
        request = request,
        authorize = authorize
    )

@router.get("/invitation")
async def invitation(token:Request, invitation_code: constr(), authorize:AuthJWT=Depends()):
    return await DraftController.invitation(
        token = token,
        invitation_code = invitation_code,
        authorize = authorize
    )

@router.get("/public_draft")
async def public_draft(draft_match_series_id: UUID4, draft_for: DraftForEnum, token: Request, authorize:AuthJWT=Depends()):
    return await DraftController.public_draft(
        draft_match_series_id = draft_match_series_id,
        draft_for = draft_for,
        token = token,
        authorize = authorize
    )

@router.get("/join_contest")
async def join_contest(user_draft_id: UUID4, token: Request, authorize:AuthJWT=Depends()):
    return await DraftController.join_contest(
        user_draft_id = user_draft_id,
        token = token,
        authorize = authorize
    )

@router.get("/player_stats")
async def player_stats(player_id: UUID4, token: Request, authorize:AuthJWT=Depends()):
    return await DraftController.player_stats(
        player_id = player_id,
        token = token,
        authorize = authorize
    )

@router.websocket("/draft")
async def play_draft(websocket: WebSocket, user_draft_id: UUID4, user_id: UUID4):
    return await DraftController.draft(
        user_draft_id = user_draft_id,
        user_id = user_id,
        websocket = websocket
    )

@router.get("/squad")
async def squad(user_draft_id: UUID4, token: Request, authorize:AuthJWT=Depends(), others: bool = False):
    return await DraftController.squad(
        user_draft_id = user_draft_id,
        token = token,
        authorize = authorize,
        others = others
    )

@router.post("/captain")
async def select_captain(user_draft_id: UUID4, request: CaptainRequestSerializer, token: Request, authorize:AuthJWT=Depends()):
    return await DraftController.select_captain(
        user_draft_id = user_draft_id,
        token = token,
        authorize = authorize,
        request = request
    )

@router.get("/get_my_contest")
async def get_my_contest(token: Request, authorize:AuthJWT=Depends(), contest_status: ContestStatusEnum = ContestStatusEnum.UPCOMING, limit: conint(ge=1) = 10, offset: conint(ge=1) = 1):
    return await DraftController.get_my_contest(
        token = token,
        authorize = authorize,
        contest_status = contest_status,
        limit = limit,
        offset = offset
    )

@router.get("/get_my_match_contest")
async def get_my_match_contest(contest_status: ContestStatusEnum, draft_match_series_id: UUID4, draft_for: DraftForEnum, token: Request, authorize:AuthJWT=Depends()):
    return await DraftController.get_my_match_contest(
        draft_match_series_id = draft_match_series_id,
        draft_for = draft_for,
        token = token,
        authorize = authorize,
        contest_status = contest_status
    )

@router.get("/get_draft_details")
async def get_draft_details(token: Request, user_draft_id: UUID4, authorize:AuthJWT=Depends()):
    return await DraftController.get_draft_details(
        user_draft_id = user_draft_id,
        token = token,
        authorize = authorize
    )

@router.get("/get_player_history")
async def get_player_history(user_draft_id: UUID4, token: Request, authorize:AuthJWT=Depends()):
    return await DraftController.get_player_history(
        user_draft_id = user_draft_id,
        token = token,
        authorize = authorize
    )

@router.websocket("/leaderboard")
async def play_draft(websocket: WebSocket, user_draft_id: UUID4, user_id: UUID4):
    return await DraftController.leaderboard(
        user_draft_id = user_draft_id,
        user_id = user_id,
        websocket = websocket
    )

@router.get("/match_status")
async def match_status():
    return await DraftController.match_status()

@router.get("/series_status_to_live")
async def series_status_to_live():
    return await DraftController.series_status_to_live()

@router.get("/series_status_completed")
async def series_status_completed():
    return await DraftController.series_status_completed()

@router.get("/update_cricket_match_to_off")
async def update_cricket_match_to_off():
    return await DraftController.update_cricket_match_to_off()

@router.get("/match_completed")
async def match_status_to_completed():
    return await DraftController.match_status_to_completed()

@router.get("/update_captain")
async def update_captain():
    return await DraftController.update_captain()

@router.get("/draft_starting_notification")
async def draft_starting_notification():
    return await DraftController.draft_starting_notification()

@router.get("/draft_cancelled_notification")
async def draft_cancelled_notification():
    return await DraftController.draft_cancelled_notification()

@router.get("/draft_not_join_cancel")
async def draft_not_join_cancel():
    return await DraftController.draft_not_join_cancel()

@router.get("/check_match_time")
async def check_match_time(draft_match_series_id: UUID4, draft_for: DraftForEnum, draft_starting_time: datetime):
    return await DraftController.check_match_time(
        draft_match_series_id = draft_match_series_id,
        draft_for = draft_for,
        draft_starting_time = draft_starting_time
    )

@router.get("/each_player_score")
async def each_player_score(token: Request, user_draft_id: UUID4, user_id: UUID4, authorize:AuthJWT=Depends()):
    return await DraftController.each_player_score(
        user_draft_id = user_draft_id,
        user_id = user_id,
        token = token,
        authorize = authorize
    )
