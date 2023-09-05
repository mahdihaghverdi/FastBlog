from sqlalchemy.ext.asyncio import create_async_engine

from src.web.config import settings

sqlalchemy_engine = create_async_engine(str(settings.database_url))
