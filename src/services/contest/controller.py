from datetime import datetime, timedelta
import random
import time

from pytz import timezone
from src.config.websocket import (
    ConnectionManager, 
    LeaderboardConnectionManager
)
from src.db.models import (
    BankVerificationEnum, 
    DraftForEnum, 
    TransactionStatusEnum, 
    TransactionTypeEnum, 
    VerificationEnum
)
from src.services.admin.controller import AdminController
from src.services.admin.schema import AdminSchema
from src.services.contest.schema import DraftSchema
from src.services.contest.serializer import (
    CaptainRequestSerializer, 
    CreateDraftRequestSerializer, 
    DraftDetailResponseSerializer, 
    IndividualContestResponseSerializer, 
    InvitationCodeResponseSerializer, 
    ListDraftResponseSerializer, 
    MaxMinPlayerResponseSerializer, 
    MyContestResponseSerializer, 
    MyMatchContestResponseSerializer, 
    MySquadResponseSerializer, 
    PlayerChoiceResponseSerializer, 
    PlayerDetailResponseSerializer, 
    PlayersResponseSerializer, 
    PlayersScoreResponseSerializer, 
    SquadResponseSerializer, 
    WinnerCompensationResponseSerializer
)
from src.services.cricket.schema import CricketMatchSchema
from src.services.notification.schema import NotificationSchema
from src.services.user.schema import UserProfileSchema
from src.utils.constant import NotificationConstant
from src.utils.entity_sports import EntitySportsLive
from src.utils.helper_functions import (
    send_mail_notification,
    send_notification
)
from src.utils.jwt import auth_check
from src.utils.response import (
    ErrorResponseSerializer, 
    SuccessResponseSerializer, 
    response_structure
)
from fastapi import (
    WebSocketDisconnect, 
    status
)
from random import randint

manager = ConnectionManager()
leaderboard_manager = LeaderboardConnectionManager()

class DraftController:

    @classmethod
    async def check_balance_kyc(cls, token, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        data = {
            "profile": True,
            "amount": True
        }
        user_data = await UserProfileSchema.get_user_data(
            user_id = user_id,
            with_base = True
        )
        if not user_data.is_email_verified or user_data.is_pan_verified != VerificationEnum.VERIFIED:
            data["profile"] = False
        
        user_balance = await UserProfileSchema.get_user_balance(
            user_id = user_id
        )

        if not user_balance or user_balance.amount < 100:
            data["amount"] = False
        
        serializer = SuccessResponseSerializer(
            message = "Balance & KYC Data",
            data = data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def check_max_min_member(cls, draft_match_series_id, draft_for):
        code_check = 1
        while code_check != None:
            invitation_code = randint(100000,999999)
            code_check = await DraftSchema.check_invitation_code(
                invitation_code = invitation_code
            )
        if draft_for == DraftForEnum.MATCH:
            match_player = await DraftSchema.match_series_team(
                cricket_match_id = draft_match_series_id
            )
            if match_player:
                player_a = await DraftSchema.match_series_team_player(
                    series_id=match_player.series_id,
                    team_id=match_player.team_a
                )
                player_b = await DraftSchema.match_series_team_player(
                    series_id=match_player.series_id,
                    team_id=match_player.team_b
                )
                player_count = len(player_a.player_id) + len(player_b.player_id)
                min_member_allowed = 2
                for i in range(min_member_allowed, 1000):
                    thresold = int(player_count/i)
                    if thresold < 5:
                        break
                    max_member_allowed = i
                serializer = SuccessResponseSerializer(
                    message = "Min And Max Player allowed for this draft",
                    data = MaxMinPlayerResponseSerializer(
                        invitation_code = invitation_code,
                        player_count = player_count,
                        min_member_allowed = min_member_allowed,
                        max_member_allowed = max_member_allowed
                    )
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_200_OK
                )
            else:
                serializer = ErrorResponseSerializer(
                    message = "Please check the match id",
                    status_code = status.HTTP_404_NOT_FOUND
                )
                return response_structure(
                    status_code = status.HTTP_404_NOT_FOUND,
                    serializer = serializer
                )
        elif draft_for == DraftForEnum.SERIES:
            series_player = await DraftSchema.match_series_team_player(
                series_id = draft_match_series_id
            )
            if series_player:
                player_count = 0
                for player in series_player:
                    player_count = player_count + len(player.player_id)
                min_member_allowed = 2
                for i in range(min_member_allowed, 1000):
                    thresold = int(player_count/i)
                    if thresold < 5:
                        break
                    max_member_allowed = i
                serializer = SuccessResponseSerializer(
                    message = "Min And Max Player allowed for this draft",
                    data = MaxMinPlayerResponseSerializer(
                        invitation_code = invitation_code,
                        player_count = player_count,
                        min_member_allowed = min_member_allowed,
                        max_member_allowed = max_member_allowed
                    )
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_200_OK
                )
            else:
                serializer = ErrorResponseSerializer(
                    message = "Please check the series id",
                    status_code = status.HTTP_404_NOT_FOUND
                )
                return response_structure(
                    status_code = status.HTTP_404_NOT_FOUND,
                    serializer = serializer
                )
        else:
            serializer = ErrorResponseSerializer(
                message="Please provide draft for properly"
            )
            return response_structure(
                status_code = status.HTTP_400_BAD_REQUEST,
                serializer = serializer
            )

    @classmethod
    async def winner_compensation(cls, amount, members, number_of_winners):
        total_amount = amount * members
        admin_commission = round(total_amount*0.1)
        winner_amount = total_amount - admin_commission
        winner_json = {}
        if members in range(2,4):
            winner_list = [1]
            number_of_winners = number_of_winners if number_of_winners else 1
        elif members in range(4,6):
            winner_list = [1,2]
            number_of_winners = number_of_winners if number_of_winners else 2
        elif members in range(6,8):
            winner_list = [1,2,3]
            number_of_winners = number_of_winners if number_of_winners else 3
        elif members in range(8,10):
            winner_list = [1,2,3,4]
            number_of_winners = number_of_winners if number_of_winners else 4
        elif members in range(10,14):
            winner_list = [1,2,3,4,5]
            number_of_winners = number_of_winners if number_of_winners else 5
        elif members in range(14, 20):
            winner_list = [1,2,3,4,5,7]
            number_of_winners = number_of_winners if number_of_winners else 7
        elif members in range(20,30):
            winner_list = [1,2,3,4,5,7,10]
            number_of_winners = number_of_winners if number_of_winners else 10
        elif members in range(30,50):
            winner_list = [1,2,3,4,5,7,10,15]
            number_of_winners = number_of_winners if number_of_winners else 15
        elif members in range(50,100):
            winner_list = [1,2,3,4,5,7,10,15,25]
            number_of_winners = number_of_winners if number_of_winners else 25
        elif members in range(100,200):
            winner_list = [1,2,3,4,5,7,10,15,25,50]
            number_of_winners = number_of_winners if number_of_winners else 50
        elif members in range(200,500):
            winner_list = [1,2,3,4,5,7,10,15,25,50,100]
            number_of_winners = number_of_winners if number_of_winners else 100
        elif members in range(500,1000):
            winner_list = [1,2,3,4,5,7,10,15,25,50,100,250]
            number_of_winners = number_of_winners if number_of_winners else 250
        elif members in range(1000,2000):
            winner_list = [1,2,3,4,5,7,10,15,25,50,100,250,500]
            number_of_winners = number_of_winners if number_of_winners else 500
        elif members in range(2000,4000):
            winner_list = [1,2,3,4,5,7,10,15,25,50,100,250,500,1000]
            number_of_winners = number_of_winners if number_of_winners else 1000
        elif members in range(4000,10000):
            winner_list = [1,2,3,4,5,7,10,15,25,50,100,250,500,1000,2000]
            number_of_winners = number_of_winners if number_of_winners else 2000
        else:
            winner_list = [1,2,3,4,5,7,10,15,25,50,100,250,500,1000,2000,5000]
            number_of_winners = number_of_winners if number_of_winners else 5000
        if number_of_winners == 1:
            winner_json["1"] = winner_amount
        if number_of_winners == 2:
            winner_json["1"] = round(winner_amount*0.7)
            winner_json["2"] = round(winner_amount*0.3)
        if number_of_winners == 3:
            winner_json["1"] = round(winner_amount*0.5)
            winner_json["2"] = round(winner_amount*0.3)
            winner_json["3"] = round(winner_amount*0.2)
        if number_of_winners == 4:
            winner_json["1"] = round(winner_amount*0.4)
            winner_json["2"] = round(winner_amount*0.25)
            winner_json["3"] = round(winner_amount*0.2)
            winner_json["4"] = round(winner_amount*0.15)
        if number_of_winners == 5:
            winner_json["1"] = round(winner_amount*0.4)
            winner_json["2"] = round(winner_amount*0.25)
            winner_json["3"] = round(winner_amount*0.15)
            winner_json["4-5"] = round(winner_amount*0.1)
        if number_of_winners == 7:
            winner_json["1"] = round(winner_amount*0.35)
            winner_json["2"] = round(winner_amount*0.19)
            winner_json["3"] = round(winner_amount*0.12)
            winner_json["4"] = round(winner_amount*0.1)
            winner_json["5-7"] = round(winner_amount*0.08)
        if number_of_winners == 10:
            winner_json["1"] = round(winner_amount*0.3)
            winner_json["2"] = round(winner_amount*0.18)
            winner_json["3"] = round(winner_amount*0.11)
            winner_json["4"] = round(winner_amount*0.075)
            winner_json["5"] = round(winner_amount*0.06)
            winner_json["6-10"] = round(winner_amount*0.055)
        if number_of_winners == 15:
            winner_json["1"] = round(winner_amount*0.25)
            winner_json["2"] = round(winner_amount*0.125)
            winner_json["3"] = round(winner_amount*0.10)
            winner_json["4"] = round(winner_amount*0.075)
            winner_json["5"] = round(winner_amount*0.05)
            winner_json["6-15"] = round(winner_amount*0.04)
        if number_of_winners == 25:
            winner_json["1"] = round(winner_amount*0.2)
            winner_json["2"] = round(winner_amount*0.12)
            winner_json["3"] = round(winner_amount*0.08)
            winner_json["4"] = round(winner_amount*0.05)
            winner_json["5"] = round(winner_amount*0.05)
            winner_json["6-25"] = round(winner_amount*0.025)
        if number_of_winners == 50:
            winner_json["1"] = round(winner_amount*0.15)
            winner_json["2"] = round(winner_amount*0.10)
            winner_json["3"] = round(winner_amount*0.08)
            winner_json["4"] = round(winner_amount*0.04)
            winner_json["5"] = round(winner_amount*0.03)
            winner_json["6-10"] = round(winner_amount*0.02)
            winner_json["11-25"] = round(winner_amount*0.015)
            winner_json["26-50"] = round(winner_amount*0.011)
        if number_of_winners == 100:
            winner_json["1"] = round(winner_amount*0.15)
            winner_json["2"] = round(winner_amount*0.10)
            winner_json["3"] = round(winner_amount*0.08)
            winner_json["4"] = round(winner_amount*0.0375)
            winner_json["5"] = round(winner_amount*0.035)
            winner_json["6-10"] = round(winner_amount*0.015)
            winner_json["11-15"] = round(winner_amount*0.010)
            winner_json["16-25"] = round(winner_amount*0.006)
            winner_json["26-100"] = round(winner_amount*0.0055)
        if number_of_winners == 250:
            winner_json["1"] = round(winner_amount*0.12)
            winner_json["2"] = round(winner_amount*0.075)
            winner_json["3"] = round(winner_amount*0.050)
            winner_json["4"] = round(winner_amount*0.030)
            winner_json["5"] = round(winner_amount*0.0225)
            winner_json["6-10"] = round(winner_amount*0.02)
            winner_json["11-15"] = round(winner_amount*0.01)
            winner_json["16-25"] = round(winner_amount*0.005)
            winner_json["26-50"] = round(winner_amount*0.0025)
            winner_json["51-250"] = round(winner_amount*0.0022)
        if number_of_winners == 500:
            winner_json["1"] = round(winner_amount*0.10)
            winner_json["2"] = round(winner_amount*0.07)
            winner_json["3"] = round(winner_amount*0.035)
            winner_json["4-5"] = round(winner_amount*0.025)
            winner_json["6-10"] = round(winner_amount*0.01)
            winner_json["11-25"] = round(winner_amount*0.003)
            winner_json["26-100"] = round(winner_amount*0.002)
            winner_json["101-250"] = round(winner_amount*0.0015)
            winner_json["251-500"] = round(winner_amount*0.0011)
        if number_of_winners == 1000:
            winner_json["1"] = round(winner_amount*0.05)
            winner_json["2"] = round(winner_amount*0.03)
            winner_json["3"] = round(winner_amount*0.017)
            winner_json["4-10"] = round(winner_amount*0.009)
            winner_json["11-50"] = round(winner_amount*0.003)
            winner_json["51-100"] = round(winner_amount*0.002)
            winner_json["101-500"] = round(winner_amount*0.0008)
            winner_json["501-1000"] = round(winner_amount*0.0006)
        if number_of_winners == 2000:
            winner_json["1"] = round(winner_amount*0.05)
            winner_json["2"] = round(winner_amount*0.03)
            winner_json["3"] = round(winner_amount*0.02)
            winner_json["4-10"] = round(winner_amount*0.01)
            winner_json["11-50"] = round(winner_amount*0.002)
            winner_json["51-100"] = round(winner_amount*0.001)
            winner_json["101-500"] = round(winner_amount*0.0005)
            winner_json["501-1000"] = round(winner_amount*0.0004)
            winner_json["1001-2000"] = round(winner_amount*0.0003)
        if number_of_winners == 5000:
            winner_json["1"] = round(winner_amount*0.04)
            winner_json["2"] = round(winner_amount*0.02)
            winner_json["3"] = round(winner_amount*0.01)
            winner_json["4-10"] = round(winner_amount*0.005)
            winner_json["11-50"] = round(winner_amount*0.0025)
            winner_json["51-100"] = round(winner_amount*0.001)
            winner_json["101-500"] = round(winner_amount*0.0005)
            winner_json["501-1000"] = round(winner_amount*0.00021)
            winner_json["1001-5000"] = round(winner_amount*0.00011)
        serializer = SuccessResponseSerializer(
            message = "Winner Json",
            data = WinnerCompensationResponseSerializer(
                winner_amount = winner_amount,
                number_of_winners = number_of_winners,
                winner_list = winner_list,
                winnner_json = winner_json
            )
        )
        return response_structure(
            status_code = status.HTTP_200_OK,
            serializer = serializer
        )


    @classmethod
    async def player_choice(cls, total_member, player_count, draft_match_series_id, draft_for, number_of_round):
        player_choice = PlayerChoiceResponseSerializer()
        bat = 0
        bowl = 0
        wk = 0
        all_rounder = 0
        if draft_for == DraftForEnum.SERIES:
            series_player = await DraftSchema.match_series_team_player(
                series_id = draft_match_series_id
            )
            for player_id in series_player:
                for player in player_id.player_id:
                    player_data = await DraftSchema.get_player_data(
                        player_id = player
                    )
                    if player_data.role == "bat":
                        bat = bat + 1
                    elif player_data.role == "all":
                        all_rounder = all_rounder + 1
                    elif player_data.role == "bowl":
                        bowl = bowl + 1
                    elif player_data.role == "wk" or player_data.role == "wkbat":
                        wk = wk + 1
                    else:
                        pass
        if draft_for == DraftForEnum.MATCH:
            match_player = await DraftSchema.match_series_team(
                cricket_match_id = draft_match_series_id
            )
            if match_player:
                player_a = await DraftSchema.match_series_team_player(
                    series_id=match_player.series_id,
                    team_id=match_player.team_a
                )
                player_b = await DraftSchema.match_series_team_player(
                    series_id=match_player.series_id,
                    team_id=match_player.team_b
                )
                for player in player_a.player_id:
                    player_data = await DraftSchema.get_player_data(
                        player_id = player
                    )
                    if player_data.role == "bat":
                        bat = bat + 1
                    elif player_data.role == "all":
                        all_rounder = all_rounder + 1
                    elif player_data.role == "bowl":
                        bowl = bowl + 1
                    elif player_data.role == "wk" or player_data.role == "wkbat":
                        wk = wk + 1
                    else:
                        pass
                for player in player_b.player_id:
                    player_data = await DraftSchema.get_player_data(
                        player_id = player
                    )
                    if player_data.role == "bat":
                        bat = bat + 1
                    elif player_data.role == "all":
                        all_rounder = all_rounder + 1
                    elif player_data.role == "bowl":
                        bowl = bowl + 1
                    elif player_data.role == "wk" or player_data.role == "wkbat":
                        wk = wk + 1
                    else:
                        pass

        player_choice.each_member_player = number_of_round
        bat_statistics = int(bat/total_member)
        player_choice.min_bat_count = 0
        player_choice.max_bat_count = bat_statistics

        bowl_statistics = int(bowl/total_member)
        player_choice.min_bowl_count = 0
        player_choice.max_bowl_count = bowl_statistics

        wk_statistics = int(wk/total_member)
        player_choice.min_wk_count = 0
        player_choice.max_wk_count = wk_statistics

        all_rounder_statistics = int(all_rounder/total_member)
        player_choice.min_all_count = 0
        player_choice.max_all_count = all_rounder_statistics

        # each_member_player = int(player_count / total_member)
        # if each_member_player >= 11:
        #     player_choice.each_member_player = 11
        #     player_choice.min_bat_count = 1
        #     player_choice.max_bat_count = 4
        #     player_choice.min_bowl_count = 1
        #     player_choice.max_bowl_count = 4
        #     player_choice.min_all_count = 1
        #     player_choice.max_all_count = 3
        #     player_choice.min_wk_count = 1
        #     player_choice.max_wk_count = 1
        # elif each_member_player == 10:
        #     player_choice.each_member_player = 10
        #     player_choice.min_bat_count = 1
        #     player_choice.max_bat_count = 4
        #     player_choice.min_bowl_count = 1
        #     player_choice.max_bowl_count = 3
        #     player_choice.min_all_count = 1
        #     player_choice.max_all_count = 3
        #     player_choice.min_wk_count = 1
        #     player_choice.max_wk_count = 1
        # elif each_member_player == 9:
        #     player_choice.each_member_player = 9
        #     player_choice.min_bat_count = 1
        #     player_choice.max_bat_count = 4
        #     player_choice.min_bowl_count = 1
        #     player_choice.max_bowl_count = 3
        #     player_choice.min_all_count = 1
        #     player_choice.max_all_count = 2
        #     player_choice.min_wk_count = 1
        #     player_choice.max_wk_count = 1
        # elif each_member_player == 8:
        #     player_choice.each_member_player = 8
        #     player_choice.min_bat_count = 1
        #     player_choice.max_bat_count = 3
        #     player_choice.min_bowl_count = 1
        #     player_choice.max_bowl_count = 3
        #     player_choice.min_all_count = 1
        #     player_choice.max_all_count = 2
        #     player_choice.min_wk_count = 1
        #     player_choice.max_wk_count = 1
        # elif each_member_player == 7:
        #     player_choice.each_member_player = 7
        #     player_choice.min_bat_count = 1
        #     player_choice.max_bat_count = 3
        #     player_choice.min_bowl_count = 1
        #     player_choice.max_bowl_count = 2
        #     player_choice.min_all_count = 1
        #     player_choice.max_all_count = 2
        #     player_choice.min_wk_count = 1
        #     player_choice.max_wk_count = 1
        # elif each_member_player == 6:
        #     player_choice.each_member_player = 6
        #     player_choice.min_bat_count = 1
        #     player_choice.max_bat_count = 3
        #     player_choice.min_bowl_count = 1
        #     player_choice.max_bowl_count = 2
        #     player_choice.min_all_count = 1
        #     player_choice.max_all_count = 1
        #     player_choice.min_wk_count = 1
        #     player_choice.max_wk_count = 1
        # elif each_member_player == 5:
        #     player_choice.each_member_player = 5
        #     player_choice.min_bat_count = 1
        #     player_choice.max_bat_count = 2
        #     player_choice.min_bowl_count = 1
        #     player_choice.max_bowl_count = 2
        #     player_choice.min_all_count = 1
        #     player_choice.max_all_count = 1
        #     player_choice.min_wk_count = 1
        #     player_choice.max_wk_count = 1
        serializer = SuccessResponseSerializer(
            data = player_choice
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )


    @classmethod
    async def create_draft(cls, token, authorize, request: CreateDraftRequestSerializer):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

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
        user_balance = await UserProfileSchema.get_user_balance(
            user_id = user_id
        )
        if not user_balance:
            serializer = ErrorResponseSerializer(
                message = f"You have not added the amount yet"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )
        if user_balance.amount < request.entry_amount:
            serializer = ErrorResponseSerializer(
                message = f"Your Amount is not sufficient"
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
        draft = await DraftSchema.create_draft(
            request = request,
            user_id = user_id
        )
        await DraftSchema.add_contest_member(
            draft_id = draft.user_draft_id,
            user_id = user_id
        )
        deduct_add, deduct_win, deduct_cash = await UserProfileSchema.update_amount(
            user_id = user_id,
            joining_amount = request.entry_amount
        )
        await UserProfileSchema.add_user_transaction(
            user_id = user_id,
            amount = -(request.entry_amount),
            transaction_type = TransactionTypeEnum.JOIN_CONTEST,
            transaction_status = TransactionStatusEnum.COMPLETED,
            meta_data = {
                "user_draft_id": str(draft.user_draft_id)
            },
            deduct_add = deduct_add,
            deduct_win = deduct_win,
            deduct_cash = deduct_cash
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
    async def invitation(cls, token, invitation_code, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        user_draft = await DraftSchema.get_draft_data(
            invitation_code = invitation_code
        )
        if not user_draft:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = "No Draft Found"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )
        member_count = await DraftSchema.get_member_count_in_draft(
            user_draft_id = user_draft.user_draft_id
        )

        if user_draft.draft_for == DraftForEnum.MATCH:
            data = await CricketMatchSchema.get_matches(
                match_id = user_draft.draft_match_series_id,
                limit=10,
                offset=1
            )
        else: # this is for series
            data = await CricketMatchSchema.get_series(
                series_id = user_draft.draft_match_series_id
            )
        list_draft = ListDraftResponseSerializer(**(data._asdict()))
        list_draft.draft_for = user_draft.draft_for

        if not data.series_use_name:
            list_draft.series_name = data.series_fc_name
        if list_draft.draft_for == DraftForEnum.MATCH:
            if not data.use_short_name_a:
                list_draft.team_short_name_a = data.fc_short_name_a
            if not data.use_logo_url_a:
                list_draft.team_logo_url_a = data.fc_logo_url_a
            if not data.use_short_name_b:
                list_draft.team_short_name_b = data.fc_short_name_b
            if not data.use_logo_url_b:
                list_draft.team_logo_url_b = data.fc_logo_url_b

        result = InvitationCodeResponseSerializer(**(user_draft._asdict()))
        result.joined_player = member_count
        list_draft.draft_data = [result]
        serializer = SuccessResponseSerializer(
            message = "List of all Drafts",
            data = list_draft
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def public_draft(cls, draft_match_series_id, draft_for, token, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        user_draft = await DraftSchema.get_draft_data(
            draft_match_series_id = draft_match_series_id,
            draft_for = draft_for,
            is_list = True,
            is_public = True
        )

        if draft_for == DraftForEnum.MATCH:
            data = await CricketMatchSchema.get_matches(
                match_id = draft_match_series_id,
                limit=10,
                offset=1
            )
        else: # this is for series
            data = await CricketMatchSchema.get_series(
                series_id = draft_match_series_id
            )
        if not data:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = "No Match or series found"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )

        list_draft = ListDraftResponseSerializer(**(data._asdict()))

        if not data.series_use_name:
            list_draft.series_name = data.series_fc_name
        if draft_for == DraftForEnum.MATCH:
            if not data.use_short_name_a:
                list_draft.team_short_name_a = data.fc_short_name_a
            if not data.use_logo_url_a:
                list_draft.team_logo_url_a = data.fc_logo_url_a
            if not data.use_short_name_b:
                list_draft.team_short_name_b = data.fc_short_name_b
            if not data.use_logo_url_b:
                list_draft.team_logo_url_b = data.fc_logo_url_b

        drafts = []
        for each in user_draft:
            joined_player = await DraftSchema.get_member_count_in_draft(
                user_draft_id = each.user_draft_id
            )
            draft = InvitationCodeResponseSerializer(**(each._asdict()))
            draft.joined_player = joined_player
            drafts.append(draft)
        list_draft.draft_data = drafts
        list_draft.series_start_day = list_draft.series_start_date.strftime('%A') if list_draft.series_start_date else None
        list_draft.match_start_day = list_draft.match_start_time.strftime('%A') if list_draft.match_start_time else None
        serializer = SuccessResponseSerializer(
            message = "List of all Drafts",
            data = list_draft
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def join_contest(cls, user_draft_id, token, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
        if draft_data.is_draft_cancelled:
            serializer = ErrorResponseSerializer(
                message = "This Draft is already Cancelled so you can not join"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )
        if draft_data.is_draft_completed:
            serializer = ErrorResponseSerializer(
                message = "This Draft is already Completed"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )
        if not draft_data:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = "Draft Not Found"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )
        contest_member = await DraftSchema.get_contest_member(
            draft_id = user_draft_id,
            is_list = True
        )
        all_position = []
        already_joined_user = False
        for contest in contest_member:
            if str(user_id) == str(contest.user_id):
                already_joined_user = True
                break
            all_position.append(contest.position)
        if not already_joined_user:
            member_joined = await DraftSchema.get_member_count_in_draft(
                user_draft_id = user_draft_id
            )
            if member_joined == draft_data.max_playing_user:
                serializer = ErrorResponseSerializer(
                    message = "Sorry this contest is full"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )
            user_balance = await UserProfileSchema.get_user_balance(
                user_id = user_id
            )
            if not user_balance:
                serializer = ErrorResponseSerializer(
                    message = f"You have not added the amount yet"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )
            if user_balance.amount < draft_data.entry_amount:
                serializer = ErrorResponseSerializer(
                    message = f"Your Amount is not sufficient"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_400_BAD_REQUEST
                )
            await DraftSchema.add_contest_member(
                draft_id = user_draft_id,
                user_id = user_id,
                position = max(all_position) + 1 if all_position else 1
            )
            deduct_add, deduct_win, deduct_cash = await UserProfileSchema.update_amount(
                user_id = user_id,
                joining_amount = draft_data.entry_amount
            )
            await UserProfileSchema.add_user_transaction(
                user_id = user_id,
                amount = -(draft_data.entry_amount),
                transaction_type = TransactionTypeEnum.JOIN_CONTEST,
                transaction_status = TransactionStatusEnum.COMPLETED,
                meta_data = {
                    "user_draft_id": str(user_draft_id)
                },
                deduct_add = deduct_add,
                deduct_win = deduct_win,
                deduct_cash = deduct_cash
            )
        else:
            await DraftSchema.update_contest_member(
                draft_id = user_draft_id,
                user_id = user_id,
                value_dict = {
                    "updated_at": datetime.now()
                }
            )
        draft_started = False
        if len(draft_data.player_selected) > 0:
            draft_started = True
        serializer = SuccessResponseSerializer(
            message = f"Added to Draft",
            data = {
                "draft_started": draft_started
            }
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )


    @classmethod
    async def get_draft_details(cls, user_draft_id, token, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )

        draft_data = DraftDetailResponseSerializer(**(draft_data._asdict()))

        user_balance = await UserProfileSchema.get_user_balance(user_id = user_id)

        x = await AdminSchema.get_discount()
        for i in x:
            cash_bonus_percentage = i.percentage
            break

        em = draft_data.entry_amount
        cash_bonus_deduct = float(round(em * cash_bonus_percentage / 100))

        if user_balance.cash_bonus_amount >= cash_bonus_deduct:
            draft_data.bonus_deduct = cash_bonus_deduct
            em = em - cash_bonus_deduct
        else:
            em = em - user_balance.cash_bonus_amount
            draft_data.bonus_deduct = user_balance.cash_bonus_amount

        if user_balance.added_amount >= 0:
            if user_balance.added_amount >= em:
                draft_data.account_deduct = em
            else:
                draft_data.account_deduct = user_balance.added_amount
                draft_data.winning_deduct = em - user_balance.added_amount
        else:
            serializer = ErrorResponseSerializer(
                message = "There is mistake in balance"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_400_BAD_REQUEST
            )

        serializer = SuccessResponseSerializer(
            message=f"Draft Details",
            data=draft_data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )


    @classmethod
    async def draft(cls, websocket, user_draft_id, user_id):
        await manager.connect(websocket, user_draft_id, user_id)
        try:
            while True:
                payload = await websocket.receive_json()
                if payload:
                    await manager.notify(user_draft_id = user_draft_id, user_id=user_id, payload = payload)
        except WebSocketDisconnect:
            await manager.disconnect(websocket, user_draft_id, user_id)
            ist_time = datetime.now() + timedelta(hours=5, minutes=30)
            draft_data = await DraftSchema.get_draft_data(
                user_draft_id = user_draft_id
            )
            contest_draft = await DraftSchema.get_contest_member(
                draft_id = user_draft_id,
                is_list = True
            )
            if (len(contest_draft) == draft_data.max_playing_user and draft_data.draft_starting_time <= ist_time):
                if manager.out_turn_user_id and manager.out_serializer and not draft_data.is_draft_completed:
                    looping_var = manager.out_serializer.response_type
                    while looping_var == 2:
                        if str(manager.out_turn_user_id) == str(user_id):
                            list_of_players = await manager.get_list_of_players(user_draft_id)
                            await manager.select_players(user_draft_id, manager.out_turn_user_id, {"player_id": "0", "player_list": list_of_players.dict()})
                            time.sleep(2)
                            serializer_player = await manager.get_list_of_players(user_draft_id)
                            payload = {
                                "round": manager.out_serializer.data["round"],
                                "position": manager.out_serializer.data["position"]
                            }
                            serializer = await manager.get_list_of_joined_members(user_draft_id, payload)
                            for user, websocket1 in manager.active_connections[user_draft_id].items():
                                await websocket1.send_json(serializer_player.json())
                                time.sleep(2)
                                await websocket1.send_json(serializer.json())
                                time.sleep(2)
                        else:
                            looping_var = 1

    @classmethod
    async def player_stats(cls, player_id, token, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        player_data = await DraftSchema.get_player_data(
            player_id = player_id
        )

        player_data = PlayerDetailResponseSerializer(
            **(player_data._asdict())
        )
        serializer = SuccessResponseSerializer(
            message = "Player Data",
            data = player_data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )


    @classmethod
    async def squad(cls, user_draft_id, token, authorize, others):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        if others:
            result = []
            contest_member = await DraftSchema.get_contest_member(
                draft_id = user_draft_id,
                is_list = True
            )
            for member in contest_member:
                if str(member.user_id) != str(user_id):
                    user_data = await UserProfileSchema.get_user_data(
                        with_base = True,
                        user_id = member.user_id
                    )
                    data = SquadResponseSerializer(**(user_data._asdict()))
                    contest_member = await DraftSchema.get_contest_member(
                        draft_id = user_draft_id,
                        user_id = member.user_id
                    )
                    for player in contest_member.player_selected:
                        player_data = await DraftSchema.get_player_data(
                            player_id = player
                        )
                        player_response = PlayersResponseSerializer(
                            **(player_data._asdict())
                        )
                        data.players.append(player_response)
                    result.append(data)
            serializer = SuccessResponseSerializer(
                message = "Others Squad",
                data = result
            )
        else:
            user_data = await UserProfileSchema.get_user_data(
                with_base = True,
                user_id = user_id
            )
            data = MySquadResponseSerializer(**(user_data._asdict()))
            contest_member = await DraftSchema.get_contest_member(
                draft_id = user_draft_id,
                user_id = user_id
            )
            draft_data = await DraftSchema.get_draft_data(
                user_draft_id = user_draft_id
            )
            data.player_choice = draft_data.player_choice
            for player in contest_member.player_selected:
                player_data = await DraftSchema.get_player_data(
                    player_id = player
                )
                player_response = PlayersResponseSerializer(
                    **(player_data._asdict())
                )
                data.players.append(player_response)
            serializer = SuccessResponseSerializer(
                message = "My Squad",
                data = data
            )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )


    @classmethod
    async def get_player_history(cls, user_draft_id, token, authorize):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )

        data = []
        if draft_data and draft_data.player_selected:
            for player_id in draft_data.player_selected:
                player_data = await DraftSchema.get_player_data(
                    player_id = player_id
                )
                if player_data:
                    player_response = PlayersResponseSerializer(
                        **(player_data._asdict())
                    )
                    member_contest = await DraftSchema.get_username_from_contest(
                        user_draft_id = user_draft_id
                    )
                    for member in member_contest:
                        if player_id in member.player_selected:
                            player_response.team = member.name
                            break
                    data.append(player_response)
        serializer = SuccessResponseSerializer(
            message = "Player History for this Draft",
            data = data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def select_captain(cls, user_draft_id, token, authorize, request: CaptainRequestSerializer):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        if request.captain == request.vice_captain:
            serializer = ErrorResponseSerializer(
                message = "Captain & Vice Captain can not be same"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_200_OK
            )

        await DraftSchema.update_contest_member(
            draft_id = user_draft_id,
            user_id = user_id,
            value_dict = {
                "captain": request.captain,
                "vice_captain": request.vice_captain,
                "updated_at": datetime.now()
            }
        )

        serializer = SuccessResponseSerializer(
            message = "Added Captain & Vice Captain"
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def get_my_contest(cls, token, authorize, contest_status, limit, offset):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        my_contest = await DraftSchema.get_my_contest(
            user_id = user_id,
            contest_status = contest_status,
            limit = limit,
            offset = offset
        )
        list_contest_data = []
        for contest in my_contest:
            if contest.draft_for == DraftForEnum.MATCH:
                data = await CricketMatchSchema.get_matches(
                    match_id = contest.draft_match_series_id,
                    limit=10,
                    offset=1
                )
            else: # this is for series
                data = await CricketMatchSchema.get_series(
                    series_id = contest.draft_match_series_id
                )
            contest_data = MyContestResponseSerializer(
                **(data._asdict())
            )
            contest_data.draft_for = contest.draft_for
            if not data.series_use_name:
                contest_data.series_name = data.series_fc_name
            if contest.draft_for == DraftForEnum.MATCH:
                if not data.use_short_name_a:
                    contest_data.team_short_name_a = data.fc_short_name_a
                if not data.use_logo_url_a:
                    contest_data.team_logo_url_a = data.fc_logo_url_a
                if not data.use_short_name_b:
                    contest_data.team_short_name_b = data.fc_short_name_b
                if not data.use_logo_url_b:
                    contest_data.team_logo_url_b = data.fc_logo_url_b
            contest_data.draft_match_series_id = contest.draft_match_series_id
            contest_data.series_start_day = contest_data.series_start_date.strftime('%A') if contest_data.series_start_date else None
            contest_data.match_start_day = contest_data.match_start_time.strftime('%A') if contest_data.match_start_time else None
            list_contest_data.append(contest_data)
        serializer = SuccessResponseSerializer(
            message = "Contest Data",
            data = list_contest_data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )


    @classmethod
    async def get_my_match_contest(cls, draft_match_series_id, draft_for, token, authorize, contest_status):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()

        if draft_for == DraftForEnum.MATCH:
            data = await CricketMatchSchema.get_matches(
                match_id = draft_match_series_id,
                limit=10,
                offset=1
            )
        else: # this is for series
            data = await CricketMatchSchema.get_series(
                series_id = draft_match_series_id
            )
        if not data:
            serializer = ErrorResponseSerializer(
                status_code = status.HTTP_404_NOT_FOUND,
                message = "No Match or series found"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_404_NOT_FOUND
            )
        list_draft = MyMatchContestResponseSerializer(**(data._asdict()))
        if not data.series_use_name:
            list_draft.series_name = data.series_fc_name
        if draft_for == DraftForEnum.MATCH:
            if not data.use_short_name_a:
                list_draft.team_short_name_a = data.fc_short_name_a
            if not data.use_logo_url_a:
                list_draft.team_logo_url_a = data.fc_logo_url_a
            if not data.use_short_name_b:
                list_draft.team_short_name_b = data.fc_short_name_b
            if not data.use_logo_url_b:
                list_draft.team_logo_url_b = data.fc_logo_url_b
        list_draft.draft_for = draft_for
        list_draft.series_start_day = list_draft.series_start_date.strftime('%A') if list_draft.series_start_date else None
        list_draft.match_start_day = list_draft.match_start_time.strftime('%A') if list_draft.match_start_time else None

        draft_data = await DraftSchema.get_draft_data(
            is_draft_cancelled = False,
            is_list = True,
            draft_for = draft_for,
            draft_match_series_id = draft_match_series_id
        )
        for draft in draft_data:
            my_match_contest = await DraftSchema.get_my_match_contest(
                user_id = user_id,
                draft_id = draft.user_draft_id,
                contest_status = contest_status
            )
            for match_contest in my_match_contest:
                dd = await DraftSchema.get_draft_data(
                    user_draft_id = match_contest.draft_id
                )
                joined_player = await DraftSchema.get_member_count_in_draft(
                    user_draft_id = match_contest.draft_id
                )
                created_by_me = True if str(dd.user_id) == str(user_id) else False
                dd = IndividualContestResponseSerializer(**(dd._asdict()))
                dd.created_by_me = created_by_me
                dd.joined_player = joined_player
                list_draft.draft_data.append(dd)
        serializer = SuccessResponseSerializer(
            message = "All your drafts",
            data = list_draft
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def leaderboard(cls, websocket, user_draft_id, user_id):
        await leaderboard_manager.connect(websocket, user_draft_id, user_id)
        try:
            while True:
                payload = await websocket.receive_json()
                if payload:
                    await leaderboard_manager.notify(user_draft_id = user_draft_id, user_id = user_id)
        except WebSocketDisconnect:
            await leaderboard_manager.disconnect(websocket, user_draft_id, user_id)

    @classmethod
    async def match_status(cls):
        data = await DraftSchema.get_todays_match()
        match_ids = []
        if len(data) > 0:
            for i in data:
                # match_status = await EntitySportsLive.entity_match_status(match_id = i.match_id)
                ist_time = datetime.now() + timedelta(hours=5, minutes=30)
                # date_start = datetime.strptime(match_status["date_start_ist"], "%Y-%m-%d %H:%M:%S")
                if i.match_start_time <= ist_time: # live
                    await DraftSchema.contest_match_status_change_to_live(
                        contest_player_id = i.contest_player_id
                    )
                    if i.cricket_match_id not in match_ids:
                        match_ids.append(i.cricket_match_id)
            for i in match_ids:
                await CricketMatchSchema.update_cricket_match_status(
                    match_id = i,
                    is_live = False
                )
        return True

    @classmethod
    async def series_status_to_live(cls):
        data = await DraftSchema.series_status_to_live()
        if len(data) > 0:
            for i in data:
                if i.match_id_point:
                    for j in i.match_id_point:
                        match_id = await CricketMatchSchema.get_match_with_cricket_match_id(
                            cricket_match_id = j
                        )
                        # match_status = await EntitySportsLive.entity_match_status(match_id = match_id.match_id)
                        ist_time = datetime.now() + timedelta(hours=5, minutes=30)
                        # date_start = datetime.strptime(match_status["date_start_ist"], "%Y-%m-%d %H:%M:%S")
                        if i.created_at <= match_id.match_start_time <= ist_time: # live
                            await DraftSchema.contest_match_status_change_to_live(
                                contest_player_id = i.contest_player_id
                            )
                            break
        return True

    @classmethod
    async def series_status_completed(cls):
        data = await DraftSchema.series_status_to_completed()
        if len(data) > 0:
            for i in data:
                series_status = await EntitySportsLive.entity_series_status(
                    series_id = i.series_id
                )
                if series_status["status"] == "result":
                    await DraftSchema.contest_match_status_change_to_completed(
                        contest_player_id = i.contest_player_id
                    )
        return True


    @classmethod
    async def update_cricket_match_to_off(cls):
        await DraftSchema.update_cricket_match_to_off()
        return True

    @classmethod
    async def match_status_to_completed(cls):
        # 1 -> Scheduled
        # 2 -> Completed
        # 3 -> Live
        # 4 -> Abandoned
        data = await DraftSchema.get_live_match()
        if len(data) > 0:
            for i in data:
                match_status = await EntitySportsLive.entity_match_status(match_id = i.match_id)
                if match_status["status"] == 2: # completed
                    await DraftSchema.contest_match_status_change_to_completed(
                        contest_player_id = i.contest_player_id
                    )
                elif match_status["status"] == 4: # Abandoned
                    pass
        return True

    @classmethod
    async def each_player_score(cls, user_draft_id, user_id, token, authorize):
        await auth_check(token=token,authorize=authorize)
        _ = authorize.get_jwt_subject()

        contest_player = await DraftSchema.get_contest_member(
            draft_id = user_draft_id,
            user_id = user_id
        )

        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
        data = []
        for player_id in contest_player.player_selected:
            player_data = await DraftSchema.get_player_data(
                player_id = player_id
            )
            if player_data:
                player_response = PlayersScoreResponseSerializer(
                    **(player_data._asdict())
                )

                if draft_data.draft_for == DraftForEnum.MATCH:
                    player_points = await DraftSchema.get_match_points(
                        cricket_player_id = player_id,
                        cricket_match_id = draft_data.draft_match_series_id
                    )
                else: # this is for series
                    player_points = 0
                    for match_id in draft_data.match_id_point:
                        points = await DraftSchema.get_match_points(
                            cricket_player_id = player_id,
                            cricket_match_id = match_id
                        )
                        if points:
                            player_points = player_points + points
                if player_points:
                    if contest_player.captain and str(contest_player.captain) == str(player_id):
                        player_points = 2 * player_points
                    elif contest_player.vice_captain and str(contest_player.vice_captain) == str(player_id):
                        player_points = 1.5 * player_points

                    player_response.score = player_points
                if contest_player.captain and str(contest_player.captain) == str(player_id):
                    player_response.is_captain = True
                if contest_player.vice_captain and str(contest_player.vice_captain) == str(player_id):
                    player_response.is_vice_captain = True
                data.append(player_response)
        
        serializer = SuccessResponseSerializer(
            message = "Player Score Data",
            data = data
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def check_match_time(cls, draft_match_series_id, draft_for, draft_starting_time):
        if draft_for == DraftForEnum.MATCH:
            data = await CricketMatchSchema.get_match_with_cricket_match_id(
                cricket_match_id = draft_match_series_id
            )
            max_time_allowed = data.match_start_time
        else: # this is for series
            serializer = SuccessResponseSerializer(
                data = {
                    "allowed": True
                }
            )
            return response_structure(
                status_code = status.HTTP_200_OK,
                serializer = serializer
            )

        if draft_starting_time + timedelta(minutes = 15) < max_time_allowed:
            serializer = SuccessResponseSerializer(
                data = {
                    "allowed": True
                }
            )
        else:
            serializer = SuccessResponseSerializer(
                message = "Please keep the draft starting time atleast 15 mins prior to start time",
                data = {
                    "allowed": False
                }
            )
        return response_structure(
            status_code = status.HTTP_200_OK,
            serializer = serializer
        )

    @classmethod
    async def update_captain(cls):
        drafts = await DraftSchema.get_todays_match()
        if len(drafts) > 0:
            for draft in drafts:
                # match_status = await EntitySportsLive.entity_match_status(match_id = draft.match_id)
                ist_time = datetime.now() + timedelta(hours=5, minutes=30)
                # date_start = datetime.strptime(match_status["date_start_ist"], "%Y-%m-%d %H:%M:%S")
                if draft.match_start_time - timedelta(minutes=5) < ist_time < draft.match_start_time:
                    if not draft.captain and draft.is_captain_allowed:
                        captain = draft.player_selected[0]
                        vice_captain = draft.player_selected[1]
                        await DraftSchema.update_contest_member_with_contest_player_id(
                            contest_player_id = draft.contest_player_id,
                            value_dict = {
                                "captain": captain,
                                "vice_captain": vice_captain
                            }
                        )

        data = await DraftSchema.series_status_to_live()
        if len(data) > 0:
            for i in data:
                if i.match_id_point:
                    for j in i.match_id_point:
                        match_id = await CricketMatchSchema.get_match_with_cricket_match_id(
                            cricket_match_id = j
                        )
                        # match_status = await EntitySportsLive.entity_match_status(match_id = match_id.match_id)
                        ist_time = datetime.now() + timedelta(hours=5, minutes=30)
                        # date_start = datetime.strptime(match_status["date_start_ist"], "%Y-%m-%d %H:%M:%S")
                        if match_id.match_start_time - timedelta(minutes=5) < ist_time < match_id.match_start_time:
                            if not draft.captain and draft.is_captain_allowed:
                                captain = draft.player_selected[0]
                                vice_captain = draft.player_selected[1]
                                await DraftSchema.update_contest_member_with_contest_player_id(
                                    contest_player_id = draft.contest_player_id,
                                    value_dict = {
                                        "captain": captain,
                                        "vice_captain": vice_captain
                                    }
                                )
        return True

    @classmethod
    async def draft_starting_notification(cls):
        drafts = await DraftSchema.draft_starting_notification()
        draft_ids = []
        for draft in drafts:
            ist_time = datetime.now() + timedelta(hours=5, minutes=30)
            if draft.draft_starting_time - timedelta(minutes=5) <= ist_time <= draft.draft_starting_time:
                notification_data = {
                    "title": "Draft Started",
                    "body": NotificationConstant.DRAFT_STARTED
                }
                notification = await NotificationSchema.add_notification(
                    user_id = draft.user_id,
                    message = notification_data["body"]
                )
                await send_notification(
                    user_id = draft.user_id,
                    data = notification_data,
                    notification_id = notification.notification_id
                )
                await send_mail_notification(
                    notification_data = notification_data,
                    email = draft.email
                )
                if draft.user_draft_id not in draft_ids:
                    await DraftSchema.update_draft_data(
                        user_draft_id = draft.user_draft_id,
                        value_dict = {
                            "is_draft_pushed": True
                        }
                    )
                    draft_ids.append(draft.user_draft_id)

        # Shuffle Logic
        for x in draft_ids:
            contest_draft = await DraftSchema.get_contest_member(
                draft_id = x,
                is_list = True
            )
            length_contest_user = len(contest_draft)
            position_list = list(range(1, length_contest_user + 1))
            for player in contest_draft:
                choice = random.choice(position_list)
                await DraftSchema.update_contest_member_with_contest_player_id(
                    contest_player_id = player.contest_player_id,
                    value_dict = {
                        "position": choice
                    }
                )
                position_list.remove(choice)
        return True

    @classmethod
    async def draft_cancelled_notification(cls):
        drafts = await DraftSchema.draft_cancelled_notification()
        for draft in drafts:
            notification_data = {
                "title": "Draft Cancelled",
                "body": NotificationConstant.DRAFT_CANCELLED.format(draft.league_name)
            }
            notification = await NotificationSchema.add_notification(
                user_id = draft.user_id,
                message = notification_data["body"]
            )
            await send_notification(
                user_id = draft.user_id,
                data = notification_data,
                notification_id = notification.notification_id
            )
            await send_mail_notification(
                notification_data = notification_data,
                email = draft.email
            )
            # To add refund logic here

            transaction = await UserProfileSchema.get_user_transaction_with_user_draft_id(
                user_id = draft.user_id,
                user_draft_id = draft.user_draft_id
            )

            if transaction:
                await UserProfileSchema.refund_amount(
                    user_id = draft.user_id,
                    actual_amount = -(transaction.amount),
                    deduct_add = transaction.deduct_add,
                    deduct_win = transaction.deduct_win,
                    deduct_cash = transaction.deduct_cash,
                    meta_data = {
                        "user_draft_id": str(draft.user_draft_id)
                    }
                )

            await DraftSchema.update_draft_data(
                user_draft_id = draft.user_draft_id,
                value_dict = {
                    "is_cancelled_pushed": True
                }
            )
        return True

    @classmethod
    async def draft_not_join_cancel(cls):
        drafts = await DraftSchema.draft_not_join_cancel()
        for draft in drafts:
            ist_time = datetime.now() + timedelta(hours=5, minutes=30)
            if draft.draft_starting_time + timedelta(hours = 1) <= ist_time:
                notification_data = {
                    "title": "Draft Cancelled",
                    "body": NotificationConstant.DRAFT_CANCELLED.format(draft.league_name)
                }
                notification = await NotificationSchema.add_notification(
                    user_id = draft.user_id,
                    message = notification_data["body"]
                )
                await send_notification(
                    user_id = draft.user_id,
                    data = notification_data,
                    notification_id = notification.notification_id
                )
                await send_mail_notification(
                    notification_data = notification_data,
                    email = draft.email
                )
                # To add refund logic here

                transaction = await UserProfileSchema.get_user_transaction_with_user_draft_id(
                    user_id = draft.user_id,
                    user_draft_id = draft.user_draft_id
                )

                if transaction:
                    await UserProfileSchema.refund_amount(
                        user_id = draft.user_id,
                        actual_amount = -(transaction.amount),
                        deduct_add = transaction.deduct_add,
                        deduct_win = transaction.deduct_win,
                        deduct_cash = transaction.deduct_cash,
                        meta_data = {
                            "user_draft_id": str(draft.user_draft_id)
                        }
                    )

                await DraftSchema.update_draft_data(
                    user_draft_id = draft.user_draft_id,
                    value_dict = {
                        "is_cancelled_pushed": True,
                        "is_draft_cancelled": True
                    }
                )
        return True
