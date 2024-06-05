# from fastapi-boilerplate.src.urls import controller\
from src.services.ping1.controller import Ping
from fastapi import APIRouter

router = APIRouter(prefix="/ping")

@router.get("/")
async def ping():
    return await Ping.ping()

