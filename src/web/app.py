from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from src.common.exceptions import ResourceNotFoundError
from src.web.api import posts

app = FastAPI(debug=True)

app.include_router(posts.router)


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_exception_handler(_, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.__str__()},
    )


from src.web.api import posts  # noqa: E402, F401
