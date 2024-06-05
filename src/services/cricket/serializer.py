#Third Party Imports
from pydantic import (
    BaseModel, 
    constr,
    UUID4
)
from typing import Optional
from datetime import datetime

#Local Imports
from src.db.database import db

class ListAnySerializer(BaseModel):
    data: dict

class MatchListResponseSerializer(BaseModel):
    cricket_match_id: Optional[UUID4]
    cricket_series_id: Optional[UUID4]
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
    is_live: bool = False


class SeriesListResponseSerializer(BaseModel):
    series_start_date: Optional[datetime]
    series_start_day: Optional[constr()]
    series_name: Optional[constr()]
    cricket_series_id: UUID4
    is_live: bool = False
   