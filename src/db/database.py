#FastAPI Imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
#Local Imports
from src.config.config import Config

Base = declarative_base()
load_dotenv()

class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None
    def __getattr__(self, name):
        return getattr(self._session, name)
    def init(self):
        self._engine = create_async_engine(
            Config.DB_CONFIG,
            future=True,
            echo=True,
            pool_size=20,
            max_overflow=10
        )
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()
    async def create_all(self):
        self._engine.begin
            # async with self._engine.begin() as conn:
            #     await conn.run_sync(Base.metadata.create_all)

db=AsyncDatabaseSession()
