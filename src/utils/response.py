from fastapi import (
    status,
    Response
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, conint, constr
from typing import Any


class SuccessResponseSerializer(BaseModel):
    status_code: conint() = status.HTTP_200_OK
    message: constr() = "Success"
    data: Any = None

class WebsocketSuccessResponseSerializer(SuccessResponseSerializer):
    response_type: conint()
    
class ErrorResponseSerializer(BaseModel):
    status_code: conint() = status.HTTP_400_BAD_REQUEST
    message: constr() = "Error"
    data: Any = None

class WebsocketErrorResponseSerializer(ErrorResponseSerializer):
    response_type: conint()

    
def response_structure(serializer, status_code):
    return Response(
        content = serializer.json(),
        media_type="application/json",
        status_code=status_code
    )