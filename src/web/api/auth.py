from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestFormStrict
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.repos.user_repo import UserRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.user_service import UserService
from src.web.core.dependencies import get_db
from src.web.core.schemas import TokenSchema, UserLoginSchema
from src.web.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/access-token", response_model=TokenSchema)
async def login_for_access_token(
    session: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
):
    async with UnitOfWork(session) as uow:
        repo = UserRepo(uow.session)
        service = UserService(repo)
        user = await service.authenticate(
            UserLoginSchema(
                username=form_data.username,
                password=form_data.password,
            ).model_dump(),
        )
        access_token = create_access_token(data={"sub": str(user["id"])})
        return {"access_token": access_token, "token_type": "bearer"}
