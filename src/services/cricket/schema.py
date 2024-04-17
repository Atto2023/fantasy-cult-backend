from typing import List
from fastapi import Depends
from sqlalchemy import (
    Date, 
    and_, 
    func, 
    or_, 
    select,
    update,
    join,
    label
)
from sqlalchemy.orm import aliased
from pydantic import (
    BaseModel,
    UUID4
)
from fastapi_jwt_auth import AuthJWT
from fastapi_mail import (
    FastMail, 
    MessageSchema,
    MessageType
)
from datetime import timedelta,datetime

#Local Imports
from src.db.database import db
from src.db.models import (
    ContestPlayers, 
    CricketMatch, 
    CricketPlayer, 
    CricketSeries, 
    CricketSeriesMatchPoints, 
    CricketSeriesSquad, 
    CricketTeam, 
    HomeScreen, 
    UserDraft
)


class DummyDataSchema:

    @classmethod
    async def add_update_series_data(cls, value_dict):
        series_data = await cls.check_series_data(series_id = value_dict["cid"])
        if series_data:
            await cls.update_series_data(
                value_dict = value_dict
            )
        else:
            series_data = await cls.add_series_data(
                value_dict = value_dict
            )
        return series_data

    @classmethod
    async def add_series_data(cls, value_dict):
        series = CricketSeries(
            series_id = value_dict["cid"],
            name = value_dict["title"],
            short_name = value_dict["abbr"],
            series_category = value_dict["category"],
            series_type = value_dict["game_format"],
            series_start_date = datetime.strptime(value_dict["datestart"], "%Y-%m-%d"),
            series_end_date =datetime.strptime(value_dict["dateend"], "%Y-%m-%d"),
            team_id = []
        )
        db.add(series)
        await db.commit()
        return series

    @classmethod
    async def check_series_data(cls, series_id):
        series_data = select(
            CricketSeries
        ).where(
            CricketSeries.series_id == series_id
        )
        series_data = await db.execute(series_data)
        return series_data.scalars().one_or_none()

    @classmethod
    async def update_series_data(cls, value_dict):
        value_dict = {
            "series_id": value_dict["cid"],
            "name": value_dict["title"],
            "short_name": value_dict["abbr"],
            "series_category": value_dict["category"],
            "series_type": value_dict["game_format"],
            "series_start_date":  datetime.strptime(value_dict["datestart"], "%Y-%m-%d"),
            "series_end_date": datetime.strptime(value_dict["dateend"], "%Y-%m-%d"),
            "team_id": value_dict["team_id"] if "team_id" in value_dict else []
        }
        await db.execute(
            update(
                CricketSeries
            ).where(
                CricketSeries.series_id == value_dict["series_id"]
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.commit()
        return True
    
    @classmethod
    async def add_update_team_data(cls, value_dict):
        team_data = await cls.check_team_data(team_id = value_dict["tid"])
        if team_data:
            await cls.update_team_data(
                value_dict = value_dict
            )
        else:
            team_data = await cls.add_team_data(
                value_dict = value_dict
            )
        return team_data

    @classmethod
    async def add_team_data(cls, value_dict):
        team_data = CricketTeam(
            team_id = value_dict["tid"],
            name = value_dict["title"],
            short_name = value_dict["abbr"],
            team_type = value_dict["type"],
            thumb_url = value_dict["thumb_url"],
            logo_url = value_dict["logo_url"],
            country = value_dict["country"],
            sex = value_dict["sex"]
        )
        db.add(team_data)
        await db.commit()
        return team_data
    
    @classmethod
    async def check_team_data(cls, team_id):
        team_data = select(
            CricketTeam
        ).where(
            CricketTeam.team_id == team_id
        )

        team_data = await db.execute(team_data)
        return team_data.scalars().one_or_none()

    @classmethod
    async def update_team_data(cls, value_dict):
        value_dict = {
            "team_id": value_dict["tid"],
            "name": value_dict["title"],
            "short_name": value_dict["abbr"],
            "team_type": value_dict["type"],
            "thumb_url": value_dict["thumb_url"],
            "logo_url": value_dict["logo_url"],
            "country": value_dict["country"],
            "sex": value_dict["sex"]
        }
        await db.execute(
            update(
                CricketTeam
            ).where(
                CricketTeam.team_id == value_dict["team_id"]
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.commit()
        return True

    @classmethod
    async def add_update_player_data(cls, value_dict):
        player_data = await cls.check_player_data(player_id = value_dict["player"]["pid"])
        if player_data:
            await cls.update_player_data(
                value_dict = value_dict 
            )
        else:
            player_data = await cls.add_player_data(
                value_dict = value_dict
            )
        return player_data

    @classmethod
    async def add_player_data(cls, value_dict):
        player = CricketPlayer(
            player_id = value_dict["player"]["pid"],
            title = value_dict["player"]["title"],
            short_name = value_dict["player"]["short_name"],
            first_name = value_dict["player"]["first_name"],
            last_name = value_dict["player"]["last_name"],
            middle_name = value_dict["player"]["middle_name"],
            thumb_url = value_dict["player"]["thumb_url"],
            team = value_dict["player"]["nationality"],
            playing_role = value_dict["player"]["playing_role"],
            batting_style = value_dict["player"]["batting_style"],
            bowling_style = value_dict["player"]["bowling_style"],
            batting_stats = value_dict["batting"],
            bowling_stats = value_dict["bowling"]
        )
        db.add(player)
        await db.commit()
        return player
    
    @classmethod
    async def check_player_data(cls, player_id):
        player_data = select(
            CricketPlayer
        ).where(
            CricketPlayer.player_id == player_id
        )
        player_data = await db.execute(player_data)
        return player_data.scalars().one_or_none()

    @classmethod
    async def update_player_data(cls, value_dict):
        value_dict = {
            "player_id": value_dict["player"]["pid"],
            "title" : value_dict["player"]["title"],
            "short_name" : value_dict["player"]["short_name"],
            "first_name" : value_dict["player"]["first_name"],
            "last_name" : value_dict["player"]["last_name"],
            "middle_name" : value_dict["player"]["middle_name"],
            "thumb_url" : value_dict["player"]["thumb_url"],
            "team" : value_dict["player"]["nationality"],
            "playing_role" : value_dict["player"]["playing_role"],
            "batting_style" : value_dict["player"]["batting_style"],
            "bowling_style" : value_dict["player"]["bowling_style"],
            "batting_stats" : value_dict["batting"],
            "bowling_stats" : value_dict["bowling"]
        }
        await db.execute(
            update(
                CricketPlayer
            ).where(
                CricketPlayer.player_id == value_dict["player_id"]
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.commit()
        return True

    @classmethod
    async def add_update_cricket_series_squad(cls, value_dict):
        cricket_series_squad = await cls.check_cricket_series_squad(
            series_id = value_dict["series_id"],
            team_id = value_dict["team_id"]
        )
        if cricket_series_squad:
            await cls.update_cricket_series_squad(
                value_dict = value_dict
            )
        else:
            cricket_series_squad = await cls.add_cricket_series_squad(
                value_dict = value_dict
            )
        return cricket_series_squad

    @classmethod
    async def add_cricket_series_squad(cls, value_dict):
        cricket_series_squad = CricketSeriesSquad(
            series_id = value_dict["series_id"],
            team_id = value_dict["team_id"],
            player_id = value_dict["player_id"]
        )
        db.add(cricket_series_squad)
        await db.commit()
        return cricket_series_squad

    @classmethod
    async def check_cricket_series_squad(cls, series_id, team_id):
        cricket_series_squad = select(
            CricketSeriesSquad
        ).where(
            CricketSeriesSquad.series_id == series_id,
            CricketSeriesSquad.team_id == team_id
        )
        cricket_series_squad = await db.execute(cricket_series_squad)
        return cricket_series_squad.scalars().one_or_none()

    @classmethod
    async def update_cricket_series_squad(cls, value_dict):
        await db.execute(
            update(
                CricketSeriesSquad
            ).where(
                CricketSeriesSquad.series_id == value_dict["series_id"],
                CricketSeriesSquad.team_id == value_dict["team_id"]
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.commit()
        return True

    @classmethod
    async def add_update_cricket_series_match(cls, value_dict):
        cricket_series_match = await cls.check_cricket_series_match(
            match_id = value_dict["match_id"]
        )
        if cricket_series_match:
            await cls.update_cricket_series_match(
                value_dict = value_dict
            )
        else:
            cricket_series_match = await cls.add_cricket_series_match(
                value_dict = value_dict
            )
        return cricket_series_match

    @classmethod
    async def add_cricket_series_match(cls, value_dict):
        cricket_series_match = CricketMatch(
            match_id = value_dict["match_id"],
            series_id = value_dict["series_id"],
            match_format = value_dict["match_format"],
            team_a = value_dict["team_a"],
            team_b = value_dict["team_b"],
            match_start_time = datetime.strptime(value_dict["match_start_time"], "%Y-%m-%d %H:%M:%S"),
            match_end_time = datetime.strptime(value_dict["match_end_time"], "%Y-%m-%d %H:%M:%S"),
            last_update_on = None
        )
        db.add(cricket_series_match)
        await db.commit()
        return cricket_series_match

    @classmethod
    async def check_cricket_series_match(cls, match_id):
        cricket_series_match = select(
            CricketMatch
        ).where(
            CricketMatch.match_id == match_id
        )
        cricket_series_match = await db.execute(cricket_series_match)
        return cricket_series_match.scalars().one_or_none()
    
    @classmethod
    async def update_cricket_series_match(cls, value_dict):
        value_dict = {
            "match_id" : value_dict["match_id"],
            "series_id" : value_dict["series_id"],
            "match_format" : value_dict["match_format"],
            "team_a" : value_dict["team_a"],
            "team_b" : value_dict["team_b"],
            "match_start_time" : datetime.strptime(value_dict["match_start_time"], "%Y-%m-%d %H:%M:%S"),
            "match_end_time" : datetime.strptime(value_dict["match_end_time"], "%Y-%m-%d %H:%M:%S"),
        }
        await db.execute(
            update(
                CricketMatch
            ).where(
                CricketMatch.match_id == value_dict["match_id"]
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.commit()
        return True
    
       
    @classmethod
    async def get_all_home_screen(cls,limit:int=10,offset:int=1):
        home_screen_data = select(
            HomeScreen
        ).limit(
            limit=limit
        ).offset(
            offset=offset-1
        )
        home_screen_data = await db.execute(home_screen_data)
        return home_screen_data.scalars().all()

class CricketMatchSchema:

    @classmethod
    async def get_matches(cls, match_id, limit, offset, is_live = None, series_id = None,search_text:str=None):
        CricketTeamA = aliased(CricketTeam)
        CricketTeamB = aliased(CricketTeam)
        matches = select(
            CricketMatch.cricket_match_id,
            CricketSeries.cricket_series_id,
            CricketSeries.name.label("series_name"),
            CricketSeries.use_name.label("series_use_name"),
            CricketSeries.fc_name.label("series_fc_name"),
            CricketSeries.series_start_date,
            CricketMatch.match_format,
            CricketMatch.match_start_time,
            CricketMatch.is_live,
            CricketTeamA.cricket_team_id.label("cricket_team_id_a"),
            CricketTeamA.short_name.label("team_short_name_a"),
            CricketTeamA.fc_short_name.label("fc_short_name_a"),
            CricketTeamA.use_short_name.label("use_short_name_a"),
            CricketTeamA.logo_url.label("team_logo_url_a"),
            CricketTeamA.fc_logo_url.label("fc_logo_url_a"),
            CricketTeamA.use_logo_url.label("use_logo_url_a"),
            CricketTeamB.cricket_team_id.label("cricket_team_id_b"),
            CricketTeamB.short_name.label("team_short_name_b"),
            CricketTeamB.fc_short_name.label("fc_short_name_b"),
            CricketTeamB.use_short_name.label("use_short_name_b"),
            CricketTeamB.logo_url.label("team_logo_url_b"),
            CricketTeamB.fc_logo_url.label("fc_logo_url_b"),
            CricketTeamB.use_logo_url.label("use_logo_url_b"),
        ).join(
            CricketSeries,
            CricketSeries.cricket_series_id == CricketMatch.series_id,
            isouter=True
        ).join(
            CricketTeamA,
            CricketTeamA.cricket_team_id == CricketMatch.team_a,
            isouter=True
        ).join(
            CricketTeamB,
            CricketTeamB.cricket_team_id == CricketMatch.team_b,
            isouter=True
        )

        if is_live is not None:
            matches = matches.where(
                CricketMatch.is_live == is_live
            )

        if series_id:
            matches = matches.where(
                CricketMatch.series_id == series_id
            )

        if match_id:
            matches = matches.where(
                CricketMatch.cricket_match_id == match_id
            )

        if search_text:
            matches = matches.where(
                or_(
                    CricketMatch.match_format.ilike(f"%{search_text}%"),
                    CricketSeries.name.ilike(f"%{search_text}%"),
                    CricketSeries.fc_name.ilike(f"%{search_text}%"),
                    CricketTeamA.short_name.ilike(f"%{search_text}%"),
                    CricketTeamB.short_name.ilike(f"%{search_text}%")
                )
            )

        matches = matches.order_by(
            CricketMatch.match_start_time
        ).limit(limit).offset(offset-1)

        matches = await db.execute(matches)
        if match_id:
            return matches.one_or_none()
        return matches.all()

    @classmethod
    async def get_matches_of_remaining_series(cls, cricket_series_id):
        ist_time = datetime.now() + timedelta(hours=5, minutes=30)
        CricketTeamA = aliased(CricketTeam)
        CricketTeamB = aliased(CricketTeam)
        match_data = select(
            CricketMatch.cricket_match_id,
            CricketMatch.match_start_time,
            CricketTeamA.cricket_team_id.label("cricket_team_id_a"),
            CricketTeamA.short_name.label("team_short_name_a"),
            CricketTeamA.logo_url.label("team_logo_url_a"),
            CricketTeamB.cricket_team_id.label("cricket_team_id_b"),
            CricketTeamB.short_name.label("team_short_name_b"),
            CricketTeamB.logo_url.label("team_logo_url_b")
        ).join(
            CricketTeamA,
            CricketTeamA.cricket_team_id == CricketMatch.team_a,
            isouter=True
        ).join(
            CricketTeamB,
            CricketTeamB.cricket_team_id == CricketMatch.team_b,
            isouter=True
        ).where(
            CricketMatch.series_id == cricket_series_id,
            CricketMatch.match_start_time > ist_time
        ).order_by(
            CricketMatch.match_start_time.asc()
        )

        match_data = await db.execute(match_data)
        return match_data.all()

    @classmethod
    async def get_series(cls, limit = None, offset = None, series_id = None, is_live = None,search_text:str=None):
        series_data = select(
            CricketSeries.cricket_series_id,
            CricketSeries.series_id,
            CricketSeries.name.label("series_name"),
            CricketSeries.series_start_date,
            CricketSeries.use_name.label("series_use_name"),
            CricketSeries.fc_name.label("series_fc_name"),
            CricketSeries.is_live
        ).order_by(
            CricketSeries.series_start_date.desc()
        )

        if is_live is not None:
            series_data = series_data.where(
                CricketSeries.is_live == is_live
            )

        if series_id:
            series_data = series_data.where(
                CricketSeries.cricket_series_id == series_id
            )

        if search_text:
            series_data = series_data.where(
                or_(
                    CricketSeries.name.ilike(f"%{search_text}%"),
                    CricketSeries.fc_name.ilike(f"%{search_text}%"),
                )
            )

        if limit and offset:
            series_data = series_data.limit(limit).offset(offset-1)

        series_data = await db.execute(series_data)
        if series_id:
            return series_data.one_or_none()
        return series_data.all()

    @classmethod
    async def get_match_with_cricket_match_id(cls, cricket_match_id):
        match_data = select(
            CricketMatch.cricket_match_id,
            CricketMatch.match_id,
            CricketMatch.match_start_time
        ).where(
            CricketMatch.cricket_match_id == cricket_match_id
        )

        match_data = await db.execute(match_data)
        return match_data.one_or_none()

    @classmethod
    async def update_cricket_match_status(cls, match_id, is_live):
        value_dict = {
            "is_live" : is_live
        }
        await db.execute(
            update(
                CricketMatch
            ).where(
                CricketMatch.cricket_match_id == match_id
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
        return True

    @classmethod
    async def update_cricket_series_status(cls, series_id, is_live):
        value_dict = {
            "is_live" : is_live
        }
        await db.execute(
            update(
                CricketSeries
            ).where(
                CricketSeries.cricket_series_id == series_id
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.commit()
        return True

    @classmethod
    async def add_match_point(cls, value_dict):
        data = CricketSeriesMatchPoints(
            cricket_series_id = value_dict["cricket_series_id"],
            series_id = value_dict["series_id"],
            cricket_match_id = value_dict["cricket_match_id"],
            match_id = value_dict["match_id"],
            cricket_player_id = value_dict["cricket_player_id"],
            player_id = value_dict["player_id"],
            points = value_dict["points"]
        )
        db.add(data)
        await db.commit()
        return data

    @classmethod
    async def update_match_point(cls, cricket_series_match_point_id, value_dict):
        await db.execute(
            update(
                CricketSeriesMatchPoints
            ).where(
                CricketSeriesMatchPoints.cricket_series_match_point_id == cricket_series_match_point_id
            ).values(
                value_dict
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        try:
            await db.commit()
        except:
            await db.rollback()
        return True

    @classmethod
    async def get_match_point(cls, series_id, match_id, player_id):
        data = select(
            CricketSeriesMatchPoints
        ).where(
            CricketSeriesMatchPoints.series_id == series_id,
            CricketSeriesMatchPoints.match_id == match_id,
            CricketSeriesMatchPoints.player_id == player_id
        )
        data = await db.execute(data)
        return data.scalars().one_or_none()

    @classmethod
    async def add_update_point(cls, value_dict):
        data = await cls.get_match_point(
            series_id = value_dict["series_id"],
            match_id = value_dict["match_id"],
            player_id = value_dict["player_id"]
        )
        if data:
            await cls.update_match_point(
                cricket_series_match_point_id = data.cricket_series_match_point_id,
                value_dict = value_dict
            )
        else:
            data = await cls.add_match_point(
                value_dict = value_dict
            )
        return data
