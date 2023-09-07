from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from src.common.exceptions import PostNotFoundError

app = FastAPI(debug=True)


@app.exception_handler(PostNotFoundError)
async def post_not_found_exception_handler(_, exc: PostNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.__str__()},
    )


from src.web.api import api  # noqa: E402, F401
