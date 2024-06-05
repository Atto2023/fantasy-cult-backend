#FastAPI Imports
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException

#Local Imports
from src.db import models
from src.db.database import db 
# from src.db.database import Base,engine
from src.urls.v1 import  cricket, user, contest, admin, payment, notification


def init_app():
    db.init()
    app = FastAPI(
        title="Fantasy Cult",
        description="Fantasy Cult",
        version="1",
    )
    @app.on_event("startup")
    async def startup():
        await db.create_all()
    @app.on_event("shutdown")
    async def shutdown():
        await db.close()
    
    @app.middleware("http")
    async def rollback_session_middleware(request, call_next):
        response = None
        try:
            response = await call_next(request)
        finally:
            # Check if there was an exception and if the session is active
            if response and response.status_code >= 500 and db._session.is_active:
                await db._session.rollback()
                await db._session.close()
                db.init()
            elif not response:
                await db._session.rollback()
                await db._session.close()
                db.init()

        return response

    # app.include_router(store_url.router)
    app.include_router(user.router, tags = ["Users"])
    app.include_router(cricket.router, tags = ['Cricket'])
    app.include_router(contest.router, tags = ['Contest'])
    app.include_router(admin.router, tags = ['Admin'])
    app.include_router(payment.router, tags = ['Payment'])
    app.include_router(notification.router, tags = ['Notification'])

    return app
app = init_app()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request:Request,exc:AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message":exc.message}
    )

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
