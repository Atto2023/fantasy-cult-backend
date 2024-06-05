from http import HTTPStatus
from datetime import datetime


class Ping():

    @classmethod
    async def ping(cls):
        data = {
            "message" : datetime.now()
        }
        return data