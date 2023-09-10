from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestFormStrict
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.repository.unit_of_work import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService
from src.web.core.schemas import TokenSchema, UserLoginSchema
from src.web.core.config import settings
from src.web.core.dependencies import get_async_sessionmaker
from src.web.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(f"/{settings.access_token_url}", response_model=TokenSchema)
async def login_for_access_token(
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
):
    async with UnitOfWork(asessionmaker) as uow:
        repo = UserRepo(uow.session)
        service = UserService(repo)
        user = await service.authenticate(
            UserLoginSchema(
                username=form_data.username,
                password=form_data.password,
            ).model_dump(),
        )
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
