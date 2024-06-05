#FastAPI Imports
from typing import Optional
from pydantic import (
    UUID4, 
    constr,
    conint
)
from fastapi import (
    APIRouter, 
    Request, 
    Depends
)
from fastapi_jwt_auth import AuthJWT

#Local Imports
from src.services.admin.controller import AdminController
from src.services.cricket.controller import (
    CricketMatchController,
    DummyDataController
)

router = APIRouter(prefix="/v1/cricket")

@router.get('/add_dummy_data')
async def add_dummy_data():
    return await DummyDataController.add_dummy_data()

@router.get('/matches')
async def get_matches(token:Request, authorize:AuthJWT=Depends(), series_id: Optional[UUID4] = None, match_id: Optional[UUID4] = None, limit: conint(ge=1) = 10, offset: conint(ge=1) = 1): # type: ignore
    return await CricketMatchController.get_matches(
        series_id = series_id,
        match_id = match_id,
        token = token,
        authorize = authorize,
        limit=limit,
        offset=offset
    )

@router.get('/series')
async def get_series(token:Request, authorize:AuthJWT=Depends(), series_id: Optional[UUID4] = None, limit: conint(ge=1) = 10, offset: conint(ge=1) = 1): # type: ignore
    return await CricketMatchController.get_series(
        series_id = series_id,
        token = token,
        authorize = authorize,
        limit=limit,
        offset=offset
    )

@router.get('/match_point')
async def match_point():
    return await DummyDataController.match_point()

@router.get('/allocate_point')
async def allocate_point():
    return await DummyDataController.allocate_point()

@router.get('/get_matches_of_remaining_series')
async def get_matches_of_remaining_series(series_id: UUID4):
    return await  CricketMatchController.get_matches_of_remaining_series(
        series_id = series_id
    )

@router.get("/get_all_home_screen")
async def get_all_home_screen(token:Request, authorize:AuthJWT=Depends(), limit: int = 10, offset: int = 1):
    return await DummyDataController.get_all_home_screen(
        token = token,
        authorize = authorize,
        limit = limit,
        offset = offset
    )