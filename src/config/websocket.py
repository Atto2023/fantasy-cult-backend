from fastapi import WebSocket
from pydantic import UUID4
from src.db.models import ContestStatusEnum, DraftForEnum
from datetime import datetime, timedelta
import time
import random

from src.services.contest.schema import DraftSchema
from src.services.contest.serializer import LeaderboardResponseSerializer, MemberLeaderboardResponseSerializer, MemberResponseSerializer, PlayersResponseSerializer, TeamResponseSerializer
from src.services.cricket.schema import CricketMatchSchema
from src.services.user.schema import UserProfileSchema
from src.utils.entity_sports import EntitySportsLive
from src.utils.response import WebsocketErrorResponseSerializer, WebsocketSuccessResponseSerializer, response_structure

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.out_serializer = None
        self.out_turn_user_id = None

    async def connect(self, websocket: WebSocket, user_draft_id: UUID4, user_id: UUID4):
        await websocket.accept()
        if user_draft_id not in self.active_connections:
            self.active_connections[user_draft_id] = {}
        # if user_id not in self.active_connections[user_draft_id]:
        self.active_connections[user_draft_id][user_id] = websocket
        print(self.active_connections)
    
    async def notify(self, user_draft_id, user_id, payload):
        print(self.active_connections)
        if payload["request_type"] == 1: # List of the Cricket Players
            serializer = await self.get_list_of_players(user_draft_id)
        elif payload["request_type"] == 2: # List of the Draft Members
            serializer = await self.get_list_of_joined_members(user_draft_id, payload)

        for user, websocket in self.active_connections[user_draft_id].items():
            if payload["request_type"] == 1 or payload["request_type"] == 2:
                await websocket.send_json(serializer.json())
            elif payload["request_type"] == 3: # Static Data
                if str(user) == str(user_id):
                    serializer = await self.static_data(user_draft_id)
                    await websocket.send_json(serializer.json())
            elif payload["request_type"] == 4: # Select Player
                if str(user) == str(user_id):
                    serializer = await self.select_players(user_draft_id, user_id, payload)
                    await websocket.send_json(serializer.json())
            elif payload["request_type"] == 5: # Complete Draft
                if str(user) == str(user_id):
                    serializer = await self.complete_draft(user_draft_id)
                    await websocket.send_json(serializer.json())
            elif payload["request_type"] == 8: # Message for all the users
                serializer = await self.send_message(user_draft_id, payload)
                if str(user) == str(user_id):
                    serializer.data["user"] = "You"
                await websocket.send_json(serializer.json())
            else:
                serializer = WebsocketErrorResponseSerializer(
                    message = "Please send proper request_type",
                    response_type = -1
                )
                if str(user) == str(user_id):
                    await websocket.send_json(serializer.json())

        looping_var = serializer.response_type
        while looping_var == 2:
            turn_user_id = None
            for member in serializer.data["all_members"]:
                if member.your_turn:
                    turn_user_id = member.user_id
                if turn_user_id:
                    break
            websocket_user_list = []
            if turn_user_id:
                for user, websocket in self.active_connections[user_draft_id].items():
                    websocket_user_list.append(str(user))
                if str(turn_user_id) not in websocket_user_list:
                    list_of_players = await self.get_list_of_players(user_draft_id)
                    await self.select_players(user_draft_id, turn_user_id, {"player_id": "0", "player_list": list_of_players.dict()})
                    time.sleep(2)
                    serializer_player = await self.get_list_of_players(user_draft_id)
                    payload = {
                        "round": serializer.data["round"],
                        "position": serializer.data["position"]
                    }
                    serializer = await self.get_list_of_joined_members(user_draft_id, payload)
                    for user, websocket in self.active_connections[user_draft_id].items():
                        await websocket.send_json(serializer_player.json())
                        time.sleep(2)
                        await websocket.send_json(serializer.json())
                        time.sleep(2)
                else:
                    looping_var = 1
            else:
                looping_var = 1


    async def send_message(self, user_draft_id, payload):
        result = {}
        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )

        last_player_selected_id = draft_data.player_selected[-1]
        player_data = await DraftSchema.get_player_data(
            player_id = last_player_selected_id
        )
        result["player"] = player_data.name

        user_data = await UserProfileSchema.get_user_data(
            user_id = payload["user_id"],
            with_base = True
        )
        result["user"] = user_data.name
        return WebsocketSuccessResponseSerializer(
            message = "Data for Selected Player",
            response_type = 8,
            data = result
        )

    async def complete_draft(self, user_draft_id):
        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
        if draft_data.is_draft_completed:
            return WebsocketSuccessResponseSerializer(
                response_type = 5,
                message = "Draft Completed"
            )
        else:
            value_dict = {
                "is_draft_completed": True,
                "updated_at": datetime.now()
            }
            await DraftSchema.update_draft_data(
                user_draft_id = user_draft_id,
                value_dict = value_dict
            )
            return WebsocketSuccessResponseSerializer(
                response_type = 5,
                message = "Draft Completed"
            )


    async def select_players(self, user_draft_id, user_id, payload):
        bat = 0
        bowl = 0
        wk = 0
        all_rounder = 0
        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
        if draft_data.is_draft_completed:
            return WebsocketSuccessResponseSerializer(
                response_type = 5,
                message = "Draft Completed"
            )
        contest_member = await DraftSchema.get_contest_member(
            draft_id = user_draft_id,
            user_id = user_id
        )
        player_selected = contest_member.player_selected
        for player in player_selected:
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

        player_choice_bat = draft_data.player_choice["bat"]
        player_choice_bowl = draft_data.player_choice["bowl"]
        player_choice_wk = draft_data.player_choice["wk"]
        player_choice_all = draft_data.player_choice["all"]

        draft_player_selected = draft_data.player_selected
        if "player_id" in payload and payload["player_id"] != "0":
            if "player_id" not in draft_player_selected:
                if player_choice_bat <= bat and player_choice_bowl <= bowl and player_choice_wk <= wk and player_choice_all <= all_rounder:
                    player_selected.append(payload["player_id"])
                    draft_player_selected.append(payload["player_id"])
                else:
                    new_player_data = await DraftSchema.get_player_data(
                        player_id = payload["player_id"]
                    )
                    if new_player_data.role == "bat":
                        if player_choice_bat <= bat:
                            if player_choice_bowl <= bowl:
                                if player_choice_wk <= wk:
                                    if player_choice_all <= all_rounder:
                                        pass
                                    else:
                                        return WebsocketErrorResponseSerializer(
                                            message = f"Please fulfill the minimum skill requirement first!",
                                            response_type = 6
                                        )
                                else:
                                    return WebsocketErrorResponseSerializer(
                                        message = f"Please fulfill the minimum skill requirement first!",
                                        response_type = 6
                                    )
                            else:
                                return WebsocketErrorResponseSerializer(
                                    message = f"Please fulfill the minimum skill requirement first!",
                                    response_type = 6
                                )
                        else:
                            pass
                    elif new_player_data.role == "bowl":
                        if player_choice_bowl <= bowl:
                            if player_choice_bat <= bat:
                                if player_choice_wk <= wk:
                                    if player_choice_all <= all_rounder:
                                        pass
                                    else:
                                        return WebsocketErrorResponseSerializer(
                                            message = f"Please fulfill the minimum skill requirement first!",
                                            response_type = 6
                                        )
                                else:
                                    return WebsocketErrorResponseSerializer(
                                        message = f"Please fulfill the minimum skill requirement first!",
                                        response_type = 6
                                    )
                            else:
                                return WebsocketErrorResponseSerializer(
                                    message = f"Please fulfill the minimum skill requirement first!",
                                    response_type = 6
                                )
                        else:
                            pass
                    elif new_player_data.role == "all":
                        if player_choice_all <= all_rounder:
                            if player_choice_bat <= bat:
                                if player_choice_bowl <= bowl:
                                    if player_choice_wk <= wk:
                                        pass
                                    else:
                                        return WebsocketErrorResponseSerializer(
                                            message = f"Please fulfill the minimum skill requirement first!",
                                            response_type = 6
                                        )
                                return WebsocketErrorResponseSerializer(
                                    message = f"Please fulfill the minimum skill requirement first!",
                                    response_type = 6
                                )
                            else:
                                return WebsocketErrorResponseSerializer(
                                    message = f"Please fulfill the minimum skill requirement first!",
                                    response_type = 6
                                )
                        else:
                            pass
                    elif new_player_data.role == "wk" or new_player_data.role == "wkbat":
                        if player_choice_wk <= wk:
                            if player_choice_bat <= bat:
                                if player_choice_bowl <= bowl:
                                    if player_choice_all <= all_rounder:
                                        pass
                                    else:
                                        return WebsocketErrorResponseSerializer(
                                            message = f"Please fulfill the minimum skill requirement first!",
                                            response_type = 6
                                        )
                                return WebsocketErrorResponseSerializer(
                                    message = f"Please fulfill the minimum skill requirement first!",
                                    response_type = 6
                                )
                            else:
                                return WebsocketErrorResponseSerializer(
                                    message = f"Please fulfill the minimum skill requirement first!",
                                    response_type = 6
                                )
                        else:
                            pass
                    else:
                        return WebsocketErrorResponseSerializer(
                            message = f"There is problem in Player Role",
                            response_type = 6
                        )
                    player_selected.append(payload["player_id"])
                    draft_player_selected.append(payload["player_id"])
            else:
                return WebsocketErrorResponseSerializer(
                    message = f"This Player is already Selected, select Again",
                    response_type = 6
                )
        else:
            repsonse_list_of_players = payload["player_list"]
            repsonse_list_of_players = repsonse_list_of_players["data"]
            selected_player_id = None 
            for list_of_player in repsonse_list_of_players:
                if not list_of_player["is_selected"]:
                    if player_choice_bat <= bat and player_choice_bowl <= bowl and player_choice_wk <= wk and player_choice_all <= all_rounder:
                        selected_player_id = list_of_player["player_id"]
                    else:
                        new_player_data = await DraftSchema.get_player_data(
                            player_id = list_of_player["player_id"]
                        )
                        if new_player_data.role == "bat":
                            if player_choice_bat <= bat:
                                continue
                            else:
                                selected_player_id = list_of_player["player_id"]
                        elif new_player_data.role == "bowl":
                            if player_choice_bowl <= bowl:
                                continue
                            else:
                                selected_player_id = list_of_player["player_id"]
                        elif new_player_data.role == "all":
                            if player_choice_all <= all_rounder:
                                continue
                            else:
                                selected_player_id = list_of_player["player_id"]
                        elif new_player_data.role == "wk" or new_player_data.role == "wkbat":
                            if player_choice_wk <= wk:
                                continue
                            else:
                                selected_player_id = list_of_player["player_id"]
                        else:
                            return WebsocketErrorResponseSerializer(
                                message = f"There is problem in Player Role",
                                response_type = 6
                            )
                    if selected_player_id:
                        player_selected.append(selected_player_id)
                        draft_player_selected.append(selected_player_id)
                        break
                    else:
                        return WebsocketErrorResponseSerializer(
                            message = f"There is problem in selecting player automatically",
                            response_type = 6
                        )
        await DraftSchema.update_draft_data(
            user_draft_id = user_draft_id,
            value_dict = {
                "player_selected": draft_player_selected,
                "updated_at": datetime.now()
            }
        )
        await DraftSchema.update_contest_member(
            draft_id = user_draft_id,
            user_id = user_id,
            value_dict = {
                "player_selected": player_selected,
                "updated_at": datetime.now()
            }
        )
        return WebsocketSuccessResponseSerializer(
            message = "Player Selected",
            response_type = 4
        )

    async def static_data(self, user_draft_id):
        result = {}
        roles = await DraftSchema.get_unique_roles()
        roles = [i[0] for i in roles]
        result["roles"] = roles

        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
        result["is_captain_allowed"] = draft_data.is_captain_allowed
        result["invitation_code"] = draft_data.invitation_code
        result["player_choice"] = draft_data.player_choice
        result["total_rounds"] = draft_data.number_of_round
        result["top_picks"] = draft_data.top_picks
        result["draft_starting_time"] = draft_data.draft_starting_time

        result["team"] = []
        if draft_data.draft_for == DraftForEnum.SERIES:
            series_data = await DraftSchema.check_series_with_id(
                series_id = draft_data.draft_match_series_id
            )
            for team in series_data[0].team_id:
                team_data = await DraftSchema.get_team_data_with_id(
                    team_id = team
                )
                result["team"].append(
                    TeamResponseSerializer(**(team_data._asdict())).name
                )
        else: # this is for the match
            match_data = await DraftSchema.match_series_team(
                cricket_match_id = draft_data.draft_match_series_id
            )
            team_data_a = await DraftSchema.get_team_data_with_id(
                team_id = match_data.team_a
            )
            team_data_b = await DraftSchema.get_team_data_with_id(
                team_id = match_data.team_b
            )
            result["team"].append(
                TeamResponseSerializer(**(team_data_a._asdict())).name
            )
            result["team"].append(
                TeamResponseSerializer(**(team_data_b._asdict())).name
            )
        return WebsocketSuccessResponseSerializer(
            message = "Static Data",
            data = result,
            response_type = 3
        )


    async def get_list_of_joined_members(self, user_draft_id, payload):
        user_draft = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
        if user_draft.is_draft_completed:
            return WebsocketSuccessResponseSerializer(
                response_type = 5,
                message = "Draft Completed"
            )
        if user_draft.draft_for == DraftForEnum.MATCH:
            x = await CricketMatchSchema.get_match_with_cricket_match_id(
                cricket_match_id = user_draft.draft_match_series_id
            )
            # match_status = await EntitySportsLive.entity_match_status(
            #     match_id = x.match_id
            # )
            ist_time = datetime.now() + timedelta(hours=5, minutes=30)
            # date_start = datetime.strptime(match_status["date_start_ist"], "%Y-%m-%d %H:%M:%S")
            if x.match_start_time <= ist_time: # Scheduled
                if not user_draft.is_draft_cancelled:
                    await DraftSchema.update_draft_data(
                        user_draft_id = user_draft_id,
                        value_dict = {
                            "is_draft_cancelled": True
                        }
                    )
                return WebsocketErrorResponseSerializer(
                    response_type = 99,
                    message = "This Match has been started, so you can not play now. Your Money will be refunded"
                )
        else:
            x = await CricketMatchSchema.get_series(
                series_id = user_draft.draft_match_series_id
            )
            series_status = await EntitySportsLive.entity_series_status(
                series_id = x.series_id
            )
            if series_status["status"] == "result": # completed
                if not user_draft.is_draft_cancelled:
                    await DraftSchema.update_draft_data(
                        user_draft_id = user_draft_id,
                        value_dict = {
                            "is_draft_cancelled": True
                        }
                    )
                return WebsocketErrorResponseSerializer(
                    response_type = 99,
                    message = "This Series has been ended, so you can not play now. Your Money will be refunded"
                )

        contest_draft = await DraftSchema.get_contest_member(
            draft_id = user_draft_id,
            is_list = True
        )
        result = {}
        result["all_members"] = []
        ist_time = datetime.now() + timedelta(hours=5, minutes=30)
        result["start_draft"] = True if (len(contest_draft) == user_draft.max_playing_user and user_draft.draft_starting_time <= ist_time) else False
        result["draft_cancelled"] = True if user_draft.is_draft_cancelled else False
        if (result["start_draft"] == False) and (user_draft.draft_starting_time + timedelta(minutes = 5) <= ist_time):
            if not user_draft.is_draft_cancelled:
                await DraftSchema.update_draft_data(
                    user_draft_id = user_draft_id,
                    value_dict = {
                        "is_draft_cancelled": True
                    }
                )
                result["draft_cancelled"] = True
        new_round = payload["round"]
        result["draft_completed"] = False
        if result["start_draft"]:
            if payload["round"] == user_draft.number_of_round:
                if len(user_draft.player_selected) == (user_draft.number_of_round * user_draft.max_playing_user):
                    result["draft_completed"] = True
            if result["draft_completed"]:
                result["round"] = payload["round"]
                result["position"] = 0
            else:
                if payload["round"] % 2 != 0: # odd round
                    if payload["position"] == user_draft.max_playing_user:
                        new_round = payload["round"] + 1 if "round" in payload else 1
                    else:
                        result["round"] = payload["round"]
                    if new_round == payload["round"]:
                        result["position"] = payload["position"] + 1 if "position" in payload else 0
                    else:
                        result["position"] = payload["position"] if "position" in payload else 0
                        result["round"] = new_round
                else: # even round
                    if payload["position"] == 1:
                        new_round = payload["round"] + 1 if "round" in payload else 1
                        result["position"] = payload["position"] if "position" in payload else 0
                        result["round"] = new_round
                    else:
                        result["position"] = payload["position"] - 1 if "position" in payload else 0
                        result["round"] = new_round
        else:
            result["round"] = 1
            result["position"] = 0
        result["max_playing_user"] = user_draft.max_playing_user
        result["player_choice"] = user_draft.player_choice
        for member in contest_draft:
            user_data = await UserProfileSchema.get_user_data(
                user_id = member.user_id,
                with_base = True
            )
            draft_member = MemberResponseSerializer(**(user_data._asdict()))
            draft_member.position = member.position
            draft_member.your_turn = True if "position" in result and member.position == result["position"] else False
            if draft_member.your_turn:
                self.out_turn_user_id = draft_member.user_id
            for player_id in member.player_selected:
                player_data = await DraftSchema.get_player_data(
                    player_id = player_id
                )
                if player_data.role == "bat":
                    draft_member.bat = draft_member.bat + 1
                elif player_data.role == "bowl":
                    draft_member.bowl = draft_member.bowl + 1
                elif player_data.role == "all":
                    draft_member.all = draft_member.all + 1
                elif player_data.role == "wk" or player_data.role == "wkbat":
                    draft_member.wk = draft_member.wk + 1
                draft_member.total_player = draft_member.total_player + 1
            result["all_members"].append(draft_member)

        x =  WebsocketSuccessResponseSerializer(
            message = "All Members List",
            data = result,
            response_type = 2
        )
        self.out_serializer = x
        return x


    async def get_list_of_players(self, user_draft_id):
        user_draft = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
        all_players = []
        contest_players = await DraftSchema.get_contest_member(
            draft_id = user_draft_id,
            is_list = True
        )
        selected_players = []
        for i in contest_players:
            for j in i.player_selected:
                selected_players.append(j)
        if user_draft.draft_for == DraftForEnum.MATCH:
            match_player = await DraftSchema.match_series_team(
                cricket_match_id = user_draft.draft_match_series_id
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
                    player_response = PlayersResponseSerializer(
                        **(player_data._asdict())
                    )
                    if player_data.player_id in selected_players:
                        player_response.is_selected = True
                    all_players.append(player_response)
                for player in player_b.player_id:
                    player_data = await DraftSchema.get_player_data(
                        player_id = player
                    )
                    player_response = PlayersResponseSerializer(
                        **(player_data._asdict())
                    )
                    if player_data.player_id in selected_players:
                        player_response.is_selected = True
                    all_players.append(player_response)

        if user_draft.draft_for == DraftForEnum.SERIES:
            series_player = await DraftSchema.match_series_team_player(
                series_id = user_draft.draft_match_series_id
            )
            for player_id in series_player:
                for player in player_id.player_id:
                    player_data = await DraftSchema.get_player_data(
                        player_id = player
                    )
                    player_response = PlayersResponseSerializer(
                        **(player_data._asdict())
                    )
                    if player_data.player_id in selected_players:
                        player_response.is_selected = True
                    all_players.append(player_response)
        return WebsocketSuccessResponseSerializer(
            message = "All Players List",
            data = all_players,
            response_type = 1
        )


    async def disconnect(self, websocket: WebSocket, user_draft_id, user_id):
        del self.active_connections[user_draft_id][user_id]
        print(self.active_connections)

class LeaderboardConnectionManager:

    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, user_draft_id: UUID4, user_id: UUID4):
        await websocket.accept()
        if user_draft_id not in self.active_connections:
            self.active_connections[user_draft_id] = {}
        #if user_id not in self.active_connections[user_draft_id]:
        self.active_connections[user_draft_id][user_id] = websocket
        print(self.active_connections)

    async def notify(self, user_draft_id, user_id):
        print(self.active_connections)
        for user, websocket in self.active_connections[user_draft_id].items():
            if str(user) == str(user_id):
                serializer = await self.get_list_of_users(user_draft_id, user_id)
                await websocket.send_json(serializer.json())

    async def get_list_of_users(self, user_draft_id, user_id):
        draft_data = await DraftSchema.get_draft_data(
            user_draft_id = user_draft_id
        )
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
        leader_board = LeaderboardResponseSerializer(**(data._asdict()))
        if not data.series_use_name:
            leader_board.series_name = data.series_fc_name
        if draft_data.draft_for == DraftForEnum.MATCH:
            if not data.use_short_name_a:
                leader_board.team_short_name_a = data.fc_short_name_a
            if not data.use_logo_url_a:
                leader_board.team_logo_url_a = data.fc_logo_url_a
            if not data.use_short_name_b:
                leader_board.team_short_name_b = data.fc_short_name_b
            if not data.use_logo_url_b:
                leader_board.team_logo_url_b = data.fc_logo_url_b
        leader_board.series_start_day = leader_board.series_start_date.strftime('%A') if leader_board.series_start_date else None
        leader_board.match_start_day = leader_board.match_start_time.strftime('%A') if leader_board.match_start_time else None
        leader_board.draft_for = draft_data.draft_for
        leader_board.top_picks = draft_data.top_picks
        leader_board.number_of_round = draft_data.number_of_round
        contest_member = await DraftSchema.get_contest_member(
            draft_id = user_draft_id,
            is_list = True,
            by_points = True
        )

        if draft_data.is_captain_allowed:
            if contest_member[0].status == ContestStatusEnum.UPCOMING:
                leader_board.show_captain_change = True
            else:
                leader_board.show_captain_change = False
        else:
            leader_board.show_captain_change = False
        rank = 1
        for member in contest_member:
            if str(user_id) == str(member.user_id):
                leader_board.logged_in_user_captain = member.captain if member.captain else None
                leader_board.logged_in_user_vice_captain = member.vice_captain if member.vice_captain else None
            user_data = await UserProfileSchema.get_user_data(
                user_id = member.user_id
            )
            member_response = MemberLeaderboardResponseSerializer(**(member._asdict()))
            member_response.name = user_data.name
            member_response.profile_image = user_data.profile_image
            member_response.position = rank
            rank = 1 if contest_member[0].status == ContestStatusEnum.UPCOMING else rank + 1
            leader_board.member_data.append(member_response)

        return WebsocketSuccessResponseSerializer(
            message = "Leaderboard",
            response_type = 1,
            data = leader_board
        )

    async def disconnect(self, websocket: WebSocket, user_draft_id, user_id):
        del self.active_connections[user_draft_id][user_id]
        print(self.active_connections)
