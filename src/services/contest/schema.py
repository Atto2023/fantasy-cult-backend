from pydantic import UUID4
from src.db.models import (
    ContestPlayers, 
    ContestStatusEnum, 
    CricketMatch, 
    CricketPlayer, 
    CricketSeries, 
    CricketSeriesMatchPoints, 
    CricketSeriesSquad, 
    CricketTeam, 
    DraftForEnum, 
    User, 
    UserDraft
)
from sqlalchemy import(
    distinct,
    or_, 
    select, 
    func, 
    update,
    join,
    text
)
from src.db.database import db
from src.services.contest.serializer import CreateDraftRequestSerializer
from datetime import datetime, timedelta, date

from src.services.cricket.schema import CricketMatchSchema

class DraftSchema:

    @classmethod
    async def check_invitation_code(cls, invitation_code):
        draft = select(
            UserDraft
        ).where(
            UserDraft.invitation_code == str(invitation_code)
        )

        draft = await db.execute(draft)
        return draft.one_or_none()

    @classmethod
    async def match_series_team(cls, cricket_match_id):
        match_player = select(
            CricketMatch.cricket_match_id,
            CricketMatch.series_id,
            CricketMatch.team_a,
            CricketMatch.team_b
        ).where(
            CricketMatch.cricket_match_id == cricket_match_id
        )

        match_player = await db.execute(match_player)
        return match_player.one_or_none()

    @classmethod
    async def match_series_team_player(cls, series_id = None, team_id = None):
        squad = select(
            CricketSeriesSquad.player_id
        )

        if series_id:
            squad = squad.where(
                CricketSeriesSquad.series_id == series_id
            )

        if team_id:
            squad = squad.where(
                CricketSeriesSquad.team_id == team_id
            )

            squad = await db.execute(squad)
            return squad.one_or_none()
        squad = await db.execute(squad)
        return squad.all()

    @classmethod
    async def check_series_with_id(cls, series_id):
        series_data = select(
            CricketSeries
        ).where(
            CricketSeries.cricket_series_id == series_id
        )

        series_data = await db.execute(series_data)
        return series_data.one_or_none()

    @classmethod
    async def create_draft(cls, request: CreateDraftRequestSerializer, user_id):
        if request.draft_for == DraftForEnum.SERIES:
            remaining_matches = await CricketMatchSchema.get_matches_of_remaining_series(
                cricket_series_id = request.draft_match_series_id
            )
            ist_time = datetime.now() + timedelta(hours=5, minutes=30)
            match_id_point = [i.cricket_match_id for i in remaining_matches if i.match_start_time.date() > ist_time.date()]
        else:
            match_id_point = [request.draft_match_series_id]
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
            number_of_round = request.number_of_round,
            is_captain_allowed = request.is_captain_allowed,
            top_picks = request.top_picks,
            player_selected = [],
            match_id_point = match_id_point,
            is_draft_completed = False
        )
        db.add(add_draft)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return add_draft

    @classmethod
    async def get_draft_data(cls, is_draft_cancelled = None, is_draft_completed = None, is_result_announce = None, is_list = None, is_public = None, user_draft_id = None, invitation_code = None, draft_for = None, draft_match_series_id = None, limit = None, offset = None,search_text:str=None,start_date: date = None, end_date: date = None):
        user_draft = select(
            UserDraft.user_draft_id,
            UserDraft.user_id,
            UserDraft.league_name,
            UserDraft.invitation_code,
            UserDraft.max_playing_user,
            UserDraft.entry_amount,
            UserDraft.fantasy_commission,
            UserDraft.winners_price,
            UserDraft.player_choice,
            UserDraft.total_amount,
            UserDraft.draft_for,
            UserDraft.draft_match_series_id,
            UserDraft.is_draft_completed,
            UserDraft.is_result_announce,
            UserDraft.is_draft_cancelled,
            UserDraft.is_public,
            UserDraft.draft_starting_time,
            UserDraft.number_of_round,
            UserDraft.player_selected,
            UserDraft.is_captain_allowed,
            UserDraft.is_cancelled_pushed,
            UserDraft.is_draft_pushed,
            UserDraft.match_id_point,
            UserDraft.top_picks,
            UserDraft.created_at
        ).order_by(
            UserDraft.created_at.desc()
        )

        if is_draft_cancelled is not None:
            user_draft = user_draft.where(
                UserDraft.is_draft_cancelled == is_draft_cancelled
            )

        if is_draft_completed is not None:
            user_draft = user_draft.where(
                UserDraft.is_draft_completed == is_draft_completed
            )

        if is_result_announce is not None:
            user_draft = user_draft.where(
                UserDraft.is_result_announce == is_result_announce
            )

        if is_public is not None:
            user_draft = user_draft.where(
                UserDraft.is_public == is_public
            )

        if draft_for:
            user_draft = user_draft.where(
                UserDraft.draft_for == draft_for
            )

        if draft_match_series_id:
            user_draft = user_draft.where(
                UserDraft.draft_match_series_id == draft_match_series_id
            )

        if user_draft_id:
            user_draft = user_draft.where(
                UserDraft.user_draft_id == user_draft_id
            )

        if invitation_code:
            user_draft = user_draft.where(
                UserDraft.invitation_code == invitation_code
            )

        if search_text:
            user_draft = user_draft.where(
                or_(
                    UserDraft.league_name.ilike(f"%{search_text}%"),
                    UserDraft.invitation_code.ilike(f"%{search_text}%"),
                )
            )

        if start_date:
            user_draft = user_draft.where(
                UserDraft.created_at >= start_date
            )

        if end_date:
            user_draft = user_draft.where(
                UserDraft.created_at <= (end_date + timedelta(days=1))
            )

        if limit and offset:
            user_draft = user_draft.limit(limit).offset(offset-1)

        user_draft = await db.execute(user_draft)
        if is_list:
            return user_draft.all()
        return user_draft.one_or_none()

    @classmethod
    async def update_draft_data(cls, user_draft_id, value_dict):
        draft = update(
            UserDraft
        ).where(
            UserDraft.user_draft_id == user_draft_id,
        ).values(
            value_dict
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(draft)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
        return True

    @classmethod
    async def get_member_count_in_draft(cls, user_draft_id):
        contest_player = select(
            func.count(ContestPlayers.contest_player_id)
        ).where(
            ContestPlayers.draft_id == user_draft_id
        )
        contest_player = await db.execute(contest_player)
        return contest_player.scalar()

    @classmethod
    async def get_player_data(cls, player_id, is_list = False):
        player_data = select(
            CricketPlayer.cricket_player_id.label("player_id"),
            CricketPlayer.first_name.label("name"),
            CricketPlayer.thumb_url.label("logo"),
            CricketPlayer.playing_role.label("role"),
            CricketPlayer.team,
            CricketPlayer.batting_style,
            CricketPlayer.bowling_style,
            CricketPlayer.batting_stats,
            CricketPlayer.bowling_stats
        )

        if is_list:
            player_data = player_data.where(
                CricketPlayer.cricket_player_id.in_(player_id)
            )
        else:
            player_data = player_data.where(
                CricketPlayer.cricket_player_id == player_id
            )

        player_data = await db.execute(player_data)
        if is_list:
            return player_data.all()
        return player_data.one_or_none()


    @classmethod
    async def add_contest_member(cls, draft_id, user_id, position = None):
        contest_member = ContestPlayers(
            draft_id = draft_id,
            user_id = user_id,
            player_selected = [],
            position = position if position else 1
        )
        db.add(contest_member)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        return contest_member

    @classmethod
    async def get_contest_member(cls, draft_id = None, user_id = None, contest_player_id = None, is_list = False, by_points = False):
        contest_member = select(
            ContestPlayers.contest_player_id,
            ContestPlayers.draft_id,
            ContestPlayers.user_id,
            ContestPlayers.player_selected,
            ContestPlayers.captain,
            ContestPlayers.vice_captain,
            ContestPlayers.position,
            ContestPlayers.points,
            ContestPlayers.amount,
            ContestPlayers.status,
            ContestPlayers.created_at
        )

        if draft_id:
            contest_member = contest_member.where(
                ContestPlayers.draft_id == draft_id
            )

        if user_id:
            contest_member = contest_member.where(
                ContestPlayers.user_id == user_id
            )

        if contest_player_id:
            contest_member = contest_member.where(
                ContestPlayers.contest_player_id == contest_player_id
            )

        if by_points:
            contest_member = contest_member.order_by(
                ContestPlayers.points.desc()
            )
        else:
            contest_member = contest_member.order_by(
                ContestPlayers.position.asc()
            )

        contest_member = await db.execute(contest_member)
        if is_list:
            return contest_member.all()
        return contest_member.one_or_none()

    @classmethod
    async def update_contest_member(cls, draft_id, user_id, value_dict):
        contest_member = update(
            ContestPlayers
        ).where(
            ContestPlayers.draft_id == draft_id,
            ContestPlayers.user_id == user_id
        ).values(
            value_dict
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(contest_member)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
        return True

    @classmethod
    async def update_contest_member_with_contest_player_id(cls, contest_player_id, value_dict):
        contest_member = update(
            ContestPlayers
        ).where(
            ContestPlayers.contest_player_id == contest_player_id
        ).values(
            value_dict
        ).execution_options(
            synchronize_session="fetch"
        )
        await db.execute(contest_member)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
        return True

    @classmethod
    async def get_unique_roles(cls):
        player_data = select(
            distinct(CricketPlayer.playing_role)
        ).where(
            CricketPlayer.playing_role != "wkbat",
            CricketPlayer.playing_role != ""
        )

        player_data = await db.execute(player_data)
        return player_data.all()

    @classmethod
    async def get_team_data_with_id(cls, team_id):
        team_data = select(
            CricketTeam.cricket_team_id,
            CricketTeam.fc_short_name,
            CricketTeam.use_short_name,
            CricketTeam.short_name
        ).where(
            CricketTeam.cricket_team_id == team_id,
            CricketTeam.short_name != "TBA"
        )

        team_data = await db.execute(team_data)
        return team_data.one_or_none()

    @classmethod
    async def get_my_contest(cls, user_id, contest_status, limit, offset):
        s_query = select(
            ContestPlayers.draft_id,
            UserDraft.draft_for,
            UserDraft.draft_match_series_id,
            CricketMatch.match_start_time,
            UserDraft.match_id_point[1].label("match_id")
        ).join(
            UserDraft,
            UserDraft.user_draft_id == ContestPlayers.draft_id
        ).join(
            CricketMatch,
            CricketMatch.cricket_match_id == UserDraft.match_id_point[1]
        ).where(
            ContestPlayers.user_id == user_id,
            ContestPlayers.status == contest_status,
            UserDraft.is_draft_cancelled == False
        ).order_by(
            UserDraft.draft_match_series_id
        ).distinct(
            UserDraft.draft_match_series_id
        ).subquery()

        if contest_status == ContestStatusEnum.COMPLETED:
            query = select(
                s_query
            ).order_by(
                s_query.c.match_start_time.desc()
            )
        else:
            query = select(
                s_query
            ).order_by(
                s_query.c.match_start_time.asc()
            )

        query = query.limit(limit).offset(offset-1)

        query = await db.execute(query)
        return query.all()

    @classmethod
    async def get_my_match_contest(cls, user_id, draft_id, contest_status):
        query = select(
            ContestPlayers.draft_id,
            ContestPlayers.amount,
        ).where(
            ContestPlayers.user_id == user_id,
            ContestPlayers.draft_id == draft_id,
            ContestPlayers.status == contest_status
        )

        query = await db.execute(query)
        return query.all()

    @classmethod
    async def get_username_from_contest(cls, user_draft_id):
        data = select(
            ContestPlayers.draft_id,
            ContestPlayers.player_selected,
            User.name
        ).join(
            User,
            User.user_id == ContestPlayers.user_id
        ).where(
            ContestPlayers.draft_id == user_draft_id
        )

        data = await db.execute(data)
        return data.all()

    @classmethod
    async def get_todays_match(cls):
        data = select(
            CricketMatch.cricket_match_id,
            CricketMatch.match_id,
            CricketMatch.match_start_time,
            UserDraft.user_draft_id,
            UserDraft.is_captain_allowed,
            ContestPlayers.contest_player_id,
            ContestPlayers.player_selected,
            ContestPlayers.captain,
            ContestPlayers.vice_captain
        ).join(
            UserDraft,
            UserDraft.draft_match_series_id == CricketMatch.cricket_match_id
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).where(
            ContestPlayers.status == ContestStatusEnum.UPCOMING
        )

        data = await db.execute(data)
        return data.all()

    @classmethod
    async def series_status_to_live(cls):
        series = select(
            CricketSeries.cricket_series_id,
            CricketSeries.series_id,
            CricketSeries.series_start_date,
            UserDraft.user_draft_id,
            UserDraft.match_id_point,
            UserDraft.created_at,
            ContestPlayers.contest_player_id
        ).join(
            UserDraft,
            UserDraft.draft_match_series_id == CricketSeries.cricket_series_id
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).where(
            ContestPlayers.status == ContestStatusEnum.UPCOMING
        )

        series = await db.execute(series)
        return series.all()

    @classmethod
    async def series_status_to_completed(cls):
        series = select(
            CricketSeries.cricket_series_id,
            CricketSeries.series_id,
            CricketSeries.series_start_date,
            UserDraft.user_draft_id,
            UserDraft.match_id_point,
            UserDraft.created_at,
            ContestPlayers.contest_player_id
        ).join(
            UserDraft,
            UserDraft.draft_match_series_id == CricketSeries.cricket_series_id
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).where(
            ContestPlayers.status == ContestStatusEnum.LIVE
        )

        series = await db.execute(series)
        return series.all()

    @classmethod
    async def update_cricket_match_to_off(cls):
        ist_time = datetime.now() + timedelta(hours=5, minutes=30)
        await db.execute(
            update(
                CricketMatch
            ).where(
                CricketMatch.match_start_time <= ist_time
            ).values(
                {"is_live" : False}
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
    async def get_matchs_for_points(cls):
        data = select(
            CricketMatch.cricket_match_id,
            CricketMatch.match_id,
            CricketMatch.match_start_time,
        ).where(
            CricketMatch.is_point_added == False
        )

        data = await db.execute(data)
        return data.all()
    
    @classmethod
    async def update_match_point_status(cls, match_id, is_point_added):
        await db.execute(
            update(
                CricketMatch
            ).where(
                CricketMatch.match_id == match_id
            ).values(
                {"is_point_added": is_point_added}
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        await db.commit()
        return True

    @classmethod
    async def get_live_match(cls):
        data = select(
            CricketMatch.cricket_match_id,
            CricketMatch.match_id,
            CricketMatch.match_start_time,
            UserDraft.user_draft_id,
            ContestPlayers.contest_player_id
        ).join(
            UserDraft,
            UserDraft.draft_match_series_id == CricketMatch.cricket_match_id
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).where(
            ContestPlayers.status == ContestStatusEnum.LIVE
        )

        data = await db.execute(data)
        return data.all()
    
    @classmethod
    async def get_completed_match(cls, user_draft_id):
        data = select(
            CricketMatch.cricket_match_id,
            CricketMatch.match_id,
            CricketMatch.match_start_time,
            UserDraft.user_draft_id,
            UserDraft.league_name,
            ContestPlayers.contest_player_id
        ).join(
            UserDraft,
            UserDraft.draft_match_series_id == CricketMatch.cricket_match_id
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).where(
            UserDraft.user_draft_id == user_draft_id,
            ContestPlayers.status == ContestStatusEnum.COMPLETED,
            UserDraft.is_result_announce == False,
            UserDraft.is_draft_completed == True
        )

        data = await db.execute(data)
        return data.all()

    @classmethod
    async def get_completed_series(cls, user_draft_id):
        data = select(
            CricketSeries.cricket_series_id,
            CricketSeries.series_id,
            CricketSeries.series_start_date,
            UserDraft.user_draft_id,
            UserDraft.league_name,
            ContestPlayers.contest_player_id
        ).join(
            UserDraft,
            UserDraft.draft_match_series_id == CricketSeries.cricket_series_id
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).where(
            UserDraft.user_draft_id == user_draft_id,
            ContestPlayers.status == ContestStatusEnum.COMPLETED,
            UserDraft.is_result_announce == False,
            UserDraft.is_draft_completed == True
        )

        data = await db.execute(data)
        return data.all()

    @classmethod
    async def contest_match_status_change_to_live(cls, contest_player_id):
        await db.execute(
            update(
                ContestPlayers
            ).where(
                ContestPlayers.status == ContestStatusEnum.UPCOMING,
                ContestPlayers.contest_player_id == contest_player_id
            ).values(
                {"status": ContestStatusEnum.LIVE}
            ).execution_options(
                synchronize_session="fetch"
            )
        )
        try:
            await db.commit()
        except Exception as e:
            print(e)
            await db.rollback()
        return True

    @classmethod
    async def contest_match_status_change_to_completed(cls, contest_player_id):
        await db.execute(
            update(
                ContestPlayers
            ).where(
                ContestPlayers.status == ContestStatusEnum.LIVE,
                ContestPlayers.contest_player_id == contest_player_id
            ).values(
                {"status": ContestStatusEnum.COMPLETED}
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
    async def get_match_points(cls, cricket_player_id, cricket_match_id):
        data = select(
            CricketSeriesMatchPoints.points
        ).where(
            CricketSeriesMatchPoints.cricket_player_id == cricket_player_id,
            CricketSeriesMatchPoints.cricket_match_id == cricket_match_id
        )

        data = await db.execute(data)
        return data.scalars().one_or_none()

    @classmethod
    async def draft_starting_notification(cls):
        data = select(
            UserDraft.user_draft_id,
            UserDraft.draft_starting_time,
            UserDraft.max_playing_user,
            ContestPlayers.contest_player_id,
            ContestPlayers.user_id,
            User.email
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).join(
            User,
            User.user_id == ContestPlayers.user_id
        ).where(
            UserDraft.is_draft_pushed == False
        )

        data = await db.execute(data)
        return data.all()

    @classmethod
    async def draft_cancelled_notification(cls):
        data = select(
            UserDraft.user_draft_id,
            UserDraft.league_name,
            ContestPlayers.contest_player_id,
            ContestPlayers.user_id,
            User.email
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).join(
            User,
            User.user_id == ContestPlayers.user_id
        ).where(
            UserDraft.is_cancelled_pushed == False,
            UserDraft.is_draft_cancelled == True
        )

        data = await db.execute(data)
        return data.all()

    @classmethod
    async def draft_not_join_cancel(cls):
        data = select(
            UserDraft.user_draft_id,
            UserDraft.league_name,
            UserDraft.draft_starting_time,
            ContestPlayers.contest_player_id,
            ContestPlayers.user_id,
            User.email
        ).join(
            ContestPlayers,
            ContestPlayers.draft_id == UserDraft.user_draft_id
        ).join(
            User,
            User.user_id == ContestPlayers.user_id
        ).where(
            UserDraft.is_draft_cancelled == False,
            UserDraft.is_draft_completed == False,
            UserDraft.is_cancelled_pushed == False
        )

        data = await db.execute(data)
        return data.all()

    @classmethod
    async def get_team_name_with_series_id(cls, player_id, series_id):
        team_data = select(
            CricketSeriesSquad.team_id,
            CricketTeam.use_short_name,
            CricketTeam.fc_short_name,
            CricketTeam.short_name,
            CricketTeam.fc_logo_url,
            CricketTeam.use_logo_url,
            CricketTeam.logo_url
        ).join(
            CricketTeam,
            CricketTeam.cricket_team_id == CricketSeriesSquad.team_id
        ).where(
            CricketSeriesSquad.series_id == series_id,
            text(f"UUID('{player_id}')=ANY(cricket_series_squad.player_id)")
        )
        team_data = await db.execute(team_data)
        team_data = team_data.one_or_none()
        return team_data
