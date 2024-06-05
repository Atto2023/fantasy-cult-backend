import os
from jose import  jwt
from fastapi import HTTPException, status
from fastapi import Depends, FastAPI, HTTPException
from dotenv import load_dotenv
from src.utils.constant import UserConstant

load_dotenv()


AUTHJWT_SECRET_KEY=os.getenv("AUTHJWT_SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

async def auth_check(authorize, token):
    if token.headers.get("Authorization"):
        jwt_token = token.headers.get("Authorization")
        jwt_token = jwt_token[7:]
        try:
            expire_time = jwt.decode(jwt_token,AUTHJWT_SECRET_KEY, algorithms=["HS256"],options={"verify_signature": False})
        except:
            raise HTTPException(
                detail='Token Expire!',
                status_code=status.HTTP_403_FORBIDDEN
            )
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            detail=UserConstant.ERROR_TOKEN,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
