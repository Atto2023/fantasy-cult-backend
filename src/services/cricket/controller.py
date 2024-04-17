#Third Party Imports
from datetime import (
    datetime, 
    timedelta
)
import time
import uuid,logging,math
from fastapi import status
from pydantic import UUID4
from src.db.models import (
    ContestStatusEnum, 
    DraftForEnum
)
from src.services.admin.serializer import HomeScreenResponseSerializer
from src.services.contest.schema import DraftSchema
from src.utils.entity_sports import (
    EntitySports, 
    EntitySportsPoint
)

#Local imports
from src.utils.jwt import auth_check
from src.utils.constant import (
    UserConstant,
    SportsConstant
)
from src.services.cricket.schema import (
    CricketMatchSchema,
    DummyDataSchema
)
from src.services.cricket.serializer import (
    MatchListResponseSerializer
)
from src.utils.response import (
    SuccessResponseSerializer,
    ErrorResponseSerializer,
    response_structure
)

class DummyDataController:

    @classmethod
    async def series_process_data(cls, series_data):
        for series in series_data:
            series_squad_data = await EntitySports.series_squad_data(
                series_id = series["cid"]
            )
            series_value = await DummyDataSchema.add_update_series_data(
                value_dict = series
            )
            team_id = []
            for series_team in series_squad_data:
                team_data = await EntitySports.cricket_team_data(
                    team_id = series_team["team"]["tid"]
                )
                team = await DummyDataSchema.add_update_team_data(
                    value_dict = team_data
                )
                cricket_team_id = team.cricket_team_id
                team_id.append(cricket_team_id)
                player_id = []
                for series_player in series_team["players"]:
                    player_data = await EntitySports.cricket_player_data(
                        player_id = series_player["pid"]
                    )
                    if player_data:
                        player = await DummyDataSchema.add_update_player_data(
                            value_dict = player_data
                        )
                        player_id.append(player.cricket_player_id)
                await DummyDataSchema.add_update_cricket_series_squad(
                    value_dict = {
                        "series_id": series_value.cricket_series_id,
                        "team_id": cricket_team_id,
                        "player_id": player_id
                    }
                )
            
            cricket_series_match_data = await EntitySports.cricket_series_match_data(
                series_id = series["cid"]
            )
            for cricket_series_match in cricket_series_match_data:
                team_a = await DummyDataSchema.check_team_data(team_id=cricket_series_match["teama"]["team_id"]) 
                team_b = await DummyDataSchema.check_team_data(team_id=cricket_series_match["teamb"]["team_id"])
                if team_a and team_b:
                    value_dict = {
                        "match_id": cricket_series_match["match_id"],
                        "series_id": series_value.cricket_series_id,
                        "match_format": cricket_series_match["format_str"],
                        "team_a": team_a.cricket_team_id,
                        "team_b": team_b.cricket_team_id,
                        "match_start_time": cricket_series_match["date_start_ist"],
                        "match_end_time": cricket_series_match["date_end_ist"]
                    }
                    await DummyDataSchema.add_update_cricket_series_match(
                        value_dict = value_dict
                    )
            
            series["team_id"] = team_id
            await DummyDataSchema.add_update_series_data(
                value_dict = series
            )

        return True


    @classmethod
    async def add_dummy_data(cls):
        series_data_live = await EntitySports.cricket_series_data_live()
        await cls.series_process_data(series_data_live)
        series_data_fixture = await EntitySports.cricket_series_data_fixture()
        await cls.series_process_data(series_data_fixture)
        return True


    @classmethod
    async def match_point(cls):
        match_point = await DraftSchema.get_matchs_for_points()
        for match in match_point:
            ist_time = datetime.now() + timedelta(hours=5, minutes=30)
            if match.match_start_time <= ist_time:
                point_data = await EntitySportsPoint.entity_sports_points(
                    match_id = match.match_id
                )
                value_dict = {}
                try:
                    if point_data["status"] == 3 or point_data["status"] == 2:# this is for live
                        match_data = await DummyDataSchema.check_cricket_series_match(
                            match_id = int(point_data["match_id"])
                        )
                        if match_data:
                            value_dict["match_id"] = match_data.match_id
                            value_dict["cricket_match_id"] = match_data.cricket_match_id
                        series_data = await DummyDataSchema.check_series_data(
                            series_id = int(point_data["competition"]["cid"])
                        )
                        if series_data:
                            value_dict["series_id"] = series_data.series_id
                            value_dict["cricket_series_id"] = series_data.cricket_series_id
                        if point_data["points"]["teama"] != '':
                            if "playing11" in point_data["points"]["teama"] and point_data["points"]["teama"]["playing11"] != '':
                                for player in point_data["points"]["teama"]["playing11"]:
                                    player_data = await DummyDataSchema.check_player_data(
                                        player_id = int(player["pid"])
                                    )
                                    if player_data and match_data and series_data:
                                        value_dict["points"] = int(player["point"])
                                        value_dict["player_id"] = player_data.player_id
                                        value_dict["cricket_player_id"] = player_data.cricket_player_id

                                        await CricketMatchSchema.add_update_point(
                                            value_dict = value_dict
                                        )
                            if "substitute" in point_data["points"]["teama"] and point_data["points"]["teama"]["substitute"] != '':
                                for player in point_data["points"]["teama"]["substitute"]:
                                    player_data = await DummyDataSchema.check_player_data(
                                        player_id = int(player["pid"])
                                    )
                                    if player_data and match_data and series_data:
                                        value_dict["points"] = int(player["point"])
                                        value_dict["player_id"] = player_data.player_id
                                        value_dict["cricket_player_id"] = player_data.cricket_player_id

                                        await CricketMatchSchema.add_update_point(
                                            value_dict = value_dict
                                        )
                        if point_data["points"]["teamb"] != '':
                            if "playing11" in point_data["points"]["teamb"] and point_data["points"]["teamb"]["playing11"] != '':
                                for player in point_data["points"]["teamb"]["playing11"]:
                                    player_data = await DummyDataSchema.check_player_data(
                                        player_id = int(player["pid"])
                                    )
                                    if player_data and match_data and series_data:
                                        value_dict["points"] = int(player["point"])
                                        value_dict["player_id"] = player_data.player_id
                                        value_dict["cricket_player_id"] = player_data.cricket_player_id

                                        await CricketMatchSchema.add_update_point(
                                            value_dict = value_dict
                                        )
                            if "substitute" in point_data["points"]["teamb"] and point_data["points"]["teamb"]["substitute"] != '':
                                for player in point_data["points"]["teamb"]["substitute"]:
                                    player_data = await DummyDataSchema.check_player_data(
                                        player_id = int(player["pid"])
                                    )
                                    if player_data and match_data and series_data:
                                        value_dict["points"] = int(player["point"])
                                        value_dict["player_id"] = player_data.player_id
                                        value_dict["cricket_player_id"] = player_data.cricket_player_id

                                        await CricketMatchSchema.add_update_point(
                                            value_dict = value_dict
                                        )

                        if point_data["status"] == 2: # this is for completed
                            await DraftSchema.update_match_point_status(
                                match_id = match.match_id,
                                is_point_added = True
                            )
                        print(match)
                except Exception as e:
                    print(f"Match ID : {match.match_id}")
                    print(f"Exception in match point : {e}")
        return True

    @classmethod
    async def allocate_point(cls):
        draft_data = await DraftSchema.get_draft_data(
            is_result_announce = False,
            is_list = True
        )
        for draft in draft_data:
            contest_data = await DraftSchema.get_contest_member(
                draft_id = draft.user_draft_id,
                is_list = True
            )
            for contest in contest_data:
                if contest.status != ContestStatusEnum.COMPLETED:
                    point_of_all_player = []
                    for player_id in contest.player_selected:
                        if draft.draft_for == DraftForEnum.MATCH:
                            player_points = await DraftSchema.get_match_points(
                                cricket_player_id = player_id,
                                cricket_match_id = draft.draft_match_series_id
                            )
                        else: # this is for series
                            player_points = 0
                            for match_id in draft.match_id_point:
                                points = await DraftSchema.get_match_points(
                                    cricket_player_id = player_id,
                                    cricket_match_id = match_id
                                )
                                if points:
                                    player_points = player_points + points
                        if player_points:
                            if contest.captain and str(contest.captain) == str(player_id):
                                x = 2.0*player_points
                                point_of_all_player.append(x)
                            elif contest.vice_captain and str(contest.vice_captain) == str(player_id):
                                x = 1.5*player_points
                                point_of_all_player.append(x)
                            else:
                                point_of_all_player.append(player_points)
                    total = 0
                    for _ in range(int(draft.top_picks)):
                        if len(point_of_all_player) > 0:
                            point = max(point_of_all_player)
                            total = total + point
                            point_of_all_player.remove(point)
                    await DraftSchema.update_contest_member_with_contest_player_id(
                        contest_player_id = contest.contest_player_id,
                        value_dict = {
                            "points": total
                        }
                    )

    @classmethod
    async def get_all_home_screen(cls, token, authorize, limit: int=10, offset: int=1):
        await auth_check(authorize=authorize, token=token)
        homescreen_id = authorize.get_jwt_subject()

        home_screen_data = await DummyDataSchema.get_all_home_screen(
            limit = limit,
            offset = offset
        )
        data = [HomeScreenResponseSerializer.from_orm(i) for i in home_screen_data]
        serializer = SuccessResponseSerializer(
            message = UserConstant.HOME_SCREEN_LIST,
            data = data,
            status_code=status.HTTP_200_OK
        )
        logging.info(
            msg="homescreen data List",
            extra={"custom_args": "GET-admin/get_all_home_screen"}
        )
        return response_structure(
            serializer = serializer,
            status_code = serializer.status_code
        )

class CricketMatchController:

    @classmethod
    async def get_matches(cls, match_id, series_id, token, authorize, limit, offset):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        matches = await CricketMatchSchema.get_matches(
            match_id = match_id,
            series_id = series_id,
            limit = limit,
            offset = offset,
            is_live = True
        )
        if match_id:
            match_serializer = MatchListResponseSerializer(**(matches._asdict()))
            if not matches.series_use_name:
                match_serializer.series_name = matches.series_fc_name
            if not matches.use_short_name_a:
                match_serializer.team_short_name_a = matches.fc_short_name_a
            if not matches.use_logo_url_a:
                match_serializer.team_logo_url_a = matches.fc_logo_url_a
            if not matches.use_short_name_b:
                match_serializer.team_short_name_b = matches.fc_short_name_b
            if not matches.use_logo_url_b:
                match_serializer.team_logo_url_b = matches.fc_logo_url_b
            match_serializer.series_start_day = match_serializer.series_start_date.strftime('%A') if match_serializer.series_start_date else None
            match_serializer.match_start_day = match_serializer.match_start_time.strftime('%A') if match_serializer.match_start_time else None
        else:
            match_serializer = []
            for i in matches:
                data  = MatchListResponseSerializer(**(i._asdict()))
                if not i.series_use_name:
                    data.series_name = i.series_fc_name
                if not i.use_short_name_a:
                    data.team_short_name_a = i.fc_short_name_a
                if not i.use_logo_url_a:
                    data.team_logo_url_a = i.fc_logo_url_a
                if not i.use_short_name_b:
                    data.team_short_name_b = i.fc_short_name_b
                if not i.use_logo_url_b:
                    data.team_logo_url_b = i.fc_logo_url_b
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
    async def get_series(cls, series_id, token, authorize, limit, offset):
        await auth_check(token=token,authorize=authorize)
        user_id = authorize.get_jwt_subject()
        series = await CricketMatchSchema.get_series(
            series_id = series_id,
            limit = limit,
            offset = offset,
            is_live = True
        )
        if series_id:
            series_serializer = MatchListResponseSerializer(**(series._asdict()))
            if not series.series_use_name:
                series_serializer.series_name = series.series_fc_name
            series_serializer.series_start_day = series_serializer.series_start_date.strftime('%A') if series_serializer.series_start_date else None
        else:
            series_serializer = []
            for i in series:
                data  = MatchListResponseSerializer(**(i._asdict()))
                if not i.series_use_name:
                    data.series_name = i.series_fc_name
                data.series_start_day = data.series_start_date.strftime('%A') if data.series_start_date else None
                series_serializer.append(data)
        serializer = SuccessResponseSerializer(
            message = "Series List",
            data = series_serializer
        )
        return response_structure(
            serializer = serializer,
            status_code = status.HTTP_200_OK
        )

    @classmethod
    async def get_matches_of_remaining_series(cls, series_id):
        remaining_matches =  await CricketMatchSchema.get_matches_of_remaining_series(
            cricket_series_id = series_id
        )
        ist_time = datetime.now() + timedelta(hours=5, minutes=30)
        if remaining_matches:
            remaining_matches = [i._asdict() for i in remaining_matches if i.match_start_time.date() > ist_time.date()]
            if remaining_matches:
                serializer = SuccessResponseSerializer(
                    data = remaining_matches,
                    message = f"Please note points from Match {remaining_matches[0]['team_short_name_a']} vs {remaining_matches[0]['team_short_name_b']} on {remaining_matches[0]['match_start_time']} IST till the final match of the series will be considered in this draft"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_200_OK
                )
            else:
                serializer = SuccessResponseSerializer(
                    status_code = status.HTTP_207_MULTI_STATUS,
                    data = {},
                    message = f"No Matches for this series are left, please create draft for another series"
                )
                return response_structure(
                    serializer = serializer,
                    status_code = status.HTTP_207_MULTI_STATUS
                )
        else:
            serializer = SuccessResponseSerializer(
                status_code = status.HTTP_207_MULTI_STATUS,
                data = {},
                message = f"No Matches for this series are left, please create draft for another series"
            )
            return response_structure(
                serializer = serializer,
                status_code = status.HTTP_207_MULTI_STATUS
            )
