from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from src.common.exceptions import (
    ResourceNotFoundError,
    DuplicateUsernameError,
    UnAuthorizedError,
)
from src.web.api import posts, users, auth, drafts, global_posts

app = FastAPI(debug=True)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(drafts.router)
app.include_router(global_posts.router)


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_exception_handler(_, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.__str__()},
    )


@app.exception_handler(DuplicateUsernameError)
async def duplicate_username_exception_handler(_, exc: DuplicateUsernameError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.__str__()},
    )


@app.exception_handler(UnAuthorizedError)
async def unauthorized_exception_handle(*_):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )


from src.web.api import posts  # noqa: E402, F401
