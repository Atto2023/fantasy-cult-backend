from fastapi import (
    APIRouter, 
    Request, 
    Depends
)
from fastapi_jwt_auth import AuthJWT
from pydantic import constr,conint

from src.services.notification.controller import NotificationController

router = APIRouter(prefix="/v1/notification")

@router.get("")
async def get_notification(token: Request, authorize:AuthJWT=Depends(),limit: conint(ge=1) = 10, offset: conint(ge=1) = 1):
    return await NotificationController.get_notification(
        token=token,
        authorize=authorize,
        limit=limit,
        offset=offset
    )

@router.get("/read")
async def read_notification(token: Request, authorize:AuthJWT=Depends()):
    return await NotificationController.read_notification(
        token=token,
        authorize=authorize
    )

@router.get("/device")
async def add_user_device(device_token: constr(min_length=1), token: Request, authorize:AuthJWT=Depends()):
    return await NotificationController.add_user_device(
        device_token=device_token,
        token=token,
        authorize=authorize
    )

@router.get("/show_mark")
async def show_mark(token: Request, authorize:AuthJWT=Depends()):
    return await NotificationController.show_mark(
        token=token,
        authorize=authorize
    )